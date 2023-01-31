import os
import sys
import json
import argparse
import mimetypes
from deepgram import Deepgram

import dotenv
dotenv.load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
CHUNK_LENGTH = 60

def main():
    # parse arguments with argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='audio file')
    args = parser.parse_args()
    mimetype = mimetypes.guess_type(args.filename)[0]

    dg_client = Deepgram(DEEPGRAM_API_KEY)

    with open(args.filename, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': mimetype}
        options = { 'language': 'ru' }
        response = dg_client.transcription.sync_prerecorded(source, options)
        print(response['results']['channels'][0]['alternatives'][0]['transcript'])

try:
    main()
except KeyboardInterrupt:
    pass
