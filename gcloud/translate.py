#!/usr/bin/env python3

import os
import re
import sys
import srt
import time
import argparse
from tqdm.std import tqdm
from dotenv import load_dotenv
from google.cloud import translate
from google.api_core import operations_v1 as operations

KEY_FILE = 'key.json'

load_dotenv()

def log(s='', newline=True):
    sys.stderr.write(s + ('\n' if newline else ''))
    sys.stderr.flush()

def remove_profanity(s):
    s = re.sub(r'\bfuck', 'f***', s)
    return s

def translate_lines(lines, from_lang, to_lang):
    client = translate.TranslationServiceClient()
    location = 'global'
    parent = f'projects/{os.environ["PROJECT_ID"]}/locations/{location}'
    response = client.translate_text(
        request={
            'parent': parent,
            'contents': lines,
            'mime_type': 'text/plain',
            'source_language_code': from_lang,
            'target_language_code': to_lang,
        }
    )
    return [remove_profanity(t.translated_text) for t in response.translations]

def translate_subs(subs, source_lang, target_lang):
    newsubs = []
    lines = [s.content for s in subs]
    translated_lines = translate_lines(lines, source_lang, target_lang)
    for sub, line in zip(subs, translated_lines):
        newsubs.append(srt.Subtitle(index=sub.index, start=sub.start, end=sub.end, content=line))
    return newsubs

def load_srt(in_file):
    f = open(in_file, 'r')
    return list(srt.parse(f.read()))

def write_srt(out_file, subs):
    f = open(out_file, 'w')
    f.writelines(srt.compose(subs))
    f.close()
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='filename', nargs='?', metavar='FILE', help='transcribe an audio file')
    parser.add_argument('--language', '-l', dest='source_lang', default='en-US', metavar='LANG', help='source language (e.g. ru-RU)')
    parser.add_argument('--target', '-t', dest='target_lang', default='en-US', metavar='LANG', help='target language (e.g. en-US)')
    args = parser.parse_args()
    if (not args.filename):
        parser.print_help()
        sys.exit(1)

    base_filename, _ = os.path.splitext(args.filename)
    target_filename = base_filename + '.' + args.target_lang + '.srt'
    subs = load_srt(args.filename)
    log('Translating...')
    translated_subs = translate_subs(subs, args.source_lang, args.target_lang)
    log('Writing subs...')
    write_srt(target_filename, translated_subs)
    log(target_filename)

if __name__ == '__main__':
    main()
