# bot/commands/new_project.py
import discord, textwrap, asyncio
from infra import llm
from core.dto import NewProjectDTO
from services.project_service import ProjectService
from utils.slugs import slugify, ensure_category
from utils.json_extractor import extract_first_json

project_service = ProjectService()

# ──────────────────────────────────────────────────────────────
# VIEW de confirmação
# ──────────────────────────────────────────────────────────────
class ConfirmProjectView(discord.ui.View):
    def __init__(self,
                 autor_id: int,
                 dto: NewProjectDTO,
                 raw_dto: dict):
        super().__init__(timeout=120)
        self.autor_id   = autor_id
        self.dto        = dto
        self.raw_dto    = raw_dto          # dict ainda não persistido
        self.msg_preview = None

    # CONFIRMAR ------------------------------------------------
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success)
    async def confirmar(self, itx: discord.Interaction, _):
        if itx.user.id != self.autor_id:
            await itx.response.send_message(
                "Apenas quem iniciou pode confirmar.", ephemeral=True
            )
            return

        await itx.response.defer(ephemeral=True, thinking=True)

        # 1) grava no Mongo
        project_id, proj_name = await project_service.create_project(
            self.dto, owner_id=self.autor_id
        )

        # 2) cria categoria + canal
        cat = await ensure_category(itx.guild, "PROJETOS CMAKER 🧩🧩")
        canal = await itx.guild.create_text_channel(slugify(proj_name),
                                                    category=cat,
                                                    reason=f"Novo projeto: {proj_name}")

        # 3) envia embed no canal
        embed = (
            discord.Embed(
                title=f"🚀 Projeto: {proj_name}",
                description=self.dto.descricao,
                color=0x00B3FF
            )
            .add_field(name="Participantes",
                       value=", ".join(self.dto.alunos) or "-",
                       inline=False)
            .set_footer(text=f"ID MongoDB: {project_id}")
        )
        await canal.send(embed=embed)

        # 4) edita pré‑visualização
        await self.msg_preview.edit(
            content=f"✅ Projeto criado em {canal.mention}",
            embed=None,
            view=None
        )
        # remove spinner editando a resposta da ação do botão
        await itx.edit_original_response(
            content=f"✅ Projeto criado em {canal.mention}",
            view=None
        )
        self.stop()

    # CANCELAR -------------------------------------------------
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancelar(self, itx: discord.Interaction, _):
        if itx.user.id != self.autor_id:
            await itx.response.send_message(
                "Apenas quem iniciou pode cancelar.", ephemeral=True
            )
            return
        await itx.response.send_message("🚫 Operação cancelada.", ephemeral=True)
        await self.msg_preview.edit(content="Operação cancelada.", embed=None, view=None)
        self.stop()


# ──────────────────────────────────────────────────────────────
# Slash‑command /novo_projeto
# ──────────────────────────────────────────────────────────────
class NewProjectCommand:
    def __init__(self, tree: discord.app_commands.CommandTree):
        self.register(tree)

    def register(self, tree):
        @tree.command(
            name="novo_projeto",
            description="Cria um projeto via IA (com confirmação)"
        )
        @discord.app_commands.describe(
            descricao="Explique o projeto e liste participantes"
        )
        async def handler(inter: discord.Interaction, descricao: str):
            await inter.response.defer(ephemeral=True)

            # -------- monta prompt --------
            autor = inter.user.display_name
            prompt = textwrap.dedent(f"""
            Você é uma função que gera JSON e NADA mais.
            Regras obrigatórias:
            1. Responda com EXATAMENTE um objeto JSON, sem texto antes ou depois.
            2. Todo conteúdo deve caber dentro desse objeto.
            3. A lista "alunos" deve conter SEMPRE o autor "{autor}" e, opcionalmente, outros nomes que o usuário citar. NÃO invente nomes.
            4. Complete a descrição com no mínimo 5 linhas, mantendo o sentido original mas complementando de maneira tecnica.

            Entrada do usuário:
            \"\"\"{descricao}\"\"\"

            Formato-alvo:
            {{
            "nomeProjeto": "...",
            "descricao": "...",
            "alunos": ["<nome1>", "<nome2>", ...]
            }}
            """).strip()

            # -------- chama LLM --------
            raw = await llm.generate(prompt)

            # -------- parse/valida --------
            try:
                payload = extract_first_json(raw)
                dto = NewProjectDTO.parse_obj(payload)
            except Exception as e:
                await inter.followup.send(f"JSON inválido: {e}", ephemeral=True)
                return

            # -------- pré‑visualização --------
            embed = (
                discord.Embed(
                    title="Pré-visualização do Projeto",
                    description=dto.descricao,
                    color=0x3498DB
                )
                .add_field(name="Nome", value=dto.nomeProjeto, inline=False)
                .add_field(name="Participantes",
                           value=", ".join(dto.alunos) or "-",
                           inline=False)
            )

            view = ConfirmProjectView(inter.user.id, dto, payload)
            msg  = await inter.followup.send(embed=embed,
                                             view=view,
                                             ephemeral=True)
            view.msg_preview = msg