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

    print('ffprobe -i "{}" -show_entries format=duration -v quiet -of csv="p=0"'.format(args.filename))
    file_length = os.popen('ffprobe -i "{}" -show_entries format=duration -v quiet -of csv="p=0"'.format(args.filename)).read()
    file_length = int(float(file_length))
    temp_filename = '.temp_audio' + os.path.splitext(args.filename)[1]

    # split file into 60 second chunks with ffmpeg
    for start_time in range(0, file_length, 60):
        end_time = start_time + 60
        os.system('ffmpeg -hide_banner -loglevel error -i "{}" -ss {} -to {} -c copy -y {}'.format(args.filename, start_time, end_time, temp_filename))

        with open(temp_filename, 'rb') as audio:
            sys.stderr.write('.')
            sys.stderr.flush()
            source = {'buffer': audio, 'mimetype': mimetype}
            options = { 'language': 'ru' }
            response = dg_client.transcription.sync_prerecorded(source, options)
            print(response['results']['channels'][0]['alternatives'][0]['transcript'])
            # print(json.dumps(response))

try:
    main()
except KeyboardInterrupt:
    pass
