from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class DisciplinaBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    codigo: str = Field(..., max_length=10)
    carga_horaria: int = Field(..., gt=0)
    vagas: int = Field(..., ge=0)

class DisciplinaCreate(DisciplinaBase):
    pass

class DisciplinaUpdate(DisciplinaBase):
    pass

class DisciplinaResponse(DisciplinaBase):
    id: int
    ativo: bool

    model_config = ConfigDict(from_attributes=True)
