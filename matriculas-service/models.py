from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime
from database import Base

class Matricula(Base):
    __tablename__ = "matriculas"

    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, nullable=False)
    disciplina_id = Column(Integer, nullable=False)
    data_matricula = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="ativa", nullable=False) # "ativa" ou "cancelada"

    # Índice único composto parcial/filtrado para impedir múltiplas matrículas ativas para o mesmo par aluno/disciplina
    __table_args__ = (
        Index(
            "idx_aluno_disciplina_status_ativa",
            "aluno_id", "disciplina_id",
            unique=True,
            sqlite_where=(status == "ativa")
        ),
    )
