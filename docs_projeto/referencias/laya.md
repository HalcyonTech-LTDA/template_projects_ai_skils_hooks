---
title: Laya - ATENCAO, dois produtos com o mesmo nome
source: https://horadecodar.com.br/laya/
type: referencia
tags: [referencia, modelo, system-one, laya, convai]
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
---

# Laya

Metodo: WebFetch (resume a pagina, pode errar) + uma WebSearch. Nada conferido por curl; tudo e "via
resumo, nao conferido literalmente".

## 0. Contradicao entre fontes: "Laya" e dois produtos

1. **Laya, modelo de decisao System One** (Convai Innovations). E o que o DSA, Hora de Codar e a Cloudflare
   chamam de Laya. Detalhes abaixo.
2. **Laya, app desktop** de Aayush Chawla (laya.aay.sh): app local-first de produtividade (cards,
   pipeline, integracoes Slack/Jira/Bitbucket). NAO e um modelo; nao tem modelo proprio; usa Ollama,
   LM Studio ou chaves Claude/GPT/Gemini; licenca "free and open source" sem nome; sem data ("2026").
   Fonte: https://laya.aay.sh/ . Nada na pagina menciona Jev, System One nem economia de tokens. O app expoe
   servidor MCP local (`http://127.0.0.1:8420/mcp/`, escopos Read/Write/Egress) e pode rodar Claude Code
   como agente. Os "ganhos" ("15 minutes gone", "50+ times per day", "23 minutes of focus", "Zero context
   switching") sao exemplos ilustrativos ou sem fonte, sem metodologia. Inconsistencia da propria pagina:
   "10-Stage" pipeline vs 4 etapas em "How Laya works".

   O link do Medium (https://medium.com/@christian.graham_49279/laya-a-free-local-alternative-to-jev-and-it-can-even-play-doom-ish-42e2292e541e)
   retornou HTTP 403 ao WebFetch; busca web tambem nao o achou. Conteudo NAO lido. O titulo trata Laya como
   alternativa local ao Jev, ou seja, o modelo (item 1), mas isso e inferencia pelo titulo.

   Inferencia minha: quem pesquisar "Laya" no Google pode cair no app (item 2) achando que e o modelo.

## 1. Laya, o modelo

- Familia de modelos de decisao open source da Convai Innovations, Apache 2.0, lancada em 18/09/2026.
  Pesquisador: Nandakishor Mukkunnoth. GitHub: github.com/NandhaKishorM/laya; `pip install laya`.
  https://horadecodar.com.br/laya/ e https://blog.dsacademy.com.br/jev-e-laya-o-que-sao-os-modelos-de-decisao-system-one-e-quando-usa-los/
- Mesma interface do Jev: estado + perguntas tipadas (choice, score, noul), devolve probabilidades.
- Checkpoints (https://horadecodar.com.br/laya/):
  - `laya`: ModernBERT-large, 421M parametros, contexto 512, ingles.
  - `laya-multilingual`: mmBERT-base, 322M, contexto 1024, 100+ idiomas.
  - `laya-typed-decisions`: ajustado no split de treino do proprio benchmark.
  - Uma busca web achou fonte dizendo 8192 de contexto; conflito nao resolvido. Conferir no model card.
- Roda local, inclusive em CPU via ONNX (partida a frio lenta). Runtimes nao oficiais: Node/ONNX, MLX, GGUF.
- Na tabela da Cloudflare, "Laya" aparece como baseline fraco (ex. BFCL 38,1; MMLU 30,7) com latencia
  mediana 5,8 ms. https://huggingface.co/Cloudflare/clef
- Integracao com Claude Code: nenhuma fonte descreve. E biblioteca Python, nao mod nem MCP.

## 2. Numeros alegados e origem

| Numero | Origem | Observacao |
|---|---|---|
| 32,8 ms mediana por decisao (T4); 7,2 ms/pergunta em lote de 10 | Autores do Laya | Sem metodologia no artigo. https://blog.dsacademy.com.br/jev-e-laya-o-que-sao-os-modelos-de-decisao-system-one-e-quando-usa-los/ |
| Zero-shot 0,362 (acaso 0,318; classe majoritaria 0,461) | Autores | Perto do acaso e abaixo da majoritaria |
| Ajustado: 0,766 vs Jev 0,727 | Autores | Treinado na particao de treino do proprio benchmark; ajuste ~4 h em GPUs gratis do Kaggle |
| Banking77: Laya 0,425 vs Jev 0,870 | Autores | Mostra a fraqueza sem especializacao |
| ECE 0,466 para 0,081 apos calibrar temperatura | Autores | Sai superconfiante por padrao |
| Respan: ~30% mudam de resposta em pares equivalentes; ~40% de injecao de prompt | Respan (vende concorrente) | Muito pior que o Jev (2% e 6%) |
| Fora do ingles: 0% de acerto com 95% de confianca media | Mesmo post | Precisa do roteador de idioma |

Nenhum numero e de terceiro independente sobre ganho de tokens ou de velocidade de desenvolvimento.

## 3. Limitacoes admitidas

- Zero-shot fraco: "base rapida para especializar" (palavras do autor do artigo). Choice degrada com mais
  de ~20 opcoes. Superconfiante. Sem texto livre nem justificativa. Custo de GPU/operacao.
  https://horadecodar.com.br/laya/ e dsacademy.
- Disputa de anterioridade com trabalho do autor de 2025 (arXiv), segundo o DSA.
