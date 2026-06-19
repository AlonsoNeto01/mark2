from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    curso = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
