// Estado da statusline: qual issue cada sessao trabalha e o cache do board.
// Fica fora do repo, sob o home, porque o hook, a CLI e a statusline rodam com cwd
// diferentes (checkout principal x worktree). O session_id e unico, entao basta ele.
const fs = require("fs");
const os = require("os");
const path = require("path");

const VALIDADE_SESSAO_MS = 7 * 24 * 60 * 60 * 1000;

function raiz() {
  return process.env.HALCYON_STATUSLINE_DIR || path.join(os.homedir(), ".claude", "halcyon-statusline");
}

function seguro(texto) {
  return String(texto).replace(/[^A-Za-z0-9._-]/g, "_");
}

function caminhoSessao(sessionId) {
  return path.join(raiz(), "sessoes", `${seguro(sessionId)}.json`);
}

function caminhoCache(repo, numero) {
  return path.join(raiz(), "cache", `${seguro(repo.replace("/", "__"))}__${numero}.json`);
}

function caminhoTokens(sessionId) {
  return path.join(raiz(), "tokens", `${seguro(sessionId)}.json`);
}

function lerJson(arquivo) {
  try {
    return JSON.parse(fs.readFileSync(arquivo, "utf8"));
  } catch {
    return null;
  }
}

function gravarJson(arquivo, dados) {
  fs.mkdirSync(path.dirname(arquivo), { recursive: true });
  const temporario = `${arquivo}.${process.pid}.tmp`;
  fs.writeFileSync(temporario, JSON.stringify(dados, null, 2));
  fs.renameSync(temporario, arquivo);
}

function lerSessao(sessionId) {
  return sessionId ? lerJson(caminhoSessao(sessionId)) : null;
}

function gravarSessao(sessionId, ref) {
  gravarJson(caminhoSessao(sessionId), { ...ref, definidaEm: Date.now() });
}

function apagarSessao(sessionId) {
  fs.rmSync(caminhoSessao(sessionId), { force: true });
}

// Sessao, cache do board e contagem de tokens: tudo que nao e tocado ha 7 dias sai.
function expirarSessoes(agora = Date.now()) {
  for (const subpasta of ["sessoes", "cache", "tokens"]) expirarPasta(path.join(raiz(), subpasta), agora);
}

function expirarPasta(pasta, agora) {
  let nomes = [];
  try {
    nomes = fs.readdirSync(pasta);
  } catch {
    return;
  }
  for (const nome of nomes) {
    const arquivo = path.join(pasta, nome);
    try {
      if (agora - fs.statSync(arquivo).mtimeMs > VALIDADE_SESSAO_MS) fs.rmSync(arquivo, { force: true });
    } catch {}
  }
}

module.exports = {
  raiz,
  caminhoSessao,
  caminhoCache,
  caminhoTokens,
  lerJson,
  gravarJson,
  lerSessao,
  gravarSessao,
  apagarSessao,
  expirarSessoes,
};
