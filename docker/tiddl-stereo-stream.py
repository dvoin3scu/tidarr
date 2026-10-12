"""Make tiddl ask Tidal for the stereo stream unless Dolby Atmos is wanted.

tiddl requests playback info without `immersiveaudio`, so Tidal returns the
Dolby Atmos stream for tracks that have one; with atmos_filter "none" tiddl
then skips every such track and downloads nothing. Pass immersiveaudio=false
when the filter is "none" so the stereo stream is returned instead.
"""
import pathlib
import sys

import tiddl

root = pathlib.Path(tiddl.__file__).parent

edits = [
    (
        root / "core/api/api.py",
        "    def get_track_stream(self, track_id: ID, quality: TrackQuality):\n"
        "        return self.client.fetch(\n"
        "            TrackStream,\n"
        "            f\"tracks/{track_id}/playbackinfopostpaywall\",\n"
        "            {\n"
        "                \"audioquality\": quality,\n",
        "    def get_track_stream(self, track_id: ID, quality: TrackQuality, immersive: bool = True):\n"
        "        return self.client.fetch(\n"
        "            TrackStream,\n"
        "            f\"tracks/{track_id}/playbackinfopostpaywall\",\n"
        "            {\n"
        "                \"audioquality\": quality,\n"
        "                \"immersiveaudio\": \"true\" if immersive else \"false\",\n",
    ),
    (
        root / "cli/commands/download/downloader.py",
        "                    stream = self.api.get_track_stream(\n"
        "                        track_id=item.id, quality=self.track_quality\n"
        "                    )\n",
        "                    stream = self.api.get_track_stream(\n"
        "                        track_id=item.id,\n"
        "                        quality=self.track_quality,\n"
        "                        immersive=self.dolby_atmos_filter != \"none\",\n"
        "                    )\n",
    ),
]

for path, old, new in edits:
    source = path.read_text()
    if source.count(old) != 1:
        sys.exit(f"tiddl patch: expected code not found in {path}, tiddl version changed?")
    path.write_text(source.replace(old, new))
    print(f"tiddl patch: updated {path}")
