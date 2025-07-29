import os, dotenv
from infra.discord_client import DiscordBot

dotenv.load_dotenv()              # carrega .env
TOKEN = "INSIRA O TOKEN AQUI"

bot = DiscordBot()
bot.run(TOKEN)
