// Resolucao de caminhos e do vinculo node_modules. Isolado porque o vinculo
// e a unica parte que depende do sistema operacional.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { listWorktrees } from './git.mjs';

export const WT_PREFIX = 'wt/';
export const NAME_RE = /^[A-Za-z0-9][A-Za-z0-9._-]{0,48}$/;

// Windows nao diferencia maiuscula no caminho (e a letra do drive varia).
function mesmoCaminho(a, b) {
  return process.platform === 'win32' ? a.toLowerCase() === b.toLowerCase() : a === b;
}

// Repositorio a que esta copia da skill pertence, quando ela esta no lugar
// canonico. Serve so para detectar invocacao cruzada entre repos.
function repoOwningThisSkill() {
  const lib = path.dirname(fileURLToPath(import.meta.url));
  const esperado = path.join('.claude', 'skills', 'worktree', 'scripts', 'lib');
  const raiz = path.resolve(lib, '..', '..', '..', '..', '..');
  return mesmoCaminho(path.join(raiz, esperado), lib) ? raiz : null;
}

// A primeira entrada de `git worktree list` e sempre a arvore principal.
export function mainRoot(cwd = process.cwd()) {
  const root = listWorktrees(cwd)[0].path;
  const dono = repoOwningThisSkill();
  if (dono && !mesmoCaminho(dono, root)) {
    process.stderr.write(
      `! atencao: esta skill vive em ${dono}, mas o diretorio atual pertence a ${root}.
` +
        `  O comando vai agir sobre ${root}. Se nao era isso, use "cd" antes.
`,
    );
  }
  return root;
}

export function worktreesDir(root) {
  return path.join(root, '.claude', 'worktrees');
}

export function worktreePath(root, name) {
  return path.join(worktreesDir(root), name);
}

export function branchFor(name) {
  return `${WT_PREFIX}${name}`;
}

// Worktrees gerenciados por estes scripts: os que vivem sob .claude/worktrees/.
export function managedWorktrees(cwd = process.cwd()) {
  const all = listWorktrees(cwd);
  const dir = worktreesDir(all[0].path);
  return all.slice(1).filter((w) => w.path.startsWith(dir + path.sep));
}

function nodeModulesLink(dir) {
  return path.join(dir, 'node_modules');
}

// Junction no Windows (nao exige admin nem Developer Mode); symlink de dir no resto.
// Repositorio sem node_modules (uma vault de documentacao, por exemplo) nao e erro:
// o worktree simplesmente nasce sem vinculo.
export function linkNodeModules(root, dir) {
  const target = path.join(root, 'node_modules');
  if (!fs.existsSync(target)) return { linked: false, reason: 'a arvore principal nao tem node_modules' };
  const link = nodeModulesLink(dir);
  if (fs.existsSync(link)) return { linked: true, link, created: false };
  fs.symlinkSync(target, link, 'junction');
  return { linked: true, link, created: true };
}

// Remove SO o vinculo, nunca o alvo. Chamado antes de `git worktree remove`,
// que apagaria o diretorio e poderia descer pela junction.
export function unlinkNodeModules(dir) {
  const link = nodeModulesLink(dir);
  let st;
  try {
    st = fs.lstatSync(link);
  } catch {
    return false;
  }
  if (!st.isSymbolicLink()) return false; // node_modules real: nao mexemos
  try {
    fs.unlinkSync(link);
  } catch {
    fs.rmdirSync(link);
  }
  return true;
}

export function isLinkedNodeModules(dir) {
  try {
    return fs.lstatSync(nodeModulesLink(dir)).isSymbolicLink();
  } catch {
    return false;
  }
}
