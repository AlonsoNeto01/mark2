from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    codigo = Column(String(10), unique=True, index=True, nullable=False)
    carga_horaria = Column(Integer, nullable=False)
    vagas = Column(Integer, nullable=False)
    ativo = Column(Boolean, default=True)
