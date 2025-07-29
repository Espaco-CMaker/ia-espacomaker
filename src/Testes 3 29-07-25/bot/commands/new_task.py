# bot/commands/new_task.py
import discord, datetime, asyncio
from core.dto import NewTaskDTO
from services.task_service import TaskService
from utils.slugs import slugify
from bson import ObjectId

task_service = TaskService()

# ──────────────────────────────────────────────────────────────
# VIEW de confirmação
# ──────────────────────────────────────────────────────────────
class ConfirmTaskView(discord.ui.View):
    def __init__(self, autor_id: int, projeto_id: str, dto: NewTaskDTO):
        super().__init__(timeout=120)
        self.autor_id    = autor_id
        self.projeto_id  = projeto_id
        self.dto         = dto
        self.msg_preview = None

    # CONFIRMAR ------------------------------------------------
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success)
    async def confirmar(self, itx: discord.Interaction, _):
        if itx.user.id != self.autor_id:
            await itx.response.send_message(
                "Apenas quem criou a tarefa pode confirmar.", ephemeral=True
            )
            return

        await itx.response.defer(ephemeral=True, thinking=True)

        # 1) grava no Mongo
        task_id = await task_service.add_task(self.projeto_id, self.dto)

        # 2) envia mensagem no canal do projeto
        #    (procura pelo slug do nome salvo no banco)
        proj_doc = await task_service.db.db[task_service.COL].find_one(
            {"_id": ObjectId(self.projeto_id)}, {"name": 1}
        )
        channel = discord.utils.get(
            itx.guild.text_channels, name=slugify(proj_doc["name"])
        )
        if channel:
            embed = (
                discord.Embed(
                    title=f"📝 Nova tarefa: {self.dto.titulo}",
                    description=self.dto.descricao,
                    color=0x2ECC71
                )
                .add_field(name="Prazo", value=self.dto.prazo.strftime("%d/%m/%Y"))
                .add_field(name="Prioridade", value=self.dto.prioridade)
                .set_footer(text=f"ID tarefa: {task_id}")
            )
            await channel.send(embed=embed)

        # 3) atualiza pré‑visualização
        await self.msg_preview.edit(
            content="✅ Tarefa registrada!",
            embed=None,
            view=None
        )
        self.stop()

    # CANCELAR -------------------------------------------------
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancelar(self, itx: discord.Interaction, _):
        if itx.user.id != self.autor_id:
            await itx.response.send_message(
                "Apenas quem criou a tarefa pode cancelar.", ephemeral=True
            )
            return
        await itx.response.send_message("🚫 Operação cancelada.", ephemeral=True)
        await self.msg_preview.edit(content="Operação cancelada.", embed=None, view=None)
        self.stop()


# ──────────────────────────────────────────────────────────────
# Slash‑command /nova_tarefa
# ──────────────────────────────────────────────────────────────
class NewTaskCommand:
    def __init__(self, tree: discord.app_commands.CommandTree):
        self.register(tree)

    def register(self, tree):
        @tree.command(
            name="nova_tarefa",
            description="Adiciona uma tarefa a um projeto, com confirmação"
        )
        @discord.app_commands.describe(
            projeto_id="ID do projeto (MongoDB)",
            titulo="Título da tarefa",
            descricao="Descrição detalhada",
            prazo="Prazo no formato YYYY-MM-DD",
            prioridade="Baixa, Média ou Alta"
        )
        async def handler(
            inter: discord.Interaction,
            projeto_id: str,
            titulo: str,
            descricao: str,
            prazo: str,
            prioridade: str = "Média"
        ):
            await inter.response.defer(ephemeral=True)

            # —— valida entrada —— #
            try:
                prazo_dt = datetime.datetime.fromisoformat(prazo)
                dto = NewTaskDTO(
                    titulo=titulo,
                    descricao=descricao,
                    prazo=prazo_dt,
                    prioridade=prioridade.capitalize()
                )
            except Exception as e:
                await inter.followup.send(f"Erro nos dados: {e}", ephemeral=True)
                return

            # —— pré‑visualização —— #
            embed = (
                discord.Embed(
                    title="Pré-visualização da Tarefa",
                    description=dto.descricao,
                    color=0x3498DB
                )
                .add_field(name="Título", value=dto.titulo, inline=False)
                .add_field(name="Prazo", value=prazo_dt.strftime("%d/%m/%Y"))
                .add_field(name="Prioridade", value=dto.prioridade)
            )

            view = ConfirmTaskView(inter.user.id, projeto_id, dto)
            msg  = await inter.followup.send(embed=embed, view=view, ephemeral=True)
            view.msg_preview = msg
