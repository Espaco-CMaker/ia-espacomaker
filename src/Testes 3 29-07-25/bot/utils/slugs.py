import re, discord
def slugify(t: str) -> str:
    return re.sub(r"[^a-z0-9-]", "",
                  re.sub(r"\s+", "-", t.lower()))[:90] or "sem-nome"

async def ensure_category(guild: discord.Guild, nome: str):
    cat = discord.utils.get(guild.categories, name=nome)
    return cat or await guild.create_category_channel(nome)
