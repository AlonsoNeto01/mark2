from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MatriculaBase(BaseModel):
    aluno_id: int
    disciplina_id: int

class MatriculaCreate(MatriculaBase):
    pass

class MatriculaUpdate(BaseModel):
    status: str # "ativa" ou "cancelada"

class MatriculaResponse(MatriculaBase):
    id: int
    data_matricula: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)

class AlunoDetail(BaseModel):
    id: int
    nome: str
    email: str
    curso: str | None
    ativo: bool

class DisciplinaDetail(BaseModel):
    id: int
    nome: str
    codigo: str
    carga_horaria: int
    vagas: int
    ativo: bool

class MatriculaCompletaResponse(MatriculaResponse):
    aluno: AlunoDetail
    disciplina: DisciplinaDetail
