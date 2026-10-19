// Tokens da sessao inteira: transcript principal + transcripts dos subagentes
// (<sessao>/subagents/**.jsonl, inclusive os de workflow). O payload da statusline
// so traz a sessao principal, e o usage de topo nao conta o advisor: ele aparece em
// usage.iterations como advisor_message.
//
// A leitura e incremental: guarda o offset de cada arquivo e le no maximo
// LIMITE_POR_EXECUCAO bytes por execucao, somando todos os arquivos, porque a
// statusline e cancelada quando outro evento chega. Sessao longa fecha a conta em poucas execucoes.
const fs = require("fs");
const path = require("path");
const { caminhoTokens, lerJson, gravarJson } = require("./estado");

const LIMITE_POR_EXECUCAO = 4 * 1024 * 1024;

function somarCampos(u) {
  return (
    (u.input_tokens || 0) +
    (u.cache_creation_input_tokens || 0) +
    (u.cache_read_input_tokens || 0) +
    (u.output_tokens || 0)
  );
}

// Com iterations, a soma delas inclui o advisor; o topo e so a soma das do tipo message.
function somarUso(usage) {
  if (Array.isArray(usage.iterations) && usage.iterations.length) {
    return usage.iterations.reduce((total, it) => total + somarCampos(it), 0);
  }
  return somarCampos(usage);
}

function listarJsonl(pasta) {
  let entradas = [];
  try {
    entradas = fs.readdirSync(pasta, { withFileTypes: true });
  } catch {
    return [];
  }
  return entradas.flatMap((e) => {
    const caminho = path.join(pasta, e.name);
    if (e.isDirectory()) return listarJsonl(caminho);
    return e.name.endsWith(".jsonl") ? [caminho] : [];
  });
}

function arquivosDaSessao(transcript, sessionId) {
  const subagentes = path.join(path.dirname(transcript), sessionId, "subagents");
  return { principal: transcript, subagentes: listarJsonl(subagentes) };
}

function lerNovasLinhas(arquivo, offset, limite) {
  const tamanho = fs.statSync(arquivo).size;
  if (tamanho < offset) return { reiniciar: true };
  const quanto = Math.min(tamanho - offset, limite);
  if (tamanho === offset) return { linhas: [], offset, completo: true };
  if (quanto <= 0) return { linhas: [], offset, completo: false };
  const buffer = Buffer.alloc(quanto);
  const fd = fs.openSync(arquivo, "r");
  try {
    fs.readSync(fd, buffer, 0, quanto, offset);
  } finally {
    fs.closeSync(fd);
  }
  const fim = buffer.lastIndexOf(0x0a);
  // Linha maior que o orcamento inteiro (saida de ferramenta gigante, nunca uma linha de
  // usage): pula o pedaco. O resto dela chega como fragmento invalido e e ignorado.
  if (fim < 0) {
    const pular = quanto === LIMITE_POR_EXECUCAO;
    return { linhas: [], offset: pular ? offset + quanto : offset, completo: false };
  }
  const linhas = buffer.subarray(0, fim).toString("utf8").split("\n");
  return { linhas, offset: offset + fim + 1, completo: offset + fim + 1 >= tamanho };
}

// Uma resposta em streaming vira varias linhas com o mesmo message.id e o mesmo usage:
// a repetida substitui a anterior em vez de somar de novo.
function acumular(estadoArquivo, linhas) {
  for (const linha of linhas) {
    if (!linha.includes('"usage"')) continue;
    let registro;
    try {
      registro = JSON.parse(linha);
    } catch {
      continue;
    }
    const mensagem = registro.type === "assistant" && registro.message;
    if (!mensagem || !mensagem.usage) continue;
    const uso = somarUso(mensagem.usage);
    const repetida = mensagem.id && mensagem.id === estadoArquivo.ultimoId;
    estadoArquivo.total += repetida ? uso - estadoArquivo.ultimoUso : uso;
    estadoArquivo.ultimoId = mensagem.id;
    estadoArquivo.ultimoUso = uso;
  }
}

function novoEstadoArquivo() {
  return { offset: 0, total: 0, ultimoId: null, ultimoUso: 0 };
}

// Devolve quantos bytes consumiu do orcamento e se o arquivo ficou em dia.
function atualizarArquivo(estados, arquivo, orcamento) {
  let estado = estados[arquivo] || novoEstadoArquivo();
  let leitura = lerNovasLinhas(arquivo, estado.offset, orcamento);
  if (leitura.reiniciar) {
    estado = novoEstadoArquivo();
    leitura = lerNovasLinhas(arquivo, 0, orcamento);
  }
  acumular(estado, leitura.linhas);
  const lidos = leitura.offset - estado.offset;
  estado.offset = leitura.offset;
  estados[arquivo] = estado;
  return { lidos, completo: leitura.completo };
}

function contarSessao(transcript, sessionId) {
  if (!transcript || !sessionId || !fs.existsSync(transcript)) return null;
  const arquivo = caminhoTokens(sessionId);
  const estados = lerJson(arquivo) || {};
  const { principal, subagentes } = arquivosDaSessao(transcript, sessionId);
  let orcamento = LIMITE_POR_EXECUCAO;
  let completo = true;
  for (const caminho of [principal, ...subagentes]) {
    const resultado = atualizarArquivo(estados, caminho, orcamento);
    orcamento -= resultado.lidos;
    completo = completo && resultado.completo;
  }
  gravarJson(arquivo, estados);
  const sub = subagentes.reduce((total, s) => total + estados[s].total, 0);
  return { total: estados[principal].total + sub, subagentes: sub, completo };
}

module.exports = { somarUso, acumular, listarJsonl, contarSessao, novoEstadoArquivo };
