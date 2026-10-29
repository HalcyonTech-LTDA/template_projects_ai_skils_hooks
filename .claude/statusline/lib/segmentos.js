// Monta a linha: issue · status │ fase · modelo recomendado │ modelo · esforco │ ctx % │ tokens da sessao.
// Funcoes puras sobre o payload da statusline, a sessao, o cache e a contagem de tokens.
const ANSI = {
  reset: "\x1b[0m",
  cinza: "\x1b[90m",
  vermelho: "\x1b[31m",
  verde: "\x1b[32m",
  amarelo: "\x1b[33m",
  azul: "\x1b[34m",
  magenta: "\x1b[35m",
  ciano: "\x1b[36m",
  negrito: "\x1b[1m",
};

const COR_DO_STATUS = {
  backlog: "cinza",
  ready: "azul",
  todo: "azul",
  "in progress": "amarelo",
  "in review": "magenta",
  done: "verde",
  open: "ciano",
  closed: "verde",
};

const LIMITE_TITULO = 30;
const SEPARADOR = ` ${ANSI.cinza}│${ANSI.reset} `;
const PONTO = ` ${ANSI.cinza}·${ANSI.reset} `;

function pintar(texto, cor) {
  return cor ? `${ANSI[cor]}${texto}${ANSI.reset}` : texto;
}

function encurtar(texto, limite = LIMITE_TITULO) {
  const limpo = String(texto).replace(/\s+/g, " ").trim();
  return limpo.length > limite ? `${limpo.slice(0, limite - 1)}…` : limpo;
}

function segmentoStatus(cache) {
  if (!cache || !cache.status) return pintar(cache && cache.erro ? "?" : "…", "cinza");
  const cor = COR_DO_STATUS[cache.status.toLowerCase()];
  return pintar(cache.status, cor) + (cache.erro ? pintar("?", "cinza") : "");
}

function segmentoIssue(sessao, cache) {
  if (!sessao) return null;
  const numero = pintar(`#${sessao.numero}`, "negrito");
  const titulo = cache && cache.titulo ? ` ${encurtar(cache.titulo)}` : "";
  return `${numero}${titulo}${PONTO}${segmentoStatus(cache)}`;
}

function nomeDoModelo(payload) {
  return String((payload.model && (payload.model.display_name || payload.model.id)) || "");
}

function segmentoModelo(payload) {
  const modelo = nomeDoModelo(payload) || "?";
  const esforco = payload.effort && payload.effort.level;
  return esforco ? `${modelo}${PONTO}${esforco}` : modelo;
}

// F5 · rec. sonnet; ⚠ quando o modelo ativo nao e o recomendado. Sem fase, sem segmento.
function segmentoFase(payload, fase) {
  if (!fase) return null;
  if (!fase.modelo) return fase.fase;
  const diverge = !nomeDoModelo(payload).toLowerCase().includes(fase.modelo.toLowerCase());
  return `${fase.fase}${PONTO}rec. ${fase.modelo}${diverge ? ` ${pintar("⚠", "amarelo")}` : ""}`;
}

function corDoContexto(percentual) {
  if (percentual > 80) return "vermelho";
  if (percentual > 60) return "amarelo";
  return null;
}

function segmentoContexto(payload) {
  const percentual = payload.context_window && payload.context_window.used_percentage;
  if (typeof percentual !== "number") return pintar("ctx —", "cinza");
  return pintar(`ctx ${Math.round(percentual)}%`, corDoContexto(percentual));
}

function formatarTokens(n) {
  if (n < 1000) return String(n);
  if (n < 999500) return `${Math.round(n / 1000)}k`;
  return `${(n / 1e6).toFixed(1)}M`;
}

// "~" enquanto a leitura incremental dos transcripts nao alcancou o fim.
function segmentoTokens(tokens) {
  if (!tokens) return null;
  const aproximado = tokens.completo ? "" : "~";
  const sub = tokens.subagentes ? ` (sub ${formatarTokens(tokens.subagentes)})` : "";
  return pintar(`tok ${aproximado}${formatarTokens(tokens.total)}${sub}`, "cinza");
}

function montar(payload, sessao, cache, tokens, fase) {
  const segmentos = [
    segmentoIssue(sessao, cache),
    segmentoFase(payload, fase),
    segmentoModelo(payload),
    segmentoContexto(payload),
    segmentoTokens(tokens),
  ];
  return segmentos.filter(Boolean).join(SEPARADOR);
}

module.exports = { montar, segmentoModelo, segmentoFase, encurtar, formatarTokens };
