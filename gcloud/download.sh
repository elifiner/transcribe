#!/bin/sh
if [ "$1" == "" ]; then
    echo "$0 <url>"
    exit 1
fi
# youtube-dl -i -o "%(title)s.%(ext)s" $1
# youtube-dl -i -o "%(title)s.%(ext)s" -x --audio-format mp3 $1
venv/bin/youtube-dl -i -o "%(title)s.%(ext)s" -x --audio-format flac $1

# convert FLAC into a lower bitrate flac which is enough for voice recognition
# ffmpeg -i russian-sample.flac -sample_fmt s16 -ar 8000 output.flac