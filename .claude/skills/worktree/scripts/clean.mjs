#!/usr/bin/env node
// node .claude/skills/worktree/scripts/clean.mjs                      (lista)
// node .claude/skills/worktree/scripts/clean.mjs --remove <nome> [--force]
// node .claude/skills/worktree/scripts/clean.mjs --prune
import fs from 'node:fs';
import path from 'node:path';
import { git, gitTry, hasTrackedChanges, isMergedInto, branchExists, currentBranch } from './lib/git.mjs';
import { mainRoot, managedWorktrees, unlinkNodeModules, isLinkedNodeModules } from './lib/paths.mjs';

function inspect(root, wt, target) {
  return {
    name: path.basename(wt.path),
    path: wt.path,
    branch: wt.branch ?? '(destacado)',
    locked: wt.locked,
    dirty: hasTrackedChanges(wt.path),
    merged: wt.branch ? isMergedInto(root, wt.branch, target) : false,
    linked: isLinkedNodeModules(wt.path),
  };
}

function list(root, target) {
  const rows = managedWorktrees(root).map((wt) => inspect(root, wt, target));
  if (rows.length === 0) {
    process.stdout.write('\nnenhum worktree em .claude/worktrees/\n\n');
    return;
  }
  process.stdout.write('\n');
  for (const r of rows) {
    const flags = [
      r.dirty ? 'SUJO' : 'limpo',
      r.merged ? `ja em ${target}` : 'pendente',
      r.locked ? 'LOCKED' : null,
      r.linked ? 'deps=vinculo' : 'deps=proprias/ausentes',
    ].filter(Boolean);
    process.stdout.write(`${r.name.padEnd(28)} ${r.branch.padEnd(34)} ${flags.join(' \u00b7 ')}\n`);
  }
  process.stdout.write('\n');
}

function assertRemovable(r, force, target) {
  if (force) return;
  if (r.dirty) throw new Error(`${r.name} tem alteracoes nao commitadas. Commite, ou repita com --force.`);
  if (!r.merged) throw new Error(`${r.name} (${r.branch}) ainda nao entrou em ${target}. Rode o merge da skill, ou repita com --force para descartar.`);
}

// No Windows `git worktree remove` desregistra e SO ENTAO apaga o diretorio.
// Se algum shell tiver o cwd la dentro, o rmdir falha com o registro ja desfeito.
// Nesse caso terminamos a limpeza no lugar do git em vez de abortar pela metade.
function dropWorktreeDir(root, wt, force) {
  const res = gitTry(['worktree', 'remove', ...(force ? ['--force'] : []), wt.path], { cwd: root });
  if (res.ok) return 'removido';
  if (managedWorktrees(root).some((w) => w.path === wt.path)) {
    throw new Error(`git recusou remover ${path.basename(wt.path)}:\n${res.out}`);
  }
  try {
    fs.rmSync(wt.path, { recursive: true, force: true });
    return 'removido (diretorio apagado fora do git)';
  } catch {
    return `desregistrado, mas o diretorio ficou em disco: ${wt.path}\n  Feche shells abertos nele, apague a mao e rode o clean com --prune`;
  }
}

function dropBranch(root, wt, merged) {
  if (!wt.branch || !branchExists(root, wt.branch)) return;
  const res = gitTry(['branch', merged ? '-d' : '-D', wt.branch], { cwd: root });
  process.stdout.write(res.ok ? `branch ${wt.branch} apagada\n` : `branch ${wt.branch} mantida (${res.out})\n`);
}

function remove(root, name, force, target) {
  const wt = managedWorktrees(root).find((w) => path.basename(w.path) === name);
  if (!wt) throw new Error(`worktree "${name}" nao encontrado em .claude/worktrees/`);
  const r = inspect(root, wt, target);
  assertRemovable(r, force, target);

  // Ordem importa: o vinculo sai antes, para que a remocao do diretorio
  // nao tenha chance de descer ate o node_modules real da raiz.
  if (unlinkNodeModules(wt.path)) process.stdout.write(`vinculo node_modules removido de ${name}\n`);
  if (r.locked) gitTry(['worktree', 'unlock', wt.path], { cwd: root });

  process.stdout.write(`worktree ${name} ${dropWorktreeDir(root, wt, force)}\n`);
  dropBranch(root, wt, r.merged);
}

function main() {
  const argv = process.argv.slice(2);
  const root = mainRoot();
  const target = currentBranch(root);
  const force = argv.includes('--force');

  if (argv.includes('--prune')) {
    git(['worktree', 'prune', '-v'], { cwd: root });
    return;
  }
  const i = argv.indexOf('--remove');
  if (i !== -1) {
    const name = argv[i + 1];
    if (!name || name.startsWith('--')) throw new Error('uso: wt clean --remove <nome> [--force]');
    remove(root, name, force, target);
    return;
  }
  list(root, target);
}

try {
  main();
} catch (err) {
  process.stderr.write(`\nwt clean — ${err.message}\n\n`);
  process.exit(1);
}
