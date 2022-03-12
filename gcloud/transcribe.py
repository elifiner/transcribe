#!/usr/bin/env python3

import os
import re
import sys
import srt
import time
import argparse
from tqdm.std import tqdm
from dotenv import load_dotenv
from google.cloud import storage
from google.cloud import speech_v1 as speech
from google.cloud import translate
from google.api_core import operations_v1 as operations

KEY_FILE = 'key.json'
BUCKET_NAME = 'transcribe-audio-upload'
MAX_CHARS = 40

storage.blob._DEFAULT_CHUNKSIZE = 2097152 # 1024 * 1024 = 1 MB
storage.blob._MAX_MULTIPART_SIZE = 2097152 # 1 MB

load_dotenv()

def log(s='', newline=True):
    sys.stderr.write(s + ('\n' if newline else ''))
    sys.stderr.flush()

def upload_to_bucket(blob_name, path_to_file, bucket_name):
    storage_client = storage.Client.from_service_account_json(KEY_FILE)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name, chunk_size=256*1024)
    with open(path_to_file, 'rb') as in_file:
        total_bytes = os.fstat(in_file.fileno()).st_size
        with tqdm.wrapattr(in_file, 'read', total=total_bytes, miniters=1, desc=blob_name) as file_obj:
            blob.upload_from_file(
                file_obj,
                size=total_bytes,
            )
    return blob.public_url


def transcribe(gc_url, language):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gc_url)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        language_code=language,
        enable_automatic_punctuation=True,
        enable_word_time_offsets=True,
        audio_channel_count=2,
    )
    operation = client.long_running_recognize(config=config, audio=audio)
    while not operation.done():
        log('.', False)
        time.sleep(1)
    log()
    response = operation.result()
    subs = []
    for result in response.results:
        subs = break_sentences(subs, result.alternatives[0])
    return subs

def break_sentences(subs, alternative):
    firstword = True
    charcount = 0
    idx = len(subs) + 1
    content = ''
    for w in alternative.words:
        if firstword:
            # first word in sentence, record start time
            start = w.start_time

        charcount += len(w.word)
        content += ' ' + w.word.strip()

        if ('.' in w.word or '!' in w.word or '?' in w.word or
                charcount > MAX_CHARS or
                (',' in w.word and not firstword)):
            # break sentence at: . ! ? or line length exceeded
            # also break if , and not first word
            subs.append(srt.Subtitle(index=idx,
                                     start=start,
                                     end=w.end_time,
                                     content=srt.make_legal_content(content)))
            firstword = True
            idx += 1
            content = ''
            charcount = 0
        else:
            firstword = False
    return subs

def write_srt(out_file, subs):
    srt_file = out_file
    f = open(srt_file, 'w')
    f.writelines(srt.compose(subs))
    f.close()
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='filename', nargs='?', metavar='FILE', help='transcribe an audio file')
    parser.add_argument('--language', '-l', dest='source_lang', default='en-US', metavar='LANG', help='source language (e.g. ru-RU)')
    args = parser.parse_args()
    if (not args.filename):
        parser.print_help()
        sys.exit(1)

    base_filename, _ = os.path.splitext(args.filename)
    audio_filename = base_filename + '.flac'
    log('Extracing audio...')
    os.system('ffmpeg -y -i "{}" -vn -acodec copy "{}"'.format(args.filename, base_filename + '.aac'))
    os.system('ffmpeg -y -i "{}" -sample_fmt s16 -ar 8000 "{}"'.format(base_filename + '.aac', audio_filename))
    os.unlink(base_filename + '.aac')
    log('Uploading...')
    upload_to_bucket(audio_filename, audio_filename, BUCKET_NAME)
    os.unlink(audio_filename)
    log('Transcribing...')
    subs = transcribe('gs://{}/{}'.format(BUCKET_NAME, audio_filename), args.source_lang)
    # log('Translating...')
    # translated_subs = translate_subs(subs, args.source_lang, args.target_lang)
    # log('Writing subs...')
    write_srt(base_filename + '.srt', subs)
    log(base_filename + '.srt')

if __name__ == '__main__':
    main()
