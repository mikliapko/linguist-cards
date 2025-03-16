import os


MOCHI_URL = os.getenv("MOCHI_URL", "https://app.mochi.cards")
MOCHI_TOKEN = os.getenv("MOCHI_TOKEN", None)

CHATGPT_URL = os.getenv("CHATGPT_URL", "https://api.openai.com")
CHATGPT_TOKEN = os.getenv("CHATGPT_TOKEN", None)
CHATGPT_MODEL = os.getenv("CHATGPT_MODEL", "gpt-4o-mini")
CHATGPT_MAX_TOKEN = 100

ENGLISH = "english"
POLISH = "polish"

TELEGRAM_BOT_TOKEN_MAP = {
    ENGLISH: {
        "deck_name": "[EN] all-in-one",
        "token": os.getenv("TELEGRAM_BOT_TOKEN_ENGLISH", None),
    },
    POLISH: {
        "deck_name": "[PL] iTalki",
        "token": os.getenv("TELEGRAM_BOT_TOKEN_POLISH", None),
    },
}

CHECK_INPUT_VALIDITY = True
