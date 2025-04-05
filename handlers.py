import logging
from dataclasses import dataclass

import config
from config import CHECK_INPUT_VALIDITY, ENGLISH
from lib.chatgpt.api import ChatGPTApiHelper
from lib.mochi.api import MochiApiHelper

logger = logging.getLogger(__name__)


@dataclass()
class TranslationData:
    word: str
    language: str
    explanation: str
    example: str
    translation: str
    transcription: str
    synonym: str

    def display_for_mochi(self):
        if self.language == ENGLISH:
            return f"{self.explanation}\n\nEx: _{self.example}_\n\n[{self.transcription}]\n\nSyn: {self.synonym}\n\n{self.translation}"
        else:
            return f"{self.explanation}\n\nEx: _{self.example}_\n\nSyn: {self.synonym}\n\n{self.translation}"

    def display_for_bot(self):
        if self.language == ENGLISH:
            return f"{self.explanation}\n\nEx: {self.example}\n\n[{self.transcription}]\n\nSyn: {self.synonym}\n\n{self.translation}"
        else:
            return f"{self.explanation}\n\nEx: {self.example}\n\nSyn: {self.synonym}\n\n{self.translation}"


def ask_and_translate(word: str, language: str) -> TranslationData:
    logger.info(f"Ask ChatGPT for translation of '{word}'")
    chatgpt = ChatGPTApiHelper(
        base_url=config.CHATGPT_URL,
        token=config.CHATGPT_TOKEN,
        language=language,
        check_validity=CHECK_INPUT_VALIDITY,
    )
    reply = chatgpt.ask_for_translation(word)
    logger.info(f"Translation:\n{reply}")

    explanation, example, translation, transcription, synonym = (i.split(":")[-1].strip() for i in reply.split("\n"))
    return TranslationData(
        word=word,
        language=language,
        explanation=explanation,
        example=example,
        translation=translation,
        transcription=transcription,
        synonym=synonym,
    )


def add_to_mochi(translation: TranslationData, deck_name: str) -> None:
    front_card = f"**{translation.word}**"
    back_card = translation.display_for_mochi()

    logging.info("Create the card in Mochi")
    mochi = MochiApiHelper(
        base_url=config.MOCHI_URL,
        token=config.MOCHI_TOKEN,
    )
    deck_id = mochi.get_deck_id_by_name(deck_name)
    mochi.create_base_card(deck_id=deck_id, name=front_card, value=back_card)
