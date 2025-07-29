"""
bot_discord_projetos.py
─────────────────────────────────────────────────────────────────────────
Bot Discord que:

1. Recebe descrição livre do usuário via comando /novo_projeto.
2. Usa LLM (função pergunta_ia) para estruturar JSON com nome, descrição
   e participantes do projeto.
3. Mostra pré-visualização (embed + botões Confirmar / Cancelar).
4. Ao confirmar:
   • grava documento no MongoDB (coleção 'projetos')
   • cria canal de texto no servidor com slug do nome
   • publica mensagem inicial no canal
─────────────────────────────────────────────────────────────────────────
Dependências:
  pip install discord.py pymongo python-dotenv
─────────────────────────────────────────────────────────────────────────
Variáveis de ambiente:
  DISCORD_BOT_TOKEN   → token do bot
  MONGO_URI           → ex.: mongodb://localhost:27017/
  MONGO_DBNAME        → ex.: iamaker
"""
import textwrap
import os, json, asyncio, re
from datetime import datetime
from functions import pergunta_ia
import discord
from discord import app_commands
from pymongo import MongoClient
from bson import ObjectId

# ────────────────────────────────────────────────────────────────────────
# 0. Configurações / helpers MongoDB
# ────────────────────────────────────────────────────────────────────────
MONGO_URI    = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "Projeto")
client_mongo = MongoClient(MONGO_URI)
db           = client_mongo[MONGO_DBNAME]

def extrair_primeiro_json(texto: str) -> dict:
    """
    Procura o primeiro {...} bem‑formado em 'texto' e devolve como dict.
    Lança ValueError se não encontrar ou JSON inválido.
    """
    # captura do 1º { até o correspondente }
    match = re.search(r"\{.*?\}", texto, flags=re.S)
    if not match:
        raise ValueError("Nenhum bloco JSON encontrado.")
    return json.loads(match.group(0))

def add_projeto(db, *, nome, descricao, status,
                projetistas, relatorios):
    """Insere e devolve _id do projeto."""
    doc = {
        "nome"        : nome,
        "descricao"   : descricao,
        "dt_criacao"  : datetime.utcnow(),
        "status"      : status,
        "projetistas" : projetistas,
        "tarefas"     : [],
        "relatorios"  : relatorios
    }
    return db.projetos.insert_one(doc).inserted_id

# ────────────────────────────────────────────────────────────────────────
# 2. Utils
# ────────────────────────────────────────────────────────────────────────
def slugify(text: str) -> str:
    """Gera slug minúsculo (a-z, 0-9, -) máx. 90 chars."""
    text = (
        text.strip()
            .lower()
            .encode("ascii", "ignore")
            .decode()
    )
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    return text[:90] or "projeto-sem-nome"


# ────────────────────────────────────────────────────────────────────────
# 3. Discord bot
# ────────────────────────────────────────────────────────────────────────
class BotProjetos(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot iniciado como {self.user}")

bot = BotProjetos()


# ────────────────────────────────────────────────────────────────────────
# 4. Comandos simples
# ────────────────────────────────────────────────────────────────────────
@bot.tree.command(name="olá_mundo", description="Diga olá")
async def ola_mundo(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Olá {interaction.user.mention}, tudo bem?"
    )

@bot.tree.command(name="eimaker", description="Repete a mensagem com IA")
async def eimaker(interaction: discord.Interaction, mensagem: str):
    await interaction.response.defer(thinking=True)
    resposta = pergunta_ia(mensagem)
    await interaction.followup.send(resposta[:2000])


# ────────────────────────────────────────────────────────────────────────
# 5. VIEW: botões Confirmar / Cancelar
# ────────────────────────────────────────────────────────────────────────
class ConfirmProjetoView(discord.ui.View):
    def __init__(self, autor: discord.Member, dados: dict):
        super().__init__(timeout=120)
        self.autor_id   = autor.id
        self.dados      = dados
        self.result_msg = None   # refer. da pré‑visualização para editar

    # ---------- CONFIRMAR ----------
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success)
    async def confirmar(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message(
                "Apenas o solicitante pode confirmar.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True, ephemeral=True)

        # 1) grava no Mongo
        autor_proj = {
            "discord_id": self.autor_id,
            "nome"      : interaction.user.display_name,
            "cargo"     : "membroMaker"
        }
        outros = [
            {"discord_id": None, "nome": n, "cargo": "membroMaker"}
            for n in self.dados["alunos"]
            if n.lower() != autor_proj["nome"].lower()
        ]
        projeto_id = add_projeto(
            db,
            nome        = self.dados["nomeProjeto"],
            descricao   = self.dados["descricao"],
            status      = "Em andamento",
            projetistas = [autor_proj, *outros],
            relatorios  = [{
                "dt_geracao": datetime.utcnow(),
                "conteudo"  : "Projeto criado via /novo_projeto"
            }]
        )

        # 2) localiza (ou cria) a categoria "PROJETOS CMAKER"
        cat_nome = "PROJETOS CMAKER 🧩🧩"
        categoria = discord.utils.get(interaction.guild.categories, name=cat_nome)

        if categoria is None:
            categoria = await interaction.guild.create_category_channel(
                name=cat_nome,
                reason="Categoria de projetos automática"
            )

        # 2.1) cria o canal dentro da categoria
        canal = await interaction.guild.create_text_channel(
            name     = slugify(self.dados["nomeProjeto"]),
            category = categoria,
            reason   = f"Novo projeto: {self.dados['nomeProjeto']}"
        )

        # 2.2) constrói mensagem inicial em embed
        participantes_txt = ", ".join([p["nome"] for p in [autor_proj, *outros]]) or "-"
        embed = (
            discord.Embed(
                title      = f"🚀 Projeto: {self.dados['nomeProjeto']}",
                description= self.dados["descricao"],
                color      = 0x00B3FF
            )
            .add_field(name="Participantes", value=participantes_txt, inline=False)
            .set_footer(text=f"ID MongoDB: {projeto_id}")
        )

        # 2.3) envia embed (tratando falha de permissão)
        try:
            await canal.send(embed=embed)
        except discord.Forbidden:
            # caso o bot não tenha permissão no canal recém‑criado
            await interaction.followup.send(
                "Projeto criado, mas não consegui enviar mensagem no canal "
                "(verifique permissões de **Send Messages** para o bot).",
                ephemeral=True
            )


        # 3) edita mensagem inicial
        await self.result_msg.edit(
            content=(
                f"✅ Projeto **{self.dados['nomeProjeto']}** criado!\n"
                f"📢 Canal: {canal.mention}\n"
                f"📄 ID: `{projeto_id}`"
            ),
            view=None
        )
        self.stop()

    # ---------- CANCELAR ----------
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message(
                "Apenas o solicitante pode cancelar.", ephemeral=True
            )
            return
        await interaction.response.send_message(
            "🚫 Operação cancelada.", ephemeral=True
        )
        await self.result_msg.edit(content="Operação cancelada.", view=None)
        self.stop()


# ────────────────────────────────────────────────────────────────────────
# 6. Comando /novo_projeto
# ────────────────────────────────────────────────────────────────────────
@bot.tree.command(
    name="novo_projeto",
    description="Cria um projeto via IA com pré-visualização"
)
@app_commands.describe(
    descricao="Explique o projeto e liste participantes"
)
async def novo_projeto(interaction: discord.Interaction, descricao: str):

    await interaction.response.defer(ephemeral=True)

    # 1) prompt p/ LLM
    autor = interaction.user.display_name

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

    loop   = asyncio.get_running_loop()
    ia_raw = await loop.run_in_executor(None, pergunta_ia, prompt)
    print(ia_raw)
    # 2) valida JSON
    try:
        dados = extrair_primeiro_json(ia_raw)
        print(dados)
    except Exception as e:
        await interaction.followup.send(
            f"❌ A IA não retornou JSON válido ({e}). Tente novamente.",
            ephemeral=True
        )
        return

    # 3) embed preview + botões
    embed = discord.Embed(
        title       = "Pré-visualização do Projeto",
        description = dados["descricao"],
        color       = 0x00B3FF
    )
    embed.add_field(name="Nome do Projeto",
                    value=dados["nomeProjeto"], inline=False)
    embed.add_field(name="Participantes",
                    value=", ".join(dados["alunos"]) or "-",
                    inline=False)

    view = ConfirmProjetoView(interaction.user, dados)
    msg  = await interaction.followup.send(embed=embed, view=view,
                                           ephemeral=True)
    view.result_msg = msg   # para poder editar depois

# ────────────────────────────────────────────────────────────────────────
# 6‑bis. Comando /excluir_projeto
# ────────────────────────────────────────────────────────────────────────
from bson import ObjectId

@bot.tree.command(
    name="excluir_projeto",
    description="Remove um projeto do MongoDB e apaga o canal correspondente"
)
@app_commands.describe(
    projeto_id="ID MongoDB fornecido na criação (24 dígitos)"
)
async def excluir_projeto(interaction: discord.Interaction, projeto_id: str):

    # permissão básica
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message(
            "❌ Você não tem permissão para excluir canais.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    # 1) tenta remover no Mongo
    try:
        _id = ObjectId(projeto_id)
    except Exception:
        await interaction.followup.send("❌ ID inválido.", ephemeral=True)
        return

    projeto = db.projetos.find_one_and_delete({"_id": _id})

    if not projeto:
        await interaction.followup.send("❌ Projeto não encontrado.", ephemeral=True)
        return

    # 2) tenta achar o canal pelo slug do nome
    nome_slug = slugify(projeto["nome"])
    canal = discord.utils.get(interaction.guild.text_channels, name=nome_slug)

    if canal:
        try:
            await canal.delete(reason=f"Projeto {projeto['nome']} excluído.")
        except discord.Forbidden:
            await interaction.followup.send(
                "Projeto removido do banco, mas não consegui excluir o canal "
                "(permissão faltando).", ephemeral=True
            )
            return

    await interaction.followup.send(
        f"🗑️ Projeto **{projeto['nome']}** e canal associados foram excluídos.",
        ephemeral=True
    )
# ────────────────────────────────────────────────────────────────────────
# 7. Inicia bot
# ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    TOKEN = "INSIRA O TOKEN"
    if not TOKEN:
        raise RuntimeError("Defina DISCORD_BOT_TOKEN no ambiente.")
    bot.run(TOKEN)
