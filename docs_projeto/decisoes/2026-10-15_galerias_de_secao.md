---
title: Galerias de secao como degrau da pesquisa de frontend
type: decisao
status: aprovado
created: 2026-10-15
updated: 2026-10-15
project: template_projetos
tags: [decisao, skills, design, frontend, tema/tooling]
---

# 2026-10-15 — Galerias de secao na pesquisa de frontend

## O que mudou

1. `.claude/skills/_shared/fontes-frontend.md`: o passo 2 ganhou o degrau 3, **"galeria da
   secao"**, com a tabela que liga cada tipo de bloco a uma galeria. "Produtos reais" passou a
   ser o degrau 4, e "pagina do componente no Arc ou no Cult", o 5
2. Ficha consolidada nova: [[../referencias/galerias-de-secao|galerias-de-secao]]
3. [[../SKILLS|SKILLS.md]] secao 8: a ordem da regra 1 e a tabela de fontes foram atualizadas
4. As quatro `SKILL.md` de design **nao foram editadas**. A regra inline delas
   (usuario > refero > produtos reais) continua valida, porque a galeria mostra captura de
   produto real. O detalhe fica so no arquivo compartilhado

## Por que

O usuario pediu para adicionar 8 sites como referencia de design: scrolltide, navbar.gallery,
footer.design, cta.gallery, 404s.design, unsection, bentogrids e 60fps.

A pesquisa mudou a premissa. Nenhum deles e "site de componentes" no sentido de Arc ou Cult.
Sete sao galerias de captura por tipo de secao e nao trazem codigo. O oitavo, scrolltide, e um
produto pago de prompt e template, com licenca que proibe redistribuir. O papel deles e,
portanto, **referencia de bloco**, e nao fonte de componente.

O degrau entrou abaixo do Refero e acima dos produtos reais por tres motivos:

- O plano gratuito do Refero mostra pouco do acervo, e as galerias sao gratis
- Seis das sete sao lidas pelo WebFetch
- Elas respondem a pergunta concreta "como sites reais resolvem este footer"

O risco e a pagina virar uma colagem de blocos de origens diferentes. Por isso a galeria
**nunca** e a referencia principal do lock.

## Decisoes do usuario

| Pergunta | Resposta |
|---|---|
| Escopo | Protocolo + fichas (sem editar as 4 skills) |
| Formato da ficha | Uma consolidada |
| Scrolltide | So referencia: olhar o efeito, nao colar o prompt |
| Site pago, fraco ou abandonado | Fica na ficha com aviso, fora do degrau |

## Achados que contradizem o anuncio

- O scrolltide anuncia "600+ prompts", mas a home conta cerca de 275 itens, 121 deles
  templates. A promessa de "prompt com source completo" nao foi confirmada
- O 60fps e voltado para iOS, e o MCP dele (pago) devolve SwiftUI
- O bentogrids mistura conceitos do Dribbble com sites em producao
- A aba de templates do unsection e vitrine paga da shadcnblocks

## Alternativas descartadas

- **So as fichas, sem mexer no protocolo.** Custaria menos, mas o agente so acharia as
  galerias se lesse o README de referencias
- **Citar os sites inline nas 4 skills.** O efeito seria mais garantido, mas o mesmo texto
  ficaria em quatro lugares para manter. Foi a divergencia que motivou o `_shared/`
- **Scrolltide como fonte de codigo no passo 4.** Descartado por ser pago e pela licenca
  pessoal sem redistribuicao. Alem disso, um prompt pronto pula a pesquisa

## Riscos em aberto

- Contagens, precos e patrocinios mudam. A ficha registra o que estava no ar em 2026-10-15
- O cta.gallery nao declara dono. Se sumir, o unsection cobre a categoria CTA
- Propagar `_shared/fontes-frontend.md` para os projetos derivados por copia, como as outras
  mudancas do protocolo
