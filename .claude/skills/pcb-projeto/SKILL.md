---
name: pcb-projeto
description: Conduz o projeto de uma placa eletronica (PCB) no KiCad 10 do requisito ao pedido de fabricacao — fases, portoes de revisao humana, estrutura de pastas, alta tensao e o toolkit de scripts da familia pcb-*. Use sempre que o usuario pedir para projetar, criar ou revisar uma placa, circuito impresso, hardware, eletronica de um produto, projeto KiCad, "faz a placa de", "precisamos de uma PCB para", ou quando nao estiver claro qual skill pcb-* usar. E a porta de entrada da familia pcb-componentes, pcb-esquematico, pcb-layout e pcb-fabricacao.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, Agent, AskUserQuestion, Skill, WebFetch, WebSearch
version: 1.0
---

# /pcb-projeto — do requisito ao pedido de fabricacao

Esta skill e o roteiro. As outras quatro da familia fazem o trabalho de cada fase:

| Fase | Skill | Entrega |
|---|---|---|
| Requisitos e arquitetura | **pcb-projeto** (esta) | Requisitos, diagrama de blocos, orcamento de potencia, classe de tensao |
| Componentes | `pcb-componentes` | Pecas com MPN, LCSC, datasheet, simbolo e footprint conferidos |
| Esquematico | `pcb-esquematico` | `.kicad_sch` gerado da spec, ERC zero, netlist provada |
| Layout | `pcb-layout` | `.kicad_pcb` posicionado, sinais simples roteados (Freerouting), DRC sem erros com paridade |
| Fabricacao | `pcb-fabricacao` | Pacote JLCPCB, portao de liberacao, registro da revisao |

Pedido localizado ("troca esse regulador", "roda o DRC", "gera os gerbers") vai direto para a skill
da fase. Pedido de placa nova ou mudanca que atravessa fases comeca aqui.

## Por que o fluxo e assim

O KiCad e o oraculo. Nenhum passo e declarado pronto sem o `kicad-cli` ter dito isso: ERC e DRC com
`--exit-code-violations`, netlist exportada e comparada com a spec. Modelo de linguagem erra pinagem,
footprint espelhado e valor de componente com a mesma confianca com que acerta — so a verificacao
mecanica e a revisao humana pegam isso. Por isso ha dois portoes humanos e nenhum "parece certo".

O KiCad 10 nao tem API headless para esquematico (a IPC API so cobre o editor de PCB e exige a
interface aberta). A familia gera o esquematico em S-expression e usa o `pcbnew` (SWIG) so onde o
CLI nao alcanca: placa a partir da netlist e Specctra para o Freerouting. **O SWIG sai no KiCad 11**
— os scripts `pcb_do_esquematico.py` e `rotear.py` precisarao migrar. Detalhes em
`references/ferramentas.md`.

## Fase 0 — ambiente

```bash
python .claude/skills/pcb-projeto/scripts/diagnostico.py
```

Mostra a versao do KiCad, o caminho do `kicad-cli`, o Python do KiCad (para os scripts SWIG), Java e
o jar do Freerouting. Se algo faltar, o diagnostico diz como instalar. Catalogo completo dos
comandos em `scripts/README.md`.

## Fase 1 — requisitos

Antes de qualquer componente, levante e registre (pergunte o que faltar — `AskUserQuestion`):

- **Alimentacao:** fonte de entrada (tensao minima/maxima, de onde vem, conector), consumo esperado,
  bateria, picos de motor/rele.
- **Tensao maxima presente na placa** (valor de pico). Acima de 60 V DC, acima de 42,4 V de pico em
  AC ou ligada a rede (127/220 VAC) e **alta tensao** — ver "Portao de alta tensao" abaixo, antes de
  seguir.
- **Interfaces:** sensores, atuadores, comunicacao (UART, I2C, SPI, RS-485, CAN, USB, Wi-Fi/BLE),
  conectores e o que se liga neles do lado de fora.
- **Ambiente:** temperatura, umidade, vibracao, poeira/agua (IP), ruido eletrico (motores, inversores).
- **Mecanica:** dimensao maxima, furos de fixacao, caixa, posicao dos conectores. Se houver caixa,
  pegue o desenho antes do layout — mudar contorno depois custa uma rodada.
- **Volume e custo alvo**, montagem manual ou SMT pela JLCPCB, prazo.
- **Certificacao** que o produto precisa (Anatel se tiver radio; ver `07_Certificacoes_Homologacoes`).

Registre em `02_Especificacoes/Requisitos_*` do projeto (modelo `Requisito_Template`) ou, para placa
pequena, na nota de diagrama de blocos.

## Fase 2 — arquitetura

1. **Diagrama de blocos** em Mermaid na nota `<placa>_Diagrama_de_Blocos.md` (criada pelo
   `novo_projeto.py --docs`). Um bloco por funcao (entrada e protecao, conversao, MCU, potencia,
   comunicacao, conectores), com tensoes e sinais nas setas. E o "diagrama eletrico" de alto nivel
   que a equipe le no Obsidian; o esquematico e o detalhe.
2. **Orcamento de potencia:** tabela por trilho (corrente tipica e de pico por consumidor, margem de
   30% ou mais, dissipacao de cada regulador). Regulador linear com queda alta dissipa
   `(Vin - Vout) x I` — 12 V para 3,3 V a 300 mA sao 2,6 W, inviavel em SOT-223: use buck.
3. **Escolhas grandes:** MCU ou modulo (modulo certificado como ESP32-S3-WROOM-1 evita projeto de RF
   e encurta homologacao), numero de camadas (2 por padrao; 4 com RF integrado, USB de alta
   velocidade, ADC sensivel ou BGA), montagem (JLCPCB SMT por padrao).
4. Decisao que mude custo, prazo ou risco vira ADR em `01_Gestao/Decisoes_Tecnicas/`.

## Criar o projeto

```bash
python .claude/skills/pcb-projeto/scripts/novo_projeto.py hardware --nome <placa> [--camadas 2|4] \
  --docs "docs_projeto/<Projeto>/03_Hardware"
```

Cria `hardware/<placa>/` (fonte KiCad, versionada) e as notas modelo em `03_Hardware/`. A divisao:

| Onde | O que | Versionado |
|---|---|---|
| `hardware/<placa>/` | `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `.kicad_dru`, `spec/<placa>.json`, `bibliotecas/` do projeto | Sim |
| `hardware/<placa>/fab/` | Saidas de trabalho do `exportar_fab.py` | Nao (`.gitignore`) |
| `hardware/<placa>/releases/rev-<R>/` | Pacote liberado pelo portao (zip Gerber, BOM, CPL, PDF, manifesto com SHA-256) | Sim |
| `03_Hardware/Eletronica/` | Diagrama de blocos, PDF do esquematico, notas de revisao (portoes), BOM comentada | Sim |
| `03_Hardware/Prototipagem/Rev_<R>/` | Bring-up, achados, mudancas para a proxima revisao | Sim |
| `03_Hardware/Mecanica/CAD_3D/` | STEP da placa para a caixa | Sim |
| `08_Producao/` | Custos de BOM por volume, fornecedores, instrucoes de montagem | Sim |

Mapa completo e convencao de nomes em `references/estrutura-de-pastas.md`.

## Fases 3 a 6 — execute pela skill da fase

Siga nesta ordem, cada uma com sua prova:

1. `pcb-componentes` — nenhuma peca entra na spec sem MPN, datasheet lido e footprint conferido.
2. `pcb-esquematico` — spec JSON → `.kicad_sch`; prova: ERC zero e `verificar.py netlist` ok.
3. **Portao 1 (humano): revisao do esquematico.** Nota `<placa>_Rev<R>_Revisao_Esquematico.md`,
   checklist de `pcb-esquematico`. Layout so comeca com `status: aprovado` e `revisores` preenchido.
   Mudar circuito depois do layout custa caro; este e o portao mais barato.
4. `pcb-layout` — prova: DRC sem erros com `--schematic-parity` e zonas reenchidas; avisos justificados na nota do portao 2.
5. `pcb-fabricacao` — pacote JLCPCB e **portao 2 (humano + script): liberacao.**
   `portao_liberacao.py` so libera com ERC/DRC zerados, BOM completa e a nota de liberacao aprovada.

O agente **nunca** marca um portao como aprovado nem preenche `revisores` com o proprio nome. Quem
revisa e uma pessoa; o agente prepara a nota, roda as verificacoes e anexa a evidencia.

## Fase 7 — bring-up e proxima revisao

Ao chegar a placa: nota de bring-up em `Prototipagem/Rev_<R>/` (modelo copiado pelo
`novo_projeto.py`). Ordem segura: inspecao visual e de curto entre trilhos com multimetro, fonte de
bancada com limite de corrente, trilho a trilho, so entao o MCU e as cargas. Todo defeito vira item
numerado na nota; correcao no esquematico abre a `Rev_<R+1>`. Nunca altere arquivos de uma revisao
ja liberada — a revisao seguinte e copia de trabalho nova.

## Portao de alta tensao

Placa com rede eletrica (127/220 VAC), mais de 60 V DC ou mais de 42,4 V de pico em AC:

1. **Primeiro pergunte se precisa.** Modulo AC-DC certificado (Mean Well, Hi-Link e similares) deixa
   a placa inteira em baixa tensao e elimina a maior parte do risco e da certificacao. Recomende isso
   antes de projetar a parte de rede.
2. Se a parte de alta tensao fica na placa: declare `tensao_max_v` na spec e coloque as redes na net
   class `HV`. Criando o projeto com `novo_projeto.py ... --alta-tensao`, as regras de
   `assets/kicad/alta-tensao.kicad_dru` ja entram no `.kicad_dru` do projeto e a nota de aprovacao e
   copiada junto com as outras; em projeto existente, concatene o arquivo e valide com
   `verificar.py dru` (regra com erro e descartada em silencio pelo KiCad).
3. Isolacao: distancias de clearance e creepage vem da norma de seguranca aplicavel (IEC 62368-1 para
   equipamento de TI/audio/video, IEC 60335 para eletrodomestico), **nao** da tabela funcional da
   IPC-2221. O valor de 2,5 mm do modelo e ponto de partida, nao aprovacao. Fendas (slots) na placa
   aumentam creepage; fusivel na entrada, varistor, e isolacao galvanica entre o lado de rede e o de
   baixa tensao.
4. A nota `<placa>_Rev<R>_Aprovacao_Alta_Tensao.md` (modelo em `assets/opcionais/`; copiada pelo
   `--alta-tensao`) fica ao lado da nota de liberacao. `portao_liberacao.py` bloqueia a liberacao sem
   essa nota aprovada por uma pessoa.

Racional e lista de verificacao em `references/alta-tensao.md`.

## O que o agente faz mal — diga isso ao usuario quando aparecer

- **Roteamento** de potencia, retorno de corrente, pares diferenciais (USB), RF, analogico sensivel e
  no de chaveamento de buck: o Freerouting nao entende nada disso. Esses ficam com o humano.
- **Pinagem e footprint**: o agente confere contra o datasheet, mas a revisao humana do portao 1 e
  da liberacao e o que garante.
- **EMC e certificacao**: pre-conformidade por boas praticas, nunca promessa de aprovacao.
- **Numeros de norma**: as fichas em `docs_projeto/referencias/` marcam o que foi lido em fonte
  secundaria. Numero marcado "conferir" nao vira regra dura sem conferencia.

## Referencias desta skill

- `references/estrutura-de-pastas.md` — arvore de `hardware/<placa>/`, nomes, revisoes, `.gitignore`.
- `references/alta-tensao.md` — portao de alta tensao em detalhe.
- `references/ferramentas.md` — por que `kicad-cli` + scripts e nao MCP; MCPs e skills de terceiros
  opcionais (KiCad MCP, `kicad-happy`); risco do KiCad 11; SKiDL como alternativa.
- `scripts/README.md` — catalogo dos comandos do toolkit.
- Fichas em `docs_projeto/referencias/`: `kicad-cli-e-formatos`, `kicad-mcp-e-skills`,
  `componentes-e-fabricacao-pcb`, `boas-praticas-pcb`.
