#!/usr/bin/env node
// node .claude/skills/worktree/scripts/new.mjs <nome> [--from <ref>]
//
// Cria .claude/worktrees/<nome> na branch wt/<nome>, partindo por padrao da
// branch que a arvore principal tem em checkout, e vincula node_modules quando
// o repositorio tiver um.
import fs from 'node:fs';
import { git, branchExists, currentBranch } from './lib/git.mjs';
import { mainRoot, worktreePath, worktreesDir, branchFor, linkNodeModules, NAME_RE } from './lib/paths.mjs';

// Windows corta em MAX_PATH (260). O prefixo .claude/worktrees/<nome>/ soma
// ~20 chars mais o nome. Um nome longo demais faz o checkout falhar pela metade:
// o worktree nasce com arquivos faltando, sem erro visivel depois.
const MAX_PATH = 250;
const WARN_PATH = 235;

function longestTrackedPath(root) {
  return git(['ls-files'], { cwd: root, quiet: true })
    .split(/\r?\n/)
    .reduce((max, file) => Math.max(max, file.length), 0);
}

function assertPathBudget(root, name) {
  const total = worktreePath(root, name).length + 1 + longestTrackedPath(root);
  if (total > MAX_PATH) {
    throw new Error(
      `o nome "${name}" estoura o MAX_PATH do Windows: o pior caminho ficaria com ${total} chars. ` +
        `Encurte o nome em pelo menos ${total - MAX_PATH} chars.`,
    );
  }
  if (total > WARN_PATH) {
    process.stdout.write(`! folga de MAX_PATH curta: pior caminho com ${total} de ${MAX_PATH} chars\n`);
  }
}

function parseArgs(argv, fallbackFrom) {
  const positional = [];
  let from = fallbackFrom;
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--from') {
      from = argv[i + 1];
      i += 1;
    } else {
      positional.push(argv[i]);
    }
  }
  return { name: positional[0], from };
}

function validate(root, name, from) {
  if (!name) throw new Error('uso: wt new <nome> [--from <ref>]');
  if (!NAME_RE.test(name)) throw new Error(`nome invalido: "${name}" (use letras, digitos, . _ -)`);
  if (!from) throw new Error('--from exige um ref');
  if (fs.existsSync(worktreePath(root, name))) throw new Error(`ja existe .claude/worktrees/${name}`);
  if (branchExists(root, branchFor(name))) throw new Error(`branch ${branchFor(name)} ja existe; escolha outro nome ou apague-a`);
  assertPathBudget(root, name);
}

function main() {
  const root = mainRoot();
  const { name, from } = parseArgs(process.argv.slice(2), currentBranch(root));
  validate(root, name, from);

  const dir = worktreePath(root, name);
  const branch = branchFor(name);
  fs.mkdirSync(worktreesDir(root), { recursive: true });

  git(['worktree', 'add', '-b', branch, dir, from], { cwd: root });
  const deps = linkNodeModules(root, dir);

  process.stdout.write(
    [
      '',
      `worktree : ${dir}`,
      `branch   : ${branch} (a partir de ${from})`,
      `deps     : ${deps.linked ? 'vinculo para o node_modules da raiz' : `sem vinculo (${deps.reason})`}`,
      '',
      'Abra o agente numa janela dedicada:',
      `  cd "${dir}" && claude`,
      '',
      'Dentro dele, ao terminar: git commit -am "..." e entao o merge da skill.',
      '',
    ].join('\n'),
  );
}

try {
  main();
} catch (err) {
  process.stderr.write(`\nwt new — ${err.message}\n\n`);
  process.exit(1);
}
