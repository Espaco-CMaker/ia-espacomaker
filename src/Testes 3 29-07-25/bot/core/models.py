# bot/core/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from bson import ObjectId           # só p/ gerar id localmente

@dataclass
class Task:
    titulo: str
    descricao: str
    prazo: datetime
    prioridade: str = "Média"
    status: str = "Pendente"
    _id: str = field(default_factory=lambda: str(ObjectId()))

@dataclass
class Project:
    name: str
    description: str
    owner_id: int
    members: List[str]
    status: str = "Em andamento"
    tasks: List[Task] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
