from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class NewProjectDTO(BaseModel):
    nomeProjeto: str = Field(..., alias="nomeProjeto")
    descricao: str
    alunos: List[str]

class NewTaskDTO(BaseModel):
    titulo: str
    descricao: str
    prazo: datetime
    prioridade: str = Field(default="Média", pattern="^(Baixa|Média|Alta)$")