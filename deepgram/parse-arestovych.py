import os
import re
import sys
import glob
import openai
import dotenv
dotenv.load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_ai_text(prompt):
    len_prompt = int(len(prompt)*1.2)
    if (len_prompt > 4096):
        return ''
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt,
        temperature=0.0,
        max_tokens=4096 - len_prompt,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response['choices'][0]['text'].strip()

def get_answer(question, text):
    prompt = '''
Here's a question:

{}

Here's text that contains the answer to the question:

{}

Answer the question in full.
'''.format(question, text)
    return generate_ai_text(prompt)

def translate(text):
    prompt = '''
Translate this text from Russian to English:

{}
'''.format(text)
    return generate_ai_text(prompt)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='transcription directory')
    args = parser.parse_args()

    for file in sorted(glob.glob(f'{args.directory}/*.txt')):
        question = file.split('.')[0].split('-')[-1].strip()
        sys.stderr.write(question + '\n')
        sys.stderr.flush()
        text = open(file).read()
        if not text.strip():
            continue
        print(translate(question))
        print()
        answer = get_answer(question, text)
        print(translate(answer))
        print('---')
        sys.stdout.flush()
