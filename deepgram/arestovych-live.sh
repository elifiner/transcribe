#!/bin/sh

if [ "$1" == "" ]; then
    echo "usage: $0 <url>"
    exit 1
fi

echo DOWNLOADING...

ID=$(yt-dlp --get-filename --replace-in-metadata channel ' ' '-' -o '%(channel)s-%(release_date)s-%(id)s' "$1")
# mkdir -p "$ID"
# yt-dlp -N 5 -f bestaudio --extract-audio --audio-format best --split-chapters -o "$ID.%(ext)s" -o "chapter:$ID/%(section_number)03d - %(section_title)s.%(ext)s" "$1"

echo TRANSCRIBING...

# for file in "$ID"/*.opus; do
#     echo "$FILE"
#     .venv/bin/python transcribe-file.py "$FILE" > "$FILE.txt"
# done

echo TRANSLATING...

.venv/bin/python parse-arestovych.py "$ID" > "$ID-English.txt"
