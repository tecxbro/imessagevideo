"""Use the installed Messages adapter for supported semantic state."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path)
    parser.add_argument("scene", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.skill))
    from ui.adapter import initial_state

    scene=json.loads(args.scene.read_text())
    events={e["id"]:e for e in scene["timeline"]["events"]}
    for name,partner in (("sofia","sofia"),("follow","assistant")):
        entry=events[f"{name}.in"]["uiState"]
        ui=initial_state({
            "conversationId": name, "localSenderId": "owner",
            "participants": {"owner":"Owner", partner:scene["copy"][name][0]},
            "initial": {"messages":entry["messages"],"draft":entry["composer"]["text"],
                        "focused":entry["composer"]["focused"]},
        })
        for eid in [e for e in events if e.startswith(name+".")]:
            event=events[eid]
            if "uiState" not in event:
                continue
            original=event["uiState"]
            if eid == "sofia.suggestion":
                ui.apply({"kind":"suggestion","phase":"visible","label":" ".join(scene["copy"]["sofia"][6])})
            if eid == "sofia.isolated":
                ui.apply({"kind":"suggestion","phase":"visible","dismissKeyboard":True})
            if eid == "sofia.send-contact":
                ui.apply({"kind":"suggestion","phase":"pressed"})
            assert bool(original["composer"]["focused"]) == ui.focused
            viewport=original["viewport"]
            verified=ui.timeline_state(viewport["anchorMessageId"],0,ui.focused)
            verified["viewport"].update(viewport)
            event["uiState"]=verified
    args.out.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+"\n")


if __name__ == "__main__":
    main()
