import os, dotenv
from infra.discord_client import DiscordBot

dotenv.load_dotenv()              # carrega .env
TOKEN = "<Insert Token>"

bot = DiscordBot()
bot.run(TOKEN)
