// Descobre o que rodar antes de devolver o trabalho para a branch alvo.
// Um repositorio de documentacao nao tem portao nenhum e isso nao e erro.
import fs from 'node:fs';
import path from 'node:path';

function readScripts(dir) {
  const pkg = path.join(dir, 'package.json');
  if (!fs.existsSync(pkg)) return null;
  try {
    return JSON.parse(fs.readFileSync(pkg, 'utf8')).scripts ?? {};
  } catch {
    return {};
  }
}

function typecheckGate(dir, scripts) {
  if (scripts.typecheck) return { cmd: 'npm run typecheck', label: 'typecheck', skippable: false };
  if (fs.existsSync(path.join(dir, 'tsconfig.json'))) return { cmd: 'npx tsc --noEmit', label: 'typecheck', skippable: false };
  return null;
}

function testGate(scripts) {
  return scripts.test ? { cmd: 'npm test', label: 'testes', skippable: true } : null;
}

export function detectGates(dir) {
  const scripts = readScripts(dir);
  if (scripts === null) return { gates: [], skipped: 'repositorio sem package.json' };
  if (!fs.existsSync(path.join(dir, 'node_modules'))) {
    return { gates: [], skipped: 'node_modules ausente neste worktree' };
  }
  return { gates: [typecheckGate(dir, scripts), testGate(scripts)].filter(Boolean), skipped: null };
}
