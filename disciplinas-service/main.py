import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Configura logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("disciplinas-service")

# Cria as tabelas do banco
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Serviço de Disciplinas", version="1.0.0")

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
    logger.warning(f"Simulação de caos no Disciplinas-Service alterada para: {caos_ativo}")
    return {"caos_ativo": caos_ativo}

@app.get("/health")
def health():
    if caos_ativo:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível (Simulação de Caos)."
        )
    return {"status": "ok", "service": "disciplinas"}

@app.post("/disciplinas", response_model=schemas.DisciplinaResponse, status_code=status.HTTP_201_CREATED)
def create_disciplina(disciplina: schemas.DisciplinaCreate, db: Session = Depends(get_db)):
    logger.info(f"Criando disciplina: {disciplina.codigo}")
    db_disciplina = db.query(models.Disciplina).filter(models.Disciplina.codigo == disciplina.codigo).first()
    if db_disciplina:
        logger.warning(f"Codigo duplicado ao tentar criar disciplina: {disciplina.codigo}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uma disciplina com este código já está cadastrada."
        )
    
    new_disciplina = models.Disciplina(
        nome=disciplina.nome,
        codigo=disciplina.codigo,
        carga_horaria=disciplina.carga_horaria,
        vagas=disciplina.vagas,
        ativo=True
    )
    db.add(new_disciplina)
    db.commit()
    db.refresh(new_disciplina)
    return new_disciplina

@app.get("/disciplinas", response_model=List[schemas.DisciplinaResponse])
def read_disciplinas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"Listando disciplinas com skip={skip} e limit={limit}")
    disciplinas = db.query(models.Disciplina).offset(skip).limit(limit).all()
    return disciplinas

@app.get("/disciplinas/{id}", response_model=schemas.DisciplinaResponse)
def read_disciplina(id: int, db: Session = Depends(get_db)):
    if caos_ativo:
        logger.error("Falha simulada no serviço de disciplinas!")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço indisponível (Simulação de Caos)"
        )
    logger.info(f"Buscando disciplina com id={id}")
    disciplina = db.query(models.Disciplina).filter(models.Disciplina.id == id).first()
    if not disciplina:
        logger.warning(f"Disciplina {id} não encontrada")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada"
        )
    return disciplina

@app.put("/disciplinas/{id}", response_model=schemas.DisciplinaResponse)
def update_disciplina(id: int, updated_disciplina: schemas.DisciplinaUpdate, db: Session = Depends(get_db)):
    logger.info(f"Atualizando disciplina com id={id}")
    disciplina = db.query(models.Disciplina).filter(models.Disciplina.id == id).first()
    if not disciplina:
        logger.warning(f"Disciplina {id} não encontrada para atualização")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada"
        )
    
    # Valida colisão de código
    if updated_disciplina.codigo != disciplina.codigo:
        colisao = db.query(models.Disciplina).filter(
            models.Disciplina.codigo == updated_disciplina.codigo, 
            models.Disciplina.id != id
        ).first()
        if colisao:
            logger.warning(f"Tentativa de atualizar disciplina {id} para código já existente: {updated_disciplina.codigo}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este código de disciplina já está em uso."
            )
            
    disciplina.nome = updated_disciplina.nome
    disciplina.codigo = updated_disciplina.codigo
    disciplina.carga_horaria = updated_disciplina.carga_horaria
    disciplina.vagas = updated_disciplina.vagas
    
    db.commit()
    db.refresh(disciplina)
    return disciplina

@app.delete("/disciplinas/{id}", response_model=schemas.DisciplinaResponse)
def delete_disciplina(id: int, db: Session = Depends(get_db)):
    logger.info(f"Realizando soft-delete da disciplina {id}")
    disciplina = db.query(models.Disciplina).filter(models.Disciplina.id == id).first()
    if not disciplina:
        logger.warning(f"Disciplina {id} não encontrada para remoção")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada"
        )
    
    disciplina.ativo = False
    db.commit()
    db.refresh(disciplina)
    return disciplina

@app.patch("/disciplinas/{id}/reativar", response_model=schemas.DisciplinaResponse)
def reativar_disciplina(id: int, db: Session = Depends(get_db)):
    logger.info(f"Reativando disciplina {id}")
    disciplina = db.query(models.Disciplina).filter(models.Disciplina.id == id).first()
    if not disciplina:
        logger.warning(f"Disciplina {id} não encontrada para reativação")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada"
        )
    if disciplina.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Disciplina já está ativa"
        )
    
    disciplina.ativo = True
    db.commit()
    db.refresh(disciplina)
    logger.info(f"Disciplina {id} reativada com sucesso")
    return disciplina
