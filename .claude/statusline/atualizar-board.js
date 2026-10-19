#!/usr/bin/env node
// Processo destacado: consulta o gh e grava o cache de uma issue.
// Uso: node atualizar-board.js <owner/repo> <numero>
// A trava evita que uma rajada de eventos da statusline dispare varios gh ao mesmo tempo.
const fs = require("fs");
const path = require("path");
const { caminhoCache, lerJson, gravarJson } = require("./lib/estado");
const { consultar, travaOcupada } = require("./lib/board");

function travar(arquivoTrava, ref) {
  fs.mkdirSync(path.dirname(arquivoTrava), { recursive: true });
  if (fs.existsSync(arquivoTrava) && !travaOcupada(ref)) fs.rmSync(arquivoTrava, { force: true });
  try {
    fs.closeSync(fs.openSync(arquivoTrava, "wx"));
    return true;
  } catch {
    return false;
  }
}

// Falha mantem o ultimo valor bom, marcado com erro; consultadoEm avanca mesmo assim
// para a proxima tentativa respeitar a validade do cache em vez de martelar o gh.
function atualizar(ref) {
  const arquivo = caminhoCache(ref.repo, ref.numero);
  const anterior = lerJson(arquivo) || {};
  let novo;
  try {
    novo = { ...consultar(ref), erro: false };
  } catch {
    novo = { titulo: anterior.titulo || null, status: anterior.status || null, erro: true };
  }
  gravarJson(arquivo, { ...ref, ...novo, consultadoEm: Date.now() });
}

function main() {
  const [repo, numeroTexto] = process.argv.slice(2);
  const numero = Number(numeroTexto);
  if (!repo || !Number.isInteger(numero)) process.exit(1);
  const ref = { repo, numero };
  const arquivoTrava = `${caminhoCache(repo, numero)}.lock`;
  if (!travar(arquivoTrava, ref)) return;
  try {
    atualizar(ref);
  } finally {
    fs.rmSync(arquivoTrava, { force: true });
  }
}

main();
