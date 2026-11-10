# Complete UI audio source and portable rebuild tools

The complete bundle contains original accepted audio, pinned music, configurations,
source snapshots, original CC0 archives/source pages, prepared effects, all6mix reports,
all canonical/source cue sheets,12finished previews and signal/codec audits.

Use an empty sandbox to preserve accepted exports:
python tools/rebuild_audio.py --example 05-linq --sandbox /your/empty/work
UI-only is the default;
--with-music uses the pinned music stem +mix-report without AI generation.

After retrieving a complete visual case, tools/mux_ui.py can combine its picture
stream with the UI audio using any of the5accepted methods. It explicitly maps only
video from the picture input and audio from the new UI track; it never copies the
source soundtrack into a new mix. UI-only preview gain is labelled separately.

tools/source_aliases.py optionally recreates legacy output/final-vXX scene paths
from portable scenes/ID for cue re-derivation. Already accepted cue schedules can
render without reading source scenes. The original Site-specific packager source
is retained for history; these portable helpers remove that implicit checkout need.

The original music-only mixer accepts --videos-json audio-recreation/videos.json.
Default full music rebuilding requires its pinned AI MP3/config snapshots, while
UI-with-music uses the accepted music.flac/mix-report directly. Music is optional.
No cookies, signed download-link responses or credentials are bundled.
