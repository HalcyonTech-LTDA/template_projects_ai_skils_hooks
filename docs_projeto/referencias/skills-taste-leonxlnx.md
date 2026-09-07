---
title: taste-skill (Leonxlnx) — pacote de 13 skills de design
source: https://github.com/Leonxlnx/taste-skill
type: referencia
status: aprovado
created: 2026-09-07
updated: 2026-09-07
verificado_em: 2026-09-07
tags: [referencia, skills, design, claude-code, tema/tooling]
---

# taste-skill (Leonxlnx)

Pacote publico de skills de design frontend, instalado via CLI `skills` (npm). Licenca MIT.

## O que e

Apesar do nome do repositorio, **`taste-skill` nao e uma skill — sao 13**. O nome do repo e
o nome da skill principal nao batem: a "taste-skill" instala com o nome
**`design-taste-frontend`**.

| Nome instalado | Linhas | O que faz |
|---|---:|---|
| `design-taste-frontend` | 1206 | Default v2. Le o brief, infere direcao, tres dials (VARIANCE / MOTION / DENSITY). Landing, portfolio, redesign |
| `design-taste-frontend-v1` | 226 | v1 preservada para compatibilidade |
| `gpt-taste` | 74 | GSAP + ScrollTrigger, estrutura AIDA, tipografia editorial |
| `high-end-visual-design` | 98 | Look de agencia "cara": fonte, espaco, sombra, profundidade |
| `minimalist-ui` | 85 | Editorial monocromatico, sem gradiente nem sombra pesada |
| `industrial-brutalist-ui` | 92 | Swiss + terminal militar, contraste extremo de escala (beta) |
| `redesign-existing-projects` | 178 | Auditoria antes de mexer; upgrade sem quebrar funcionalidade |
| `stitch-design-taste` | 184 | Gera `DESIGN.md` para o Google Stitch. Traz `DESIGN.md` junto |
| `image-to-code` | 1228 | Gera imagem de referencia e implementa. **Escrita para o Codex** |
| `imagegen-frontend-web` | 987 | So gera imagem de referencia de site |
| `imagegen-frontend-mobile` | 1465 | So gera imagem de tela mobile |
| `brandkit` | 798 | So gera board de identidade visual |
| `full-output-enforcement` | 49 | Proibe placeholder e truncamento. Unica nao-estetica do pacote |

## Como foi instalado

O comando divulgado (`npx skills add Leonxlnx/taste-skill`) entra em **selecao interativa**
e nao termina numa sessao de agente sem TTY. O que roda de fato:

```bash
npx --yes skills add Leonxlnx/taste-skill -s '*' -a claude-code --copy -y
```

Tres flags importam:

- **`-a claude-code`** — o agente **nao** se chama `claude`. Esse valor e rejeitado
- **`--copy`** — o default e **symlink**. Como este template desce por copia para os
  projetos derivados, symlink quebraria no destino
- **`-s '*'`** — sem isso o CLI pergunta quais skills instalar

O CLI grava `.claude/skills/<nome>/SKILL.md` e um `skills-lock.json` na raiz. Nao cria
`node_modules` nem exige `package.json`.

## Armadilhas

- **Nome do repo ≠ nome da skill.** `-s taste-skill` falha; o nome e `design-taste-frontend`
- **Quatro skills exigem gerador de imagem** e estao inertes neste stack — ver secao 3 de
  [[../SKILLS|SKILLS.md]]
- **`design-taste-frontend` se exclui de dashboard e tabela de dados** por escrito. Para UI
  de produto, a skill certa continua sendo `ui-ux-pro-max`
- **O autor declara a v2 como "experimental, actively iterating"** — por isso a politica
  aqui e fork proprio, sem `skills update`

## Fonte

- Repositorio: https://github.com/Leonxlnx/taste-skill
- Indice das skills: `skills/llms.txt` no proprio repo
- CLI: pacote npm `skills` (`npx skills --help`)
