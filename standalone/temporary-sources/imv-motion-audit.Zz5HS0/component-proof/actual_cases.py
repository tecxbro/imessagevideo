from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()))
from ui.adapter import compile_conversation

output = Path(sys.argv[1])
def msg(mid, sender, text, **args):
    return {"id": mid, "senderId": sender, "text": text, **args}

def action(name, kind, frame, durationFrames=4, **args):
    return {"id": name, "kind": kind, "frame": frame, "durationFrames": durationFrames, **args}

me, other = "local", "remote"
prior = msg("north-door", other, "I’m at the north door.")
latest = msg("in-transit", me, "Meet by the bench.")
other_reply = msg("ready", other, "See you there.")
draft = action("type-now", "draft", 8, text=latest["text"])
send = action("send-now", "send", 18, message=latest)
context = action("open-actions", "overlay", 8, surface="context", messageId=prior["id"])
cases = {
    "photos-under-fixed-heading": (
        {"messages": [msg("other-photo", other, "", attachmentIds=["first", "second"]),
                      msg("selected-photo", other, "", attachmentIds=["first", "second"])]},
        [action("page-now", "media.page", 12, index=1, messageId="selected-photo")], [12, 16]
    ),
    "conversation-handoff": ({"messages": [prior]}, [draft, send, action("reply-now", "receive", 25, message=other_reply)], [8, 29]),
    "composer-type": ({"messages": [prior]}, [action("type-start", "draft", 5, text="M"), draft], [5, 12]),
    "draft-send-flight": ({"draft": latest["text"], "messages": [prior]}, [send], [18, 22]),
    "typing-indicator-cycle": ({"messages": [prior, latest]}, [action("typing-now", "typing", 8, active=True, senderId=other)], [8, 12]),
    "reply-makes-room": ({"messages": [prior, latest]}, [action("reply-now", "receive", 8, message=other_reply)], [8, 12]),
    "delivery-receipt-handoff": ({"draft": latest["text"], "messages": [prior]}, [
        send, action("confirm-delivery", "receipt", 24, messageId=latest["id"], status="Delivered")], [18, 28]),
    "long-press-actions": ({"messages": [prior]}, [context], [8, 13]),
    "reaction-attach": ({"messages": [prior]}, [context, action("mark-now", "reaction", 19, messageId=prior["id"], mark="Love")], [8, 23]),
    "edit-message-reflow": ({"messages": [prior, latest]}, [action("correct-text", "edit", 8, messageId=latest["id"], text="Meet by the blue bench on the east side.")], [8, 12]),
    "undo-send-remove": ({"messages": [prior, latest]}, [action("remove-send", "unsend", 8, messageId=latest["id"])], [8, 12]),
    "keyboard-focus-reflow": ({"messages": [prior, latest]}, [action("open-keyboard", "focus", 8, focused=True)], [8, 12]),
    "app-drawer": ({"messages": [prior]}, [action("open-drawer", "overlay", 8, surface="tray")], [8, 12]),
}

records = []
for motion, (initial, events, window) in cases.items():
    assets = {"first": "motion/assets/landscape-1.png", "second": "motion/assets/landscape-2.png"} if motion.startswith("photos") else {}
    conversation = {"version": 1, "skin": "contact-thread", "conversationId": "thread.meeting", "title": "Jamie",
                    "participants": {me: "Me", other: "Jamie"}, "localSenderId": me, "fps": 30, "frameCount": 40,
                    "display": {"width": 390, "height": 700, "handset": True},
                    "events": deepcopy(events), "initial": deepcopy(initial), "assets": assets}
    scene = compile_conversation(conversation, output_dir=output)
    (output / f"{motion}.json").write_text(json.dumps(scene))
    records.append({"id": motion, "eventIds": [event["id"] for event in events], "window": window})
(output / "cases.json").write_text(json.dumps(records))
