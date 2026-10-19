// Muda o Status da issue no board. A /issue chama ao iniciar a implementacao (In progress) e no
// fim (In review ou Done). Os ids saem do proprio item da issue no Project, entao funciona com o
// BOARD.md ainda vazio; sem Project com campo Status, nao move nada.
const { execFileSync } = require("child_process");

// O workflow "Pull request merged -> In review" roda em segundo plano e pode chegar depois do
// item-edit; com conferencia, espera, rele e reaplica uma vez.
const ESPERA_CONFERENCIA_MS = 10 * 1000;

const CONSULTA = `query($dono: String!, $repo: String!, $numero: Int!) {
  repository(owner: $dono, name: $repo) { issue(number: $numero) { projectItems(first: 20) { nodes {
    id
    fieldValueByName(name: "Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } }
    project { id title field(name: "Status") { ... on ProjectV2SingleSelectField { id options { id name } } } }
  } } } }
}`;

function gh(args) {
  return execFileSync("gh", args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    timeout: 20000,
    windowsHide: true,
    env: { ...process.env, GH_NO_UPDATE_NOTIFIER: "1", GH_PROMPT_DISABLED: "1" },
  });
}

function itensDoBoard(ref) {
  const [dono, repo] = ref.repo.split("/");
  const args = ["api", "graphql", "-f", `query=${CONSULTA}`, "-f", `dono=${dono}`, "-f", `repo=${repo}`];
  const resposta = JSON.parse(gh([...args, "-F", `numero=${ref.numero}`]));
  const issue = resposta.data && resposta.data.repository && resposta.data.repository.issue;
  if (!issue) throw new Error(`issue ${ref.repo}#${ref.numero} nao encontrada`);
  return issue.projectItems.nodes;
}

// Boards em ingles (molde da /trilha) e em portugues (ex.: TelemeVisus) convivem; qualquer nome de
// um grupo acha a opcao do outro idioma.
const SINONIMOS = [
  ["in progress", "em andamento", "andamento"],
  ["in review", "em revisao", "revisao"],
  ["done", "feito", "concluido"],
];

function normalizar(texto) {
  return String(texto).normalize("NFD").replace(/[̀-ͯ]/g, "").trim().toLowerCase();
}

function nomesAceitos(nomeStatus) {
  const pedido = normalizar(nomeStatus);
  return SINONIMOS.find((grupo) => grupo.includes(pedido)) || [pedido];
}

// Primeiro Project com campo Status, como a statusline; a opcao e comparada sem caixa e sem acento.
function escolherAlvo(itens, nomeStatus) {
  const item = (itens || []).find((i) => i.project && i.project.field && i.project.field.options);
  if (!item) return { erro: "sem-board" };
  const campo = item.project.field;
  const aceitos = nomesAceitos(nomeStatus);
  const opcao = campo.options.find((o) => aceitos.includes(normalizar(o.name)));
  if (!opcao) return { erro: "sem-opcao", board: item.project.title, opcoes: campo.options.map((o) => o.name) };
  return {
    itemId: item.id,
    projectId: item.project.id,
    fieldId: campo.id,
    opcaoId: opcao.id,
    opcao: opcao.name,
    atual: item.fieldValueByName ? item.fieldValueByName.name : null,
    board: item.project.title,
  };
}

function aplicar(alvo) {
  gh([
    "project", "item-edit",
    "--id", alvo.itemId,
    "--project-id", alvo.projectId,
    "--field-id", alvo.fieldId,
    "--single-select-option-id", alvo.opcaoId,
  ]);
}

function esperar(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function conferir(ref, nomeStatus, alvo) {
  esperar(ESPERA_CONFERENCIA_MS);
  const depois = escolherAlvo(itensDoBoard(ref), nomeStatus);
  if (depois.erro || depois.atual === depois.opcao) return alvo;
  aplicar(depois);
  return { ...alvo, reaplicadoSobre: depois.atual };
}

function mover(ref, nomeStatus, opcoes = {}) {
  const alvo = escolherAlvo(itensDoBoard(ref), nomeStatus);
  if (alvo.erro) return alvo;
  if (alvo.atual !== alvo.opcao) aplicar(alvo);
  return opcoes.conferir ? conferir(ref, nomeStatus, alvo) : alvo;
}

module.exports = { escolherAlvo, mover };
