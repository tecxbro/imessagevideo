"""Editable, local-coordinate surfaces for the conversation film skin."""

from base64 import b64decode
from io import BytesIO
from pathlib import Path

from PIL import Image

from .components import INK, LAVENDER, PAPER, PLUM, TextLayout, clusters, group, rect, text

KEYBOARD_HEIGHT = 208
DIVIDER = "#d0c0d0"


def _letters(value):
    return [(char.lower(), char, 1) for char in value]


KEY_ROWS = (
    _letters("QWERTYUIOP"),
    _letters("ASDFGHJKL"),
    [("shift", "⇧", 1.35), *_letters("ZXCVBNM"), ("delete", "⌫", 1.35)],
    [("numbers", "123", 1.45), ("comma", ",", .8), ("space", "space", 4.2),
     ("period", ".", .8), ("return", "↵", 1.45)],
)


def keyboard(width):
    """Return a QWERTY accessory in the keyboard parent's 208-unit space.

    Key groups carry semantic IDs such as ``ui.keyboard.key.delete``. The
    parent controls keyboard motion. A shot can animate a key independently.
    """
    if width < 200:
        raise ValueError("keyboard needs at least 200 units of width")
    prefix = "ui.keyboard"
    layers = [rect(f"{prefix}.panel", 0, 0, width, KEYBOARD_HEIGHT, LAVENDER),
              rect(f"{prefix}.divider", 0, 0, width, 1, DIVIDER)]
    gap = min(6, width / 65)
    gutter = width * .03
    unit = (width - 2 * gutter - 9 * gap) / 10
    for row_index, row in enumerate(KEY_ROWS):
        widths = [unit * weight for _, _, weight in row]
        row_width = sum(widths) + (len(widths) - 1) * gap
        x = (width - row_width) / 2
        y = 18 + row_index * 45
        for (key, label, weight), key_width in zip(row, widths):
            key_id = f"{prefix}.key.{key}"
            action = key in {"shift", "delete", "return", "numbers"}
            body = rect(f"{key_id}.body", 0, 0, key_width, 38,
                        PLUM if action else PAPER, 8)
            size = min(16 if len(label) == 1 else 11, key_width * .68)
            mark = text(f"{key_id}.label", label, key_width / 2, (38 - size) / 2 - 1,
                        size, textAnchor="middle", fontWeight=700,
                        fill=PAPER if action else INK)
            layers.append(group(key_id, x, y, [body, mark]))
            x += key_width + gap
    return layers


def _label(layout, layer_id, value, x, y, width, size, *, lines=1, color=INK, weight=400):
    # The full source label remains editable in the conversation description.
    wrapped = layout.wrap(" ".join(value.split()), width, size, weight)
    if len(wrapped) > lines:
        tail = list(clusters(wrapped[lines - 1].rstrip()))
        while tail and layout.width("".join(tail) + "…", size, weight) > width:
            tail.pop()
        wrapped = [*wrapped[:lines - 1], "".join(tail).rstrip() + "…"]
    return text(layer_id, "\n".join(wrapped), x, y, size, fill=color,
                fontWeight=weight, lineHeight=round(size * 1.2, 2))


def tray(width, height, items):
    """Return the attachment chooser at the caller's panel origin.

    The title and choices are live text. Item group IDs use the input positions
    and survive copy edits. The panel needs 38 units per row beneath its title.
    """
    if width < 160 or height < 60:
        raise ValueError("attachment tray needs at least 160 by 60 units")
    layout = TextLayout()
    prefix = "ui.overlay.tray"
    inset, top, gap = 12, 48, 6
    columns = min(max(1, int(width // 136)), len(items) or 1)
    rows = (len(items) + columns - 1) // columns
    cell_height = (height - top - inset - max(0, rows - 1) * gap) / max(1, rows)
    if items and cell_height < 38:
        raise ValueError("attachment tray needs more height for its items")
    cell_width = (width - 2 * inset - gap * (columns - 1)) / columns
    layers = [rect(f"{prefix}.panel", 0, 0, width, height, LAVENDER, 18),
              text(f"{prefix}.heading", "Add to chat", inset + 4, 15, 17,
                   fontWeight=700, fill=PLUM)]
    for index, label in enumerate(items):
        row, column = divmod(index, columns)
        item_id = f"{prefix}.item.{index}"
        # Use a left guide and an aligned label in each tile.
        mark = _label(layout, f"{item_id}.label", label, 20, 0,
                      cell_width - 28, 12, lines=2, weight=700)
        mark["y"] = (cell_height - mark["lineHeight"] * (1 + mark["text"].count("\n"))) / 2
        children = [rect(f"{item_id}.body", 0, 0, cell_width, cell_height, PAPER, 9),
                    rect(f"{item_id}.accent", 9, (cell_height - 16) / 2, 3, 16, PLUM, 1), mark]
        layers.append(group(item_id, inset + column * (cell_width + gap),
                            top + row * (cell_height + gap), children))
    return layers


def context_menu(width, height, labels, *, reaction_labels=()):
    """Return a compact action panel for the currently targeted message.

    Position the panel in viewport coordinates and animate its group as a unit.
    ``reaction_labels`` optionally adds a separate reaction strip above actions.
    The applied reaction is owned by the message and drawn in its own group.
    """
    if width < 140 or height < 36:
        raise ValueError("context menu needs at least 140 by 36 units")
    layout = TextLayout()
    prefix = "ui.overlay.context"
    inset = 8
    layers = [rect(f"{prefix}.panel", 0, 0, width, height, PAPER, 13,
                   stroke=DIVIDER, strokeWidth=1)]
    strip = 38 if reaction_labels else 0
    row_height = (height - 2 * inset - strip) / max(1, len(labels))
    if (labels and row_height < 23) or (reaction_labels and height < strip + 2 * inset):
        raise ValueError("context menu needs more height for its actions")
    if reaction_labels:
        cell_width = (width - 2 * inset) / len(reaction_labels)
        if cell_width < 24:
            raise ValueError("context menu needs more width for its reactions")
        layers.append(rect(f"{prefix}.reaction-strip", inset, inset, width - 2 * inset,
                           31, LAVENDER, 10))
        for index, label in enumerate(reaction_labels):
            layers.append(_label(layout, f"{prefix}.reaction.{index}", label,
                                 inset + cell_width * index + 4, inset + 8,
                                 cell_width - 8, 11, color=PLUM, weight=700))
    for index, label in enumerate(labels):
        y = inset + strip + row_height * index
        item_id = f"{prefix}.action.{index}"
        if index:
            layers.append(rect(f"{item_id}.divider", inset + 5, y, width - 2 * inset - 10,
                               1, DIVIDER))
        layers.append(_label(layout, f"{item_id}.label", label, inset + 8,
                             y + (row_height - 15) / 2, width - 2 * inset - 16,
                             13, weight=700))
    return layers


def _image_dimensions(src):
    if src.startswith("data:"):
        _, value = src.split(",", 1)
        source = BytesIO(b64decode(value, validate=True))
    else:
        source = Path(src)
    with Image.open(source) as image:
        return image.size


def media_viewer(width, height, title, src, *, image_size=None):
    """Return viewport chrome and an aspect-fitted image on separate layers.

    Provide ``image_size`` for scene-relative sources, or pass a readable local
    path or base64 raster URI as ``src`` to determine intrinsic dimensions.
    """
    header, margin = 50, 12
    if width < 140 or height <= header + 2 * margin:
        raise ValueError("media viewer needs room for its header and image")
    source_width, source_height = image_size if image_size is not None else _image_dimensions(src)
    if source_width <= 0 or source_height <= 0:
        raise ValueError("media dimensions must be positive")
    scale = min((width - 2 * margin) / source_width, (height - header - 2 * margin) / source_height)
    display_width, display_height = source_width * scale, source_height * scale
    prefix = "ui.overlay.viewer"
    return [
        rect(f"{prefix}.matte", 0, 0, width, height, INK, 0),
        {"id": f"{prefix}.asset", "type": "image", "src": src, "width": display_width,
         "height": display_height, "x": (width - display_width) / 2,
         "y": header + (height - header - display_height) / 2},
        rect(f"{prefix}.header", 0, 0, width, header, PLUM),
        text(f"{prefix}.close", "×", 14, 8, 25, fill=PAPER, fontWeight=700),
        _label(TextLayout(), f"{prefix}.title", title, 53, 15, width - 68,
               15, color=PAPER, weight=700),
    ]
