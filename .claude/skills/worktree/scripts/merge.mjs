#!/usr/bin/env node
// node .claude/skills/worktree/scripts/merge.mjs [--skip-tests]
//
// Rodado DE DENTRO de um worktree. Serializa o retorno para a branch alvo via
// lock, rebaseia, roda os portoes e faz fast-forward. Nunca da checkout da
// branch alvo dentro do worktree: git proibe, e e essa proibicao que evita a
// colisao entre sessoes.
import path from 'node:path';
import { git, gitTry, hasTrackedChanges, currentBranch, changedFiles, dirtyFiles } from './lib/git.mjs';
import { mainRoot, managedWorktrees } from './lib/paths.mjs';
import { detectGates } from './lib/gates.mjs';
import { withLock } from './lib/lock.mjs';
import { run } from './lib/run.mjs';

// O lock mora no git dir compartilhado, visivel a todos os worktrees do repo.
function gitCommonDir(root) {
  return path.resolve(root, git(['rev-parse', '--git-common-dir'], { cwd: root, quiet: true }));
}

// O alvo e a branch que a arvore principal tem em checkout — nao um nome fixo.
function resolveTarget(root) {
  const target = currentBranch(root);
  if (target === 'HEAD') throw new Error('a arvore principal esta em HEAD destacado; de checkout na branch alvo antes');
  return target;
}

function resolveContext() {
  const root = mainRoot();
  const here = process.cwd();
  const wt = managedWorktrees(root).find((w) => here === w.path || here.startsWith(w.path + path.sep));
  if (!wt) throw new Error(`rode este comando de dentro de um worktree em .claude/worktrees/ (cwd: ${here})`);
  if (!wt.branch) throw new Error('worktree em HEAD destacado; crie uma branch antes de mesclar');
  return { root, dir: wt.path, branch: wt.branch, target: resolveTarget(root) };
}

// A arvore principal nao precisa estar limpa: so precisa nao ter edicao pendente
// nos MESMOS arquivos que o fast-forward vai reescrever. E a condicao que o
// proprio git aplicaria, dita antes para o erro sair legivel.
function assertMainTreeAccepts(root, touched) {
  const pending = new Set(dirtyFiles(root));
  const colisoes = touched.filter((f) => pending.has(f));
  if (colisoes.length === 0) return;
  const lista = colisoes.map((f) => `  ${f}`).join('\n');
  throw new Error(
    `a arvore principal tem edicao pendente nos arquivos que este merge reescreve:\n${lista}\n` +
      'Commite ou guarde essas alteracoes antes de mesclar.',
  );
}

function warnIfDepsChanged(touched) {
  if (!touched.some((f) => f === 'package.json' || f === 'package-lock.json')) return;
  process.stdout.write('\n! esta branch altera dependencias — node_modules e um vinculo para a raiz.\n');
  process.stdout.write('  Rode "npm ci" na arvore principal depois do merge.\n');
}

function assertReady({ root, dir, branch, target }) {
  if (hasTrackedChanges(dir)) throw new Error('ha alteracoes nao commitadas neste worktree; commite antes de mesclar');
  if (currentBranch(root) !== target) throw new Error(`a arvore principal saiu de "${target}"; refaca o comando`);
  const touched = changedFiles(root, target, branch);
  assertMainTreeAccepts(root, touched);
  warnIfDepsChanged(touched);
}

function rebaseOntoTarget({ dir, branch, target }) {
  const res = gitTry(['rebase', target], { cwd: dir });
  if (res.ok) return;
  gitTry(['rebase', '--abort'], { cwd: dir });
  throw new Error(`rebase de ${branch} sobre ${target} conflitou. Resolva no worktree com "git rebase ${target}".\n\n${res.out}`);
}

function runGates({ dir }, { skipTests }) {
  const { gates, skipped } = detectGates(dir);
  if (skipped) {
    process.stdout.write(`\n> portoes: nenhum (${skipped})\n`);
    return;
  }
  for (const gate of gates) {
    if (skipTests && gate.skippable) {
      process.stdout.write(`\n> ${gate.label}: PULADO por --skip-tests\n`);
      continue;
    }
    run(gate.cmd, { cwd: dir, label: gate.label });
  }
}

function fastForward({ root, branch }) {
  git(['merge', '--ff-only', branch], { cwd: root });
}

function main() {
  const skipTests = process.argv.includes('--skip-tests');
  const ctx = resolveContext();
  assertReady(ctx);

  const lockDir = path.join(gitCommonDir(ctx.root), 'wt-merge.lock');
  withLock(
    lockDir,
    { owner: ctx.branch, onWait: (who) => process.stdout.write(`\naguardando a fila de merge (ocupada por ${who})...\n`) },
    () => {
      assertReady(ctx); // o dono anterior da fila acabou de mover a branch alvo
      rebaseOntoTarget(ctx);
      runGates(ctx, { skipTests });
      fastForward(ctx);
    },
  );

  process.stdout.write(
    `\n${ctx.branch} entrou em ${ctx.target} por fast-forward.\n` +
      `Limpeza: node .claude/skills/worktree/scripts/clean.mjs --remove ${path.basename(ctx.dir)}\n\n`,
  );
}

try {
  main();
} catch (err) {
  process.stderr.write(`\nwt merge — ${err.message}\n\n`);
  process.exit(1);
}
