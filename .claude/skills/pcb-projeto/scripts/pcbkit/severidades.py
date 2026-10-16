"""Severidades e exclusoes do `.kicad_pro`: o que o projeto rebaixou ou escondeu do ERC e do DRC.

O kicad-cli aplica o `rule_severities` e as exclusoes do `.kicad_pro` mesmo com `--severity-all`:
regra em `ignore` some do relatorio (medido no 10.0.0: `invalid_outline: ignore` zera um DRC que
tinha 1 erro). O relatorio sozinho nao prova nada; o portao le o `.kicad_pro` e confere aqui.

Onde ficam: DRC em `board.design_settings.rule_severities` e `.drc_exclusions`; ERC em
`erc.rule_severities` e `erc.erc_exclusions`. Chave ausente = padrao do KiCad. Exclusao e
`["tipo|x|y|uuid|uuid", "comentario"]` (ou so a string, em projeto antigo).

Padroes (KiCad 10.0.0): DRC = o `rule_severities` que o pcbnew grava num projeto novo
(`NewBoard` + `SaveBoard`, 2026-10-12). ERC: o portao roda o ERC em modo estrito (aviso tambem
bloqueia), entao so `ignore` esconde violacao; as tres regras que o KiCad ja ignora por padrao nao
contam como rebaixamento.

Criticas: rebaixar bloqueia o portao. DRC critica precisa ficar `error`; paridade com o esquematico
e `warning` por padrao no 10.0.0 (o portao bloqueia qualquer violacao de paridade, de qualquer
severidade) e so nao pode ir para `ignore`. ERC critica so nao pode ir para `ignore`.
`conflicting_netclasses` (citada no plano) nao existe no 10.0.0 e `via_diameter` nao aparece no
padrao do pcbnew 10; ficam na lista para o caso de projeto antigo trazer a chave.
"""

from dataclasses import dataclass, field

ORDEM = {"ignore": 0, "warning": 1, "error": 2}

PADRAO_DRC = {
    "annular_width": "error", "clearance": "error", "connection_width": "warning",
    "copper_edge_clearance": "error", "copper_sliver": "warning", "courtyards_overlap": "error",
    "creepage": "error", "diff_pair_gap_out_of_range": "error", "diff_pair_uncoupled_length_too_long": "error",
    "drill_out_of_range": "error", "duplicate_footprints": "warning", "extra_footprint": "warning",
    "footprint": "error", "footprint_filters_mismatch": "ignore", "footprint_symbol_field_mismatch": "warning",
    "footprint_symbol_mismatch": "warning", "footprint_type_mismatch": "ignore", "hole_clearance": "error",
    "hole_to_hole": "warning", "holes_co_located": "warning", "invalid_outline": "error",
    "isolated_copper": "warning", "item_on_disabled_layer": "error", "items_not_allowed": "error",
    "length_out_of_range": "error", "lib_footprint_issues": "warning", "lib_footprint_mismatch": "warning",
    "malformed_courtyard": "error", "microvia_drill_out_of_range": "error",
    "mirrored_text_on_front_layer": "warning", "missing_courtyard": "ignore", "missing_footprint": "warning",
    "missing_tuning_profile": "warning", "net_conflict": "warning", "nonmirrored_text_on_back_layer": "warning",
    "npth_inside_courtyard": "error", "padstack": "warning", "pth_inside_courtyard": "error",
    "shorting_items": "error", "silk_edge_clearance": "warning", "silk_over_copper": "warning",
    "silk_overlap": "warning", "skew_out_of_range": "error", "solder_mask_bridge": "error",
    "starved_thermal": "error", "text_height": "warning", "text_on_edge_cuts": "error",
    "text_thickness": "warning", "through_hole_pad_without_hole": "error", "too_many_vias": "error",
    "track_angle": "error", "track_dangling": "warning", "track_not_centered_on_via": "ignore",
    "track_on_post_machined_layer": "error", "track_segment_length": "error", "track_width": "error",
    "tracks_crossing": "error", "tuning_profile_track_geometries": "ignore", "unconnected_items": "error",
    "unresolved_variable": "error", "via_dangling": "warning", "zones_intersect": "error",
}

CRITICAS_DRC = {r: "error" for r in (
    "unconnected_items", "clearance", "copper_edge_clearance", "shorting_items", "tracks_crossing",
    "hole_clearance", "annular_width", "drill_out_of_range", "track_width", "via_diameter", "creepage",
    "invalid_outline", "items_not_allowed")}
CRITICAS_DRC.update({r: "warning" for r in (
    "missing_footprint", "extra_footprint", "net_conflict", "footprint_symbol_mismatch",
    "duplicate_footprints", "footprint_symbol_field_mismatch")})

CRITICAS_ERC = ("pin_not_connected", "power_pin_not_driven", "pin_to_pin", "conflicting_netclasses",
                "different_unit_net", "label_dangling", "multiple_net_names", "net_not_bus_member",
                "pin_not_driven", "wire_dangling", "duplicate_reference", "unannotated")
IGNORADAS_ERC_PADRAO = {"footprint_filter", "four_way_junction", "single_global_label"}


@dataclass
class Auditoria:
    criticas_rebaixadas: list = field(default_factory=list)    # bloqueiam: "DRC clearance: warning (precisa error)"
    rebaixadas: list = field(default_factory=list)             # nao bloqueiam, vao para detalhes e manifesto
    exclusoes_drc: list = field(default_factory=list)          # [{"violacao", "comentario"}]
    exclusoes_erc: list = field(default_factory=list)

    def como_dict(self):
        return {"criticas_rebaixadas": self.criticas_rebaixadas, "rebaixadas": self.rebaixadas,
                "exclusoes_drc": self.exclusoes_drc, "exclusoes_erc": self.exclusoes_erc}


def _rank(severidade):
    return ORDEM.get(str(severidade).lower(), -1)     # valor desconhecido conta como abaixo de ignore


def _drc(severidades, aud):
    for regra, sev in sorted(severidades.items()):
        minimo = CRITICAS_DRC.get(regra)
        if minimo and _rank(sev) < _rank(minimo):
            aud.criticas_rebaixadas.append(f"DRC {regra}: '{sev}' (precisa '{minimo}')")
        elif regra in PADRAO_DRC and _rank(sev) < _rank(PADRAO_DRC[regra]):
            aud.rebaixadas.append(f"DRC {regra}: '{sev}' (padrao '{PADRAO_DRC[regra]}')")


def _erc(severidades, aud):
    for regra, sev in sorted(severidades.items()):
        if _rank(sev) > _rank("ignore"):
            continue
        if regra in CRITICAS_ERC:
            aud.criticas_rebaixadas.append(f"ERC {regra}: '{sev}' (nao pode ser ignorada)")
        elif regra not in IGNORADAS_ERC_PADRAO:
            aud.rebaixadas.append(f"ERC {regra}: '{sev}'")


def _exclusoes(lista):
    saida = []
    for item in lista or []:
        chave, comentario = (item[0], item[1] if len(item) > 1 else "") if isinstance(item, list) else (item, "")
        saida.append({"violacao": str(chave), "comentario": str(comentario or "")})
    return saida


def auditar(dados_pro):
    """Le severidades e exclusoes do dict do `.kicad_pro` (vazio ou None = tudo no padrao)."""
    dados_pro = dados_pro or {}
    ds = (dados_pro.get("board") or {}).get("design_settings") or {}
    erc = dados_pro.get("erc") or {}
    aud = Auditoria()
    _drc(ds.get("rule_severities") or {}, aud)
    _erc(erc.get("rule_severities") or {}, aud)
    aud.exclusoes_drc = _exclusoes(ds.get("drc_exclusions"))
    aud.exclusoes_erc = _exclusoes(erc.get("erc_exclusions"))
    return aud
