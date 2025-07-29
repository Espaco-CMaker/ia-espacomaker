from core.models import Project
from core.dto import NewProjectDTO
from infra import db
from bson import ObjectId

class ProjectService:
    COL = "projetos"

    async def create_project(self, dto: NewProjectDTO, owner_id: int) -> tuple[str, str]:
        proj = Project(
            name        = dto.nomeProjeto,
            description = dto.descricao,
            owner_id    = owner_id,
            members     = dto.alunos
        )
        _id = await db.insert_one(self.COL, proj.__dict__)
        return str(_id), proj.name

    async def delete_project(self, project_id: str) -> dict | None:
        return await db.find_one_and_delete(self.COL, {"_id": ObjectId(project_id)})
