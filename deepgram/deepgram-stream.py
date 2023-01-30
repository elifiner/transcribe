import os
import base64
import json
import websockets
import asyncio

import dotenv
dotenv.load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

def connect(key, language='en-US'):
    return websockets.connect(
        'wss://api.deepgram.com/v1/listen?language={}'.format(language),
        extra_headers = {
            'Authorization': 'Token {}'.format(key)
        }
    )

async def transcribe(key, language, data):
    async with connect(key, language) as ws:
        async def sender(ws):
            while True:
                audio = await data.get()
                if audio is None:
                    break
                await ws.send(audio)
            await ws.send(json.dumps({ 'type': 'CloseStream' }))
        async def receiver(ws):
            async for msg in ws:
                msg = json.loads(msg)
                transcript = ''
                if 'alternatives' in msg:
                    transcript = msg['alternatives'][0]['transcript']
                elif 'channel' in msg and msg['is_final']:
                    transcript = msg['channel']['alternatives'][0]['transcript']
                if transcript:
                    print(transcript)
        await asyncio.wait([
            asyncio.ensure_future(sender(ws)),
            asyncio.ensure_future(receiver(ws))
        ])

if __name__ == '__main__':
    outbox = asyncio.Queue()
    with open('sample-russian.mp3', 'rb') as f:
        while True:
            piece = f.read(4096)
            if piece == b'':
                break
            outbox.put_nowait(piece)
    outbox.put_nowait(None)
    asyncio.run(transcribe(DEEPGRAM_API_KEY, 'ru', outbox))
