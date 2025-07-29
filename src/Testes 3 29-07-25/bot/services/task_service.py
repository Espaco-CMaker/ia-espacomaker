# bot/services/task_service.py
from bson import ObjectId
from datetime import datetime
from infra import db
from core.dto import NewTaskDTO
from core.models import Task

class TaskService:
    COL = "projetos"

    async def add_task(self, project_id: str, dto: NewTaskDTO) -> str:
        """Insere uma nova tarefa no array de um projeto e devolve o id da tarefa."""
        task = Task(**dto.dict())          # converte DTO → dataclass
        await db.db[self.COL].update_one(
            {"_id": ObjectId(project_id)},
            {"$push": {"tasks": task.__dict__}}
        )
        return task._id

    async def list_tasks(self, project_id: str) -> list[dict]:
        proj = await db.db[self.COL].find_one({"_id": ObjectId(project_id)},
                                              {"tasks": 1, "_id": 0})
        return proj.get("tasks", []) if proj else []

    async def update_task_status(self, project_id: str, task_id: str, status: str):
        await db.db[self.COL].update_one(
            {"_id": ObjectId(project_id), "tasks._id": task_id},
            {"$set": {"tasks.$.status": status}}
        )

    async def delete_task(self, project_id: str, task_id: str):
        await db.db[self.COL].update_one(
            {"_id": ObjectId(project_id)},
            {"$pull": {"tasks": {"_id": task_id}}}
        )
