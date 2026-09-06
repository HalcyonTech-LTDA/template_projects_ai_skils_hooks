// Fila de merge. mkdir e atomico em NTFS e em POSIX, entao serve de mutex
// entre processos `claude` que nao se conhecem.
import fs from 'node:fs';
import path from 'node:path';

const STALE_MS = 20 * 60 * 1000;
const OWNER_FILE = 'owner';

function sleepSync(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function readOwner(lockDir) {
  try {
    return fs.readFileSync(path.join(lockDir, OWNER_FILE), 'utf8').trim().replace(/\n/g, ' | ');
  } catch {
    return '(dono desconhecido)';
  }
}

function isStale(lockDir) {
  try {
    return Date.now() - fs.statSync(lockDir).mtimeMs > STALE_MS;
  } catch {
    return false;
  }
}

export function release(lockDir) {
  fs.rmSync(lockDir, { recursive: true, force: true });
}

export function acquire(lockDir, { timeoutMs = 15 * 60 * 1000, pollMs = 2000, owner = '', onWait } = {}) {
  const startedAt = Date.now();
  let warned = false;
  for (;;) {
    try {
      fs.mkdirSync(lockDir);
      fs.writeFileSync(
        path.join(lockDir, OWNER_FILE),
        `branch=${owner}\npid=${process.pid}\nts=${new Date().toISOString()}\n`,
      );
      return;
    } catch (err) {
      if (err.code !== 'EEXIST') throw err;
      if (isStale(lockDir)) {
        release(lockDir);
        continue;
      }
      if (Date.now() - startedAt > timeoutMs) {
        throw new Error(`fila de merge ocupada ha mais de ${Math.round(timeoutMs / 60000)} min por ${readOwner(lockDir)}`);
      }
      if (!warned) {
        warned = true;
        onWait?.(readOwner(lockDir));
      }
      sleepSync(pollMs);
    }
  }
}

export function withLock(lockDir, opts, fn) {
  acquire(lockDir, opts);
  try {
    return fn();
  } finally {
    release(lockDir);
  }
}
