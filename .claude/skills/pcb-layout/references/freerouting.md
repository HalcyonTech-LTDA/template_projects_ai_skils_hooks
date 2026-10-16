# Freerouting

Tudo aqui foi medido em 2026-10-12 com o Freerouting **2.5.0** (2026-10-05), Java 26 e KiCad 10.0.0,
na placa exemplo (`pcb-projeto/assets/exemplo/placa-exemplo.json`). O `rotear.py` ja aplica o que
esta abaixo; esta ficha explica o porque e o que revisar.

## Instalacao

- Baixe `freerouting-2.5.0.jar` em https://github.com/freerouting/freerouting/releases (64 MB; nao ha
  checksum publicado para o jar). Precisa de **Java 21+** no PATH.
- Aponte a variavel no bloco `env` do `.claude/settings.local.json` (ignorado pelo git):
  `"env": {"FREEROUTING_JAR": "C:/ferramentas/freerouting/freerouting-2.5.0.jar"}`.
  `python .claude/skills/pcb-projeto/scripts/diagnostico.py` confirma.
- **Nao use o `freerouting-cli` nativo** (zip de 20 MB, checksum confere): na 2.5.0 ele trava no
  roteamento headless (`UnsupportedFeatureError: SerializationConstructorAccessor ... ComponentOutline`,
  erro de build do GraalVM) e fica parado ate o timeout. Por isso o `rotear.py` so usa o jar.
- Sem `--user_data_path` o Freerouting cria `%APPDATA%/freerouting/freerouting.json` e um log em
  `%LOCALAPPDATA%/freerouting/` ja no primeiro `--help`. O `rotear.py` aponta tudo para uma pasta
  temporaria; nada fica no perfil do usuario.
- **Telemetria vem ligada** (`allow_telemetry: true`, `disable_analytics: false`). O `rotear.py`
  passa `-da` e `FREEROUTING__USAGE_AND_DIAGNOSTIC_DATA__DISABLE_ANALYTICS=true`.

## Flags reais da 2.5.0 (as que o `rotear.py` usa)

| Flag | Efeito |
|---|---|
| `-de placa.dsn -do placa.ses` | entrada e saida; com as duas o roteamento roda sem interface |
| `--gui.enabled=false` | sem janela (o jar avisa que o log e a unica saida) |
| `--router.autorouter.max_passes=N` | passes do autorouter (o `-mp` ainda funciona, mas e obsoleto) |
| `-mt N` | threads do otimizador (padrao: nucleos - 1) |
| `--router.autorouter.ignore_net_classes=Power,HV` | net classes que ele nao roteia (`-inc` e obsoleto) |
| `--router.fanout.enabled=false` | desliga a etapa de fanout (ver problemas) |
| `--router.neck_width_um=150` | largura da "tentativa estreita" quando uma rede nao passa (padrao 125) |
| `-da`, `--user_data_path=<dir>` | sem telemetria; config e log fora do perfil |

`-l <idioma>` nao serve para o log: com `-l en` ele criou uma pasta `en/` com o log no diretorio atual.
O `--help` sai no idioma do sistema (aqui, portugues de Portugal). Uma chave errada so gera
`WARN Unknown settings property` no log; nao falha.

## Como o `rotear.py` usa

1. Trava as trilhas que ja existem. O KiCad as exporta como `(wire ... (type fix))`; o Freerouting
   nao mexe nelas e nao as devolve no SES; o `ImportSpecctraSES` apaga as trilhas da placa **menos as
   travadas**. No fim, so o que o script travou e destravado. Provado: 57 trilhas/vias de `Power`
   feitas antes voltaram intactas (mesmo uuid, geometria e largura), uma vez cada.
2. Tira os `(plane ...)` do DSN. Com plano, o Freerouting liga o GND por via ao plano, mas as trilhas
   picotam a zona em ilhas sem ligacao entre si: sobraram 5 conexoes de GND no exemplo. Sem plano o
   GND e roteado por trilha e a zona entra por cima.
3. Classes ignoradas: a flag funciona no autorouter, mas o fanout (se ligado) poe tocos e vias nelas.
   Por garantia o script tira do SES tudo o que estiver numa rede ignorada antes de importar.
4. Neckdown: na entrada de pino fino ele afina a trilha (0,1874 mm = 0,75 x 0,25 no ESP32) e as vezes
   chega a 0,125 mm, abaixo da minima de 0,15 (erro `track_width`). O script alarga para a minima e
   roda o DRC; se a trilha alargada violar alguma regra, volta como estava e avisa.
5. **Ele nao conta trilha existente como ligacao** (`fix` ou `protect`): numa placa ja roteada, roteia
   tudo de novo em paralelo (+70 trilhas no exemplo). O script roda antes um DRC numa copia sem zonas
   e so aceita do SES as redes com ligacao faltando; sem nenhuma, nem chama o Freerouting. Rede com
   parte ja roteada ainda pode ganhar trecho paralelo: confira na revisao.

## O que ele roteia bem e mal

- **Bem:** sinais digitais lentos ponto a ponto (GPIO, UART, I2C lento, EN/BOOT, LED), em placa com
  espaco. No exemplo (GND por trilha, sem plano): 89 ligacoes em 5 a 8 passes, o `rotear.py` inteiro
  em 15 a 25 s, 0 violacoes no log.
- **Mal (fica com a pessoa):** potencia (nao sabe largura por corrente nem laco de retorno), no de
  chaveamento do buck, pares diferenciais e impedancia (USB, RF), antena, analogico sensivel,
  isolacao de alta tensao. Ele so liga pontos respeitando largura e clearance da net class.
- Sai com muitas vias e trilhas em diagonal longas na face de baixo, cortando o plano de GND.
- **Otimizacao so com 100% roteado:** com classe ignorada, ou com trilha fixa na placa, ele conta
  ligacoes pendentes ("Skipping optimization stage") e entrega o roteamento sem otimizar.
- Repete o resultado para o mesmo DSN (4 execucoes iguais), mas qualquer mudanca na placa, ate os
  uuids de uma placa regerada, muda passes, trilhas e neckdowns. Rode o DRC depois de toda execucao.

## Revisao do resultado

1. `python verificar.py drc <placa> --paridade`: zero erros. Conexao faltando so pode ser de classe
   ignorada (o `rotear.py` lista por net class).
2. `kicad-cli pcb render --side top` e `--side bottom`: procure trilha passando sob o modulo de radio,
   entre os pads do buck, ou atravessando o plano de GND da face de baixo de ponta a ponta.
3. Na GUI: trilha de sinal colada em no de chaveamento, via no pad, retorno de GND longo do
   desacoplamento ate o pino de GND do CI.
4. Registre o que foi refeito a mao na nota de liberacao (portao 2).

## Problemas encontrados (2026-10-12)

| Sintoma | Causa | O que o `rotear.py` faz |
|---|---|---|
| `freerouting-cli` parado ate o timeout | erro de serializacao do build nativo | usa so o jar |
| Arquivos em `%APPDATA%`/`%LOCALAPPDATA%` | config padrao | `--user_data_path` temporario |
| Tocos e vias em rede de `Power` ignorada | fanout ignora `ignore_net_classes` | fanout desligado e SES filtrado |
| `track_width` 0,125 mm | micro neckdown do fanout e neckdown de pino | fanout desligado; alarga e confere |
| GND com conexoes faltando apos refill | zona exportada como plano, ilhas soltas | tira os planos do DSN |
| Cobre duplicado ao rodar de novo | trilha existente nao conta como ligacao | so importa rede pendente |
