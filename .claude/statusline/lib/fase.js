// Fase da /issue (F1..F8) e modelo recomendado, por sessao. Independe de haver issue registrada:
// issue em texto solto nao grava sessao, mas a fase aparece mesmo assim.
const fs = require("fs");
const { caminhoFase, lerJson, gravarJson, expirarSessoes } = require("./estado");

const FASE_VALIDA = /^F[1-8]$/;
const LIMITE_MODELO = 20;
const USO_FASE = "uso: issue.js fase [F1..F8 [--modelo <nome>] | --limpar]";

// Texto livre curto: sem caractere de controle (nao deixa escape ANSI chegar na barra) e cortado.
function limparModelo(texto) {
  const bruto = typeof texto === "string" ? texto : "";
  return bruto.replace(/[\x00-\x1f\x7f-\x9f]/g, " ").replace(/\s+/g, " ").trim().slice(0, LIMITE_MODELO).trim();
}

// Estado ilegivel ou fora do formato vira "sem fase"; nunca lanca.
function lerFase(sessionId) {
  if (!sessionId) return null;
  const dados = lerJson(caminhoFase(sessionId));
  if (!dados || !FASE_VALIDA.test(dados.fase)) return null;
  return { fase: dados.fase, modelo: limparModelo(dados.modelo) };
}

function gravarFase(sessionId, fase, modelo) {
  gravarJson(caminhoFase(sessionId), { fase, modelo: limparModelo(modelo), definidaEm: Date.now() });
}

function apagarFase(sessionId) {
  fs.rmSync(caminhoFase(sessionId), { force: true });
}

// Como registrar() da issue: varre o estado velho e grava.
function registrarFase(sessionId, fase, modelo) {
  expirarSessoes();
  gravarFase(sessionId, fase, modelo);
}

// Argumentos do comando `fase`: devolve a acao ou null quando o uso esta errado.
function interpretarArgs(args) {
  if (args.length === 0) return { acao: "mostrar" };
  if (args.length === 1 && args[0] === "--limpar") return { acao: "limpar" };
  const [fase, ...resto] = args;
  if (!FASE_VALIDA.test(fase)) return null;
  if (resto.length === 0) return { acao: "definir", fase, modelo: "" };
  const modelo = resto.length === 2 && resto[0] === "--modelo" ? limparModelo(resto[1]) : "";
  return modelo ? { acao: "definir", fase, modelo } : null;
}

function descreverFase(fase) {
  if (!fase) return "statusline: nenhuma fase nesta sessao";
  return `statusline: ${fase.fase}${fase.modelo ? ` · rec. ${fase.modelo}` : ""}`;
}

module.exports = { USO_FASE, lerFase, gravarFase, apagarFase, registrarFase, interpretarArgs, descreverFase, limparModelo };
