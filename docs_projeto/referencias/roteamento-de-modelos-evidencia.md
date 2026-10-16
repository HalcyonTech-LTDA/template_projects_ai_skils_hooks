---
title: Roteamento de modelos e modelos de decisao (Jev, Laya, Clef) - evidencia independente
source: https://blog.cloudflare.com/clef-decision-models/
type: referencia
status: rascunho
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, roteamento, modelos-de-decisao, jev, laya, clef, custo, tema/agentes]
---

# Roteamento de modelos e modelos de decisao: o que a evidencia sustenta

Ficha de evidencia, nao de adocao. Conferida em 2026-10-15. Fontes lidas via WebFetch
(resumo de pagina): onde ha numero ou citacao, vale como "via resumo, nao conferida" ate
alguem abrir a fonte. Nada aqui foi executado ou medido por nos.

## 1. Resumo

- Os tres sao "modelos de decisao" (System One): nao geram texto; recebem um estado e
  perguntas tipadas e devolvem probabilidade por opcao, numa passada.
- Servem para classificar, rotear, pontuar, checar condicao. Nao escrevem nem editam codigo.
  "Economia de tokens" so existe se eles substituirem chamadas LLM que seriam
  classificacao; nao fazem o trabalho do implementer.
- **Nao achei benchmark independente de economia de tokens ou de qualidade em tarefa de
  codigo (SWE-bench ou similar) para Jev, Laya ou Clef.** Todo numero de economia em fluxo
  de dev vem de vendedor, do autor da ferramenta ou de demo de uma sessao.
- Tudo tem 1 a 4 semanas de vida (lancamentos 2026-09-15 a 2026-10-01). Sem historico.

## 2. Atencao: "Laya" e dois projetos diferentes

- `laya.aay.sh` NAO e o modelo. E um app desktop de notificacoes (Gmail, Slack, Jira,
  GitHub) com pipeline de IA, de Aayush Chawla; sem benchmark, sem alegacao de tokens.
  Fonte: https://laya.aay.sh/ (via resumo).
- O modelo "Laya" e outro: ConvAI Innovations / NandhaKishorM, Apache-2.0, 421M
  (ModernBERT-large), contexto 512 na descricao do llmreference, lancado 2026-09-18.
  Fontes: https://www.llmreference.com/model/laya ,
  https://huggingface.co/convaiinnovations/laya ,
  https://github.com/NandhaKishorM/laya
- Existem copias/forks do nome no HF (`nishanth-kj/laya`, `aaroncool9/laya`,
  `UNUSABLE07/laya`), listados em
  https://huggingface.co/nishanth-kj/laya e https://huggingface.co/aaroncool9/laya.
  Cuidado ao baixar: use so o repo do autor.

## 3. O que cada um e (fonte primaria ou o mais proximo)

### Jev (TypeSafe AI)
- Fechado: pesos, arquitetura e dados nao divulgados. Preco afirmado: US$ 0,042 por
  milhao de tokens de entrada, saida gratis, 70-500 ms. Lancamento (early access)
  ~2026-09-15/16. Fonte: https://metricnexus.ai/blog/jev-benchmarks-pricing e
  https://letsdatascience.com/news/typesafe-ai-launches-jev-decision-model-889a38c0
- Afirmado pelo vendedor: ate 193,6x mais rapido e 444,6x mais barato, em 4 workflows
  escritos pela propria TypeSafe. Fonte: https://metricnexus.ai/blog/jev-benchmarks-pricing
- Nao e feito para chat nem geracao de codigo (mesma fonte do letsdatascience acima).

### Clef e Clef-flash (Cloudflare)
- Anuncio oficial, 2026-10-01: https://blog.cloudflare.com/clef-decision-models/ .
  Pesos Apache-2.0 em https://huggingface.co/Cloudflare/clef ; 27B (Clef), 9B (flash);
  backbone Qwen post-treinado; API compativel com Jev. Backbone e tamanhos:
  https://www.theregister.com/a/5300649
- Model card (via resumo): ~19.3 mil downloads no mes, 2.18k likes.
  https://huggingface.co/Cloudflare/clef
- Hardware local: GPU de pelo menos 41 GB de VRAM (flash) ou 85 GB (Clef), contexto 64k
  e concorrencia 1. Preco hospedado US$ 0,24/M tokens, ~6x o do Jev. Dados de treino nao
  sao publicos, apesar de "open source". Fonte: https://www.theregister.com/a/5300649
- O post da Cloudflare nao fala de agentes de codigo; exemplos sao triagem de ticket e
  classificacao de dominio. Fonte: https://blog.cloudflare.com/clef-decision-models/ (via resumo).

### Laya (modelo)
- Pequeno, rodavel local (T4 em ~33 ms por pergunta, segundo o README). Fonte:
  https://github.com/NandhaKishorM/laya
- Limitacoes do proprio autor: "Base checkpoints are near chance on typed-decisions
  zero-shot"; "a fast base to specialise, not a zero-shot decision engine"; sai
  superconfiante; Banking77 0,425 contra 0,870 do Jev; `action.act_probability` sem sinal
  util (issue #185). Fonte: https://huggingface.co/convaiinnovations/laya (via resumo).
- README: confianca "orders decisions" mas "does not establish that a decision is
  correct"; vies de posicao nas opcoes. Fonte: https://github.com/NandhaKishorM/laya

## 4. Adocao (numeros que variam por fonte)

- GitHub NandhaKishorM/laya: 33,1k estrelas, 3,0k forks, 52 issues abertas, 69 PRs, 2.213
  commits, v0.4.8, lido em 2026-10-15 (via resumo): https://github.com/NandhaKishorM/laya .
  Um review de 2026-09-25 dava 23.805 estrelas e 158 issues uma semana apos a criacao:
  https://andrew.ooo/posts/laya-review-open-weight-jev-alternative-system-1-decision-model/
  Crescimento muito rapido; nao verifiquei se e organico. Inferencia minha: estrelas
  nao medem qualidade.
- HF Laya: 48.894 downloads/mes, 5,63k likes. https://huggingface.co/convaiinnovations/laya
- Jev: Vercel e DigitalOcean listam o modelo; "mais times pagos em 24h" e afirmacao da
  Vercel relatada por imprensa: https://letsdatascience.com/news/typesafe-ai-launches-jev-decision-model-889a38c0
- Plugin jev-use (MIT, 0.8.0, 2026-09-22, ~6,3 mil downloads/mes):
  https://pi.dev/packages/jev-use?name=jev

## 5. Medido por terceiros (o que ha)

| Fonte | O que mediu | Resultado | Ressalva |
|---|---|---|---|
| Requesty, 2026-10-05, https://www.requesty.ai/blog/decision-model-benchmark-clef-sference-cloudflare-perplexity | ~22 mil decisoes, Clef contra LLMs | Tarefas rotuladas por humanos: GPT-5.5 87,0%, Opus 5.5 86,6%, Clef 83,2%. Clef ~US$ 0,13 por mil itens contra US$ 3,80 (Opus); ~0,45 s | Vende router (interessado). Rotulos de roteamento vieram do Opus. Uma rodada, um dia. Prompts de LLM sem ajuste |
| Mesma fonte | Pontos fracos do Clef | Gating de tool-call: 68,7% contra 90,0% do Opus; complexidade em 3 niveis: concorda 51,9% com Opus | idem |
| arXiv 2609.34024v2 (via https://metricnexus.ai/blog/jev-benchmarks-pricing) | Jev 1.13 em 4 benchmarks medicos | 100% respostas validas; empata no PubMedQA (78,4 contra 78,2), perde >20 pontos em diagnostico; US$ 0,082 contra US$ 6,87 | Dominio medico; rotas e concorrencia diferentes, nao comparavel |
| arXiv 2609.28613, 2026-09-23, https://arxiv.org/abs/2609.28613 | Injecao de prompt no Jev (510 casos InjecAgent) | Raramente escolhe o alvo do atacante; ataque adaptativo sobe sucesso de 1,8% para 3,5% | So Jev |
| Wavect, https://wavect.io/blog/cloudflare-clef-vs-jev/ | Critica metodologica | Clef pontua o schema em conjunto, Jev por pergunta; recomenda retestar | Inferencia de arquitetura, sem teste |

- A Register e outros apontam que os numeros do Clef sao autodeclarados e "ainda nao
  reproduzidos no Decision Index oficial": https://www.theregister.com/a/5300649
- Clef perde para o Jev em GPQA Diamond (48,0 contra 78,3) e em alguns itens (When2Call,
  BRIGHT, observabilidade de trace): https://huggingface.co/Cloudflare/clef ,
  https://wavect.io/blog/cloudflare-clef-vs-jev/
- Nao achei: reproducao independente do Decision Index; benchmark de Laya por terceiro com
  metodologia; qualquer paper que mea esses modelos em SWE-bench ou em sessao real de
  Claude Code.

## 6. Integracao com Claude Code (comunidade, nao oficial)

- Nao encontrei integracao oficial da Anthropic nem da Cloudflare com Claude Code.
  O skill oficial da TypeSafe e documentacao empacotada, nao runtime (resumo de busca; nao conferi).
- jev-router (Engin Diri, Pulumi, 2026-09-28): proxy local que muda o campo `model`
  por mensagem do usuario, com 3 perguntas ao Jev (tipo de trabalho, risco, alegacao de
  tier). Tier so sobe na sessao. Fonte:
  https://www.pulumi.com/blog/route-every-claude-code-message-to-the-right-model-with-jev/
  - "51% economizado" vem de UMA sessao demo contra tudo no modelo topo; o proprio post
    nao apresenta benchmark independente de qualidade de roteamento.
  - Autor do post e da ferramenta e o mesmo; o blog promove Pulumi. Interessado.
  - Cita avaliacao independente em que uma frase injetada mudou a resposta do Jev em
    73,5% dos tickets. Nao consegui confirmar esse numero (achei 73,3% de acuracia em
    deteccao de injecao, outro contexto): busca em https://arxiv.org/pdf/2609.28613 .
    Tratar como nao verificado.
  - Requer Node 22+, chave Jev paga; depende de proxy entre o Claude Code e a Anthropic.
- jev-use (shitianfang, MIT): "measured p50 ~230 ms and ~$0.02 per 1,000 judgments"; os
  dados estariam em `bench/RESULTS.md` do repo, que nao li. Pagina avisa que pacote Pi
  executa codigo: https://pi.dev/packages/jev-use?name=jev

## 7. Literatura do padrao (roteamento e cascata)

- FrugalGPT (Chen, Zaharia, Zou, 2023): cascata de LLMs, "ate 98%" menos custo e a cota
  de melhor caso; exige dados rotulados e um avaliador treinado.
  https://arxiv.org/abs/2305.05176 (percepcao do 98% como maximo: via busca).
- RouteLLM (Ong et al., ICLR 2025): roteador forte/fraco com dados de preferencia; corte de
  custo acima de 2x em MMLU e MT-Bench sem queda substancial de qualidade; generaliza
  para outro par de modelos. Benchmarks de chat/conhecimento, nao de agente.
  https://arxiv.org/abs/2406.18665
- Roteamento e cascata unificados (arXiv 2410.10347): em SWE-Bench o roteamento nao
  superou um baseline trivial (segundo resumo da busca; nao conferi no paper):
  https://arxiv.org/pdf/2410.10347
- TwinRouterBench (arXiv 2605.18859, 18 autores): avalia roteadores por passo de agente em
  SWE-bench Verified (100 casos) medindo resolucao e gasto real. Nao li os numeros:
  https://arxiv.org/abs/2605.18859 . Melhor lugar para buscar evidencia propria.
- Not Diamond Code (vendedor): corte de 39% (Poly-SWE-bench Verified) e 61% (LongCodeQA)
  com qualidade "perto do Opus", autodeclarado: https://www.notdiamond.ai/blog/not-diamond-code-intelligent-model-routing-for-coding-agents
- Ressalva pratica (blog Unblocked): roteador pode baixar a fatura e subir iteracoes e
  retrabalho; execucoes agenticas na mesma tarefa variam ate 30x em tokens:
  https://getunblocked.com/blog/model-routing-coding-agents

## 8. O que a evidencia sustenta e o que nao

Sustenta (medido, com ressalvas):
- Para classificacao fechada (intencao, triagem, etiqueta), modelos de decisao custam
  ordens de grandeza menos que Opus/GPT e respondem em dezenas a centenas de ms
  (Requesty, paper medico).
- Roteamento forte/fraco corta custo em torno de 2x em tarefas de chat/conhecimento (RouteLLM).

Nao sustenta (sem evidencia independente):
- Economia de tokens em fluxo de dev com Claude Code: so demos e numeros de vendedor.
- Qualidade de roteamento em codigo (qual issue e "simples"): nada medido por terceiro
  para esses modelos; os pontos fracos medidos (tool-call 68,7%, complexidade 51,9%)
  sao exatamente a decisao que um roteador de dev toma.
- Que o Clef/Laya sejam melhores que o Jev: numeros do Clef sao autodeclarados.

## 9. Riscos

1. Roteamento errado de tarefa dificil para modelo barato: custo aparece em retrabalho.
2. Injecao de prompt: o texto que o decisor le (issue, codigo, resultado de tool) e nao
   confiavel; Jev mostrou sensibilidade, mesmo que baixa (arXiv 2609.28613).
3. Superconfianca: Laya e Jev tem calibracao ruim fora do dominio; confianca nao e acerto
   (README do Laya).
4. Laya zero-shot e proximo do acaso; exige fine-tuning com dados proprios (HF Laya).
5. Dependencia e custo escondido: Jev e fechado e pago; Clef local pede 41-85 GB de VRAM;
   proxies de terceiros ficam entre voce e a Anthropic com sua credencial passando.
6. Maturidade: semanas de idade; ferramentas de integracao sao nao oficiais.
7. Licenca: Clef e Laya Apache-2.0; Jev pesos fechados; jev-use MIT (fontes acima).

## 10. Relacao com este template (inferencia, nao da fonte)

- O template ja roteia por tamanho de issue (haiku/sonnet/opus) de forma deterministica,
  com a label `size/*`. Um decisor probabilistico so se justificaria se a classificacao por
  label fosse o gargalo, o que nao ha dado de que seja.
- Se for testar, medir antes: N issues reais, tamanho decidido pelo decisor contra decidido
  por humano, custo total incluindo retrabalho. Nao adotar com base nos posts acima.

## 11. O que procurei e nao achei

- Paper ou relato independente de economia de tokens com Jev/Clef/Laya em Claude Code ou
  em SWE-bench.
- Pagina da Anthropic mencionando esses modelos.
- Reproducao externa do Decision Index do Clef.
- Issues abertas do Clef (repo de codigo): nao localizei repo. As 11 discussoes do HF nao li.
- Levelup/gitconnected e Towards AI: 403 ou paywall; nao lidos
  (https://pub.towardsai.net/introducing-system-one-models-laya-and-jev-56b7271da9c2).
