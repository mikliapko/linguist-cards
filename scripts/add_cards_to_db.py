# The script updates translations.db with some cards.
# Originally, it was designed to add cards that have been added to Mochi before making db file consistent.
# Might be reworked or reused for other purposes.

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import config
from lib.mochi.api import MochiApiHelper
from sqlite import TranslationDbHandler


def main():
    mochi_api = MochiApiHelper(
        base_url=config.MOCHI_URL,
        token=config.MOCHI_TOKEN,
    )
    # Get all cards in desired deck
    deck_id = mochi_api.get_deck_id_by_name(config.TELEGRAM_BOT_TOKEN_MAP["english"]["deck_name"])
    cards = mochi_api.get_cards_in_deck(deck_id=deck_id)
    cards_by_date = {card["name"]: card["created-at"]["date"] for card in cards}
    print(f"Words to handle - {len(cards_by_date)}")

    # Add cards to the database
    table_name = "english"
    db = TranslationDbHandler("../db/translations.db", table_name)
    for word, date in cards_by_date.items():
        existing_word = db.select_by_word(word)
        if existing_word:
            print(f"Word '{word}' already exists in the database.")
            continue

        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            f"INSERT INTO {table_name} (word, is_added, date, user_id) VALUES (?, ?, ?, ?)",
            (word, 1, date, 1)
        )


if __name__ == "__main__":
    main()
