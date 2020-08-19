#!/usr/bin/env python3

import os
import sys
import time
import argparse
import requests

import config

API_URL = 'https://api.assemblyai.com/v2/'
CDN_URL = 'https://cdn.assemblyai.com/'

def log(s='', newline=True):
    sys.stderr.write(s + ('\n' if newline else ''))
    sys.stderr.flush()

def upload_file_to_api(filename):
    if not os.path.exists(filename):
        return None

    def read_file(filename, chunk_size=64*1024):
        with open(filename, 'rb') as _file:
            while True:
                log('.', False)
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data
        log()

    headers = {'authorization': config.ASSEMBLYAI_KEY}
    response = requests.post(''.join([API_URL, 'upload']), headers=headers, data=read_file(filename))
    response = response.json()
    if 'upload_url' not in response:
        raise Exception(response)
    return response['upload_url'].split('/')[-1]

def initiate_transcription(file_id):
    endpoint = ''.join([API_URL, 'transcript'])
    json = {'audio_url': ''.join([CDN_URL, 'upload/{}'.format(file_id)])}
    headers = {
        'authorization': config.ASSEMBLYAI_KEY,
        'content-type': 'application/json'
    }
    response = requests.post(endpoint, json=json, headers=headers)
    response = response.json()
    if 'id' not in response:
        raise Exception(response)
    return response['id']

def get_transcription(transcription_id):
    endpoint = ''.join([API_URL, 'transcript/{}'.format(transcription_id)])
    headers = {'authorization': config.ASSEMBLYAI_KEY}
    response = requests.get(endpoint, headers=headers)
    return response.json()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    log('Uploading...')
    file_id = upload_file_to_api(args.filename)
    log('Starting transcription...')
    transcription_id = initiate_transcription(file_id)
    status = None
    count = 1
    log('Waiting...')
    while status not in ['completed', 'error']:
        response = get_transcription(transcription_id)
        status = response['status']
        log('{} ({} sec)'.format(status, count))
        time.sleep(1)
        count += 1
    if status == 'completed':
        print(response)
        print(response['text'])
    else:
        print(response)

if __name__ == '__main__':
    main()
