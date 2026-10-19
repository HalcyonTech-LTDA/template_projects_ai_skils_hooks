#!/usr/bin/env node
// Diz a statusline qual issue esta sessao trabalha e move a issue no board. Chamado pela skill /issue.
// Uso:
//   node .claude/statusline/issue.js definir <42 | #42 | owner/repo#42 | URL>
//   node .claude/statusline/issue.js mostrar
//   node .claude/statusline/issue.js limpar
//   node .claude/statusline/issue.js mover "<Status>" [ref] [--conferir]
// A sessao vem de CLAUDE_CODE_SESSION_ID, que o Claude Code poe no ambiente do Bash.
// mover sai com 0 ao mover, 3 quando nao ha o que mover (sem Project ou sem a opcao) e 1 em erro.
const { registrar } = require("./lib/registro");
const { lerSessao, apagarSessao } = require("./lib/estado");
const { lerCache, disparar } = require("./lib/board");
const { interpretar, repoDoCheckout } = require("./lib/referencia");
const { mover } = require("./lib/mover");

const USO = 'uso: issue.js definir <ref> | mostrar | limpar | mover "<Status>" [ref] [--conferir]';

function sair(mensagem, codigo) {
  (codigo ? console.error : console.log)(mensagem);
  process.exit(codigo);
}

function exigirSessao(sessionId) {
  if (!sessionId) sair("CLAUDE_CODE_SESSION_ID ausente: rode de dentro de uma sessao do Claude Code", 1);
  return sessionId;
}

function definir(sessionId, texto) {
  if (!texto) sair("uso: issue.js definir <42 | owner/repo#42 | URL>", 1);
  const ref = registrar(exigirSessao(sessionId), texto, process.cwd());
  if (!ref) sair(`referencia nao reconhecida ou sem remote origin no GitHub: ${texto}`, 1);
  sair(`statusline: ${ref.repo}#${ref.numero}`, 0);
}

function mostrar(sessionId) {
  const sessao = lerSessao(exigirSessao(sessionId));
  if (!sessao) sair("statusline: nenhuma issue nesta sessao", 0);
  sair(JSON.stringify({ sessao, cache: lerCache(sessao) }, null, 2), 0);
}

function descreverMovimento(ref, resultado) {
  const nome = `${ref.repo}#${ref.numero}`;
  if (resultado.erro === "sem-board") return [`board: ${nome} nao esta em nenhum Project com campo Status; nada movido`, 3];
  if (resultado.erro === "sem-opcao") {
    return [`board: "${resultado.board}" nao tem a opcao pedida (tem: ${resultado.opcoes.join(", ")}); nada movido`, 3];
  }
  const reaplicado = resultado.reaplicadoSobre ? ` (o board tinha voltado para ${resultado.reaplicadoSobre}; reaplicado)` : "";
  return [`board: ${nome} ${resultado.atual || "sem status"} -> ${resultado.opcao}${reaplicado}`, 0];
}

function moverIssue(sessionId, args) {
  const conferir = args.includes("--conferir");
  const [nomeStatus, texto] = args.filter((a) => a !== "--conferir");
  if (!nomeStatus) sair(USO, 1);
  const ref = texto ? interpretar(texto, repoDoCheckout(process.cwd())) : lerSessao(sessionId);
  if (!ref) sair("sem issue: passe a referencia ou rode issue.js definir antes", 1);
  let resultado;
  try {
    resultado = mover(ref, nomeStatus, { conferir });
  } catch (erro) {
    const detalhe = String((erro.stderr || erro.message || "")).trim().split("\n")[0];
    sair(`gh falhou ao mover ${ref.repo}#${ref.numero}: ${detalhe}\nSem escopo de Project? gh auth refresh -s project`, 1);
  }
  disparar(ref);
  sair(...descreverMovimento(ref, resultado));
}

function main() {
  const sessionId = process.env.CLAUDE_CODE_SESSION_ID;
  const [comando, ...resto] = process.argv.slice(2);
  if (comando === "definir") return definir(sessionId, resto[0]);
  if (comando === "mostrar") return mostrar(sessionId);
  if (comando === "mover") return moverIssue(sessionId, resto);
  if (comando === "limpar") {
    apagarSessao(exigirSessao(sessionId));
    return sair("statusline: issue removida desta sessao", 0);
  }
  sair(USO, 1);
}

main();
