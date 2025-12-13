import argparse
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN_MAP
from handlers import TranslationProcessor, add_to_mochi
from sqlite import TranslationDbHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(description="A bot for language translation and cards creation")
    parser.add_argument("-l", dest="language", choices=("english", "polish"), help="Translate from")
    return parser.parse_args()


class TelegramBot:
    def __init__(self, token: str, language: str, deck_name: str, database: TranslationDbHandler):
        self.token = token
        self.language = language
        self.deck_name = deck_name
        self.database = database

        self.translation_processor = None

        self.user_message = None
        self.translation_data = None
        self.translation_message = None

    async def start(self, update: Update, context) -> None:
        """Sends a welcome message when the /start command is issued."""
        await update.message.reply_text('Hello! Send me a message, and I will process and reply!')

    async def _create_confirmation_keyboard(self) -> InlineKeyboardMarkup:
        """Creates the confirmation keyboard for adding to Mochi."""
        keyboard = [
            [InlineKeyboardButton("Yes 👍", callback_data='yes')],
            [InlineKeyboardButton("No 👎", callback_data='no')],
            [InlineKeyboardButton("Rerun 🔄", callback_data='rerun')],
        ]
        return InlineKeyboardMarkup(keyboard)

    async def _process_translation(self, update: Update) -> bool:
        """Process translation and update the message. Returns True if successful."""
        logger.info(f"Received message: {self.translation_processor.word}")

        try:
            self.translation_data = self.translation_processor.ask_and_translate()
            if self.translation_message:
                await self.translation_message.edit_text(self.translation_data.display_for_bot())
            else:
                self.translation_message = await update.message.reply_text(self.translation_data.display_for_bot())
            return True
        except ValueError:
            return False

    async def handle_message(self, update: Update, context) -> None:
        """Process and respond to a user message."""
        self.user_message = update.message
        self.translation_processor = TranslationProcessor(
            message=self.user_message,
            language=self.language,
            database=self.database
        )
        self.translation_message = None

        if not await self._process_translation(update):
            await update.message.reply_text("The word or phrase is incorrect ❌")
            return

        if self.translation_processor.searched_before:
            if self.translation_processor.added_to_mochi:
                await update.message.reply_text("Searched before and added to Mochi 🤪")
                return
            else:
                await update.message.reply_text("Searched before, but not added to Mochi 🧠")

        reply_markup = await self._create_confirmation_keyboard()
        await update.message.reply_text("Add to Mochi cards?", reply_markup=reply_markup)

    async def confirmation_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handles the user's confirmation response."""
        query = update.callback_query
        await query.answer()

        if query.data == "yes":
            add_to_mochi(self.translation_data, self.deck_name)
            self.database.update_is_added_status(is_added=True)
            await query.edit_message_text("ADDED ✅")
        elif query.data == "rerun":
            await query.edit_message_text("Re-running translation... ⏳")

            if not await self._process_translation(update):
                await query.edit_message_text("The word or phrase is incorrect ❌")
                return

            reply_markup = await self._create_confirmation_keyboard()
            await query.edit_message_text("Add to Mochi cards?", reply_markup=reply_markup)
        else:
            await query.edit_message_text("NOT ADDED ❌")

    # Define the main function to start the bot
    def main(self):
        """Start the bot."""
        application = ApplicationBuilder().token(self.token).build()

        # Register handlers
        application.add_handler(CommandHandler("start", self.start))  # Handle /start command
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        # Register the handler for the button click (callback query)
        application.add_handler(CallbackQueryHandler(self.confirmation_response))

        # Start the bot
        application.run_polling()


if __name__ == "__main__":
    args = parse_arguments()

    database = TranslationDbHandler("db/translations.db", args.language)
    database.init_table()

    bot = TelegramBot(
        token=TELEGRAM_BOT_TOKEN_MAP[args.language]["token"],
        language=args.language,
        deck_name=TELEGRAM_BOT_TOKEN_MAP[args.language]["deck_name"],
        database=database,
    )
    bot.main()
