---
title: Clef (Cloudflare) - modelo de decisao System One
source: https://huggingface.co/Cloudflare/clef
type: referencia
tags: [referencia, modelo, system-one, cloudflare, clef]
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
---

# Clef (Cloudflare)

Metodo: WebFetch (resume a pagina, pode errar), nada conferido por curl. Fonte primaria (model card), mas
os numeros sao da propria Cloudflare.

## 1. O que e

- Modelo multimodal de 27B parametros (BF16, safetensors). Recebe estado + perguntas tipadas e devolve
  probabilidade por opcao. "There is no free-form text generation and no output parsing."
  https://huggingface.co/Cloudflare/clef
- Base: Qwen/Qwen3.8-27B com encoder de visao. Variante menor: Clef-Flash. Licenca Apache-2.0.
- Publicador: Cloudflare. Data de lancamento: a pagina nao informa. Cita post do blog da Cloudflare sem data.
- Compativel com a API Jev/SystemOne. Nao e modelo de geracao de codigo; e do mesmo tipo do Jev e Laya.
- Hardware: testado em uma H200 (torch 2.11, transformers 5.10.2); SGLang cita H200, B200, B300. Ou seja,
  nao e para rodar em notebook; sao GPUs de datacenter.

## 2. Integracao

- Python: `snapshot_download("Cloudflare/clef")`, `load_release_model(path, device="cuda")`,
  `encode_record`, softmax por pergunta. Entrada padrao de 16.384 tokens.
- Servidores: `sglang serve --model-path Cloudflare/clef --port 30000` (endpoint `/v1/systemone`);
  `vllm serve "Cloudflare/clef"`; `docker model run hf.co/Cloudflare/clef`.
- O artigo https://horadecodar.com.br/mods-no-claude-code-2/ cita Cloudflare Workers AI como caminho de
  acesso para mods do Jev; nao diz que o Clef esta la (nao confirmado).
- Claude Code: nenhuma fonte descreve integracao. Inferencia minha: seria um juiz de decisao chamado por
  hook/script, nao um substituto do modelo do agente.

## 3. Numeros e origem

Origem unica: "benchmark interno (Decision Index 0.2.1)", execucao interna da Cloudflare, sem verificacao de
terceiros. https://huggingface.co/Cloudflare/clef (a pagina nao detalha mais a metodologia). Nao ha
numero de economia de tokens nem de produtividade de desenvolvimento. Amostra (Clef / Jev):

| Benchmark | Clef | Jev |
|---|---|---|
| BFCL | 98,5 | 95,8 |
| BANKING77 (macro-F1) | 94,2 | 79,7 |
| CRUXEval | 86,7 | 73,0 |
| MMLU | 90,3 | 91,7 |
| GPQA Diamond | 48,0 | 78,3 |
| BBH | 73,7 | 92,9 |
| Latencia mediana (ms) | 209,3 | 524,1 |

Workflows (Typesafe Evals, rotulos de consenso): faturas, acoes exatas 64,7 vs 61,8; atendimento 76,3 vs
76,0; incidentes 62,9 vs 61,7; observabilidade de agentes (acao primaria) 68,5 vs 71,6. Diferencas de 1 a 3
pontos, sem intervalo de confianca.

## 4. Limitacoes admitidas ou visiveis

- Resultados internos, sem verificacao independente.
- Nem sempre superior: o Jev vence em GPQA, MMLU-Pro, BBH e outros; Clef-Flash vence em varios.
- Nao gera texto; so probabilidades. Tabela deixa o Laya com latencia mediana de 5,8 ms contra 209,3 do Clef.
- Testado so em uma configuracao (H200).

## 5. Nao encontrado

- Data de lancamento, post do blog da Cloudflare (so citado), preco em Workers AI, qualquer uso dentro do
  Claude Code ou medicao de economia de tokens.
