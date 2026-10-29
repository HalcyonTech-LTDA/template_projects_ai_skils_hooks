// node --test .claude/statusline/testes/*.test.js
const test = require("node:test");
const assert = require("node:assert");
const fs = require("fs");
const os = require("os");
const path = require("path");

process.env.HALCYON_STATUSLINE_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "statusline-fase-"));
process.env.HALCYON_STATUSLINE_OFFLINE = "1";
test.after(() => fs.rmSync(process.env.HALCYON_STATUSLINE_DIR, { recursive: true, force: true }));

const estado = require("../lib/estado");
const fase = require("../lib/fase");

test("fase grava, le e apaga sem sessao de issue", () => {
  fase.registrarFase("f-1", "F5", "sonnet");
  assert.deepStrictEqual(fase.lerFase("f-1"), { fase: "F5", modelo: "sonnet" });
  assert.strictEqual(estado.lerSessao("f-1"), null);
  fase.apagarFase("f-1");
  assert.strictEqual(fase.lerFase("f-1"), null);
  fase.apagarFase("f-1");
  assert.strictEqual(fase.lerFase(undefined), null);
});

test("fase sem modelo recomendado volta com modelo vazio", () => {
  fase.registrarFase("f-2", "F3");
  assert.deepStrictEqual(fase.lerFase("f-2"), { fase: "F3", modelo: "" });
  fase.registrarFase("f-2", "F4", "opus");
  fase.registrarFase("f-2", "F5");
  assert.deepStrictEqual(fase.lerFase("f-2"), { fase: "F5", modelo: "" });
});

test("estado ilegivel ou fora do formato vira sem fase", () => {
  const escrever = (texto) => {
    fs.mkdirSync(path.dirname(estado.caminhoFase("f-3")), { recursive: true });
    fs.writeFileSync(estado.caminhoFase("f-3"), texto);
  };
  for (const texto of ["{nao e json", "", "null", "5", "[]", '{"fase":"F9"}', '{"fase":5}', '{"modelo":"opus"}', '{"fase":"f5"}']) {
    escrever(texto);
    assert.strictEqual(fase.lerFase("f-3"), null, texto);
  }
  escrever('{"fase":"F2","modelo":{"x":1}}');
  assert.deepStrictEqual(fase.lerFase("f-3"), { fase: "F2", modelo: "" });
});

test("modelo recomendado e texto curto e sem controle", () => {
  assert.strictEqual(fase.limparModelo("  son\x1b[31mnet \n 5  "), "son [31mnet 5");
  assert.strictEqual(fase.limparModelo("x".repeat(50)).length, 20);
  assert.strictEqual(fase.limparModelo(undefined), "");
  fase.registrarFase("f-4", "F1", "\x1b[2Jopus");
  assert.strictEqual(fase.lerFase("f-4").modelo, "[2Jopus");
});

test("a fase expira com o resto, em 7 dias", () => {
  fase.registrarFase("f-velha", "F6", "opus");
  fase.registrarFase("f-nova", "F6", "opus");
  const velho = new Date(Date.now() - 8 * 24 * 60 * 60 * 1000);
  fs.utimesSync(estado.caminhoFase("f-velha"), velho, velho);
  estado.expirarSessoes();
  assert.strictEqual(fase.lerFase("f-velha"), null);
  assert.strictEqual(fase.lerFase("f-nova").fase, "F6");
});

test("registrar a fase varre estado velho de outras sessoes", () => {
  fase.registrarFase("f-antiga", "F2");
  const velho = new Date(Date.now() - 9 * 24 * 60 * 60 * 1000);
  fs.utimesSync(estado.caminhoFase("f-antiga"), velho, velho);
  fase.registrarFase("f-atual", "F2");
  assert.strictEqual(fase.lerFase("f-antiga"), null);
});

test("argumentos do comando fase", () => {
  assert.deepStrictEqual(fase.interpretarArgs([]), { acao: "mostrar" });
  assert.deepStrictEqual(fase.interpretarArgs(["--limpar"]), { acao: "limpar" });
  assert.deepStrictEqual(fase.interpretarArgs(["F1"]), { acao: "definir", fase: "F1", modelo: "" });
  assert.deepStrictEqual(fase.interpretarArgs(["F8", "--modelo", "haiku"]), { acao: "definir", fase: "F8", modelo: "haiku" });
  const invalidos = [["F0"], ["F9"], ["F10"], ["5"], ["f5"], ["F5", "--modelo"], ["F5", "--modelo", ""], ["F5", "sonnet"], ["F5", "--modelo", "a", "b"], ["--limpar", "F5"], ["--modelo", "opus"]];
  for (const args of invalidos) assert.strictEqual(fase.interpretarArgs(args), null, args.join(" "));
});

test("descreve a fase para a CLI", () => {
  assert.strictEqual(fase.descreverFase({ fase: "F5", modelo: "sonnet" }), "statusline: F5 · rec. sonnet");
  assert.strictEqual(fase.descreverFase({ fase: "F3", modelo: "" }), "statusline: F3");
  assert.strictEqual(fase.descreverFase(null), "statusline: nenhuma fase nesta sessao");
});

const { montar } = require("../lib/segmentos");

const semCor = (texto) => texto.replace(/\x1b\[\d+m/g, "");
const payload = {
  model: { display_name: "Opus 5.5", id: "claude-opus-5-5" },
  effort: { level: "high" },
  context_window: { used_percentage: 34 },
};

test("segmento da fase fica antes do modelo, com o modelo recomendado", () => {
  const linha = semCor(montar(payload, null, null, null, { fase: "F4", modelo: "opus" }));
  assert.strictEqual(linha, "F4 · rec. opus │ Opus 5.5 · high │ ctx 34%");
});

test("modelo ativo diferente do recomendado avisa com ⚠ amarelo", () => {
  const bruta = montar(payload, null, null, null, { fase: "F5", modelo: "sonnet" });
  assert.strictEqual(semCor(bruta), "F5 · rec. sonnet ⚠ │ Opus 5.5 · high │ ctx 34%");
  assert.ok(bruta.includes("\x1b[33m⚠\x1b[0m"));
  assert.ok(!montar(payload, null, null, null, { fase: "F5", modelo: "opus" }).includes("⚠"));
});

test("a comparacao ignora caixa e cai para o id quando nao ha display_name", () => {
  assert.ok(!montar(payload, null, null, null, { fase: "F2", modelo: "OPUS" }).includes("⚠"));
  const soId = { model: { id: "claude-sonnet-5-5" } };
  assert.ok(!montar(soId, null, null, null, { fase: "F5", modelo: "Sonnet" }).includes("⚠"));
  assert.ok(montar(soId, null, null, null, { fase: "F5", modelo: "opus" }).includes("⚠"));
});

test("fase sem modelo recomendado mostra so a fase, sem aviso", () => {
  const linha = montar(payload, null, null, null, { fase: "F3", modelo: "" });
  assert.strictEqual(semCor(linha), "F3 │ Opus 5.5 · high │ ctx 34%");
});

test("sem fase a linha e identica a de antes", () => {
  const tokens = { total: 5000, subagentes: 0, completo: true };
  const antes = montar(payload, { numero: 42 }, { titulo: "T", status: "open" }, tokens);
  assert.strictEqual(montar(payload, { numero: 42 }, { titulo: "T", status: "open" }, tokens, null), antes);
  assert.strictEqual(montar(payload, { numero: 42 }, { titulo: "T", status: "open" }, tokens, undefined), antes);
  assert.strictEqual(semCor(antes), "#42 T · open │ Opus 5.5 · high │ ctx 34% │ tok 5k");
});

test("a fase vem depois da issue e antes do modelo e dos tokens", () => {
  const tokens = { total: 5000, subagentes: 0, completo: true };
  const linha = semCor(montar(payload, { numero: 42 }, { titulo: "T", status: "open" }, tokens, { fase: "F6", modelo: "sonnet" }));
  assert.strictEqual(linha, "#42 T · open │ F6 · rec. sonnet ⚠ │ Opus 5.5 · high │ ctx 34% │ tok 5k");
});

const { spawnSync } = require("child_process");

const ISSUE_JS = path.join(__dirname, "..", "issue.js");
const STATUSLINE_JS = path.join(__dirname, "..", "statusline.js");

function ambiente(sessao) {
  const env = { ...process.env };
  delete env.CLAUDE_CODE_SESSION_ID;
  return sessao ? { ...env, CLAUDE_CODE_SESSION_ID: sessao } : env;
}

function issueJs(sessao, ...args) {
  const r = spawnSync(process.execPath, [ISSUE_JS, ...args], { env: ambiente(sessao), encoding: "utf8" });
  return { codigo: r.status, saida: r.stdout.trim(), erro: r.stderr.trim() };
}

function barra(sessionId, extra = {}) {
  const entrada = JSON.stringify({ session_id: sessionId, model: { display_name: "Opus 5.5" }, ...extra });
  const r = spawnSync(process.execPath, [STATUSLINE_JS], { env: ambiente(), input: entrada, encoding: "utf8" });
  assert.strictEqual(r.status, 0);
  return semCor(r.stdout);
}

test("CLI: fase grava, mostra, aparece na barra sem issue e limpa", () => {
  assert.deepStrictEqual(issueJs("c-1", "fase", "F5", "--modelo", "sonnet"), { codigo: 0, saida: "statusline: F5 · rec. sonnet", erro: "" });
  assert.strictEqual(issueJs("c-1", "fase").saida, "statusline: F5 · rec. sonnet");
  assert.strictEqual(estado.lerSessao("c-1"), null);
  assert.strictEqual(barra("c-1"), "F5 · rec. sonnet ⚠ │ Opus 5.5 │ ctx —");

  assert.strictEqual(issueJs("c-1", "fase", "F6").saida, "statusline: F6");
  assert.strictEqual(barra("c-1"), "F6 │ Opus 5.5 │ ctx —");

  assert.deepStrictEqual(issueJs("c-1", "fase", "--limpar"), { codigo: 0, saida: "statusline: fase removida desta sessao", erro: "" });
  assert.strictEqual(issueJs("c-1", "fase").saida, "statusline: nenhuma fase nesta sessao");
  assert.strictEqual(barra("c-1"), "Opus 5.5 │ ctx —");
});

test("CLI: a fase e de cada sessao", () => {
  issueJs("c-a", "fase", "F2", "--modelo", "opus");
  assert.strictEqual(barra("c-a"), "F2 · rec. opus │ Opus 5.5 │ ctx —");
  assert.strictEqual(barra("c-b"), "Opus 5.5 │ ctx —");
  assert.strictEqual(issueJs("c-b", "fase").saida, "statusline: nenhuma fase nesta sessao");
});

test("CLI: fase fora de F1..F8 sai com 1 e imprime o uso, sem gravar", () => {
  for (const args of [["F0"], ["F9"], ["5"], ["F5", "--modelo"], ["F5", "sonnet"]]) {
    const r = issueJs("c-2", "fase", ...args);
    assert.strictEqual(r.codigo, 1, args.join(" "));
    assert.match(r.erro, /^uso: issue\.js fase \[F1\.\.F8/);
  }
  assert.strictEqual(fase.lerFase("c-2"), null);
});

test("CLI: sem CLAUDE_CODE_SESSION_ID falha como os outros comandos", () => {
  for (const args of [["fase"], ["fase", "F3"], ["fase", "--limpar"]]) {
    const r = issueJs(undefined, ...args);
    assert.strictEqual(r.codigo, 1, args.join(" "));
    assert.match(r.erro, /CLAUDE_CODE_SESSION_ID ausente/);
  }
});

test("CLI: limpar tira a issue e a fase", () => {
  estado.gravarSessao("c-3", { repo: "o/r", numero: 3 });
  fase.registrarFase("c-3", "F7", "opus");
  assert.strictEqual(issueJs("c-3", "limpar").codigo, 0);
  assert.strictEqual(estado.lerSessao("c-3"), null);
  assert.strictEqual(fase.lerFase("c-3"), null);
});

test("barra: estado da fase corrompido nao quebra a linha", () => {
  const semFase = barra("c-4");
  for (const texto of ["{nao e json", "[1,2", '{"fase":"F99","modelo":"opus"}', "\x00\x01"]) {
    fs.mkdirSync(path.dirname(estado.caminhoFase("c-4")), { recursive: true });
    fs.writeFileSync(estado.caminhoFase("c-4"), texto);
    assert.strictEqual(barra("c-4"), semFase, texto);
  }
});

test("barra: a fase convive com a issue da sessao", () => {
  estado.gravarSessao("c-5", { repo: "o/r", numero: 5 });
  // o cache traz titulo e status; offline a barra nunca preenche isso sozinha
  estado.gravarJson(estado.caminhoCache("o/r", 5), { titulo: "T", status: "open", consultadoEm: Date.now() });
  fase.registrarFase("c-5", "F4", "opus");
  assert.strictEqual(barra("c-5"), "#5 T · open │ F4 · rec. opus │ Opus 5.5 │ ctx —");
});
