---
title: REA — engenharia reversa por agente (MCP + CLI)
source: https://github.com/morluto/rea
type: referencia
status: aprovado
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, mcp, engenharia-reversa, seguranca, tema/tooling]
---

# REA — Reverse Engineer Anything

Servidor MCP + CLI que da ao agente ferramentas de engenharia reversa: binario nativo,
app JavaScript/Electron, .NET, APK, firmware, WASM, site e captura de rede. Roda **local**
e cada resultado vem com a evidencia e os limites da conclusao. Guardado aqui para quando
precisarmos entender como um produto de terceiro faz algo, interoperar com um sistema sem
documentacao ou auditar um binario que recebemos.

| | |
|---|---|
| Repositorio | `morluto/rea` — MIT (codigo proprio; terceiros em `THIRD_PARTY_NOTICES.md`) |
| Pacote npm | `rea-agents` — versao **6.5.0** em 2026-10-14 |
| Site e guias | https://rea.tools (guias, casos reais em `/showcase/`) |
| Atividade | ~271 mil estrelas, push diario (conferido na API do GitHub em 2026-10-15) |
| Requisito | Node 22.19+, 24.11+ ou 26+ |

## O que cobre

| Alvo | O que devolve | Depende de |
|---|---|---|
| Binario nativo | Pseudocodigo, assembly, strings, simbolos, chamadas, referencias | Hopper, Ghidra ou IDA (**nao vem junto**) |
| Go e Rust | Inspecao do binario | Nada extra |
| JavaScript / Electron | Modulos, imports, rotas, IPC, add-ons nativos | Nada extra (analise estatica) |
| .NET, APK (JADX), Android via `adb`, Flutter | Classes, metodos decompilados, manifesto | JDK + JADX; `adb` |
| Firmware, WASM, bytecode EVM, SQLite | Estrutura e conteudo | Binwalk/Unblob, WABT |
| Site e captura de rede (HAR, SAZ) | Estrutura, scripts, requisicoes, payloads expostos | Navegador Chrome; TShark |
| Processo em execucao | Captura de runtime | **So Linux e macOS** |

## Instalacao: nao use o `setup` padrao

`npx rea-agents setup` registra o MCP no **escopo `user`** (`mcpServers.rea` em
`~/.claude.json`) e instala a skill `reverse-engineer-anything` em `~/.claude/skills/`.
Resultado: **todo projeto aberto no Claude Code passa a carregar as tools do REA**, o que
contraria a regra de 3 a 6 servidores e o escopo por projeto de [[../MCPS|MCPS.md]].

Prefira o registro manual em escopo `local`, so na pasta onde vai investigar:

```powershell
# Windows nativo (o cmd.exe embrulha o npx para o cliente stdio conseguir lancar)
claude mcp add --scope local rea -- cmd.exe /d /c npx -y rea-agents@6.5.0 mcp
```

```bash
# Linux / macOS
claude mcp add --scope local rea -- npx -y rea-agents@6.5.0 mcp
```

- **Fixe a versao** (`@6.5.0`), nao `@latest`: o pacote recebe release quase todo dia.
- Esse caminho **nao instala a skill**. Se quiser o fluxo de investigacao guiado, copie
  `.agents/skills/reverse-engineer-anything/` do repo para `.claude/skills/` do projeto
  derivado, nao para `~/.claude/skills/`.
- **Nao use `--scope project`** — a propria doc do REA desaconselha: grava `.mcp.json` no
  repositorio, onde vai parar no commit.
- Remocao: `claude mcp remove --scope local rea`, na mesma pasta. `rea doctor` e
  `rea uninstall` so enxergam o registro `user`; nao acham o `local`.
- Uso pontual sem MCP: `npx -y rea-agents@6.5.0 analyze-javascript-application <caminho-absoluto> --json`.

## Custo de contexto

Alto. O catalogo de tools e gerado por versao (consulte com a tool `binary_session` no
servidor em execucao) e passa de dezenas. Ligue so na sessao de investigacao e remova ao
terminar, como o MCP de KiCad (secao 4.1 do [[../MCPS|MCPS.md]]). Se o cliente reclamar do
tamanho do schema, `REA_MCP_INPUT_SCHEMA_PROFILE=compact` reduz a descricao das entradas sem
tirar tools; `REA_MCP_MAX_RESPONSE_BYTES` limita o tamanho da resposta.

## Armadilhas

- **Este PC e Windows.** Ghidra no Windows e experimental e so leitura ("P0": PE x86,
  x86-64, ARM64). Captura de runtime nao existe no Windows. Para binario nativo, Linux
  (WSL) ou macOS e o caminho estavel.
- **Motor nativo por sua conta.** O REA nao instala Ghidra nem IDA; o `setup` so oferece
  instalar o Hopper (macOS/Linux), com aprovacao. IDA, Hopper e JEB exigem licenca
  propria — o REA nao concede nenhuma.
- **Binario grande demora a abrir.** Aumente `REA_GHIDRA_STARTUP_TIMEOUT_MS` ou
  `REA_HOPPER_STARTUP_TIMEOUT_MS`.
- **Estatico nao executa; runtime executa.** Inspecao estatica so le o arquivo. Captura de
  runtime roda ou interage com o alvo com as permissoes do seu usuario: alvo suspeito vai
  para VM ou sandbox, nunca para a maquina de trabalho.
- **O dado sai da maquina pelo modelo.** A analise e local, mas o resultado entra no
  contexto do agente e segue a politica do provedor do modelo. Binario de cliente sob NDA
  so com autorizacao para isso.
- A skill avisa: para repositorio com codigo-fonte completo, **nao use o REA** — Read,
  Grep e o `explorer` resolvem mais barato.

## Uso legal

O projeto se declara para pesquisa, educacao, interoperabilidade, preservacao e analise de
software proprio ou com autorizacao. Antes de investigar produto de terceiro, confira a
licenca/EULA do alvo. A lei brasileira de software (Lei 9.609/98) nao tem excecao explicita
para descompilacao, como a diretiva europeia; o art. 6, IV so cobre integrar um programa a um
sistema quando isso e indispensavel ao uso proprio. Em caso de duvida, consulte o juridico.
Engenharia reversa para "ver como o concorrente fez" serve para entender, nao para reproduzir
codigo.

## Comandos uteis

```bash
rea --help                                          # com instalacao global (npm i -g rea-agents)
npx -y rea-agents@6.5.0 doctor --client claude_code --json   # diagnostica sem alterar nada
npx -y rea-agents@6.5.0 setup --client claude_code --dry-run # mostra o que o setup faria
```

## Fontes

- README: https://github.com/morluto/rea
- Instalacao e escopo: https://github.com/morluto/rea/blob/main/docs/installation.md
- Contratos e tools: https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md
- Skill: https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything
- Ghidra no Windows: https://github.com/morluto/rea/blob/main/docs/windows-ghidra-p0.md
