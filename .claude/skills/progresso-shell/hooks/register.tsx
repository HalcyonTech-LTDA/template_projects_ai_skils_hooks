import type { EngineInterface, Register } from 'claude-code'

import type { Job, Progress } from '../types'
import { classify, describe, hasResult, parse, shouldWrap, wrap } from './parse'

const TICK_MS = 1000

// Module state: a reload drops it, and the next command sets it again.
let activeId: string | undefined
let lastTest: string | undefined

async function prepareLog($: EngineInterface, id: string): Promise<string> {
  const tmp = (await $.env.get('TEMP')) ?? (await $.env.get('TMPDIR')) ?? '/tmp'
  const path = `${tmp.replace(/\\/g, '/')}/claude-progresso/${id}.log`
  await $.fs.write(path, '')

  return path
}

function fresh(id: string, job: Job): Progress {
  return { ...job, id, passed: 0, failed: 0, skipped: 0, suites: 0, total: null, percent: null, lines: 0 }
}

async function readLog($: EngineInterface, path: string, base: Progress): Promise<Progress> {
  const text = await $.fs.read(path).catch(() => undefined)

  return typeof text === 'string' ? { ...base, ...parse(text, base.kind) } : base
}

// While a command runs, its line; with nothing to say, the last test result.
function show($: EngineInterface, progress: Progress) {
  if (progress.id !== activeId) return

  const text = describe(progress)
  $.ui.status(text === null ? lastTest : `▶ ${text}`)
}

// A finished test run stays pinned until the next one, so it does not flash by.
function finish($: EngineInterface, progress: Progress) {
  if (progress.id !== activeId) return

  activeId = undefined
  const text = progress.kind === 'test' && hasResult(progress) ? describe(progress) : null
  if (text !== null) lastTest = `${progress.failed > 0 ? '✖' : '✔'} ${text}`
  $.ui.status(lastTest)
}

async function tick($: EngineInterface, path: string, base: Progress) {
  show($, await readLog($, path, base))
}

export const register: Register = on => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    if (!shouldWrap(e.command, e.run_in_background)) return next(e)

    const path = await prepareLog($, e.tool_use_id)
    const base = fresh(e.tool_use_id, classify(e.command))
    activeId = base.id
    show($, base)
    const timer = $.clock.every(TICK_MS, () => void tick($, path, base))

    try {
      return await next({ ...e, command: wrap(e.command, path) })
    } finally {
      timer.cancel()
      finish($, await readLog($, path, base))
      await $.fs.write(path, '').catch(() => undefined)
    }
  }).catch(($, e, next) => next(e))
}
