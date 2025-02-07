# Bot configuration and constants
import os

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')  # Will be set from environment

# Colors (for formatted messages)
COLORS = {
    'PRIMARY': '#0088CC',    # Telegram blue
    'SECONDARY': '#26A69A',  # Teal
    'ACCENT': '#FFC107',     # Amber
    'BACKGROUND': '#FFFFFF', # White
    'TEXT': '#333333'        # Dark grey
}

# Game settings
WELCOME_BONUS = 1500
COIN_TO_TOKEN_RATIO = 100
DAILY_REWARD_MIN = 100
DAILY_REWARD_MAX = 500

# Message templates
WELCOME_MESSAGE = """
🌟 *Welcome to MetaVerse: The New Era* 🌟

You've received {bonus} Metarush Coins as a welcome bonus! 🎉
Start your journey in the MetaVerse now!

Commands:
/play - Start a game
/wallet - Check your balance
/daily - Claim daily reward
/leaderboard - View top players
/airdrop - Check available airdrops
"""

HELP_MESSAGE = """
🎮 *MetaVerse Bot Commands* 🎮

/start - Start the bot
/play - Play the game
/wallet - View your wallet
/daily - Claim daily reward
/leaderboard - View rankings
/airdrop - Check airdrops
/help - Show this help
"""