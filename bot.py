import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from config import TOKEN
from handlers.commands import start_command, help_command, wallet_command, leaderboard_command
from handlers.game import play_command, handle_answer
from handlers.rewards import daily_command, airdrop_command

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting bot with provided token...")

    try:
        # Create updater
        updater = Updater(TOKEN)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # Add command handlers
        dp.add_handler(CommandHandler("start", start_command))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("wallet", wallet_command))
        dp.add_handler(CommandHandler("play", play_command))
        dp.add_handler(CommandHandler("daily", daily_command))
        dp.add_handler(CommandHandler("airdrop", airdrop_command))
        dp.add_handler(CommandHandler("leaderboard", leaderboard_command))

        # Add callback query handler
        dp.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))

        logger.info("All handlers registered successfully")

        # Start the bot
        updater.start_polling()
        logger.info("Bot started successfully!")

        # Run the bot until you press Ctrl-C
        updater.idle()

    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        raise

if __name__ == '__main__':
    main()