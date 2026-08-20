// Execucao de comandos de projeto (npx/npm), com stdio herdado para o agente
// ver a saida do jest e do tsc em tempo real.
import { spawnSync } from 'node:child_process';

export function run(command, { cwd, label }) {
  process.stdout.write(`\n> ${label ?? command}\n`);
  const res = spawnSync(command, { cwd, stdio: 'inherit', shell: true });
  if (res.status !== 0) {
    throw new Error(`${label ?? command} falhou (exit ${res.status ?? 'sinal ' + res.signal})`);
  }
}
