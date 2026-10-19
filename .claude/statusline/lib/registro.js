// Liga uma sessao a uma issue. Usado pelo hook (/issue 42 no prompt) e pela CLI (skill /issue).
const { interpretar, repoDoCheckout } = require("./referencia");
const { gravarSessao, expirarSessoes } = require("./estado");
const { disparar } = require("./board");

function registrar(sessionId, texto, cwd, repoPadrao) {
  if (!sessionId) return null;
  const ref = interpretar(texto, repoPadrao || repoDoCheckout(cwd));
  if (!ref) return null;
  expirarSessoes();
  gravarSessao(sessionId, ref);
  disparar(ref);
  return ref;
}

module.exports = { registrar };
