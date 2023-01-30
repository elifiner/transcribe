#!/bin/sh

if [ "$1" == "" ]; then
    echo "usage: $0 <url>"
    exit 1
fi

FILENAME=$(yt-dlp -N 5 -f bestaudio --extract-audio --audio-format best --get-filename -o '%(id)s.%(ext)s' "$1")
yt-dlp -N 5 -f bestaudio --extract-audio --audio-format best -o $FILENAME "$1"
