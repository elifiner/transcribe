import os
from deepgram import Deepgram
import json
import dotenv
dotenv.load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

# Replace with your file path and audio mimetype
PATH_TO_FILE = 'sample-english.mp3'
MIMETYPE = 'audio/mpeg'

def main():
    # Initializes the Deepgram SDK
    dg_client = Deepgram(DEEPGRAM_API_KEY)

    with open(PATH_TO_FILE, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': MIMETYPE}
        options = { "punctuate": True, "model": "general", "language": "en-US", "tier": "enhanced" }

        print('Requesting transcript...')
        print('Your file may take up to a couple minutes to process.')
        print('While you wait, did you know that Deepgram accepts over 40 audio file formats? Even MP4s.')
        print('To learn more about customizing your transcripts check out developers.deepgram.com')

        response = dg_client.transcription.sync_prerecorded(source, options)
        print(json.dumps(response, indent=4))

main()
