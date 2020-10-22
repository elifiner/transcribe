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
    json = {
        'audio_url': ''.join([CDN_URL, 'upload/{}'.format(file_id)]),
        'speaker_labels': True
    }
    headers = {
        'authorization': config.ASSEMBLYAI_KEY,
        'content-type': 'application/json'
    }
    response = requests.post(endpoint, json=json, headers=headers)
    response = response.json()
    if 'id' not in response:
        raise Exception(response)
    return response['id']

def get_transcription_endpoint(transcription_id):
    return ''.join([API_URL, 'transcript/{}'.format(transcription_id)])

def get_transcription(transcription_id):
    endpoint = get_transcription_endpoint(transcription_id)
    headers = {'authorization': config.ASSEMBLYAI_KEY}
    response = requests.get(endpoint, headers=headers)
    return response.json()

def get_transcription_srt(transcription_id):
    endpoint = get_transcription_endpoint(transcription_id) + '/srt'
    headers = {'authorization': config.ASSEMBLYAI_KEY}
    response = requests.get(endpoint, headers=headers)
    return response.text

def get_transcription_curl(transcription_id, format = None):
    url = get_transcription_endpoint(transcription_id)
    if format == 'text':
        url = url + '/srt'
        return "curl {} --header 'authorization: {}'| awk '(NR+1) % 4 == 0'".format(url, config.ASSEMBLYAI_KEY)
    elif format == 'srt':
        url = url + '/srt'
        return "curl {} --header 'authorization: {}'".format(url, config.ASSEMBLYAI_KEY)

def get_speakers(transcription_id):
    data = get_transcription(transcription_id)
    return '\n'.join('Speaker {speaker}: {text}'.format(**utterance) for utterance in data['utterances'])

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--transcribe', '-t', dest='transcribe', metavar='FILE', help='transcribe an mp3')
    group.add_argument('--show', '-s', dest='show', metavar='ID', help='show transcription')
    parser.add_argument('--text', dest='format', action='store_const', const='text', help='text tanscription format')
    parser.add_argument('--srt', dest='format', action='store_const', const='srt', help='SRT tanscription format')
    args = parser.parse_args()

    if args.transcribe:
        log('Uploading...')
        file_id = upload_file_to_api(args.transcribe)
        log('Starting transcription...')
        transcription_id = initiate_transcription(file_id)
        print('transcribe --show {}'.format(transcription_id))
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
            print('transcribe --show {}'.format(transcription_id))
        else:
            print(response)
    elif args.show:
        if args.format == 'srt':
            print(get_transcription_srt(args.show))
        else:
            print(get_speakers(args.show))

if __name__ == '__main__':
    main()
