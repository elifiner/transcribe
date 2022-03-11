import os
from google.cloud import translate


# Initialize Translation client
def translate_text(text="YOUR_TEXT_TO_TRANSLATE", project_id="YOUR_PROJECT_ID"):
    """Translating Text."""

    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    # Translate text from English to French
    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "source_language_code": "ru-RU",
            "target_language_code": "en-US",
        }
    )

    # Display the translation for each input text provided
    for translation in response.translations:
        print("Translated text: {}".format(translation.translated_text))



s = '''
Ну просто я реально когда может быть не надо было со мной так поступить Да вот именно Господу чтобы я наконец прозрел что-ли и попытался донести до тех людей которые находятся сейчас на нашей территории России который ещё может быть до конца не врубается Что здесь происходит Извините за простое слово но здесь реально ребята которые будут смотреть вот это вот Интернет видео там да думайте обо мне что хотите вот как что меня там заставили Написали мне текст неважно я вот скажу как есть Да если бы он на моей территории кто-то бы пришёл Я бы поступил точно так же вот как эти люди сейчас и был бы прав и сейчас они правы А я сижу здесь Я радуюсь я оправдываюсь я не понимаю За что мне очень стыдно за это потому что у меня дед воевал А я сейчас получаюсь в роли каратели
'''
translate_text(s, os.environ['PROJECT_ID'])