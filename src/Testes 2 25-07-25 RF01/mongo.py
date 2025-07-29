"""
Funções utilitárias para gerenciar Projetos, Projetistas, Relatórios e Tarefas no MongoDB.
"""

from datetime import datetime
from typing import List, Dict
from pymongo import MongoClient
from bson import ObjectId

# ────────────────────────────────────────────────────────────────────────────────
# 1. Conexão básica
# ────────────────────────────────────────────────────────────────────────────────

def get_db(uri: str = "mongodb://localhost:27017/", db_name: str = "iamaker"):
    """Abre uma conexão e devolve o handle do database."""
    client = MongoClient(uri)
    return client[db_name]

# ────────────────────────────────────────────────────────────────────────────────
# 2. CRUD de Projeto (inclui projetistas e relatórios na criação)
# ────────────────────────────────────────────────────────────────────────────────

def add_projeto(db, nome: str, descricao: str, status: str = "Em andamento", projetistas: List[Dict] | None = None, relatorios: List[Dict] | None = None,) -> ObjectId:
    """
    Cria um novo projeto e já embute projetistas e relatórios.
    - projetistas: lista com dicts {"discord_id": int, "nome": str, "cargo": str}
    - relatorios : lista com dicts {"dt_geracao": datetime, "conteudo": str}
    Retorna o _id do projeto criado.
    """
    doc = {
        "nome": nome,
        "descricao": descricao,
        "dt_criacao": datetime.utcnow(),
        "status": status,
        "projetistas": projetistas or [],
        "tarefas": [],                 # inicia vazio; preenchido por add_tarefa()
        "relatorios": relatorios or []
    }
    result = db.projetos.insert_one(doc)
    return result.inserted_id

# ────────────────────────────────────────────────────────────────────────────────
# 3. CRUD de Tarefas (operam no array "tarefas" do documento Projeto)
# ────────────────────────────────────────────────────────────────────────────────

def add_tarefa(db, projeto_id: str | ObjectId, titulo: str, descricao: str, prazo: datetime, prioridade: str = "Média", status: str = "Pendente",) -> dict:
    """
    Adiciona uma nova tarefa ao array tarefas de um Projeto.
    Retorna o subdocumento da tarefa que foi inserido.
    """
    tarefa = {
        "_id": ObjectId(),   # gera id próprio para facilitar updates futuros
        "titulo": titulo,
        "descricao": descricao,
        "prazo": prazo,
        "prioridade": prioridade,
        "status": status
    }
    db.projetos.update_one(
        {"_id": ObjectId(projeto_id)},
        {"$push": {"tarefas": tarefa}}
    )
    return tarefa

# ────────────────────────────────────────────────────────────────────────────────
# 4. Exemplos de uso (rodam só se o arquivo for executado diretamente)
# ────────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db = get_db()

    # 4.1 Criar projeto com um projetista e um relatório inicial
    proj_id = add_projeto(
        db,
        nome="IA Maker",
        descricao="Sistema de apoio para projetos de engenharia com IA",
        projetistas=[{
            "discord_id": 123456789,
            "nome": "Vinicius",
            "cargo": "moderador"
        }],
        relatorios=[{
            "dt_geracao": datetime.utcnow(),
            "conteudo": "Kick‑off do projeto registrado."
        }]
    )
    print("Projeto criado:", proj_id)

    # 4.2 Adicionar uma tarefa
    tarefa_doc = add_tarefa(
        db,
        projeto_id=proj_id,
        titulo="Definir arquitetura",
        descricao="Escolher entre MongoDB ou SQL",
        prazo=datetime(2025, 8, 1),
        prioridade="Alta"
    )
    print("Tarefa criada:", tarefa_doc)
