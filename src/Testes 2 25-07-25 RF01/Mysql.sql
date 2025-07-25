/* ================================
   Modelo_Logico_RF01  — revisado
   Compatível MySQL 8.x
   ================================ */

/* ---------- Tabelas principais ---------- */

CREATE TABLE Projeto (
    ID          INT AUTO_INCREMENT PRIMARY KEY,
    Nome        VARCHAR(255)  NOT NULL,
    Descricao   TEXT,
    Dt_Criacao  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Status      ENUM('ativo','finalizado') NOT NULL
);

CREATE TABLE Projetista (
    Discord_ID  BIGINT PRIMARY KEY,
    Nome        VARCHAR(255),
    Cargo       ENUM('membro','membroMaker','admin') NOT NULL
);

CREATE TABLE Tarefa (
    ID          INT AUTO_INCREMENT PRIMARY KEY,
    Titulo      VARCHAR(255)  NOT NULL,
    Descricao   TEXT,
    Prazo       TIMESTAMP,
    Prioridade  ENUM('alta','media','baixa') NOT NULL,
    Status      ENUM('pendente','concluida') NOT NULL
);

CREATE TABLE Relatorio (
    ID          INT AUTO_INCREMENT PRIMARY KEY,
    Dt_Geracao  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Conteudo    TEXT
);

/* ---------- Tabelas de junção ---------- */

CREATE TABLE Projeto_Projetista (
    Projeto_ID    INT     NOT NULL,
    Projetista_ID BIGINT  NOT NULL,
    PRIMARY KEY (Projeto_ID, Projetista_ID),
    CONSTRAINT FK_PP_Projeto     FOREIGN KEY (Projeto_ID)
        REFERENCES Projeto(ID)        ON DELETE CASCADE,
    CONSTRAINT FK_PP_Projetista  FOREIGN KEY (Projetista_ID)
        REFERENCES Projetista(Discord_ID) ON DELETE CASCADE
);

CREATE TABLE Projeto_Relatorio (
    Projeto_ID    INT NOT NULL,
    Relatorio_ID  INT NOT NULL,
    PRIMARY KEY (Projeto_ID, Relatorio_ID),
    CONSTRAINT FK_PR_Projeto    FOREIGN KEY (Projeto_ID)
        REFERENCES Projeto(ID)      ON DELETE CASCADE,
    CONSTRAINT FK_PR_Relatorio  FOREIGN KEY (Relatorio_ID)
        REFERENCES Relatorio(ID)    ON DELETE CASCADE
);

CREATE TABLE Projeto_Tarefa (
    ID          INT AUTO_INCREMENT PRIMARY KEY,  -- chave surrogate
    Projeto_ID  INT NOT NULL,
    Tarefa_ID   INT NULL,        -- agora pode receber NULL

    UNIQUE (Projeto_ID, Tarefa_ID),  -- garante que não haja duplicatas

    CONSTRAINT FK_PT_Projeto
      FOREIGN KEY (Projeto_ID)
      REFERENCES Projeto(ID)
      ON DELETE CASCADE,

    CONSTRAINT FK_PT_Tarefa
      FOREIGN KEY (Tarefa_ID)
      REFERENCES Tarefa(ID)
      ON DELETE SET NULL
);
