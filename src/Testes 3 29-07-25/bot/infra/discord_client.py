import discord
from discord import app_commands
from commands.new_project import NewProjectCommand
from commands.delete_project import DeleteProjectCommand
from commands.new_task import NewTaskCommand

class DiscordBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # registra comandos
        NewProjectCommand(self.tree)
        DeleteProjectCommand(self.tree)
        NewTaskCommand(self.tree)
        await self.tree.sync()

    async def on_ready(self):
        print(f"Conectado como {self.user}")
