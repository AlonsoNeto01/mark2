import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
from database import engine, get_db

# Configura logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("alunos-service")

# Cria as tabelas do banco
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Serviço de Alunos", version="1.0.0")

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado de simulação de caos para testes/apresentação
caos_ativo = False

@app.post("/toggle-chaos")
def toggle_chaos(status: dict):
    global caos_ativo
    caos_ativo = status.get("ativo", False)
    logger.warning(f"Simulação de caos no Alunos-Service alterada para: {caos_ativo}")
    return {"caos_ativo": caos_ativo}

@app.get("/health")
def health():
    if caos_ativo:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível (Simulação de Caos)."
        )
    return {"status": "ok", "service": "alunos"}

@app.post("/alunos", response_model=schemas.AlunoResponse, status_code=status.HTTP_201_CREATED)
def create_aluno(aluno: schemas.AlunoCreate, db: Session = Depends(get_db)):
    logger.info(f"Criando aluno: {aluno.email}")
    db_aluno = db.query(models.Aluno).filter(models.Aluno.email == aluno.email).first()
    if db_aluno:
        logger.warning(f"Email duplicado ao tentar criar aluno: {aluno.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Um aluno com este email já está cadastrado."
        )
    
    new_aluno = models.Aluno(
        nome=aluno.nome,
        email=aluno.email,
        curso=aluno.curso,
        ativo=True
    )
    db.add(new_aluno)
    db.commit()
    db.refresh(new_aluno)
    return new_aluno

@app.get("/alunos", response_model=List[schemas.AlunoResponse])
def read_alunos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"Listando alunos com skip={skip} e limit={limit}")
    alunos = db.query(models.Aluno).offset(skip).limit(limit).all()
    return alunos

@app.get("/alunos/{id}", response_model=schemas.AlunoResponse)
def read_aluno(id: int, db: Session = Depends(get_db)):
    if caos_ativo:
        logger.error("Falha simulada no serviço de alunos!")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço indisponível (Simulação de Caos)"
        )
    logger.info(f"Buscando aluno com id={id}")
    aluno = db.query(models.Aluno).filter(models.Aluno.id == id).first()
    if not aluno:
        logger.warning(f"Aluno {id} não encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado"
        )
    return aluno

@app.put("/alunos/{id}", response_model=schemas.AlunoResponse)
def update_aluno(id: int, updated_aluno: schemas.AlunoUpdate, db: Session = Depends(get_db)):
    logger.info(f"Atualizando aluno com id={id}")
    aluno = db.query(models.Aluno).filter(models.Aluno.id == id).first()
    if not aluno:
        logger.warning(f"Aluno {id} não encontrado para atualização")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado"
        )
    
    # Valida colisão de email
    if updated_aluno.email != aluno.email:
        colisao = db.query(models.Aluno).filter(
            models.Aluno.email == updated_aluno.email, 
            models.Aluno.id != id
        ).first()
        if colisao:
            logger.warning(f"Tentativa de atualizar aluno {id} para email já existente: {updated_aluno.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email já está em uso por outro aluno."
            )
            
    aluno.nome = updated_aluno.nome
    aluno.email = updated_aluno.email
    aluno.curso = updated_aluno.curso
    
    db.commit()
    db.refresh(aluno)
    return aluno

@app.delete("/alunos/{id}", response_model=schemas.AlunoResponse)
def delete_aluno(id: int, db: Session = Depends(get_db)):
    logger.info(f"Realizando soft-delete do aluno {id}")
    aluno = db.query(models.Aluno).filter(models.Aluno.id == id).first()
    if not aluno:
        logger.warning(f"Aluno {id} não encontrado para remoção")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado"
        )
    
    aluno.ativo = False
    db.commit()
    db.refresh(aluno)
    return aluno

@app.patch("/alunos/{id}/reativar", response_model=schemas.AlunoResponse)
def reativar_aluno(id: int, db: Session = Depends(get_db)):
    logger.info(f"Reativando aluno {id}")
    aluno = db.query(models.Aluno).filter(models.Aluno.id == id).first()
    if not aluno:
        logger.warning(f"Aluno {id} não encontrado para reativação")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado"
        )
    if aluno.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aluno já está ativo"
        )
    
    aluno.ativo = True
    db.commit()
    db.refresh(aluno)
    logger.info(f"Aluno {id} reativado com sucesso")
    return aluno
