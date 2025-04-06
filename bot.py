import argparse
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from config import TELEGRAM_BOT_TOKEN_MAP
from handlers import ask_and_translate, add_to_mochi
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
        self.translation_data = None

    async def start(self, update: Update, context) -> None:
        """Sends a welcome message when the /start command is issued."""
        await update.message.reply_text('Hello! Send me a message, and I will process and reply!')

    async def handle_message(self, update: Update, context) -> None:
        """Process and respond to a user message."""
        user_message = update.message.text  # Get the message text
        user_message = user_message[0].lower() + user_message[1:]  # Uncapitalize the first letter
        user_id = update.message.from_user.id  # Get the user ID
        logger.info(f"Received message: {user_message}")

        try:
            reply = ask_and_translate(user_message, self.language)
            self.database.insert_translation(word=user_message, user_id=user_id)
            self.translation_data = reply
            await update.message.reply_text(reply.display_for_bot())
        except ValueError:
            reply = "The word or phrase is incorrect ❌"
            await update.message.reply_text(reply)
            return

        # Ask for confirmation after message processing
        keyboard = [
            [InlineKeyboardButton("Yes 👍", callback_data='yes')],
            [InlineKeyboardButton("No 👎", callback_data='no')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Add to Mochi cards?", reply_markup=reply_markup)

    async def confirmation_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handles the user's confirmation response."""
        query = update.callback_query
        await query.answer()
        if query.data == "yes":
            add_to_mochi(self.translation_data, self.deck_name)
            self.database.update_is_added_status(is_added=True)
            await query.edit_message_text("ADDED ✅")
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

    database = TranslationDbHandler("translations.db", args.language)
    database.init_table()

    bot = TelegramBot(
        token=TELEGRAM_BOT_TOKEN_MAP[args.language]["token"],
        language=args.language,
        deck_name=TELEGRAM_BOT_TOKEN_MAP[args.language]["deck_name"],
        database=database,
    )
    bot.main()
