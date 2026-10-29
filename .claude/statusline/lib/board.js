// Status da issue no GitHub. A consulta ao gh leva ~1 s e a statusline e cancelada
// quando outro evento chega (debounce de 300 ms), entao ela nunca chama o gh: le o cache e,
// se ele estiver velho, dispara um processo destacado que o renova.
const fs = require("fs");
const path = require("path");
const { execFileSync, spawn } = require("child_process");
const { caminhoCache, lerJson } = require("./estado");
const { semRede, exigirRede } = require("./rede");

const VALIDADE_CACHE_MS = 60 * 1000;
const VALIDADE_TRAVA_MS = 30 * 1000;
const ATUALIZADOR = path.join(__dirname, "..", "atualizar-board.js");

function lerCache(ref) {
  return lerJson(caminhoCache(ref.repo, ref.numero));
}

function precisaAtualizar(cache, agora = Date.now()) {
  return !cache || agora - (cache.consultadoEm || 0) > VALIDADE_CACHE_MS;
}

function travaOcupada(ref, agora = Date.now()) {
  try {
    return agora - fs.statSync(`${caminhoCache(ref.repo, ref.numero)}.lock`).mtimeMs < VALIDADE_TRAVA_MS;
  } catch {
    return false;
  }
}

// Devolve se o atualizador foi disparado: nao dispara offline nem com a trava ocupada.
function disparar(ref) {
  if (semRede() || travaOcupada(ref)) return false;
  spawn(process.execPath, [ATUALIZADOR, ref.repo, String(ref.numero)], {
    detached: true,
    stdio: "ignore",
    windowsHide: true,
  }).unref();
  return true;
}

// Primeiro Project com status; sem Project, o estado da issue (open/closed).
function extrairStatus(issue) {
  const item = (issue.projectItems || []).find((p) => p.status && p.status.name);
  if (item) return item.status.name;
  return issue.state ? issue.state.toLowerCase() : null;
}

function verIssue(ref, campos) {
  exigirRede();
  const saida = execFileSync("gh", ["issue", "view", String(ref.numero), "-R", ref.repo, "--json", campos], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "ignore"],
    timeout: 10000,
    windowsHide: true,
    env: { ...process.env, GH_NO_UPDATE_NOTIFIER: "1", GH_PROMPT_DISABLED: "1" },
  });
  return JSON.parse(saida);
}

// Sem escopo de Project o gh recusa o pedido inteiro, entao tenta de novo sem projectItems
// para ainda mostrar titulo e open/closed.
function consultar(ref) {
  let issue;
  try {
    issue = verIssue(ref, "state,title,projectItems");
  } catch {
    issue = verIssue(ref, "state,title");
  }
  return { titulo: issue.title, status: extrairStatus(issue) };
}

module.exports = { lerCache, precisaAtualizar, travaOcupada, disparar, extrairStatus, consultar };
