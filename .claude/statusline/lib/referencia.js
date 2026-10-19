// Interpreta a referencia de uma issue: URL, owner/repo#42, #42 ou 42.
// Numero sem repo usa o repo do remote origin, como o passo 1 da /issue.
const { execFileSync } = require("child_process");

const URL_ISSUE = /^https?:\/\/github\.com\/([\w.-]+)\/([\w.-]+)\/issues\/(\d+)/i;
const REPO_E_NUMERO = /^([\w.-]+)\/([\w.-]+)#(\d+)$/;
const SO_NUMERO = /^#?(\d+)$/;
const REMOTE = /github\.com[:/]([\w.-]+)\/([\w.-]+?)(?:\.git)?\/?$/i;

function interpretar(texto, repoPadrao) {
  const valor = String(texto || "").trim();
  const url = valor.match(URL_ISSUE) || valor.match(REPO_E_NUMERO);
  if (url) return { repo: `${url[1]}/${url[2]}`, numero: Number(url[3]) };
  const numero = valor.match(SO_NUMERO);
  if (numero && repoPadrao) return { repo: repoPadrao, numero: Number(numero[1]) };
  return null;
}

function repoDoRemote(urlRemote) {
  const achado = String(urlRemote || "").trim().match(REMOTE);
  return achado ? `${achado[1]}/${achado[2]}` : null;
}

function repoDoCheckout(cwd) {
  try {
    const url = execFileSync("git", ["-C", cwd, "remote", "get-url", "origin"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
      timeout: 3000,
      windowsHide: true,
    });
    return repoDoRemote(url);
  } catch {
    return null;
  }
}

module.exports = { interpretar, repoDoRemote, repoDoCheckout };
