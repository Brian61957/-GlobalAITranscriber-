from transformers import pipeline

translator = None


def load_translator():

    global translator

    if translator is None:

        print("Loading translation model...")

        translator = pipeline(
            "translation",
            model="facebook/nllb-200-distilled-600M"
        )


def translate_text(
        text,
        source_language="auto",
        target_language="eng_Latn"
):

    load_translator()

    try:

        result = translator(
            text,
            tgt_lang=target_language
        )

        return result[0]["translation_text"]

    except Exception as e:

        print("Translation error:", e)

        return text