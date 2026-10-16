---
title: Jev (TypeSafe AI) - modelo de decisao System One
source: https://blog.dsacademy.com.br/jev-e-laya-o-que-sao-os-modelos-de-decisao-system-one-e-quando-usa-los/
type: referencia
tags: [referencia, modelo, system-one, typesafe, jev]
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
---

# Jev (TypeSafe AI)

Metodo: WebFetch (resume a pagina, pode errar). Nenhum trecho foi conferido por curl. Tudo e "via resumo,
nao conferido literalmente". Todas as fontes sobre Jev sao blogs/cursos (fonte interessada) que
repetem material de lancamento do fabricante. Nao achei pagina primaria da TypeSafe nem benchmark
independente (nao busquei o site typesafe.ai; lacuna).

## 1. O que e

- Modelo de IA que NAO gera texto: recebe estado nao estruturado + perguntas tipadas e devolve
  valores tipados com probabilidades. "um modelo de decisao estruturada, sem geracao de texto."
  https://horadecodar.com.br/workflow-com-jev/
- Primeiro modelo da classe "System One" da TypeSafe AI. Tres primitivas: Choice, Score, Noul (sim/nao com
  probabilidade). https://horadecodar.com.br/workflow-com-jev/ e dsacademy (URL acima)
- Anunciado em 15/09/2026. https://horadecodar.com.br/workflow-com-jev/ (artigo de 18/09/2026)
- Criador, segundo a cobertura citada: Diogo Almeida (ex-OpenAI, RLHF/InstructGPT); seed de US$ 40 mi
  liderada pela DCVC. Fonte: https://horadecodar.com.br/mods-no-claude-code-2/ (que cita The New Stack;
  nao conferi o original).
- Servico hospedado, sem pesos abertos, sem artigo tecnico; arquitetura, parametros e dados de
  treino nao divulgados; foco em ingles. https://blog.dsacademy.com.br/jev-e-laya-o-que-sao-os-modelos-de-decisao-system-one-e-quando-usa-los/
- Cloudflare publicou o Clef, "compativel com a API Jev/SystemOne" (ver clef.md), o que sugere que a
  API /v1/systemone virou interface de fato. https://huggingface.co/Cloudflare/clef

## 2. Acesso e integracao

- Early access com fila; chaves emitidas pelo console TypeSafe. Alternativa: OpenRouter
  `typesafe/jev-1.13` e `~typesafe/jev-latest` (um unico provedor). `jev-latest` aponta para a versao
  mais nova (pode mudar). https://horadecodar.com.br/workflow-com-jev/
- Python: `python -m pip install typesafe-sdk` (>= 3.10, env `TYPESAFE_API_KEY`). JS:
  `npm install @typesafe-ai/sdk` (Node >= 20). HTTP: `POST https://api.typesafe.ai/v1/systemone`.
  https://horadecodar.com.br/workflow-com-jev/
- Claude Code: skill de agente, nao substitui o modelo. `claude plugin marketplace add typesafe-ai/skills`
  e `claude plugin install typesafe@typesafe-ai`. https://horadecodar.com.br/workflow-com-jev/
- "Mods" do Jev no Claude Code acessam o modelo via OpenRouter, Vercel AI Gateway, Cloudflare Workers AI,
  LiteLLM ou API da TypeSafe; sao de terceiros; `jev-code` e ferramenta, nao mod. Instalacao de mod:
  `claude plugin install <plugin>@<marketplace>`. https://horadecodar.com.br/mods-no-claude-code-2/
- Contexto de 32.000 tokens no Jev 1.13, entao a base de conhecimento nao cabe inteira no estado.
  https://horadecodar.com.br/workflow-com-jev/

Inferencia minha: Jev nao troca o Opus/Sonnet do fluxo. Serve como juiz barato em pontos de decisao
(classificar, rotear, pontuar, aprovar/rejeitar) dentro de hooks ou scripts. Nenhuma fonte mostra
isso funcionando como roteador de modelo do Claude Code.

## 3. Numeros alegados e origem

| Numero | Origem | Metodologia |
|---|---|---|
| "20 a 200 vezes mais rapido e 40 a 400 vezes mais barato" que LLMs comparaveis em decisao estruturada | Material de lancamento da TypeSafe, repetido pelo autor | Nao divulgada; autor diz que nao e medicao independente e nao achou benchmark de terceiros. https://horadecodar.com.br/workflow-com-jev/ |
| "70 a 500 ms" por passada paralela | "dado do fabricante" https://horadecodar.com.br/mods-no-claude-code-2/ | Nenhuma |
| US$ 0,042 por 1M tokens de entrada, saida gratis | Artigos de Hora de Codar | Sem fonte citada. https://horadecodar.com.br/workflow-com-jev/ |
| Acuracia 67,8% (4 fluxos: incidentes, observabilidade de agentes, faturas, atendimento) | Benchmark da propria TypeSafe | Empresa "reconhece vieses"; nao prova que preco nao e subsidiado. https://blog.dsacademy.com.br/jev-e-laya-o-que-sao-os-modelos-de-decisao-system-one-e-quando-usa-los/ |
| GPT-5.6 Terra 67,9%, US$ 0,0304/caso, 10,1 s; Jev US$ 0,0004, 0,4 s (~1/76 do custo) | Mesmo benchmark | Idem |
| GPT-5.6 Sol 74,1%; Claude Opus 5 73,1% (5 a 6 pontos acima do Jev) | Mesmo benchmark | Idem |
| Vercel: revisor de seguranca de comandos "ate 18 vezes mais rapido no p95" | CEO da Vercel, via DSA | Nao medido de forma independente |
| Consistencia: ~2% dos pares reescritos mudam a resposta; injecao de prompt: ~6% mudam a decisao | Respan | Respan vende classificador concorrente; DSA trata como nao neutra |
| Jev 0,727 (typed-decisions) e 0,870 no Banking77 | Citados nos artigos sobre Laya | Medido por terceiros segundo DSA |

Comparacao no benchmark interno da Cloudflare (nao independente): Jev vence o Clef em GPQA Diamond
(78,3 vs 48,0), MMLU-Pro, BBH. https://huggingface.co/Cloudflare/clef

## 4. Limitacoes admitidas pelas fontes

- Acesso por fila; dependencia de API externa; preco possivelmente subsidiado.
- 5 a 6 pontos abaixo de modelos de fronteira; sem raciocinio em varias etapas nem justificativa
  escrita; "nao alucina" so quer dizer que o formato nao quebra.
- Recomendacao do autor: controle de fluxo e efeitos colaterais ficam no codigo; o modelo so julga dados
  nao estruturados. Limiares 0,90/0,10 do exemplo sao ilustrativos.
- Mods do Claude Code nao rodam em sandbox: tem as permissoes do usuario, leem chaves e prompts.
  https://horadecodar.com.br/mods-no-claude-code-2/

## 5. Nao encontrado

- Pagina primaria da TypeSafe, artigo tecnico, benchmark independente, evidencia de economia de tokens
  no fluxo de desenvolvimento (o "ganho" alegado e por chamada de decisao, nao por sessao de dev).
