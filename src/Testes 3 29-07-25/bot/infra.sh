bot/
│
├── core/                    # Camada de domínio (entidades e regras puras)
│   ├── models.py
│   └── dto.py
│
├── infra/                   # Gateways externos (Mongo, Llama, Discord)
│   ├── db.py
│   ├── llm.py
│   └── discord_client.py
│
├── services/               # Casos de uso (application layer)
│   ├── project_service.py
│   └── task_service.py
│
├── commands/               # Slash‑commands (interface Discord)
│   ├── new_project.py
│   └── delete_project.py
│
└── main.py                 # Inicia o bot (composition root)
