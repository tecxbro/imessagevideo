import os
import sys

blocked = ("/Users/darshan/Downloads/sidehoe.mp4", "/Users/darshan/Documents/ChatGPT/imessage-video")

def guard(event, args):
    if event == "open" and isinstance(args[0], (str, bytes)):
        path = os.path.realpath(os.fsdecode(args[0]))
        if any(path == prefix or path.startswith(prefix + "/") for prefix in blocked):
            raise PermissionError("source and workspace are outside the clean project")
    if event.startswith("socket."):
        raise PermissionError("network is outside the clean project")

sys.addaudithook(guard)
