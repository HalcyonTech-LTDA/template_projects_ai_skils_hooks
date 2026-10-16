"""pcbkit: biblioteca da familia de skills pcb-* (KiCad 10).

Stdlib apenas, exceto `pcbkit.swig`, que roda so no Python embarcado do KiCad.
Modulos:
- ambiente     localiza KiCad, kicad-cli, Python do KiCad, Java, Freerouting e bibliotecas
- sexpr        parser/serializador S-expression do KiCad
- bibliotecas  tabelas de biblioteca, resolucao de `Lib:Nome`, pinos, busca
- kicad_cli    chamadas ao kicad-cli e leitura dos relatorios JSON
"""

# Versoes de formato gravadas pelo KiCad 10.0.0 (ver "## Oraculo" no handoff da skill).
VERSAO_SCH = 20260306
VERSAO_PCB = 20260206
VERSAO_SYM = 20251024
VERSAO_MOD = 20260206
GERADOR = "pcbkit"
GERADOR_VERSAO = "10.0"
