"""Lay out an editable film screen and project frame-addressed state into it."""
from .accessories import KEYBOARD_HEIGHT, context_menu, keyboard, media_viewer, tray
from .components import (
    FOOTER, GUTTER, HEADER, INK, LAVENDER, MUTED, PAPER, PALETTES, PLUM, TextLayout,
    bubble, clip, composer, font_path, group, header, rect, text, typing,
)
from .inbox import INBOX_CONTROL_HEIGHT, INBOX_HEADER_HEIGHT, inbox_chrome, inbox_rows, search_rows
from .rich import build_card, payment_approval
from .state import copy, integer, require
from .tracks import Tracks


class Layout:
    def __init__(self, doc, assets, inbox, fps, frames):
        display = doc.get("display", {})
        require(isinstance(display, dict), "display must be an object")
        self.width = integer(display.get("width", 390), "display width", 320, 1080)
        self.height = integer(display.get("height", 720), "display height", 480, 1920)
        canvas = doc.get("canvas", {})
        require(isinstance(canvas, dict), "canvas must be an object")
        self.canvas_width = integer(canvas.get("width", self.width), "canvas width", 160, 2560)
        self.canvas_height = integer(canvas.get("height", self.height), "canvas height", 160, 2560)
        self.center_x = (self.canvas_width - self.width) / 2
        self.center_y = (self.canvas_height - self.height) / 2
        self.size = integer(display.get("textSize", 16), "text size", 13, 24)
        self.outgoing_color, self.incoming_color = PALETTES[doc.get("skin", "film-paper")]
        self.measure = TextLayout()
        self.assets = assets
        self.tracks = Tracks(fps, frames)
        self.rows = {}
        self.inbox = inbox
        self.typing = group("ui.typing", GUTTER, 0, [], opacity=0)
        self.transcript = group("ui.transcript", 0, 0, [self.typing])
        self.viewport = group("ui.viewport", 0, HEADER, [self.transcript],
                              clip=clip(self.width, self.height - HEADER - FOOTER))
        self.keyboard = group("ui.keyboard", 0, self.height, keyboard(self.width))
        self.composer = group("ui.composer", 0, 0, [])
        self.suggestion = group("ui.suggestion", 0, self.height, [], opacity=0)
        self.header = header(self.width, copy(doc["title"], "title", False),
                             copy(doc.get("service", "Messages"), "service"), self.measure)
        self.overlay = group("ui.overlay", 0, self.height, [], opacity=0)
        self.context_id = None
        self.context_frame = 0
        self.context_reveal = 0
        self.shade = rect("ui.context.shade", 0, 0, self.width, self.height, INK, opacity=0)
        self.inbox_list = group("ui.inbox.rows", 0, 0, [], opacity=0)
        self.inbox_results = group("ui.inbox.results", 0, 0, [], opacity=0)
        self.inbox_chrome = group("ui.inbox.chrome", 0, 0, [])
        inbox_clip = clip(self.width, self.height - INBOX_HEADER_HEIGHT - INBOX_CONTROL_HEIGHT)
        self.navigation = group("ui.inbox", 0, 0, [
            rect("ui.inbox.paper", 0, 0, self.width, self.height, PAPER),
            group("ui.inbox.viewport", 0, INBOX_HEADER_HEIGHT,
                  [self.inbox_list, self.inbox_results], clip=inbox_clip),
            self.inbox_chrome,
        ], opacity=0)
        screen = group("ui.screen", 0, 0, [
            rect("ui.paper", 0, 0, self.width, self.height, PAPER),
            self.shade, self.viewport, self.keyboard, self.composer, self.suggestion,
            rect("ui.footer", 0, self.height - FOOTER, self.width, FOOTER, PAPER),
            self.header, self.overlay, self.navigation,
        ], clip=clip(self.width, self.height))
        self.camera = group("ui.camera", self.center_x, self.center_y, [screen],
                            originX=self.width / 2, originY=self.height / 2)

    def photo(self, id, asset_id, x, y, width, height):
        src, iw, ih = self.assets[asset_id]
        scale = min(width / iw, height / ih)
        w, h = round(iw * scale, 3), round(ih * scale, 3)
        return dict(id=id, type="image", src=src, x=x + (width - w) / 2,
                    y=y + (height - h) / 2, width=w, height=h)

    def new_row(self, mid, frame):
        id = f"ui.message/{mid}"
        row = group(id, 0, 0, [], start=frame / self.tracks.fps)
        row["children"] = [
            group(id + "/isolation", 0, 0, [], opacity=0),
            group(id + "/body", 0, 0, []),
            group(id + "/media", 0, 0, []),
            group(id + "/reaction", 0, 0, [], opacity=0),
            group(id + "/receipt", 0, 0, []),
            group(id + "/card", 0, 0, []),
        ]
        self.transcript["children"].insert(-1, row)
        self.rows[mid] = row
        return row

    def media_stack(self, id, attachments, width):
        stride = width + 8
        height = round(min(width * .63, 190))
        tiles = []
        for i, aid in enumerate(attachments):
            tiles.extend([
                rect(id + f"/{aid}/matte", i * stride, 0, width, height, LAVENDER, 9),
                self.photo(id + f"/{aid}/image", aid, i * stride, 0, width, height),
            ])
        return height, stride, tiles

    def message(self, state, message, joined, selected, frame, duration):
        mid = message["id"]
        row = self.rows.get(mid)
        new = row is None
        if new:
            row = self.new_row(mid, frame)
        id = row["id"]
        isolation, body, media, reaction, receipt, card = row["children"]
        outgoing = message["senderId"] == state.owner
        unsent = message["unsent"]
        show_name = len(state.people) > 2 and not outgoing
        cursor = 0
        label_width = 0
        parts = []
        attachments = [] if unsent else message["attachmentIds"]
        marks = {} if unsent else message["reactions"]
        if marks:
            cursor += 13
        if show_name:
            name = self.measure.ellipsis(state.people[message["senderId"]], self.width - GUTTER * 2, 11)
            label_width = self.measure.width(name, 11)
            parts.append(text(id + "/sender", name, 0, cursor, 11, fill=MUTED))
            cursor += 17
        if message["replyTo"] and not unsent:
            quoted = state.messages[message["replyTo"]]
            original = "Message removed" if quoted["unsent"] else quoted["text"] or (
                quoted["card"]["title"] if quoted["card"] else "Attachment"
            )
            snippet = self.measure.ellipsis(original, self.width * .66 - 18, 11)
            label_width = max(label_width, 8 + self.measure.width(snippet, 11))
            parts.extend([
                rect(id + "/quote-rule", 0, cursor + 2, 2, 13, PLUM, 1),
                text(id + "/quote", snippet, 8, cursor, 11, fill=MUTED),
            ])
            cursor += 20
        copy = "Message removed" if unsent else message["text"]
        card_payload = message["card"] if not unsent else None
        media_width = min(250, round(self.width * .71)) if attachments or card_payload else 0
        bubble_width = 0
        if copy:
            color = "#786579" if unsent else self.outgoing_color if outgoing else self.incoming_color
            bubble_width, h, bubble_parts = bubble(id, copy, outgoing, self.width, self.measure,
                                                   joined, self.size, color=color)
            parts.append(group(id + "/text", 0, cursor, bubble_parts))
            cursor += h
        width = max(bubble_width, media_width, label_width)
        x = self.width - GUTTER - width if outgoing else GUTTER
        if copy and outgoing and bubble_width < width:
            parts[-1]["x"] = width - bubble_width
        self.tracks.move(body, frame, 0, x=x)
        if attachments:
            if copy:
                cursor += 5
            height, stride, tiles = self.media_stack(id + "/tiles", attachments, media_width)
            if not media["children"]:
                rail = group(id + "/rail", 0, 0, tiles)
                media["children"].append(group(id + "/media-window", 0, 0, [rail],
                                                clip=clip(media_width, height, 9)))
            rail = media["children"][0]["children"][0]
            self.tracks.move(rail, frame, 0 if new else duration, x=-message["page"] * stride)
            self.tracks.move(media, frame, 0 if new else duration,
                             x=self.width - GUTTER - media_width if outgoing else GUTTER, y=cursor,
                             opacity=1)
            cursor += height
            if len(attachments) > 1:
                parts.append(text(id + "/page", f"{message['page'] + 1} / {len(attachments)}",
                                  width / 2, cursor + 3, 10, textAnchor="middle", fill=MUTED))
                cursor += 17
        elif media["children"]:
            self.tracks.move(media, frame, 0, opacity=0)
        if card_payload:
            if copy or attachments:
                cursor += 5
            card_height, card_parts = build_card(card["id"], card_payload, media_width, self.measure)
            self.tracks.revise(card, card_parts, frame)
            card_x = self.width - GUTTER - media_width if outgoing else GUTTER
            self.tracks.move(card, frame, 0, x=card_x, y=cursor)
            cursor += card_height
        else:
            self.tracks.revise(card, [], frame)
        self.tracks.revise(body, parts, frame)
        if marks:
            label = self.measure.ellipsis("  ".join(marks.values()), self.width * .52 - 16, 11, 700)
            badge_width = self.measure.width(label, 11, 700) + 16
            self.tracks.revise(reaction, [
                rect(id + "/reaction-chip", 0, 0, badge_width, 20, "#fffaf4", 7, stroke=PLUM, strokeWidth=1),
                text(id + "/reaction-mark", label, badge_width / 2, 3, 11, fill=PLUM,
                     textAnchor="middle", fontWeight=700),
            ], frame)
            self.tracks.move(reaction, frame, 0, x=max(GUTTER, x + width - badge_width - 6))
            self.tracks.move(reaction, frame, duration, opacity=1)
        else:
            self.tracks.move(reaction, frame, 0, opacity=0)
        detail = []
        if message["edited"] and not unsent:
            detail.append("Edited")
        if state.receipt_id == mid and message["receipt"] and not unsent:
            detail.append(message["receipt"])
        self.tracks.revise(receipt, [
            text(id + "/status", " · ".join(detail), 0, 0, 10, fill=MUTED,
                 textAnchor="end" if outgoing else "start")
        ] if detail else [], frame)
        self.tracks.move(receipt, frame, 0, x=x + width if outgoing else x, y=cursor + 3)
        height = cursor + (16 if detail else 0)
        if selected:
            self.tracks.revise(isolation, [
                rect(id + "/backing", 0, -3, width + 8, height + 6, PAPER, 12),
            ], frame)
            self.tracks.move(isolation, frame, 0, x=x - 4)
        self.tracks.move(isolation, frame, min(2, duration), opacity=1 if selected else 0)
        return row, new, height

    def render_state(self, state, frame, duration, action=None, target=None):
        keyboard_height = KEYBOARD_HEIGHT if state.focused and not (
            state.overlay and state.overlay["surface"] == "tray") else 0
        composer_height, composer_parts = composer(self.width, state.draft, state.focused, self.measure)
        composer_y = self.height - FOOTER - keyboard_height - composer_height
        self.tracks.revise(self.composer, composer_parts, frame)
        self.tracks.move(self.composer, frame, duration, y=composer_y)
        self.tracks.move(self.keyboard, frame, duration, y=self.height - FOOTER - keyboard_height)
        suggestion_height = self.render_suggestion(state, composer_y, frame, duration)
        messages = list(state.messages.values())
        cursor = 11
        bounds = []
        arriving = None
        context_id = state.overlay["messageId"] if state.overlay and state.overlay["surface"] == "context" else None
        for chrome in (self.header, self.keyboard, self.composer):
            self.tracks.move(chrome, frame, duration, opacity=.59 if context_id else 1)
        self.tracks.move(self.shade, frame, duration, opacity=.12 if context_id else 0)
        for i, message in enumerate(messages):
            joined = (i + 1 < len(messages) and message["senderId"] == messages[i + 1]["senderId"]
                      and not (message["unsent"] or messages[i + 1]["unsent"]))
            row, new, height = self.message(state, message, joined,
                                            message["id"] == context_id, frame, duration)
            bounds.append((message, cursor, cursor + height))
            if new:
                row["y"] = cursor + (11 if frame else 0)
                if frame:
                    row["opacity"] = .66 if action == "send" else .38
                    if action == "send" and message["id"] == target:
                        arriving = (row, cursor, height)
            if not arriving or row is not arriving[0]:
                reflow = action in {"edit", "unsend", "card.update", "reaction"}
                self.tracks.move(row, frame, 0 if reflow else duration, y=cursor)
            self.tracks.move(row, frame, min(5, duration), opacity=.43 if context_id and message["id"] != context_id else 1)
            cursor += height + (4 if joined else 10)
        if state.typist:
            self.tracks.revise(self.typing, typing("ui.typing", state.people[state.typist], self.width, self.measure), frame)
            self.tracks.move(self.typing, frame, 0, y=cursor)
            self.tracks.move(self.typing, frame, duration, opacity=1)
            cursor += 39
        else:
            self.tracks.move(self.typing, frame, 0, opacity=0)
        live_height = composer_y - HEADER - suggestion_height
        bottom = min(0, live_height - cursor)
        scroll_y = min(0, bottom + state.scroll)
        if action in {"send", "receive"} and frame and duration > 1 and state.scroll == 0 and scroll_y < self.tracks.value(self.transcript, "y", frame - 1):
            # Advance enough on the first action frame for the new row to enter the viewport.
            previous_y = self.tracks.value(self.transcript, "y", frame - 1)
            self.tracks.move(self.transcript, frame, 0, y=max(scroll_y, previous_y - 32))
            self.tracks.move(self.transcript, frame + 1, max(0, duration - 1), y=scroll_y)
        else:
            self.tracks.move(self.transcript, frame, duration, y=scroll_y)
        if arriving:
            row, top, height = arriving
            # Start near the field in viewport coordinates. Keep older rows in
            # transcript coordinates so a short history never follows the send.
            field_y = self.tracks.value(self.composer, "y", frame)
            scroll_at_frame = self.tracks.value(self.transcript, "y", frame)
            launch_y = field_y - suggestion_height - height - 2 - HEADER - scroll_at_frame
            row["y"] = max(top, launch_y)
            self.tracks.move(row, frame, duration, settle=True, y=top)
        self.render_overlay(state, bounds, scroll_y, live_height, frame, duration)
        surface = state.overlay["surface"] if state.overlay else "conversation"
        anchor = None
        if surface not in {"list", "search"}:
            anchor = next((m["id"] for m, top, end in reversed(bounds)
                           if not m["unsent"] and end + scroll_y > 0 and top + scroll_y < live_height), None)
        keyboard_visible = bool(keyboard_height and surface not in {"list", "search", "media"})
        return anchor, scroll_y - bottom, keyboard_visible

    def render_suggestion(self, state, composer_y, frame, duration):
        suggestion = state.suggestion
        if suggestion is None:
            self.tracks.move(self.suggestion, frame, duration, opacity=0, y=composer_y)
            return 0
        height = 40
        title = self.measure.ellipsis(suggestion["label"], self.width - GUTTER * 2 - 26, 13, 700)
        self.tracks.revise(self.suggestion, [
            rect("ui.suggestion.paper", 0, 0, self.width, height, PAPER),
            rect("ui.suggestion.button", GUTTER, 3, self.width - GUTTER * 2, 32, LAVENDER, 9),
            text("ui.suggestion.label", title, GUTTER + 12, 11, 13, fontWeight=700, fill=PLUM),
        ], frame)
        opacity = .48 if suggestion["phase"] == "pressed" else 1
        self.tracks.move(self.suggestion, frame, duration, opacity=opacity, y=composer_y - height)
        return height

    def render_overlay(self, state, bounds, scroll_y, live_height, frame, duration):
        overlay = state.overlay
        surface = overlay["surface"] if overlay else "conversation"
        self.render_inbox(surface, state, frame, duration)
        if surface != "context":
            self.context_id = None
        if surface in {"conversation", "list", "search"}:
            self.tracks.move(self.overlay, frame, duration, opacity=0)
            return
        width = self.width
        follow = None
        if surface == "tray":
            height = min(190, self.height - HEADER - FOOTER)
            layers = tray(width, height, overlay["items"])
            y = self.height - FOOTER - height
            x = 0
        elif surface == "context":
            width = min(276, self.width - GUTTER * 2)
            height = 162
            labels = ["Reply", "Copy", "More"]
            layers = context_menu(width, height, labels, reaction_labels=["Like", "Love", "Wow"])
            if self.context_id != overlay["messageId"]:
                self.context_id = overlay["messageId"]
                self.context_frame = frame
                self.context_reveal = min(duration, max(1, round(.13 * self.tracks.fps)))
            rail = [node for node in layers if ".reaction" in node["id"]]
            layers = [node for node in layers if ".reaction" not in node["id"]]
            layers.append(group("ui.overlay.context.rail", 0, 0, rail,
                                start=(self.context_frame + self.context_reveal) / self.tracks.fps))
            selected = next((b for b in bounds if b[0]["id"] == overlay["messageId"]))
            row_y = HEADER + scroll_y + selected[1]
            row_end = HEADER + scroll_y + selected[2]
            lift = max(5, row_end + 7 + height - (HEADER + live_height))
            lift = min(lift, max(0, row_y - HEADER - 6))
            row = self.rows[overlay["messageId"]]
            self.tracks.move(row, frame, duration, y=selected[1] - lift)
            y = max(HEADER + 4, min(self.height - FOOTER - height, row_end - lift + 7))
            x = self.width - GUTTER - width if selected[0]["senderId"] == state.owner else GUTTER
            if row_end - row_y + height + 14 < live_height:
                follow = row, selected[2] - selected[1]
        elif surface == "payment-approval":
            card = state.messages[overlay["messageId"]]["card"]
            layers = payment_approval(width, self.height, card, self.measure)
            x, y = 0, 0
        else:
            message = state.messages[overlay["messageId"]]
            asset = self.assets[message["attachmentIds"][message["page"]]]
            layers = media_viewer(width, self.height, f"Photo {message['page'] + 1}", asset[0],
                                  image_size=asset[1:])
            x, y = 0, 0
        if follow:
            row, row_height = follow
            self.tracks.move(self.overlay, frame, 0, x=x)
            for f in range(frame, min(self.tracks.count, frame + max(1, duration))):
                rowend = HEADER + row_height + self.tracks.value(row, "y", f)
                rowend += self.tracks.value(self.transcript, "y", f)
                self.tracks.move(self.overlay, f, 0, y=max(HEADER + 4, rowend + 7))
        elif duration > 1 and self.tracks.value(self.overlay, "opacity", max(0, frame - 1)) == 0:
            self.tracks.move(self.overlay, frame, 0, x=x, y=y + 10)
            self.tracks.move(self.overlay, frame + 1, max(0, duration - 1), x=x, y=y)
        else:
            self.tracks.move(self.overlay, frame, duration, x=x, y=y)
        self.tracks.revise(self.overlay, layers, frame)
        self.tracks.move(self.overlay, frame, duration, opacity=1)

    def render_inbox(self, surface, state, frame, duration):
        if surface not in {"list", "search"}:
            self.tracks.move(self.navigation, frame, duration, opacity=0)
            return
        height = self.height - INBOX_HEADER_HEIGHT - INBOX_CONTROL_HEIGHT
        searching = surface == "search"
        query = state.query if searching else None
        self.tracks.revise(self.inbox_list, inbox_rows(self.width, height, self.inbox), frame)
        if searching:
            self.tracks.revise(self.inbox_results, search_rows(self.width, height, self.inbox, query), frame)
        self.tracks.revise(self.inbox_chrome, inbox_chrome(self.width, self.height, query), frame)
        self.tracks.move(self.inbox_list, frame, duration, y=-64 if searching else 0,
                         opacity=0 if searching else 1)
        self.tracks.move(self.inbox_results, frame, duration, opacity=1 if searching else 0)
        self.tracks.move(self.navigation, frame, duration, opacity=1)

    def event_layers(self, kind, target):
        row = self.rows.get(target)
        if kind == "camera":
            return ["ui.camera"]
        if kind == "suggestion":
            return ["ui.suggestion"]
        if kind == "search.query":
            return ["ui.inbox.results", "ui.inbox.chrome"]
        if kind in {"draft", "focus"}:
            return ["ui.composer", "ui.keyboard"] if kind == "focus" else ["ui.composer"]
        if kind == "scroll":
            return ["ui.transcript"]
        if kind == "typing":
            return ["ui.typing"]
        if kind == "overlay":
            return ["ui.overlay", "ui.inbox"]
        suffix = {"reaction": "/reaction", "media.page": "/media", "receipt": "/receipt",
                  "card.update": "/card", "card.vote": "/card"}
        return [row["id"] + suffix.get(kind, "")]
