# Portao de alta tensao

**Alta tensao, para esta familia:** qualquer placa com conexao a rede eletrica (127/220 VAC), com
mais de 60 V DC ou com mais de 42,4 V de pico em AC (cerca de 30 V eficazes) em algum ponto. Os
limites acompanham a faixa de tensao de seguranca extra-baixa (ES1) da IEC 62368-1; acima dela o
erro de projeto vira choque ou incendio, nao so placa que nao funciona. Na spec, `tensao_max_v` e
sempre o valor de **pico** e `"tensao_ac": true` troca o limite de 60 V pelo de 42,4 V.

## 1. A primeira pergunta: precisa estar na placa?

Na maioria dos produtos de mecatronica a resposta e nao. Um modulo AC-DC certificado (Mean Well,
Hi-Link e similares, encapsulado ou de trilho DIN) entrega 5/12/24 V isolado. A placa inteira fica
em baixa tensao, e a parte perigosa vem com certificacao do fabricante do modulo.

Recomende o modulo e so siga com rede na placa se houver motivo concreto (custo em volume, espaco,
acionamento direto de carga AC por rele/triac). Registre o motivo numa ADR.

## 2. Se a rede fica na placa

### Esquematico

- Fusivel na entrada de fase, antes de tudo. Varistor (MOV) depois do fusivel.
- Isolacao galvanica entre o lado de rede e o de baixa tensao: fonte isolada, optoacoplador ou
  isolador digital nos sinais que cruzam, rele com isolacao bobina-contato especificada.
- Redes do lado de rede na net class `HV`. Nomeie redes claramente: `AC_L`, `AC_N`, `HV_BUS`.
- `tensao_max_v` na spec com o valor de pico real (220 VAC tem pico de ~311 V; com tolerancia de
  rede, considere mais).

### Layout

- Inclua `assets/kicad/alta-tensao.kicad_dru` nas regras do projeto (concatenado ao
  `<placa>.kicad_dru`). Ele aplica clearance e creepage para a net class `HV`. O valor de 2,5 mm do
  modelo e **ponto de partida**, nao aprovacao.
- Os valores definitivos de clearance e creepage vem da norma de seguranca do produto (IEC 62368-1
  para equipamento de TI/AV, IEC 60335 para eletrodomestico, IEC 61010 para instrumento de medicao),
  em funcao de tensao de trabalho, grau de poluicao, grupo de material e categoria de sobretensao.
- **Nao use a tabela 6-1 da IPC-2221 como distancia de seguranca.** Ela e isolacao funcional; a
  ficha `docs_projeto/referencias/boas-praticas-pcb.md` registra que as fontes secundarias divergem
  em faixas como 101-150 V e que certificador nao a aceita como tabela de seguranca.
- Fenda (slot) fresada entre lado de rede e baixa tensao aumenta creepage; marque a area de alta
  tensao na serigrafia com o simbolo de risco eletrico.
- Nada de plano de terra de baixa tensao passando por baixo da area de rede.

### Fabricacao e teste

- Pedido com espessura de cobre e mascara compativeis; inspecao da isolacao antes de energizar.
- Bring-up de rede so com transformador isolador e protecao (DR), nunca sozinho.

## 3. O que o script verifica

`portao_liberacao.py` exige `tensao_max_v` finito na spec (`null`, ausente ou nao numerico bloqueia,
porque nao da para saber se a placa e segura) e trata a placa como alta tensao quando:

- `|tensao_max_v|` passa do limite (60 V, ou 42,4 V com `tensao_ac: true`); ou
- a spec declara redes na net class `HV`; ou
- alguma rede da netlist exportada pelo KiCad esta na classe `HV` — inclusive por padrao regex no
  `.kicad_pro` ou com duas classes na mesma rede (`HV,Power`).

Nesse caso exige:

1. a nota `<placa>_Rev<R>_Aprovacao_Alta_Tensao.md` (modelo em `assets/opcionais/`; procurada ao lado
   da nota de liberacao ou passada por `--aprovacao-hv`) com `type: gate`, `gate: alta-tensao`, a
   `placa` e a `revisao` do projeto, `status: aprovado`, `revisores` preenchido e todos os itens
   marcados — e que nao seja o mesmo arquivo da nota de liberacao;
2. regras validas para a net class `HV` no `.kicad_dru`: condicao `A.hasNetclass('HV')` (ou com
   `|| B.hasNetclass('HV')`), sem `severity` diferente de error, sem restricao de camada, com
   `clearance` e `creepage` de pelo menos 2,5 mm (podem estar em regras separadas, como no modelo) —
   e o arquivo aceito pelo KiCad (regra-canario: arquivo invalido e descartado em silencio). Se a nota
   de alta tensao declarar `clearance_mm` e `creepage_mm` no frontmatter (os valores tirados da
   norma), esses passam a ser o minimo exigido.

**As regras `HV` ficam no fim do `.kicad_dru`.** No KiCad vale a ultima regra que casa, mesmo que
seja mais ampla: uma regra generica de clearance escrita depois das de `HV` anula a isolacao, e o
portao bloqueia esse caso. O `novo_projeto.py --alta-tensao` ja concatena o modelo no fim.

O agente nunca aprova essa nota. Ele prepara, verifica e anexa a evidencia (relatorio de DRC,
captura da area de isolacao).
