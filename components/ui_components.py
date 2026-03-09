"""
ui_components.py - NDC Genie UI Rendering Functions

Provides reusable HTML/CSS rendering utilities for the Streamlit Transaction tab,
including NDC flow ID chains (shopping offer IDs, priced offer ID, seat/service IDs,
order ID) that show which IDs were used and returned at each NDC short-sell stage.
"""

# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------

STATUS_COLORS = {
    "Completed":   ("#d1fae5", "#065f46", "#059669"),
    "Failed":      ("#fee2e2", "#991b1b", "#dc2626"),
    "In Progress": ("#dbeafe", "#1e40af", "#2563eb"),
    "Refunded":    ("#ede9fe", "#4c1d95", "#7c3aed"),
    "Cancelled":   ("#f3f4f6", "#374151", "#6b7280"),
}

PRIORITY_COLORS = {
    "Critical": ("#fee2e2", "#991b1b", "#dc2626"),
    "High":     ("#fef3c7", "#92400e", "#d97706"),
    "Medium":   ("#dbeafe", "#1e40af", "#2563eb"),
    "Low":      ("#f0fdf4", "#166534", "#16a34a"),
}

NDC_STAGE_COLORS = {
    "completed":   ("#d1fae5", "#065f46"),
    "failed":      ("#fee2e2", "#991b1b"),
    "in_progress": ("#dbeafe", "#1e40af"),
    "not_reached": ("#f3f4f6", "#9ca3af"),
}


def get_status_badge(status: str) -> str:
    bg, text, border = STATUS_COLORS.get(status, ("#f3f4f6", "#374151", "#6b7280"))
    return (
        f'<span style="background:{bg};color:{text};border:1px solid {border};'
        f'padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;">'
        f'{status}</span>'
    )


def get_priority_badge(priority: str) -> str:
    bg, text, border = PRIORITY_COLORS.get(priority, ("#f3f4f6", "#374151", "#6b7280"))
    return (
        f'<span style="background:{bg};color:{text};border:1px solid {border};'
        f'padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;">'
        f'{priority}</span>'
    )


def get_ndc_stage_badge(status: str) -> str:
    bg, text = NDC_STAGE_COLORS.get(status, ("#f3f4f6", "#9ca3af"))
    label = status.replace("_", " ").title()
    return (
        f'<span style="background:{bg};color:{text};'
        f'padding:2px 8px;border-radius:8px;font-size:11px;font-weight:600;">'
        f'{label}</span>'
    )


# ---------------------------------------------------------------------------
# Metric Card
# ---------------------------------------------------------------------------

def render_metric_card(title: str, value: str, delta: str = "", color: str = "#2563eb") -> str:
    delta_html = ""
    if delta:
        delta_color = "#16a34a" if delta.startswith("+") else "#dc2626"
        delta_html = f'<p style="margin:0;font-size:13px;color:{delta_color};">{delta}</p>'
    return f"""
    <div style="background:white;border-radius:12px;padding:20px;
                box-shadow:0 1px 3px rgba(0,0,0,0.1);border-left:4px solid {color};">
        <p style="margin:0;font-size:13px;color:#6b7280;font-weight:500;">{title}</p>
        <p style="margin:4px 0 0;font-size:28px;font-weight:700;color:#111827;">{value}</p>
        {delta_html}
    </div>
    """


# ---------------------------------------------------------------------------
# NDC Flow Lifecycle Visual (Transaction Tab - main visual)
# ---------------------------------------------------------------------------

NDC_STAGE_LABELS = {
    "shopping":             "🔍 Shopping",
    "offer_price":          "💰 OfferPrice",
    "seat_availability":    "💺 Seat Avail",
    "service_availability": "🧳 Service Avail",
    "order_create":         "📋 OrderCreate",
}

NDC_STAGE_ORDER = [
    "shopping",
    "offer_price",
    "seat_availability",
    "service_availability",
    "order_create",
]


def render_lifecycle_visual(lifecycle: dict) -> str:
    """Render the NDC flow pipeline as a horizontal step indicator."""
    parts = []
    for i, key in enumerate(NDC_STAGE_ORDER):
        stage = lifecycle.get(key, {})
        st = stage.get("status", "not_reached")
        label = NDC_STAGE_LABELS[key]
        bg, text = NDC_STAGE_COLORS.get(st, ("#f3f4f6", "#9ca3af"))

        icon_map = {
            "completed": "✓",
            "failed": "✗",
            "in_progress": "⟳",
            "not_reached": "–",
        }
        icon = icon_map.get(st, "–")

        parts.append(
            f'<div style="flex:1;text-align:center;padding:8px 4px;">'
            f'  <div style="width:32px;height:32px;border-radius:50%;background:{bg};'
            f'              color:{text};font-weight:700;font-size:14px;'
            f'              display:inline-flex;align-items:center;justify-content:center;'
            f'              margin-bottom:4px;">{icon}</div>'
            f'  <div style="font-size:11px;color:#374151;font-weight:500;">{label}</div>'
            f'  <div style="font-size:10px;color:{text};">{st.replace("_"," ").title()}</div>'
            f'</div>'
        )
        if i < len(NDC_STAGE_ORDER) - 1:
            arrow_color = "#d1d5db" if st in ("not_reached",) else "#6b7280"
            parts.append(
                f'<div style="display:flex;align-items:center;padding-bottom:18px;">'
                f'  <div style="width:20px;height:2px;background:{arrow_color};"></div>'
                f'  <div style="color:{arrow_color};font-size:10px;">▶</div>'
                f'</div>'
            )

    return (
        '<div style="display:flex;align-items:flex-start;flex-wrap:nowrap;'
        'overflow-x:auto;padding:8px 0;">'
        + "".join(parts)
        + "</div>"
    )


# ---------------------------------------------------------------------------
# NDC ID Chain Panel (new — shown in Transaction detail)
# ---------------------------------------------------------------------------

def _id_chip(id_val: str, color: str = "#2563eb") -> str:
    """Render a single ID as a monospace chip."""
    return (
        f'<code style="background:#f0f4ff;color:{color};border:1px solid #c7d7fe;'
        f'border-radius:6px;padding:2px 8px;font-size:11px;margin:2px;'
        f'display:inline-block;word-break:break-all;">{id_val}</code>'
    )


def _id_list_chips(ids: list, color: str = "#2563eb", max_show: int = 5) -> str:
    """Render a list of IDs as chips, collapsing long lists."""
    if not ids:
        return '<span style="color:#9ca3af;font-size:12px;">—</span>'
    shown = ids[:max_show]
    chips = " ".join(_id_chip(i, color) for i in shown)
    if len(ids) > max_show:
        chips += (
            f'<span style="color:#6b7280;font-size:11px;margin-left:4px;">'
            f'+{len(ids) - max_show} more</span>'
        )
    return chips


def render_ndc_id_chain(ndc_flow: dict, lifecycle: dict) -> str:
    """
    Render the full NDC ID chain for a transaction in a structured card.
    Shows IDs at each stage — only for stages that were reached.
    Clearly shows which ID is passed into each stage vs returned from it.
    """
    deepest = ndc_flow.get("deepest_stage", "Shopping")
    stage_index = ndc_flow.get("stage_index", 0)

    rows = []

    # ---- Shopping ----
    shopping_lc = lifecycle.get("shopping", {})
    shopping_status = shopping_lc.get("status", "not_reached")
    shopping_offers = ndc_flow.get("shopping_offer_ids", [])
    count = ndc_flow.get("shopping_offer_count", len(shopping_offers))

    rows.append(_ndc_row(
        stage_icon="🔍",
        stage_name="Shopping",
        status=shopping_status,
        input_label=None,
        input_value=None,
        output_label=f"Offers Returned ({count})",
        output_value=_id_list_chips(shopping_offers, "#2563eb"),
        note=f"Device: {shopping_lc.get('device','—')}",
    ))

    # ---- OfferPrice ----
    if stage_index >= 1:
        ofp_lc = lifecycle.get("offer_price", {})
        ofp_status = ofp_lc.get("status", "not_reached")
        selected_id = ndc_flow.get("selected_shopping_offer_id", "")
        priced_id = ndc_flow.get("priced_offer_id", "")
        rows.append(_ndc_row(
            stage_icon="💰",
            stage_name="OfferPrice",
            status=ofp_status,
            input_label="Shopping Offer ID (input)",
            input_value=_id_chip(selected_id, "#7c3aed") if selected_id else None,
            output_label="Priced Offer ID (output)",
            output_value=_id_chip(priced_id, "#059669") if priced_id else None,
        ))
    else:
        rows.append(_ndc_row_not_reached("💰", "OfferPrice"))

    # ---- SeatAvailability ----
    if stage_index >= 2:
        seat_lc = lifecycle.get("seat_availability", {})
        seat_status = seat_lc.get("status", "not_reached")
        seat_ids = ndc_flow.get("seat_offer_ids", [])
        rows.append(_ndc_row(
            stage_icon="💺",
            stage_name="SeatAvailability",
            status=seat_status,
            input_label="Transaction ID (input)",
            input_value=None,  # txn_id shown in header
            output_label=f"Seat Offer IDs ({len(seat_ids)})",
            output_value=_id_list_chips(seat_ids, "#d97706"),
        ))
    else:
        rows.append(_ndc_row_not_reached("💺", "SeatAvailability"))

    # ---- ServiceAvailability ----
    if stage_index >= 3:
        svc_lc = lifecycle.get("service_availability", {})
        svc_status = svc_lc.get("status", "not_reached")
        svc_ids = ndc_flow.get("service_offer_ids", [])
        rows.append(_ndc_row(
            stage_icon="🧳",
            stage_name="ServiceAvailability",
            status=svc_status,
            input_label="Transaction ID (input)",
            input_value=None,
            output_label=f"Service Offer IDs ({len(svc_ids)})",
            output_value=_id_list_chips(svc_ids, "#0891b2"),
        ))
    else:
        rows.append(_ndc_row_not_reached("🧳", "ServiceAvailability"))

    # ---- OrderCreate ----
    if stage_index >= 4:
        ord_lc = lifecycle.get("order_create", {})
        ord_status = ord_lc.get("status", "not_reached")
        priced_id = ndc_flow.get("priced_offer_id", "")
        seat_ids = ndc_flow.get("seat_offer_ids", [])
        svc_ids = ndc_flow.get("service_offer_ids", [])
        order_id = ndc_flow.get("order_id", "")

        input_html = ""
        if priced_id:
            input_html += f'<div style="margin-bottom:2px;"><span style="font-size:11px;color:#6b7280;">Priced Offer: </span>{_id_chip(priced_id, "#059669")}</div>'
        if seat_ids:
            input_html += f'<div style="margin-bottom:2px;"><span style="font-size:11px;color:#6b7280;">Seat Offers: </span>{_id_list_chips(seat_ids, "#d97706")}</div>'
        if svc_ids:
            input_html += f'<div><span style="font-size:11px;color:#6b7280;">Service Offers: </span>{_id_list_chips(svc_ids, "#0891b2")}</div>'

        rows.append(_ndc_row(
            stage_icon="📋",
            stage_name="OrderCreate",
            status=ord_status,
            input_label="Inputs (IDs from previous stages)",
            input_value=input_html if input_html else None,
            output_label="Order ID (output)",
            output_value=_id_chip(order_id, "#dc2626") if order_id else None,
            note=f"PNR: {ord_lc.get('pnr','—')}  |  E-Ticket: {ord_lc.get('e_ticket','—')}" if ord_status == "completed" else "",
        ))
    else:
        rows.append(_ndc_row_not_reached("📋", "OrderCreate"))

    body = "\n".join(rows)
    return f"""
    <div style="background:white;border-radius:12px;
                border:1px solid #e5e7eb;overflow:hidden;margin-top:12px;">
        <div style="background:#1e3a5f;color:white;padding:12px 16px;font-weight:600;font-size:14px;">
            🔗 NDC Short-Sell ID Chain
        </div>
        <div style="padding:0;">
            {body}
        </div>
    </div>
    """


def _ndc_row(
    stage_icon: str,
    stage_name: str,
    status: str,
    input_label,
    input_value,
    output_label,
    output_value,
    note: str = "",
) -> str:
    bg, text = NDC_STAGE_COLORS.get(status, ("#f3f4f6", "#9ca3af"))
    status_badge = get_ndc_stage_badge(status)

    input_block = ""
    if input_label and input_value:
        input_block = f"""
        <div style="margin-bottom:6px;">
            <div style="font-size:11px;color:#9ca3af;font-weight:500;margin-bottom:2px;">
                ↳ {input_label}
            </div>
            <div>{input_value}</div>
        </div>
        """

    output_block = ""
    if output_label and output_value:
        output_block = f"""
        <div>
            <div style="font-size:11px;color:#9ca3af;font-weight:500;margin-bottom:2px;">
                ↪ {output_label}
            </div>
            <div>{output_value}</div>
        </div>
        """

    note_block = ""
    if note:
        note_block = f'<div style="font-size:11px;color:#9ca3af;margin-top:6px;">{note}</div>'

    return f"""
    <div style="display:flex;border-bottom:1px solid #f3f4f6;padding:12px 16px;
                align-items:flex-start;gap:12px;">
        <div style="width:36px;height:36px;border-radius:8px;background:{bg};
                    display:flex;align-items:center;justify-content:center;
                    font-size:16px;flex-shrink:0;">{stage_icon}</div>
        <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <span style="font-weight:600;font-size:13px;color:#111827;">{stage_name}</span>
                {status_badge}
            </div>
            {input_block}
            {output_block}
            {note_block}
        </div>
    </div>
    """


def _ndc_row_not_reached(icon: str, stage_name: str) -> str:
    return f"""
    <div style="display:flex;border-bottom:1px solid #f3f4f6;padding:12px 16px;
                align-items:center;gap:12px;opacity:0.45;">
        <div style="width:36px;height:36px;border-radius:8px;background:#f3f4f6;
                    display:flex;align-items:center;justify-content:center;
                    font-size:16px;">{icon}</div>
        <div>
            <span style="font-weight:600;font-size:13px;color:#9ca3af;">{stage_name}</span>
            <span style="font-size:11px;color:#d1d5db;margin-left:8px;">— not reached</span>
        </div>
    </div>
    """


# ---------------------------------------------------------------------------
# Transaction Summary Row (used in the browser table)
# ---------------------------------------------------------------------------

def render_transaction_summary_row(txn: dict) -> str:
    """
    Compact row for the transaction list showing key IDs inline.
    """
    ndc = txn.get("ndc_flow", {})
    deepest = ndc.get("deepest_stage", "Shopping")
    order_id = ndc.get("order_id", "")
    priced_id = ndc.get("priced_offer_id", "")
    shopping_count = ndc.get("shopping_offer_count", 0)

    id_summary = f'<span style="color:#6b7280;font-size:11px;">Shopping: {shopping_count} offers</span>'
    if priced_id:
        id_summary += f' → {_id_chip(priced_id, "#059669")}'
    if order_id:
        id_summary += f' → {_id_chip(order_id, "#dc2626")}'

    return f"""
    <div style="font-size:12px;color:#6b7280;margin-top:2px;">
        <strong>Flow:</strong> {deepest} &nbsp;|&nbsp; {id_summary}
    </div>
    """