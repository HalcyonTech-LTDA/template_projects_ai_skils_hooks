#!/usr/bin/env node
// Statusline do Claude Code: le o payload no stdin e imprime uma linha.
// Nunca chama rede; o status do board vem do cache (ver lib/board.js).
const fs = require("fs");
const { lerSessao } = require("./lib/estado");
const { lerCache, precisaAtualizar, disparar } = require("./lib/board");
const { contarSessao } = require("./lib/tokens");
const { montar, segmentoModelo } = require("./lib/segmentos");

function lerPayload() {
  try {
    return JSON.parse(fs.readFileSync(0, "utf8") || "{}");
  } catch {
    return {};
  }
}

function tokensDaSessao(payload) {
  try {
    return contarSessao(payload.transcript_path, payload.session_id);
  } catch {
    return null;
  }
}

function linha(payload) {
  const sessao = lerSessao(payload.session_id);
  const cache = sessao ? lerCache(sessao) : null;
  if (sessao && precisaAtualizar(cache)) disparar(sessao);
  return montar(payload, sessao, cache, tokensDaSessao(payload));
}

const payload = lerPayload();
try {
  process.stdout.write(linha(payload));
} catch {
  process.stdout.write(segmentoModelo(payload));
}
