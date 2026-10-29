// node --test .claude/statusline/testes/
const test = require("node:test");
const assert = require("node:assert");

process.env.HALCYON_STATUSLINE_OFFLINE = "1";

const { escolherAlvo } = require("../lib/mover");

const opcoes = [
  { id: "o1", name: "In progress" },
  { id: "o2", name: "In review" },
  { id: "o3", name: "Done" },
];

function item(id, campo, statusAtual) {
  return {
    id,
    fieldValueByName: statusAtual ? { name: statusAtual } : null,
    project: { id: `P-${id}`, title: `Board ${id}`, field: campo },
  };
}

test("escolhe o primeiro Project com Status e a opcao sem caixa", () => {
  const itens = [item("a", {}, null), item("b", { id: "F", options: opcoes }, "In progress")];
  assert.deepStrictEqual(escolherAlvo(itens, "in review"), {
    itemId: "b",
    projectId: "P-b",
    fieldId: "F",
    opcaoId: "o2",
    opcao: "In review",
    atual: "In progress",
    board: "Board b",
  });
});

test("sem Project com Status, nada a mover", () => {
  assert.deepStrictEqual(escolherAlvo([], "Done"), { erro: "sem-board" });
  assert.deepStrictEqual(escolherAlvo([item("a", null, null)], "Done"), { erro: "sem-board" });
});

test("nome em ingles acha opcao em portugues e vice-versa", () => {
  const emPortugues = [
    { id: "p1", name: "Em andamento" },
    { id: "p2", name: "Em revisão" },
    { id: "p3", name: "Feito" },
  ];
  const board = [item("a", { id: "F", options: emPortugues }, null)];
  assert.strictEqual(escolherAlvo(board, "In progress").opcao, "Em andamento");
  assert.strictEqual(escolherAlvo(board, "In review").opcao, "Em revisão");
  assert.strictEqual(escolherAlvo(board, "Done").opcao, "Feito");
  assert.strictEqual(escolherAlvo([item("b", { id: "F", options: opcoes }, null)], "em revisão").opcao, "In review");
});

test("opcao inexistente lista as que o board tem", () => {
  const resultado = escolherAlvo([item("a", { id: "F", options: opcoes }, null)], "Bloqueado");
  assert.strictEqual(resultado.erro, "sem-opcao");
  assert.deepStrictEqual(resultado.opcoes, ["In progress", "In review", "Done"]);
});

test("item ainda sem status aparece como atual nulo", () => {
  assert.strictEqual(escolherAlvo([item("a", { id: "F", options: opcoes }, null)], "Done").atual, null);
});
