import { expect, test } from 'claude-code/testing'

import type { Job } from '../types'
import { classify, describe, hasResult, parse, resultLine, runningLine, shouldWrap, wrap } from './parse'

function show(output: string, job: Job) {
  return describe({ ...job, id: 't', ...parse(output, job.kind) })
}

const TESTS: Job = { kind: 'test', label: 'Testes' }
const SHELL: Job = { kind: 'shell', label: 'Shell' }

test('classify separa teste de shell e nomeia o tipo de teste', async () => {
  expect(classify('npm test').kind).toBe('test')
  expect(classify('cd api && ./gradlew test').kind).toBe('test')
  expect(classify('go test ./...').kind).toBe('test')
  expect(classify('node --test tests/').kind).toBe('test')
  expect(classify('pytest tests/unit').label).toBe('Testes unitários')
  expect(classify('npx playwright test').label).toBe('Testes e2e')
  expect(classify('ls -la')).toEqual({ kind: 'shell', label: 'Shell' })
  expect(classify('git log --grep test').kind).toBe('shell')
  expect(classify('python -m pytest -q').kind).toBe('test')
  expect(classify('FOO=1 npx vitest run').kind).toBe('test')
  expect(classify('make build | tee out.log; yarn test').kind).toBe('test')
})

test('regressao: runner citado em texto nao e teste', async () => {
  expect(classify('git commit -m "add pytest and unit tests"').kind).toBe('shell')
  expect(classify("gh pr create --body 'runs node --test and jest'").kind).toBe('shell')
  const heredoc = 'git commit -m "$(cat <<\'MSG\'\nfeat: parse pytest, jest, vitest\n- Testes unitários\nMSG\n)"'
  expect(classify(heredoc).kind).toBe('shell')
  expect(classify('echo pytest').kind).toBe('shell')
})

test('regressao: teste que terminou sem contar nada nao vira resultado', async () => {
  const empty = { kind: 'test' as const, label: 'Testes', id: 't', ...parse('', 'test') }
  expect(hasResult(empty)).toBe(false)
  expect(hasResult({ ...empty, passed: 1 })).toBe(true)
  expect(hasResult({ ...empty, total: 3 })).toBe(true)
})

test('shouldWrap recusa background, & solto, exec e comando vazio', async () => {
  expect(shouldWrap('npm test 2>&1 | head')).toBe(true)
  expect(shouldWrap('a && b &> out.txt')).toBe(true)
  expect(shouldWrap('npm run dev &')).toBe(false)
  expect(shouldWrap('npm test', true)).toBe(false)
  expect(shouldWrap('exec bash')).toBe(false)
  expect(shouldWrap('   ')).toBe(false)
})

test('wrap fecha o grupo numa linha propria e escapa aspas do caminho', async () => {
  const out = wrap('npm test # fim', "/tmp/a'b.log")
  expect(out.startsWith('{ npm test # fim\n} > >(tee ')).toBe(true)
  expect(out).toContain(`'/tmp/a'\\''b.log'`)
  expect(out.endsWith('(exit $__cc_rc)')).toBe(true)
})

test('pytest: total do collected e pontos ao vivo', async () => {
  const out = 'collected 12 items\n\ntests/test_a.py ..F.  [ 33%]\n'
  expect(show(out, TESTS)).toBe('Testes 4/12 · 1 falha')
})

test('pytest -q sem nome de arquivo', async () => {
  expect(show('collected 5 items\n...s. [100%]\n', TESTS)).toBe('Testes 5/5')
})

test('jest: o resumo final manda', async () => {
  const out = 'PASS src/a.test.js\nFAIL src/b.test.js\nTests:       2 failed, 10 passed, 12 total\n'
  expect(show(out, TESTS)).toBe('Testes 12/12 · 2 falhas')
})

test('jest sem resumo ainda: conta arquivos', async () => {
  expect(show('PASS src/a.test.js\nPASS src/b.test.js\n', TESTS)).toBe('Testes · 2 arquivos')
})

test('vitest: linha por arquivo com contagem', async () => {
  const out = ' ✓ src/a.test.ts (5 tests) 3ms\n ❯ src/b.test.ts (4 tests | 1 failed) 9ms\n'
  expect(show(out, TESTS)).toBe('Testes 9 feitos · 1 falha')
})

test('node --test: marcas ao vivo e resumo no fim', async () => {
  expect(show('✔ soma (1ms)\n✖ divide (2ms)\n', TESTS)).toBe('Testes 2 feitos · 1 falha')
  const done = '✔ soma (1ms)\nℹ tests 3\nℹ pass 3\nℹ fail 0\n'
  expect(show(done, TESTS)).toBe('Testes 3/3')
})

test('maven: soma por classe e o resumo final', async () => {
  const live = 'Tests run: 3, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 0.1 s -- in com.x.ATest\n'
  expect(show(live, TESTS)).toBe('Testes 3 feitos · 1 falha')
  const end = `${live}Results:\nTests run: 8, Failures: 1, Errors: 0, Skipped: 1\n`
  expect(show(end, TESTS)).toBe('Testes 8/8 · 1 falha')
})

test('gradle, go e cargo', async () => {
  expect(show('ATest > soma() PASSED\nATest > div() FAILED\n', TESTS)).toBe('Testes 2 feitos · 1 falha')
  expect(show('--- PASS: TestA (0.00s)\n--- PASS: TestB (0.00s)\n', TESTS)).toBe('Testes 2 feitos')
  const cargo = 'running 2 tests\ntest a ... ok\nrunning 1 test\ntest b ... FAILED\n'
  expect(show(cargo, TESTS)).toBe('Testes 2/3 · 1 falha')
})

test('dotnet: linha de resumo', async () => {
  const out = 'Failed!  - Failed:     1, Passed:    11, Skipped:     0, Total:    12, Duration: 1 s\n'
  expect(show(out, TESTS)).toBe('Testes 12/12 · 1 falha')
})

test('teste sem saida ainda', async () => {
  expect(show('', TESTS)).toBe('Testes 0/?')
})

test('cores ANSI nao atrapalham', async () => {
  expect(show('\x1b[32m✓\x1b[39m soma\n', TESTS)).toBe('Testes 1 feitos')
})

test('shell: ultimo percentual, senao linhas, senao nada', async () => {
  expect(show('Baixando 10%\rBaixando 45%\r', SHELL)).toBe('Shell 45%')
  expect(show('a\nb\n\nc\n', SHELL)).toBe('Shell · 3 linhas')
  expect(show('uso 250%\n', SHELL)).toBe('Shell · 1 linhas')
  expect(show('', SHELL)).toBe(null)
})

test('regressao: shell que termina limpa a linha em vez de repetir teste antigo', async () => {
  const shell = { ...SHELL, id: 's', ...parse('a\nb\n', 'shell') }
  expect(runningLine(shell)).toBe('▶ Shell · 2 linhas')
  expect(resultLine(shell)).toBe(undefined)
  expect(runningLine({ ...SHELL, id: 's', ...parse('', 'shell') })).toBe(undefined)
})

test('resultado de teste: marca de sucesso ou falha, e nada sem contagem', async () => {
  const ok = { ...TESTS, id: 't', ...parse('collected 2 items\nt.py .. [100%]\n', 'test') }
  expect(resultLine(ok)).toBe('✔ Testes 2/2')
  const bad = { ...TESTS, id: 't', ...parse('✔ a\n✖ b\n', 'test') }
  expect(resultLine(bad)).toBe('✖ Testes 2 feitos · 1 falha')
  expect(resultLine({ ...TESTS, id: 't', ...parse('', 'test') })).toBe(undefined)
})
