"""Project a procedural scene's events into the skill's measured-timeline schema."""
import argparse
import importlib.util
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("scene",type=Path)
    p.add_argument("resolver",type=Path)
    p.add_argument("out",type=Path)
    args=p.parse_args()
    scene=json.loads(args.scene.read_text())
    timeline=scene["timeline"]
    targets=sorted({event["target"] for event in timeline["events"]})
    for event in timeline["events"]:
        event["layerIds"]=[event["target"]]
    for cue in timeline["cues"]:
        cue.pop("asset")
    clock_scene={
        "width":scene["outputSize"],"height":scene["outputSize"],"fps":scene["fps"],
        "duration":scene["duration"],"timeline":timeline,
        "layers":[{"id":name,"type":"group","children":[]} for name in targets],
    }
    spec=importlib.util.spec_from_file_location("timeline_contract", args.resolver)
    resolver=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resolver)
    event_map=resolver.resolve(clock_scene)
    args.out.write_text(json.dumps(event_map,ensure_ascii=False,indent=2)+"\n")
    print(f"{len(event_map['events'])} events, {len(event_map['cues'])} cues, {event_map['sampleCount']} audio samples")


if __name__=="__main__":
    main()
