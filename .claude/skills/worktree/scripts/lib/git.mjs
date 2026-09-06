// Camada fina sobre o executavel `git`. Nenhuma regra de negocio mora aqui.
import { execFileSync } from 'node:child_process';
import path from 'node:path';

export function git(args, { cwd = process.cwd(), quiet = false } = {}) {
  return execFileSync('git', args, {
    cwd,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', quiet ? 'pipe' : 'inherit'],
  }).trim();
}

// Variante que nao lanca: devolve { ok, out } com stdout+stderr concatenados.
export function gitTry(args, opts = {}) {
  try {
    return { ok: true, out: git(args, { ...opts, quiet: true }) };
  } catch (err) {
    return { ok: false, out: `${err.stdout ?? ''}${err.stderr ?? ''}`.trim() };
  }
}

// Apenas arquivos rastreados. O `?? .claude/worktrees/` da raiz nao conta como sujeira.
export function hasTrackedChanges(cwd) {
  return git(['status', '--porcelain', '--untracked-files=no'], { cwd, quiet: true }) !== '';
}

export function currentBranch(cwd) {
  return git(['rev-parse', '--abbrev-ref', 'HEAD'], { cwd, quiet: true });
}

export function branchExists(cwd, branch) {
  return gitTry(['rev-parse', '--verify', `refs/heads/${branch}`], { cwd }).ok;
}

export function isMergedInto(cwd, branch, target) {
  const out = git(['branch', '--merged', target], { cwd, quiet: true });
  return out.split('\n').some((l) => l.replace(/^[*+]/, '').trim() === branch);
}

export function changedFiles(cwd, base, head) {
  const out = git(['diff', '--name-only', `${base}...${head}`], { cwd, quiet: true });
  return out === '' ? [] : out.split('\n');
}

// Le `git worktree list --porcelain` uma vez e devolve tudo que os comandos precisam.
export function listWorktrees(cwd = process.cwd()) {
  const out = git(['worktree', 'list', '--porcelain'], { cwd, quiet: true });
  const entries = [];
  let cur = null;
  for (const line of out.split('\n')) {
    if (line.startsWith('worktree ')) {
      cur = { path: path.resolve(line.slice('worktree '.length).trim()), locked: false, detached: false };
      entries.push(cur);
    } else if (!cur) {
      continue;
    } else if (line.startsWith('branch ')) {
      cur.branch = line.slice('branch '.length).trim().replace('refs/heads/', '');
    } else if (line === 'locked' || line.startsWith('locked ')) {
      cur.locked = true;
    } else if (line === 'detached') {
      cur.detached = true;
    }
  }
  return entries;
}

// Arquivos rastreados com alteracao (staged ou nao), sem os untracked.
export function dirtyFiles(cwd) {
  const out = git(['status', '--porcelain', '--untracked-files=no'], { cwd, quiet: true });
  return out === '' ? [] : out.split(/\r?\n/).map((l) => l.slice(3).trim());
}
