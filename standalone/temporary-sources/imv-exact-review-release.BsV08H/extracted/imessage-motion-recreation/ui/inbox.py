"""Editable inbox and search surfaces for the film skin."""

from unicodedata import normalize

from .components import GUTTER, HEADER, INK, LAVENDER, LINE, MUTED, PAPER, PLUM, TextLayout, group, rect, text

INBOX_HEADER_HEIGHT = HEADER
INBOX_CONTROL_HEIGHT = 68
ROW_HEIGHT = 58
ROW_GAP = 7


def _rows(width, entries, surface):
    measure = TextLayout()
    row_width = width - GUTTER * 2
    copy_width = row_width - 54
    rows = []
    for index, entry in enumerate(entries):
        row_id = f"ui.{surface}/row/{entry['id']}"
        title = measure.ellipsis(entry["title"], copy_width, 16, 700)
        preview = measure.ellipsis(entry["preview"], copy_width, 12)
        rows.append(group(row_id, GUTTER, ROW_GAP + index * (ROW_HEIGHT + ROW_GAP), [
            rect(f"{row_id}/surface", 0, 0, row_width, ROW_HEIGHT, "#fffaf4", 11,
                 stroke=LINE, strokeWidth=1),
            rect(f"{row_id}/accent", 10, 19, 3, 20, PLUM, 1),
            text(f"{row_id}/title", title, 21, 9, 16, fontWeight=700),
            text(f"{row_id}/preview", preview, 21, 33, 12, fill=MUTED),
            text(f"{row_id}/open", "›", row_width - 17, 15, 22,
                 textAnchor="middle", fill=PLUM),
        ]))
    return rows


def inbox_rows(width, height, entries):
    """Return rows in body-local coordinates, including those below its clip.

    The body group owns clipping and scrolling. Each entry supplies ``id``,
    ``title`` and ``preview``. IDs stay attached to entries during reordering.
    """
    if width < 160 or height < 1:
        raise ValueError("inbox needs a body at least 160 units wide")
    return _rows(width, entries, "inbox")


def _index(value):
    return " ".join(normalize("NFKC", value).casefold().split())


def search_rows(width, height, entries, query):
    """Return preview/title matches within the caller's clipped search body.

    A blank focused field has no results. Matching is case-insensitive and
    accent-preserving. Authored entries determine result order.
    """
    if width < 160 or height < 1:
        raise ValueError("search needs a body at least 160 units wide")
    term = _index(query)
    if not term:
        return []
    results = [entry for entry in entries
               if term in _index(entry["title"]) or term in _index(entry["preview"])]
    if results:
        return _rows(width, results, "search")
    return [text("ui.search/empty", "No matches", width / 2, 16, 14,
                 fill=MUTED, textAnchor="middle")]


def inbox_chrome(width, height, query=None, title="Messages"):
    """Return the fixed header and bottom controls in full-viewport coordinates.

    ``None`` shows the inactive search controls. Any string represents focused
    search. The field and trailing action stay in the same place across modes.
    """
    if width < 160 or height <= INBOX_HEADER_HEIGHT + INBOX_CONTROL_HEIGHT:
        raise ValueError("inbox chrome needs space for both controls and the body")
    measure = TextLayout()
    active = query is not None
    field_width = width - GUTTER * 2 - 46
    message = measure.ellipsis(query or "Search messages", field_width - 42, 13)
    heading = "ui.inbox-header"
    controls = "ui.inbox-controls"
    return [
        group(heading, 0, 0, [
            rect(f"{heading}/paper", 0, 0, width, INBOX_HEADER_HEIGHT, PAPER),
            text(f"{heading}/title", measure.ellipsis(title, width - GUTTER * 2, 25, 700),
                 GUTTER, 19, 25, fontWeight=700),
            rect(f"{heading}/rule", GUTTER, INBOX_HEADER_HEIGHT - 1,
                 width - GUTTER * 2, 1, LINE),
        ]),
        group(controls, 0, height - INBOX_CONTROL_HEIGHT, [
            rect(f"{controls}/paper", 0, 0, width, INBOX_CONTROL_HEIGHT, PAPER),
            rect(f"{controls}/rule", GUTTER, 0, width - GUTTER * 2, 1, LINE),
            rect(f"{controls}/field", GUTTER, 9, field_width, 40, "#fffaf4", 10,
                 stroke=PLUM if active else LINE, strokeWidth=1),
            {"id": f"{controls}/magnifier", "type": "path", "x": GUTTER + 13, "y": 22,
             "d": "M 5 0 A 5 5 0 1 1 5 10 A 5 5 0 1 1 5 0 M 9 9 L 13 13",
             "fill": "none", "stroke": MUTED, "strokeWidth": 1.5},
            text(f"{controls}/query", message, GUTTER + 32, 20, 13,
                 fill=INK if query else MUTED),
            rect(f"{controls}/action", width - GUTTER - 38, 9, 38, 40,
                 LAVENDER if active else PLUM, 10),
            text(f"{controls}/action-mark", "×" if active else "+", width - GUTTER - 19,
                 15, 22, textAnchor="middle", fill=PLUM if active else PAPER),
        ]),
    ]
