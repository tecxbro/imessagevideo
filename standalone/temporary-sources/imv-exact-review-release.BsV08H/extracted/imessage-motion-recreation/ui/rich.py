"""Render generic rich-message cards as editable scene geometry."""

from .components import INK, LAVENDER, LINE, MUTED, PLUM, group, rect, text


KIND_LABELS = {
    "app": "App",
    "link": "Link",
    "location": "Location",
    "audio": "Audio",
    "file": "File",
    "poll": "Poll",
    "payment-mock": "Payment · Test mock",
}
PAYMENT_MOCK_STATES = {"requested": "Awaiting payment", "paid": "Paid · Simulated"}
CARD = "#fffaf4"
PAD = 12


def build_card(id, payload, width, measure):
    """Return local height and layers for a validated rich-message payload.

    Every kind has a title and may show detail and an action label. A poll adds
    its authored options and counts. The selected option has a filled marker.
    The labels describe a card's content. Navigation, playback and voting
    require separate authored events.
    """
    kind = payload["kind"]
    inner_width = width - 2 * PAD
    layers = [
        rect(id + "/accent", PAD, 15, 3, 9, PLUM, 1.5),
        text(id + "/kind", KIND_LABELS[kind], PAD + 9, 12, 11, fill=PLUM, fontWeight=700),
    ]
    y = 32
    title = measure.wrap(payload["title"], inner_width, 16, 700)
    layers.append(text(id + "/title", "\n".join(title), PAD, y, 16, lineHeight=21, fontWeight=700))
    y += len(title) * 21
    if payload.get("detail"):
        detail = measure.wrap(payload["detail"], inner_width, 12)
        layers.append(text(id + "/detail", "\n".join(detail), PAD, y + 4, 12, lineHeight=16, fill=MUTED))
        y += 4 + len(detail) * 16
    if kind == "payment-mock":
        layers.append(text(id + "/status", PAYMENT_MOCK_STATES[payload["status"]],
                           PAD, y + 8, 12, fill=PLUM, fontWeight=700))
        y += 25
    if kind == "poll":
        options = payload.get("options", [])
        count_width = max((measure.width(str(option["votes"]), 12, 700) for option in options), default=0)
        selected = payload.get("selected")
        for option in options:
            key = id + "/option/" + option["id"]
            active = option["id"] == selected
            label = measure.wrap(option["label"], inner_width - count_width - 44, 12)
            row_height = max(32, len(label) * 16 + 14)
            middle = y + 7 + row_height / 2
            layers.extend([
                rect(key + "/surface", PAD, y + 7, inner_width, row_height,
                     LAVENDER if active else CARD, 7, stroke=PLUM if active else LINE, strokeWidth=1),
                rect(key + "/marker", PAD + 9, middle - 4, 8, 8,
                     PLUM if active else CARD, 2, stroke=PLUM, strokeWidth=1),
                text(key + "/label", "\n".join(label), PAD + 24,
                     middle - len(label) * 8, 12, lineHeight=16, fill=INK),
                text(key + "/count", str(option["votes"]), width - PAD - 9,
                     middle - 8, 12, textAnchor="end", fill=PLUM if active else MUTED, fontWeight=700),
            ])
            y += 7 + row_height
    if payload.get("action"):
        action = measure.wrap(payload["action"], inner_width, 12, 700)
        layers.extend([
            rect(id + "/action-divider", PAD, y + 9, inner_width, 1, LINE),
            text(id + "/action", "\n".join(action), PAD, y + 16, 12,
                 lineHeight=16, fill=PLUM, fontWeight=700),
        ])
        y += 16 + len(action) * 16
    height = y + PAD
    return height, [rect(id + "/surface", 0, 0, width, height, CARD, 12, stroke=LINE, strokeWidth=1), *layers]


def payment_approval(width, height, payload, measure):
    """The mock approval occupies its own screen-space surface."""
    prefix = "ui.overlay.payment"
    inset = 16
    panel_width = min(360, width - 2 * inset)
    content_width = panel_width - 2 * inset
    title = measure.ellipsis(payload["title"], content_width, 17, 700)
    detail = measure.ellipsis(payload.get("detail", ""), content_width, 13)
    panel_height = 180
    return [
        rect(prefix + ".shade", 0, 0, width, height, INK, opacity=.28),
        group(prefix + ".sheet", (width - panel_width) / 2, height - panel_height - 22, [
            rect(prefix + ".panel", 0, 0, panel_width, panel_height, CARD, 16, stroke=LINE, strokeWidth=1),
            text(prefix + ".mode", "TEST MOCK · NO CHARGE", inset, 14, 11, fill=PLUM, fontWeight=700),
            text(prefix + ".title", "Review test payment", inset, 37, 17, fontWeight=700),
            text(prefix + ".item", title, inset, 69, 17, fontWeight=700),
            text(prefix + ".detail", detail, inset, 94, 13, fill=MUTED),
            rect(prefix + ".button", inset, 125, content_width, 36, PLUM, 9),
            text(prefix + ".button-label", "Simulated approval", panel_width / 2, 135, 12,
                 fill=CARD, fontWeight=700, textAnchor="middle"),
        ]),
    ]
