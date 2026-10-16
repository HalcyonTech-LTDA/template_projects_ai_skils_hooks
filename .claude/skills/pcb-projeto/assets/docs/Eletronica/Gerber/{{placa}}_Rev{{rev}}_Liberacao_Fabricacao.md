---
title: {{placa}} Rev {{rev}} · Liberacao para fabricacao (portao 2)
type: gate
gate: liberacao
status: rascunho
created: {{data}}
updated: {{data}}
project: {{projeto}}
module: 03_Hardware
layer: hardware
placa: {{placa}}
revisao: {{rev}}
revisores: []
date:
fabricante: JLCPCB
tags: [gate, layer/hardware, module/hardware, tema/fabricacao]
---

# {{placa}} Rev {{rev}} · Liberacao para fabricacao

Portao 2. O pacote so vai para `hardware/{{placa}}/releases/rev-{{rev}}/` quando
`portao_liberacao.py` passa **e** esta nota esta em `status: aprovado`, com `revisores` preenchido
por quem revisou (pessoa, nao o agente) e nenhum item `- [ ]` em aberto. Item que nao se aplica:
`- [x] N/A — motivo`.

## Evidencia automatica

- Comando: `python .claude/skills/pcb-projeto/scripts/portao_liberacao.py hardware/{{placa}} --checklist <esta nota>`
- Resultado (cole o resumo):
- Pre-visualizacao: render top/bottom em `hardware/{{placa}}/fab/rev-{{rev}}/`
- Avisos de DRC e justificativa:

| Aviso | Onde | Justificativa |
|---|---|---|
| | | |

## Checklist de layout

- [ ] Avisos de DRC listados pelo portao copiados abaixo, cada um com a justificativa (ou corrigidos, ou excluidos no KiCad com comentario)
- [ ] Exclusoes e regras com severidade rebaixada que o portao listou foram conferidas por uma pessoa (cada exclusao tem comentario que a justifica)
- [ ] Contorno, furos de fixacao e posicao dos conectores batem com o desenho mecanico ou a caixa
- [ ] Capacitores de desacoplamento junto aos pinos, com via curta ao plano
- [ ] Laco de entrada do buck minimo; no de chaveamento curto; realimentacao longe do no de chaveamento
- [ ] Plano de GND continuo sob os sinais; nenhuma fenda sob trilha rapida
- [ ] Antena do modulo de radio na borda, com a area de exclusao do datasheet livre de cobre
- [ ] Cristal perto do MCU, cercado por GND, sem sinal passando por baixo
- [ ] Trilhas de potencia dimensionadas para a corrente com elevacao de temperatura definida; vias suficientes nas trocas de camada
- [ ] Pad termico de drivers e reguladores com vias termicas para o plano
- [ ] Rotas do Freerouting revisadas; redes Power e HV roteadas ou conferidas por uma pessoa
- [ ] Pares diferenciais (USB) roteados como par, com impedancia se aplicavel
- [ ] Zonas reenchidas, sem ilha de cobre solta
- [ ] Polarizados com marcacao visivel na serigrafia (pino 1, catodo, +)
- [ ] Serigrafia legivel (altura de 1 mm ou mais, linha de 0,15 mm ou mais), fora dos pads
- [ ] Nome da placa, revisao e data na serigrafia
- [ ] Test points nos trilhos e nos sinais de depuracao
- [ ] Fiduciais quando houver montagem SMT com passo fino
- [ ] Componentes afastados da borda o bastante para fresagem ou painel

## Checklist de fabricacao

- [ ] Gerbers revisados visualmente camada por camada (visualizador da JLC ou GerbView)
- [ ] Furacao: PTH e NPTH conferidos, furos de fixacao no diametro certo
- [ ] BOM JLC: todo item montado tem codigo LCSC com estoque; pecas Extended contadas e aceitas
- [ ] CPL: rotacao de cada componente conferida no preview da JLC e corrigida onde divergiu
- [ ] Parametros do pedido conferidos: camadas, espessura, acabamento, cor, cobre, posicao do numero do pedido
- [ ] Custo e prazo registrados em `08_Producao/Custos_BOM/`
- [ ] Imposto de importacao estimado (empresa paga regime diferente de pessoa fisica — ver `pcb-componentes`)

## Pedido

| Item | Valor |
|---|---|
| Camadas / espessura / acabamento | |
| Quantidade de placas / montadas | |
| Tipo de montagem (Economic/Standard) | |
| Custo placa + montagem + frete | |
| Numero do pedido | |
| Data do pedido | |
