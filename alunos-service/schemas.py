from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class AlunoBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    curso: Optional[str] = None

class AlunoCreate(AlunoBase):
    pass

class AlunoUpdate(AlunoBase):
    pass

class AlunoResponse(AlunoBase):
    id: int
    ativo: bool

    model_config = ConfigDict(from_attributes=True)
