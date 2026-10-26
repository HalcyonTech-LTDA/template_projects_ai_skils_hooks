import type { Job, Progress } from '../types'

export type Counts = Pick<
  Progress,
  'passed' | 'failed' | 'skipped' | 'suites' | 'total' | 'percent' | 'lines'
>

const RUNNERS = [
  /\b(?:pytest|py\.test|jest|vitest|mocha|ava|phpunit|rspec|ctest|unittest)\b/,
  /\b(?:npm|pnpm|yarn|bun)(?: run)? test\b/,
  /\bnode\b[^|;&]*\s--test\b/,
  /\b(?:playwright test|cypress run|go test|cargo (?:test|nextest)|dotnet test)\b/,
  /\bmvnw?\b[^|;&]*\b(?:test|verify|install)\b/,
  /\bgradlew?\b[^|;&]*\b(?:test|check|build)\b/,
]

// A lone `&` sends a job to the background: the wrap would wait on it.
const LONE_AMP = /(^|[^&>|<\d])&(?![&>])/

const ANSI = /\x1b\[[0-9;?]*[A-Za-z]/g

const PASS = [
  /^\s*(?:✓|✔|√)\s/,
  /^\s*ok \d/,
  /^\s*--- PASS:/,
  /^test .+ \.\.\. ok$/,
  /\s>\s.+\sPASSED$/,
  /::\S+\s+PASSED\b/,
  /^\s*Passed\s+\S/,
]

const FAIL = [
  /^\s*(?:✗|✖|×|✕|❌)\s/,
  /^\s*not ok \d/,
  /^\s*--- FAIL:/,
  /^test .+ \.\.\. FAILED$/,
  /\s>\s.+\sFAILED$/,
  /::\S+\s+(?:FAILED|ERROR)\b/,
  /^\s*Failed\s+\S/,
]

const SKIP = [/\s>\s.+\sSKIPPED$/, /::\S+\s+SKIPPED\b/, /^\s*--- SKIP:/]

export function classify(command: string): Job {
  if (!RUNNERS.some(re => re.test(command))) {
    return { kind: 'shell', label: 'Shell' }
  }

  return { kind: 'test', label: testLabel(command) }
}

function testLabel(command: string): string {
  if (/e2e|playwright|cypress/i.test(command)) return 'Testes e2e'
  if (/integra/i.test(command)) return 'Testes de integração'
  if (/unit/i.test(command)) return 'Testes unitários'

  return 'Testes'
}

export function shouldWrap(command: string, isBackground?: boolean): boolean {
  const isBlank = command.trim() === ''

  return !isBackground && !isBlank && !LONE_AMP.test(command) && !/\bexec\b/.test(command)
}

// The group runs in the current shell, so `cd` and `exit` behave as before;
// `wait $!` lets tee flush before the status is handed back.
export function wrap(command: string, logPath: string): string {
  const quoted = `'${logPath.replace(/'/g, `'\\''`)}'`

  return `{ ${command}\n} > >(tee ${quoted}) 2>&1; __cc_rc=$?; wait $! 2>/dev/null; (exit $__cc_rc)`
}

export function parse(raw: string, kind: Job['kind']): Counts {
  const text = raw.replace(ANSI, '')
  const lines = text.split(/\r\n|\r|\n/).filter(line => line.trim() !== '')
  const percent = lastPercent(text)

  if (kind === 'shell') {
    return { passed: 0, failed: 0, skipped: 0, suites: 0, total: null, percent, lines: lines.length }
  }

  const counted = countLines(lines)
  const summary = findSummary(text)

  return { ...counted, total: findTotal(text), ...summary, percent, lines: lines.length }
}

function countLines(lines: string[]) {
  const counts = { passed: 0, failed: 0, skipped: 0, suites: 0 }

  for (const line of lines) {
    addLine(counts, line)
  }

  return counts
}

function addLine(counts: Record<'passed' | 'failed' | 'skipped' | 'suites', number>, line: string) {
  const dots = /^(?:\S+\.py\s+)?([.FEsxX]+)\s*\[\s*\d+%\]\s*$|^\S+\.py\s+([.FEsxX]+)\s*$/.exec(line)
  const file = /^\s*(?:✓|❯|×)\s+\S+\s+\((\d+) tests?(?: \| (\d+) failed)?/.exec(line)
  const maven = /Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+).*\bin\b/.exec(line)

  if (dots) {
    const marks = dots[1] ?? dots[2] ?? ''
    counts.passed += (marks.match(/\./g) ?? []).length
    counts.failed += (marks.match(/[FE]/g) ?? []).length
    counts.skipped += (marks.match(/[sxX]/g) ?? []).length
  } else if (file) {
    const failed = Number(file[2] ?? 0)
    counts.passed += Number(file[1]) - failed
    counts.failed += failed
  } else if (maven) {
    const [run = 0, failures = 0, errors = 0, skipped = 0] = maven.slice(1).map(Number)
    counts.passed += run - failures - errors - skipped
    counts.failed += failures + errors
    counts.skipped += skipped
  } else if (FAIL.some(re => re.test(line))) {
    counts.failed += 1
  } else if (PASS.some(re => re.test(line))) {
    counts.passed += 1
  } else if (SKIP.some(re => re.test(line))) {
    counts.skipped += 1
  } else if (/^(?:PASS|FAIL)\s+\S/.test(line)) {
    counts.suites += 1
  }
}

function findTotal(text: string): number | null {
  const collected = /collected (\d+) items?/.exec(text)
  if (collected) return Number(collected[1])

  const running = [...text.matchAll(/running (\d+) tests?/g)]
  if (running.length > 0) return running.reduce((sum, m) => sum + Number(m[1]), 0)

  const plan = /^1\.\.(\d+)$/m.exec(text)

  return plan && Number(plan[1]) > 0 ? Number(plan[1]) : null
}

// The runner's closing line is the truth: it replaces what the lines counted.
function findSummary(text: string): Partial<Counts> {
  const jest = /^Tests:\s+(.*?\d+ total)/m.exec(text)
  if (jest) return fromWords(jest[1] ?? '', /(\d+) total/)

  const vitest = /^\s*Tests\s+(.*\((\d+)\))/m.exec(text)
  if (vitest) return fromWords(vitest[1] ?? '', /\((\d+)\)/)

  const node = /^(?:ℹ|#) tests (\d+)$/m.exec(text)
  if (node) return fromNode(text, Number(node[1]))

  const dotnet = /Failed:\s+(\d+), Passed:\s+(\d+), Skipped:\s+(\d+), Total:\s+(\d+)/.exec(text)
  if (dotnet) {
    const [failed = 0, passed = 0, skipped = 0, total = 0] = dotnet.slice(1).map(Number)
    return { failed, passed, skipped, total }
  }

  const maven = /^.*Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$/m.exec(text)
  if (maven) {
    const [total = 0, failures = 0, errors = 0, skipped = 0] = maven.slice(1).map(Number)
    return { total, failed: failures + errors, skipped, passed: total - failures - errors - skipped }
  }

  const pytest = /^=+ (.*\b(?:passed|failed)\b.*) in [\d.]+s/m.exec(text)

  return pytest ? fromWords(pytest[1] ?? '', null) : {}
}

function fromWords(line: string, totalRe: RegExp | null): Partial<Counts> {
  const word = (name: string) => Number(new RegExp(`(\\d+) ${name}`).exec(line)?.[1] ?? 0)
  const passed = word('passed')
  const failed = word('failed') + word('errors?')
  const skipped = word('skipped')
  const total = totalRe ? Number(totalRe.exec(line)?.[1]) : passed + failed + skipped

  return { passed, failed, skipped, total }
}

function fromNode(text: string, total: number): Partial<Counts> {
  const value = (name: string) => Number(new RegExp(`^(?:ℹ|#) ${name} (\\d+)$`, 'm').exec(text)?.[1] ?? 0)

  return { total, passed: value('pass'), failed: value('fail'), skipped: value('skipped') }
}

function lastPercent(text: string): number | null {
  const tail = text.slice(-4000)
  const found = [...tail.matchAll(/(\d{1,3}(?:[.,]\d+)?)\s?%/g)]
    .map(m => Number((m[1] ?? '').replace(',', '.')))
    .filter(value => value <= 100)

  const last = found.at(-1)

  return last === undefined ? null : Math.round(last)
}

export function describe(p: Progress): string | null {
  if (p.kind === 'shell') {
    if (p.percent !== null) return `Shell ${p.percent}%`

    return p.lines > 0 ? `Shell · ${p.lines} linhas` : null
  }

  const done = p.passed + p.failed + p.skipped
  const fails = p.failed > 0 ? ` · ${p.failed} ${p.failed === 1 ? 'falha' : 'falhas'}` : ''

  if (p.total !== null) return `${p.label} ${Math.min(done, p.total)}/${p.total}${fails}`
  if (done > 0) return `${p.label} ${done} feitos${fails}`
  if (p.percent !== null) return `${p.label} ${p.percent}%`
  if (p.suites > 0) return `${p.label} · ${p.suites} arquivos`

  return `${p.label} 0/?`
}
