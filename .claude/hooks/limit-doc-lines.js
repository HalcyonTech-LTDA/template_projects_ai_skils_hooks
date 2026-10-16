#!/usr/bin/env node
// Teto de linhas para documentacao: CLAUDE.md e todo .md de docs_projeto/.
// Modo hook (PostToolUse em Write|Edit): le o payload do stdin e, se o arquivo
// escrito passou do teto, sai com codigo 2 para o Claude dividir o arquivo.
// Modo varredura (`--all`): lista todos os violadores do repositorio.
const fs = require("fs");
const path = require("path");

const LIMITE = 300;
const DOCS_DIR = "docs_projeto/";
const IGNORAR = new Set([".git", "node_modules", ".obsidian"]);

function lerPayload() {
  try {
    return JSON.parse(fs.readFileSync(0, "utf8") || "{}");
  } catch {
    return {};
  }
}

function caminhoRelativo(raiz, arquivo) {
  return path.relative(raiz, path.resolve(raiz, arquivo)).split(path.sep).join("/");
}

function estaNoEscopo(relativo) {
  if (!relativo.toLowerCase().endsWith(".md")) return false;
  if (relativo.toLowerCase() === "claude.md") return true;
  return relativo.startsWith(DOCS_DIR);
}

function contarLinhas(arquivo) {
  const texto = fs.readFileSync(arquivo, "utf8");
  if (texto === "") return 0;
  const linhas = texto.split(/\r?\n/);
  return linhas[linhas.length - 1] === "" ? linhas.length - 1 : linhas.length;
}

function listarMarkdown(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) => {
    if (IGNORAR.has(d.name)) return [];
    const completo = path.join(dir, d.name);
    if (d.isDirectory()) return listarMarkdown(completo);
    return d.name.toLowerCase().endsWith(".md") ? [completo] : [];
  });
}

function mensagem(relativo, linhas) {
  return (
    `${relativo} tem ${linhas} linhas; o teto de documentacao e ${LIMITE}. ` +
    "Divida o arquivo agora: mova a secao mais autonoma para um arquivo irmao, " +
    "deixe um resumo com link no lugar e atualize quem apontava para ela. " +
    "Regra em docs_projeto/CONVENCOES.md secao 7."
  );
}

function modoHook() {
  const payload = lerPayload();
  const raiz = process.env.CLAUDE_PROJECT_DIR || payload.cwd || process.cwd();
  const arquivo = payload.tool_input && payload.tool_input.file_path;
  if (!arquivo || !fs.existsSync(arquivo)) return 0;
  const relativo = caminhoRelativo(raiz, arquivo);
  if (!estaNoEscopo(relativo)) return 0;
  const linhas = contarLinhas(arquivo);
  if (linhas <= LIMITE) return 0;
  process.stderr.write(mensagem(relativo, linhas));
  return 2;
}

function modoVarredura() {
  const raiz = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const violadores = listarMarkdown(raiz)
    .map((arquivo) => [caminhoRelativo(raiz, arquivo), arquivo])
    .filter(([relativo]) => estaNoEscopo(relativo))
    .map(([relativo, arquivo]) => [relativo, contarLinhas(arquivo)])
    .filter(([, linhas]) => linhas > LIMITE);
  violadores.forEach(([relativo, linhas]) => console.log(`${linhas}\t${relativo}`));
  if (violadores.length === 0) console.log(`Nenhum doc acima de ${LIMITE} linhas.`);
  return violadores.length === 0 ? 0 : 1;
}

process.exit(process.argv.includes("--all") ? modoVarredura() : modoHook());
