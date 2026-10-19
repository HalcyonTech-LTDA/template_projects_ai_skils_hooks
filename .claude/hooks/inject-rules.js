#!/usr/bin/env node
// Lembrete curto a cada prompt. Skills e agentes ja estao no prompt do sistema;
// cada byte daqui e relido em toda chamada da sessao. Detalhe em docs_projeto/HOOKS.md.
const rules = `<project-rules>
Regras do projeto (detalhe em docs_projeto/HOOKS.md):
1. Use a skill que combinar com a tarefa. Desenvolvimento passa por /issue; frente de trabalho no GitHub, por /trilha.
2. Economia (docs_projeto/ECONOMIA.md): poucas chamadas, com leituras independentes juntas, varias checagens num Bash so e sem reler o que ja esta na conversa. Modelo pelo tamanho da tarefa.
3. Pergunte so o ambiguo. Em tarefa M ou maior: 5 perguntas (escopo, restricoes, estilo, aceite, edge cases) e 2 alternativas com tradeoffs antes de executar.
4. Funcoes pequenas e modulos coesos. Referencia nova vai para docs_projeto/referencias/; mudanca so termina com docs_projeto/ atualizado.
</project-rules>`;

process.stdout.write(rules);
