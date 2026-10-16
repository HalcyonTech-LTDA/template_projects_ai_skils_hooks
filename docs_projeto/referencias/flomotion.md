# FloMotion (flomotion.app)

Ficha de referencia. Data da pesquisa: 2026-10-15. Metodo: WebFetch (resume a pagina, pode errar) em
home, /features/motion, /resources e 4 artigos; nenhum trecho foi conferido por curl. Tudo abaixo e
"via resumo, nao conferido literalmente", salvo as aspas curtas, que tambem vieram do resumo.

## 1. O que e, para quem, problema

- "Agentic Robotics Studio": estudio de robotica com IA, "from schematic to motion". Cobre
  eletronica, CAD mecanico, simulacao e controle de movimento num so lugar. Fonte: https://flomotion.app/
- Publico: a home nao define explicitamente; o foco e quem constroi robos (ha catalogo de robos com
  fork e comunidade). Inferencia. Fonte: https://flomotion.app/
- Problema: ligar projeto eletronico + mecanico + movimento sem trocar de ferramenta, com agente de IA
  fazendo o rascunho. Inferencia a partir de https://flomotion.app/features/motion e de
  https://flomotion.app/resources

## 2. Funcionalidades e fluxo

- Home: descrever o projeto em linguagem natural, um agente configura o workspace; explorar robos
  existentes e fazer fork; filtros por base, controle, parte, tipo e licenca. https://flomotion.app/
- Motion Agent (beta): gera o movimento de um assembly estatico a partir de descricao; roda sob fisica
  real no navegador, pensado para transferir ao robo fisico. Fluxo: criar assembly em CAD, vincular a
  cena de controle, descrever comportamento, ver simulacao, aplicar ao robo real.
  https://flomotion.app/features/motion
- "Em breve" (mesma pagina): construcao de mundo por agente (chao, obstaculos, camera) e aprendizado
  por reforco (politica treinada incorporada a script de controle).
- Eletronica: agente posiciona componentes, desenha redes e roteia; simulacao de circuito (conexoes,
  alimentacao, terra, sobrecarga, osciloscopio, componente queimando; difere de SPICE).
  https://flomotion.app/article/online-electronics-editor-with-ai e /article/circuit-simulation
- Mecanica: usuario descreve a peca, agente cria e edita sob pedido; funciona em celular, sem
  instalacao. https://flomotion.app/article/online-cad-editor-with-ai
- CAM: agente gera trajetorias e exporta G-code para fresadora CNC.
  https://flomotion.app/article/ai-generated-gcode-for-cnc
- Cena controlavel manualmente (teclado/mouse/toque), emissores em robos, contato de dardo.
  https://flomotion.app/article/interactive-robot-simulation

## 3. Stack visivel ou inferivel

- Web app + app desktop. O desktop e "um shell open source em torno do cliente web"; simulacao de
  circuito e capturas so funcionam dentro da janela ("The window is not optional").
  https://flomotion.app/article/coding-agent-of-choice
- Simulacao fisica: MuJoCo (cita MuJoCo Menagerie; "same physics as any other scene").
  https://flomotion.app/article/robot-library-and-mjcf-import
- Formatos:
  - Importa MJCF (zip com XML na raiz + malhas) e STEP. URDF: nao mencionado na pagina de MJCF
    (nao confirmado). Conversoes na importacao: m para mm, rad para graus, elipsoide vira caixa.
    https://flomotion.app/article/robot-library-and-mjcf-import e /article/import-step-files
  - Exporta: esquematico para KiCad; peca em STEP ou STL; assembly em STEP; peca usinada em G-code.
    https://flomotion.app/article/coding-agent-of-choice
- Exemplos de hardware na home: ESP32, Raspberry Pi, servos, NEMA17, G-code, ROS 2 (so como exemplos
  de robos do catalogo, nao como integracao confirmada). https://flomotion.app/
- Kernel CAD, linguagem de script das pecas, se e paramétrico: nao confirmado (o artigo de CAD nao
  diz; a home fala em "CAD parametrico" nos exemplos, e a pagina de STEP fala em "script editavel"
  gerado pelo agente, o que sugere CAD por codigo; isso e inferencia).
  https://flomotion.app/article/online-cad-editor-with-ai e /article/import-step-files
- Repositorio GitHub: nao encontrado (busca web nao achou); so se sabe que o shell desktop e open
  source segundo o artigo acima. URL do repo: nao confirmado.

## 4. IA / LLM

- Agente embutido gera: programa de movimento, pecas 3D, esquematico, G-code. (secao 2)
- Agente externo: Claude Code, Codex CLI e Gemini CLI rodam comandos `flomotion` no terminal; o app
  desktop os executa com a conta logada; "No API key is created". Comandos: `flomotion agent` (estado
  em JSON), `flomotion act` (executa ferramenta), `flomotion job` (tarefas longas no servidor).
  Cursor aparece so como exemplo de agente, nao como testado. https://flomotion.app/article/coding-agent-of-choice
- Decisao notavel: nao usa MCP, com o argumento de que a lista de tools consumiria mais tokens que o
  trabalho. Ferramentas carregam em dois niveis (papel: bootstrap/manager/electronics/mechanics/
  control; e skills sob demanda). Mesmo artigo.
- Qual modelo de LLM o assistente embutido usa: nao confirmado.
- Limitacao declarada pelo proprio site: esquematico gerado e "a fast first draft, not a finished
  design"; pode errar funcao de pino, polaridade, pull-up; nao faz layout de PCB nem DRC; footprints
  especificos exigem escolha manual no KiCad. https://flomotion.app/article/ai-generated-schematics-for-kicad

## 5. Modelo de negocio e preco

- Existe /pricing, mas o WebFetch voltou vazio (provavel SPA). Planos e valores: nao confirmado.
  https://flomotion.app/pricing
- Indicio de modelo por creditos: cada acao no servidor custa 0,2 credito; acoes na janela
  (captura, simulacao) sao gratuitas; o FloMotion nao cobra o modelo de IA no uso via agente externo.
  Mesmo artigo de coding-agent-of-choice. Existe tambem assistente embutido (consumo de creditos nao
  detalhado).
- Catalogo de robos tem filtro de licenca (indica projetos compartilhados em comunidade). Home.
- Comunidade em Discord e r/FloMotion (links na home).

## 6. Diferencial vs. alternativas (inferencia, nao afirmado pelo site)

- Cadeia unica no navegador: esquematico + CAD + simulacao fisica MuJoCo + agente, com export para
  formatos abertos (KiCad, STEP/STL, G-code, MJCF).
- Controle por CLI de agentes de codigo ja populares, sem MCP e sem chave de API.
- Fraquezas visiveis: sem layout de PCB/DRC, beta no motion, RL e mundo ainda "em breve".
- Nao comparei com concorrentes por busca; qualquer comparacao nominal e nao confirmada.

## O que procurei e nao achei

- Pagina de precos com valores (vazia no fetch).
- GitHub, docs separadas, changelog, blog: nao aparecem na home. Os artigos de /resources (10, de
  mai a out/2026) funcionam como blog/changelog informal.
- Busca web por "flomotion.app" e "Agentic Robotics Studio": nenhum resultado sobre o produto
  (Product Hunt, HN e X nao foram achados; busca generica, nao exaustiva).
- Nao abri: /features/cad, /features/electronics, /motion/demos, /projects, artigos de 3D print,
  circuit-simulation, import-step.

## Fontes

- https://flomotion.app/
- https://flomotion.app/pricing (vazio)
- https://flomotion.app/features/motion
- https://flomotion.app/resources
- https://flomotion.app/article/coding-agent-of-choice
- https://flomotion.app/article/ai-generated-schematics-for-kicad
- https://flomotion.app/article/online-cad-editor-with-ai
- https://flomotion.app/article/robot-library-and-mjcf-import
- Titulos/resumos (via /resources) de: /article/circuit-simulation, /article/import-step-files,
  /article/ai-generated-gcode-for-cnc, /article/interactive-robot-simulation,
  /article/online-electronics-editor-with-ai
