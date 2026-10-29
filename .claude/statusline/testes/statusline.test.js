// node --test .claude/statusline/testes/
const test = require("node:test");
const assert = require("node:assert");
const fs = require("fs");
const os = require("os");
const path = require("path");

process.env.HALCYON_STATUSLINE_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "statusline-teste-"));
process.env.HALCYON_STATUSLINE_OFFLINE = "1";
test.after(() => fs.rmSync(process.env.HALCYON_STATUSLINE_DIR, { recursive: true, force: true }));

const { interpretar, repoDoRemote } = require("../lib/referencia");
const { montar, encurtar, formatarTokens } = require("../lib/segmentos");
const { somarUso, contarSessao } = require("../lib/tokens");
const { extrairStatus, precisaAtualizar, disparar, consultar } = require("../lib/board");
const { semRede } = require("../lib/rede");
const estado = require("../lib/estado");

const semCor = (texto) => texto.replace(/\x1b\[\d+m/g, "");

test("interpreta URL, owner/repo#n, #n e n", () => {
  assert.deepStrictEqual(interpretar("https://github.com/o/r/issues/42", null), { repo: "o/r", numero: 42 });
  assert.deepStrictEqual(interpretar("o/r.x#7"), { repo: "o/r.x", numero: 7 });
  assert.deepStrictEqual(interpretar("#9", "a/b"), { repo: "a/b", numero: 9 });
  assert.deepStrictEqual(interpretar("9", "a/b"), { repo: "a/b", numero: 9 });
  assert.strictEqual(interpretar("9", null), null);
  assert.strictEqual(interpretar("conserta o login", "a/b"), null);
});

test("le o repo do remote https e ssh", () => {
  assert.strictEqual(repoDoRemote("https://github.com/HalcyonTech-LTDA/vendas.git\n"), "HalcyonTech-LTDA/vendas");
  assert.strictEqual(repoDoRemote("git@github.com:o/r.git"), "o/r");
  assert.strictEqual(repoDoRemote("https://gitlab.com/o/r"), null);
});

test("status: primeiro Project com status, senao o estado", () => {
  const comBoard = { state: "OPEN", projectItems: [{ title: "X" }, { status: { name: "In review" } }] };
  assert.strictEqual(extrairStatus(comBoard), "In review");
  assert.strictEqual(extrairStatus({ state: "CLOSED", projectItems: [] }), "closed");
});

test("cache vale 60 s", () => {
  assert.strictEqual(precisaAtualizar(null), true);
  assert.strictEqual(precisaAtualizar({ consultadoEm: 1000 }, 50_000), false);
  assert.strictEqual(precisaAtualizar({ consultadoEm: 1000 }, 70_000), true);
});

test("offline: nao dispara o atualizador nem consulta o gh", () => {
  assert.strictEqual(disparar({ repo: "o/r", numero: 1 }), false);
  assert.throws(() => consultar({ repo: "o/r", numero: 1 }), /HALCYON_STATUSLINE_OFFLINE/);
});

test("so HALCYON_STATUSLINE_OFFLINE=1 desliga a rede", () => {
  const antes = process.env.HALCYON_STATUSLINE_OFFLINE;
  try {
    for (const [valor, esperado] of [["1", true], ["0", false], ["", false], [undefined, false]]) {
      if (valor === undefined) delete process.env.HALCYON_STATUSLINE_OFFLINE;
      else process.env.HALCYON_STATUSLINE_OFFLINE = valor;
      assert.strictEqual(semRede(), esperado, String(valor));
    }
  } finally {
    process.env.HALCYON_STATUSLINE_OFFLINE = antes;
  }
});

const payload = {
  model: { display_name: "Opus 5.5" },
  effort: { level: "high" },
  context_window: { used_percentage: 34 },
  cost: { total_cost_usd: 1.2 },
};

test("linha completa com issue", () => {
  const tokens = { total: 4_620_000, subagentes: 870_000, completo: true };
  const linha = semCor(montar(payload, { numero: 42 }, { titulo: "Login com TOTP", status: "In progress" }, tokens));
  assert.strictEqual(linha, "#42 Login com TOTP · In progress │ Opus 5.5 · high │ ctx 34% │ tok 4.6M (sub 870k)");
});

test("sem issue, sem esforco e contexto ainda nulo", () => {
  const linha = semCor(montar({ model: { display_name: "Haiku 5.5" }, context_window: { used_percentage: null } }, null, null));
  assert.strictEqual(linha, "Haiku 5.5 │ ctx —");
});

test("antes do primeiro cache e com erro do gh", () => {
  assert.match(semCor(montar(payload, { numero: 42 }, null)), /^#42 · … │/);
  assert.match(semCor(montar(payload, { numero: 42 }, { titulo: "T", status: "open", erro: true })), /^#42 T · open\? │/);
});

test("titulo longo e encurtado", () => {
  assert.strictEqual(encurtar("a".repeat(40)).length, 30);
});

test("sessao grava, le e apaga", () => {
  estado.gravarSessao("s-1", { repo: "o/r", numero: 3 });
  assert.strictEqual(estado.lerSessao("s-1").numero, 3);
  estado.apagarSessao("s-1");
  assert.strictEqual(estado.lerSessao("s-1"), null);
  assert.strictEqual(estado.lerSessao(undefined), null);
});

test("formata tokens", () => {
  assert.deepStrictEqual([999, 1499, 225_400, 999_600, 4_620_000].map(formatarTokens), ["999", "1k", "225k", "1.0M", "4.6M"]);
  assert.match(semCor(montar(payload, null, null, { total: 5000, subagentes: 0, completo: false })), /│ tok ~5k$/);
});

test("usage com iterations inclui o advisor", () => {
  const usage = {
    input_tokens: 4,
    output_tokens: 10,
    iterations: [
      { type: "message", input_tokens: 2, output_tokens: 4, cache_read_input_tokens: 100 },
      { type: "advisor_message", input_tokens: 1000, output_tokens: 50 },
      { type: "message", input_tokens: 2, output_tokens: 6, cache_creation_input_tokens: 10 },
    ],
  };
  assert.strictEqual(somarUso(usage), 1174);
  assert.strictEqual(somarUso({ input_tokens: 1, cache_creation_input_tokens: 2, cache_read_input_tokens: 3, output_tokens: 4 }), 10);
});

function linhaAssistente(id, entrada, saida) {
  return JSON.stringify({ type: "assistant", message: { id, usage: { input_tokens: entrada, output_tokens: saida } } }) + "\n";
}

test("soma principal e subagentes, sem contar duas vezes a mesma mensagem", () => {
  const pasta = fs.mkdtempSync(path.join(process.env.HALCYON_STATUSLINE_DIR, "proj-"));
  const principal = path.join(pasta, "s-9.jsonl");
  const workflows = path.join(pasta, "s-9", "subagents", "workflows", "wf_1");
  fs.mkdirSync(workflows, { recursive: true });
  // streaming: tres linhas com o mesmo id; vale a ultima
  fs.writeFileSync(principal, linhaAssistente("m1", 10, 1) + linhaAssistente("m1", 10, 1) + linhaAssistente("m1", 10, 5) + '{"type":"user"}\n');
  fs.writeFileSync(path.join(pasta, "s-9", "subagents", "agent-a.jsonl"), linhaAssistente("a1", 100, 0));
  fs.writeFileSync(path.join(workflows, "agent-b.jsonl"), linhaAssistente("b1", 1000, 0));
  assert.deepStrictEqual(contarSessao(principal, "s-9"), { total: 1115, subagentes: 1100, completo: true });

  fs.appendFileSync(principal, linhaAssistente("m2", 7, 3) + '{"type":"assistant","message":{"id":"m3"');
  assert.deepStrictEqual(contarSessao(principal, "s-9"), { total: 1125, subagentes: 1100, completo: false });
  assert.strictEqual(contarSessao(path.join(pasta, "nao-existe.jsonl"), "s-9"), null);
});
