"""Generación del informe de cuantificación (HTML de una página).

`build_report_html(data, t)` devuelve un HTML compatible con QTextDocument
(subconjunto de rich-text de Qt: tablas con atributos, estilos en línea básicos),
pensado para una sola página A4. `t` es la función de traducción (I18n.t).
"""

NAVY = "#0B2545"
BLUE = "#1B5299"
ACCENT = "#2E8BC0"
MUTED = "#5A7184"
BORDER = "#C9D8EA"
HEADBG = "#13315C"
ZEBRA = "#F0F6FC"


def _f(x, n=2):
    try:
        return f"{float(x):.{n}f}"
    except (TypeError, ValueError):
        return "-"


def _meta_row(label, value):
    if value is None or str(value).strip() == "":
        return ""
    return (f'<tr>'
            f'<td style="color:{MUTED};" width="22%"><b>{label}</b></td>'
            f'<td>{value}</td></tr>')


def build_report_html(d, t, logo_src="logo"):
    def esc(s):
        return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    # ---- Cabecera ----
    header = f"""
    <table width="100%" cellspacing="0" cellpadding="0">
      <tr>
        <td width="64" valign="middle"><img src="{logo_src}" width="56" height="56"></td>
        <td valign="middle">
          <span style="font-size:20pt; font-weight:bold; color:{NAVY};">{esc(t('report_title'))}</span><br>
          <span style="font-size:8pt; color:{MUTED};">{esc(t('report_generated').format(date=esc(d.get('date','')), ver=esc(d.get('version',''))))}</span>
        </td>
      </tr>
    </table>
    <hr>
    """

    # ---- Metadatos (solo lo que tenga valor) ----
    meta = "".join([
        _meta_row(t("report_sample_code"), esc(d.get("sample_code", ""))),
        _meta_row(t("report_analyte"), esc(d.get("analyte", ""))),
        _meta_row(t("report_analyst"), esc(d.get("analyst", ""))),
        _meta_row(t("report_solvent"), esc(d.get("solvent", ""))),
        _meta_row(t("report_date_field"), esc(d.get("report_date", ""))),
    ])
    meta_block = f'<table width="100%" cellspacing="0" cellpadding="3">{meta}</table>' if meta else ""

    # ---- Método ----
    method = f"""
    <p style="font-size:12pt; font-weight:bold; color:{BLUE}; margin-bottom:2px;">{esc(t('report_method'))}</p>
    <p style="font-size:9pt; margin-top:0;">
      {esc(t('report_is'))}: <b>{esc(d.get('is_label',''))}</b>
      &nbsp;|&nbsp; {esc(t('report_purity'))}: {_f(d.get('is_purity'), 4)}
      &nbsp;|&nbsp; {esc(t('report_target_signal'))}: MW {_f(d.get('target_mw'))} g/mol, {d.get('target_n','')} H
    </p>
    <p style="font-size:9pt; color:{MUTED}; margin-top:0;">
      P (% w/w) = (I<sub>x</sub>/I<sub>IS</sub>) &middot; (N<sub>IS</sub>/N<sub>x</sub>) &middot;
      (M<sub>x</sub>/M<sub>IS</sub>) &middot; (m<sub>IS</sub>/m<sub>x</sub>) &middot; P<sub>IS</sub> &middot; 100
    </p>
    """

    # ---- Tabla de réplicas ----
    head_cells = [t("report_rep"), t("col_is_weight"), t("col_sample_weight"),
                  t("col_target_integral"), t("col_is_integral"), t("lbl_conc_pp")]
    head = "".join(f'<th bgcolor="{HEADBG}" style="color:white;">{esc(h)}</th>' for h in head_cells)
    body = ""
    for i, r in enumerate(d.get("replicates", []), 1):
        bg = ZEBRA if i % 2 == 0 else "#FFFFFF"
        body += (f'<tr bgcolor="{bg}">'
                 f'<td align="center">{i}</td>'
                 f'<td align="center">{_f(r.get("is_w"))}</td>'
                 f'<td align="center">{_f(r.get("sample_w"))}</td>'
                 f'<td align="center">{_f(r.get("integral"), 3)}</td>'
                 f'<td align="center">{_f(r.get("is_integral"), 3)}</td>'
                 f'<td align="center"><b>{_f(r.get("result"))} %</b></td>'
                 f'</tr>')
    table = f"""
    <p style="font-size:12pt; font-weight:bold; color:{BLUE}; margin-bottom:2px;">{esc(t('report_results'))}</p>
    <table width="100%" border="1" cellspacing="0" cellpadding="5"
           style="border-color:{BORDER}; font-size:9pt;">
      <tr>{head}</tr>
      {body}
    </table>
    """

    # ---- Resumen ----
    summary_cells = [(t("lbl_mean"), f'{_f(d.get("mean"))} %')]
    if d.get("sd") is not None:
        summary_cells.append((t("lbl_sd"), _f(d.get("sd"))))
    if d.get("rsd") is not None:
        summary_cells.append((t("lbl_rsd"), f'{_f(d.get("rsd"))} %'))
    if d.get("pv") is not None:
        summary_cells.append((t("lbl_mean_pv"), f'{_f(d.get("pv"))} %'))
    if d.get("gl") is not None:
        summary_cells.append((t("lbl_conc_gl"), f'{_f(d.get("gl"))} g/L'))
    cells = "".join(
        f'<td align="center" bgcolor="{ZEBRA}" style="border-color:{BORDER};">'
        f'<span style="color:{MUTED}; font-size:8pt;">{esc(lab)}</span><br>'
        f'<span style="color:{NAVY}; font-size:14pt; font-weight:bold;">{val}</span></td>'
        for lab, val in summary_cells)
    summary = f"""
    <table width="100%" border="1" cellspacing="0" cellpadding="6"
           style="border-color:{BORDER}; margin-top:6px;">
      <tr>{cells}</tr>
    </table>
    """

    # ---- Preparación y notas (opcionales) ----
    extras = ""
    if str(d.get("prep_details", "")).strip():
        extras += (f'<p style="font-size:12pt; font-weight:bold; color:{BLUE}; margin-bottom:2px;">'
                   f'{esc(t("report_preparation"))}</p>'
                   f'<p style="font-size:9pt; white-space:pre-wrap;">{esc(d["prep_details"])}</p>')
    if str(d.get("notes", "")).strip():
        extras += (f'<p style="font-size:12pt; font-weight:bold; color:{BLUE}; margin-bottom:2px;">'
                   f'{esc(t("report_notes"))}</p>'
                   f'<p style="font-size:9pt; white-space:pre-wrap;">{esc(d["notes"])}</p>')

    # ---- Pie / firma ----
    footer = f"""
    <br><table width="100%" cellspacing="0" cellpadding="0"><tr>
      <td style="color:{MUTED}; font-size:8pt;">{esc(t('report_footer'))}</td>
      <td align="right" style="color:{MUTED}; font-size:8pt;">{esc(t('report_signature'))}: __________________</td>
    </tr></table>
    """

    return f"""<html><body style="font-family:'Segoe UI', Arial, sans-serif; color:#0B2545;">
    {header}{meta_block}{method}{table}{summary}{extras}{footer}
    </body></html>"""
