"""Authorable conversation state and frame-addressed actions."""
from copy import deepcopy
from dataclasses import dataclass, field
import math
import re

from .rich import KIND_LABELS

ID = re.compile(r"[a-z0-9][a-z0-9._:-]*")
KINDS = {
    "draft", "focus", "send", "receive", "typing", "reaction", "scroll",
    "camera", "edit", "unsend", "receipt", "overlay", "media.page", "suggestion", "search.query",
    "card.update", "card.vote",
}
RECEIPTS = {"", "Delivered", "Read", "Failed"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identifier(value, label):
    require(isinstance(value, str) and ID.fullmatch(value), f"invalid {label}: {value!r}")
    return value


def integer(value, label, low, high):
    require(type(value) is int and low <= value <= high,
            f"{label} must be an integer between {low} and {high}")
    return value


def number(value, label, low, high):
    require(type(value) in (int, float) and math.isfinite(value) and low <= value <= high,
            f"{label} must be between {low} and {high}")
    return value


def copy(value, label, allow_empty=True):
    require(isinstance(value, str) and (allow_empty or bool(value.strip())), f"invalid {label}")
    return value


def attachment_ids(value):
    require(isinstance(value, list), "attachments must be an array of asset IDs")
    normalized = [identifier(item, "asset ID") for item in value]
    require(len(normalized) == len(set(normalized)), "duplicate attachment ID")
    return normalized


def card_payload(value):
    require(isinstance(value, dict), "card must be an object")
    kind = value["kind"]
    require(kind in KIND_LABELS, f"unsupported card kind: {kind}")
    result = {"kind": kind, "title": copy(value["title"], "card title", False)}
    for key in ("detail", "action"):
        if key in value:
            result[key] = copy(value[key], f"card {key}")
    if kind == "poll":
        options = value["options"]
        require(isinstance(options, list) and 2 <= len(options) <= 12, "poll needs 2 to 12 options")
        result["options"] = []
        ids = set()
        for option in options:
            key = identifier(option["id"], "poll option ID")
            require(key not in ids, f"duplicate poll option {key}")
            ids.add(key)
            result["options"].append({
                "id": key, "label": copy(option["label"], "poll option label", False),
                "votes": integer(option["votes"], "vote count", 0, 1_000_000),
            })
        selected = value.get("selected")
        require(selected is None or isinstance(selected, str) and selected in ids, "unknown selected option")
        result["selected"] = selected
    return result


@dataclass
class Conversation:
    id: str
    owner: str
    people: dict
    messages: dict = field(default_factory=dict)
    draft: str = ""
    focused: bool = False
    typist: str | None = None
    scroll: float = 0
    overlay: dict | None = None
    receipt_id: str | None = None
    suggestion: dict | None = None
    query: str = ""

    def add(self, message):
        require(isinstance(message, dict), "message must be an object")
        mid = identifier(message["id"], "message ID")
        require(mid not in self.messages, f"duplicate message ID: {mid}")
        sender = identifier(message["senderId"], "sender ID")
        require(sender in self.people, f"unknown sender {sender}")
        body = copy(message.get("text", ""), "message text")
        attachments = attachment_ids(message.get("attachmentIds", []))
        card = card_payload(message["card"]) if "card" in message else None
        reply_to = message.get("replyTo")
        require(reply_to is None or (isinstance(reply_to, str) and reply_to in self.messages),
                f"{mid}: replyTo must identify an earlier message")
        require(body.strip() or attachments or card, f"{mid}: supply text, attachmentIds or card")
        require(message.get("receipt", "") in RECEIPTS, f"{mid}: unsupported receipt")
        require(not message.get("receipt") or sender == self.owner, f"{mid}: receipt belongs to an outgoing message")
        self.messages[mid] = {
            "id": mid, "senderId": sender, "text": body, "attachmentIds": attachments,
            "replyTo": reply_to, "reactions": {}, "page": 0, "edited": False, "card": card,
            "unsent": False, "receipt": message.get("receipt", ""),
        }
        if sender == self.owner and (message.get("receipt") or self.receipt_id is None):
            self.receipt_id = mid

    def timeline_state(self, anchor, scroll_offset, keyboard_visible):
        messages = []
        for mid, message in self.messages.items():
            if message["unsent"]:
                continue
            item = {k: message[k] for k in (
                "id", "senderId", "text", "attachmentIds", "reactions", "edited", "receipt",
            )}
            if message["replyTo"] is not None:
                item["replyTo"] = message["replyTo"]
            if message["attachmentIds"]:
                item["page"] = message["page"]
            messages.append(deepcopy(item))
        selected = self.overlay.get("messageId") if self.overlay else None
        surface = self.overlay["surface"] if self.overlay else "conversation"
        selection = {"selection": [selected]} if selected is not None else {}
        return {
            "conversationId": self.id,
            "messages": messages,
            "composer": {"text": self.draft, "focused": self.focused, "keyboardVisible": keyboard_visible},
            "viewport": {"surface": surface, "anchorMessageId": anchor,
                         "scrollOffset": scroll_offset, **selection},
            "typingSenderIds": [self.typist] if self.typist else [],
        }

    def apply(self, event):
        kind = event["kind"]
        if kind == "camera":
            return self.id
        if kind == "draft":
            self.draft = copy(event["text"], "draft")
        elif kind == "focus":
            require(type(event["focused"]) is bool, "focused must be true or false")
            self.focused = event["focused"]
        elif kind in {"send", "receive"}:
            message = dict(event["message"])
            if kind == "send":
                message.setdefault("senderId", self.owner)
                message.setdefault("text", self.draft)
                require(message["senderId"] == self.owner, "send belongs to the local sender")
            else:
                require(message["senderId"] != self.owner, "receive belongs to a remote sender")
            self.add(message)
            if kind == "send":
                self.draft = ""
                self.scroll = 0
            if self.typist == message["senderId"]:
                self.typist = None
            return message["id"]
        elif kind == "typing":
            sender = event["senderId"]
            require(isinstance(sender, str) and sender in self.people and sender != self.owner,
                    "typing requires a remote participant")
            require(type(event["active"]) is bool, "typing active must be true or false")
            if event["active"]:
                self.typist = sender
            elif sender == self.typist:
                self.typist = None
            return sender
        elif kind == "scroll":
            self.scroll = number(event["offset"], "scroll offset", 0, 1_000_000)
        elif kind == "suggestion":
            phase = event["phase"]
            require(phase in {"visible", "pressed", "hidden"}, "unknown suggestion phase")
            dismiss = event.get("dismissKeyboard", False)
            require(type(dismiss) is bool, "dismissKeyboard must be true or false")
            label = event.get("label", (self.suggestion or {}).get("label"))
            self.suggestion = {"label": copy(label, "suggestion label", False), "phase": phase} if phase != "hidden" else None
            if dismiss:
                self.focused = False
        elif kind == "search.query":
            require(self.overlay and self.overlay["surface"] == "search", "search query requires an open search")
            self.query = copy(event["query"], "search query")
        elif kind == "overlay":
            return self.set_overlay(event)
        else:
            target = self.message_id(event["messageId"])
            message = self.messages[target]
            if kind == "reaction":
                sender = event.get("senderId", self.owner)
                require(isinstance(sender, str) and sender in self.people, "unknown reaction sender")
                mark = copy(event["mark"], "reaction mark")
                if mark.strip():
                    message["reactions"][sender] = mark
                else:
                    message["reactions"].pop(sender, None)
                if self.overlay and self.overlay.get("messageId") == target and self.overlay["surface"] == "context":
                    self.overlay = None
            elif kind == "edit":
                message["text"] = copy(event["text"], "edited message", bool(message["attachmentIds"] or message["card"]))
                message["edited"] = True
            elif kind == "unsend":
                message["unsent"] = True
                if self.receipt_id == target:
                    self.receipt_id = next((mid for mid in reversed(self.messages)
                                            if not self.messages[mid]["unsent"] and self.messages[mid]["receipt"]), None)
                if self.overlay and self.overlay.get("messageId") == target:
                    self.overlay = None
            elif kind == "receipt":
                require(message["senderId"] == self.owner, "receipt requires an outgoing message")
                require(event["status"] in RECEIPTS, "unsupported receipt status")
                message["receipt"] = event["status"]
                if message["receipt"] or self.receipt_id == target:
                    self.receipt_id = target
            elif kind == "media.page":
                count = len(message["attachmentIds"])
                require(count >= 2, "media.page requires multiple attachments")
                message["page"] = integer(event["index"], "media index", 0, count - 1)
            elif kind == "card.update":
                require(message["card"] is not None, "card.update requires a card")
                message["card"] = card_payload(event["card"])
            elif kind == "card.vote":
                card = message["card"]
                require(card is not None and card["kind"] == "poll", "card.vote requires a poll")
                selected = identifier(event["optionId"], "poll option ID")
                option = next((item for item in card["options"] if item["id"] == selected), None)
                require(option is not None, f"unknown poll option {selected}")
                option["votes"] = integer(event["votes"], "vote count", 0, 1_000_000)
                card["selected"] = selected
            return target
        return self.id

    def message_id(self, value):
        mid = identifier(value, "message ID")
        require(mid in self.messages and not self.messages[mid]["unsent"], f"message is unavailable: {mid}")
        return mid

    def set_overlay(self, event):
        surface = event["surface"]
        if surface == "conversation":
            target = self.overlay.get("messageId") if self.overlay else None
            self.overlay = None
            return target or self.id
        if surface == "tray":
            items = event.get("items", ["Photos", "Camera", "Files", "Location"])
            require(isinstance(items, list) and items, "tray items must be a list of labels")
            self.overlay = {"surface": surface, "items": [copy(item, "tray label", False) for item in items]}
            return self.id
        if surface in {"list", "search"}:
            self.overlay = {"surface": surface}
            if surface == "search" and "query" in event:
                self.query = copy(event["query"], "search query")
            return self.id
        require(surface in {"context", "media"}, f"unsupported overlay: {surface}")
        mid = self.message_id(event["messageId"])
        if surface == "media":
            require(bool(self.messages[mid]["attachmentIds"]), "media overlay requires an attachment")
        self.overlay = {"surface": surface, "messageId": mid}
        return mid
