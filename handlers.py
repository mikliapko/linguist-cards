import logging
from dataclasses import dataclass
from functools import cached_property

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
            return (f"{self.explanation}\n\n"
                    f"Ex: _{self.example}_\n\n"
                    f"[{self.transcription}]\n\n"
                    f"Syn: {self.synonym}\n\n"
                    f"{self.translation}")
        else:
            return (f"{self.explanation}\n\n"
                    f"Ex: _{self.example}_\n\n"
                    f"Syn: {self.synonym}\n\n"
                    f"{self.translation}")

    def display_for_bot(self):
        if self.language == ENGLISH:
            return (f"{self.explanation}\n\n"
                    f"Ex: {self.example}\n\n"
                    f"[{self.transcription}]\n\n"
                    f"Syn: {self.synonym}\n\n"
                    f"{self.translation}")
        else:
            return (f"{self.explanation}\n\n"
                    f"Ex: {self.example}\n\n"
                    f"Syn: {self.synonym}\n\n"
                    f"{self.translation}")


class TranslationProcessor:
    def __init__(self, message, language, database):
        self.message = message
        self.language = language
        self.database = database
        self.searched_before = self.is_searched_before()
        self.added_to_mochi = self.is_added_to_mochi()

    @cached_property
    def user_id(self):
        return self.message.from_user.id

    @cached_property
    def word(self):
        _user_message = self.message.text
        return _user_message[0].lower() + _user_message[1:]

    def is_searched_before(self) -> bool:
        rows = self.database.select_by_word(self.word)
        if rows and rows[0]["user_id"] == self.user_id:
            return True
        return False

    def is_added_to_mochi(self) -> bool:
        rows = self.database.select_by_word(self.word)
        if rows and rows[0]["is_added"] == 1:
            return True
        return False

    def ask_and_translate(self) -> TranslationData:
        logger.info(f"Ask ChatGPT for translation of '{self.word}'")
        chatgpt = ChatGPTApiHelper(
            base_url=config.CHATGPT_URL,
            token=config.CHATGPT_TOKEN,
            language=self.language,
            check_validity=CHECK_INPUT_VALIDITY,
        )
        reply = chatgpt.ask_for_translation(self.word)
        logger.info(f"Translation:\n{reply}")

        self.database.insert_translation(word=self.word, user_id=self.user_id)

        _fields = [i.split(":")[-1].strip() for i in reply.split("\n")]
        explanation, example, translation, transcription, synonym = _fields
        return TranslationData(
            word=self.word,
            language=self.language,
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
