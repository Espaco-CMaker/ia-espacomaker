import discord
from services.project_service import ProjectService
from utils.slugs import slugify

project_service = ProjectService()

class DeleteProjectCommand:
    def __init__(self, tree: discord.app_commands.CommandTree):
        self.register(tree)

    def register(self, tree):
        @tree.command(name="excluir_projeto",
                      description="Apaga projeto e canal associado")
        async def handler(inter: discord.Interaction, projeto_id: str):
            if not inter.user.guild_permissions.manage_channels:
                await inter.response.send_message("Sem permissão.", ephemeral=True); return
            await inter.response.defer(ephemeral=True)

            proj = await project_service.delete_project(projeto_id)
            if not proj:
                await inter.followup.send("Projeto não encontrado.", ephemeral=True); return

            ch = discord.utils.get(inter.guild.text_channels, name=slugify(proj["name"]))
            if ch:
                await ch.delete(reason="Projeto excluído")
            await inter.followup.send("Projeto removido.", ephemeral=True)

            await inter.edit_original_response(
            content=f"🗑️ Projeto **{proj['name']}** e canal associados foram excluídos."
            )
