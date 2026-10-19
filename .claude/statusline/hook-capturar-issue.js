#!/usr/bin/env node
// Hook UserPromptSubmit: um prompt que comeca com "/issue <ref>" liga a sessao a issue,
// antes mesmo de a skill rodar. Qualquer outro prompt sai com 0 e sem saida.
const fs = require("fs");
const { registrar } = require("./lib/registro");

const COMANDO_ISSUE = /^\s*\/issue\s+(\S+)/;

try {
  const payload = JSON.parse(fs.readFileSync(0, "utf8") || "{}");
  const achado = String(payload.prompt || "").match(COMANDO_ISSUE);
  if (achado) registrar(payload.session_id, achado[1], payload.cwd || process.cwd());
} catch {}
process.exit(0);
