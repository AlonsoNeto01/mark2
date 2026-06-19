import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import clients
from database import engine, get_db

# Configura logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("matriculas-service")

# Cria as tabelas do banco
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Serviço de Matrículas", version="1.0.0")

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "matriculas"}

@app.post("/matriculas", response_model=schemas.MatriculaResponse, status_code=status.HTTP_201_CREATED)
def create_matricula(matricula: schemas.MatriculaCreate, db: Session = Depends(get_db)):
    logger.info(f"Iniciando processo de matrícula para aluno={matricula.aluno_id} na disciplina={matricula.disciplina_id}")
    
    # 1. Validação de Aluno no Alunos-Service (comunicação HTTP síncrona)
    aluno_data = clients.get_aluno(matricula.aluno_id)
    if not aluno_data.get("ativo", True):
        logger.warning(f"Aluno {matricula.aluno_id} está inativo")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível matricular um aluno inativo."
        )

    # 2. Validação de Disciplina no Disciplinas-Service (comunicação HTTP síncrona)
    disciplina_data = clients.get_disciplina(matricula.disciplina_id)
    if not disciplina_data.get("ativo", True):
        logger.warning(f"Disciplina {matricula.disciplina_id} está inativa")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível se matricular em uma disciplina inativa."
        )

    # 3. Validação de Matrícula Duplicada / Existente Ativa no Banco Local
    existente = db.query(models.Matricula).filter(
        models.Matricula.aluno_id == matricula.aluno_id,
        models.Matricula.disciplina_id == matricula.disciplina_id,
        models.Matricula.status == "ativa"
    ).first()
    if existente:
        logger.warning(f"Matrícula já ativa para aluno={matricula.aluno_id} na disciplina={matricula.disciplina_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O aluno já possui uma matrícula ativa para esta disciplina."
        )

    new_matricula = models.Matricula(
        aluno_id=matricula.aluno_id,
        disciplina_id=matricula.disciplina_id,
        status="ativa"
    )
    db.add(new_matricula)
    db.commit()
    db.refresh(new_matricula)
    logger.info(f"Matrícula {new_matricula.id} criada com sucesso.")
    return new_matricula

@app.get("/matriculas", response_model=List[schemas.MatriculaResponse])
def read_matriculas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"Listando matrículas com skip={skip} e limit={limit}")
    return db.query(models.Matricula).offset(skip).limit(limit).all()

@app.get("/matriculas/{id}", response_model=schemas.MatriculaResponse)
def read_matricula(id: int, db: Session = Depends(get_db)):
    logger.info(f"Buscando matrícula com id={id}")
    matricula = db.query(models.Matricula).filter(models.Matricula.id == id).first()
    if not matricula:
        logger.warning(f"Matrícula {id} não encontrada")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula não encontrada"
        )
    return matricula

@app.get("/matriculas/{id}/completa", response_model=schemas.MatriculaCompletaResponse)
def read_matricula_completa(id: int, db: Session = Depends(get_db)):
    logger.info(f"Agregando dados completos para matrícula {id}")
    matricula = db.query(models.Matricula).filter(models.Matricula.id == id).first()
    if not matricula:
        logger.warning(f"Matrícula {id} não encontrada")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula não encontrada"
        )

    # Chamadas aos microsserviços parceiros
    aluno = clients.get_aluno(matricula.aluno_id)
    disciplina = clients.get_disciplina(matricula.disciplina_id)

    return schemas.MatriculaCompletaResponse(
        id=matricula.id,
        aluno_id=matricula.aluno_id,
        disciplina_id=matricula.disciplina_id,
        data_matricula=matricula.data_matricula,
        status=matricula.status,
        aluno=schemas.AlunoDetail(**aluno),
        disciplina=schemas.DisciplinaDetail(**disciplina)
    )

@app.put("/matriculas/{id}", response_model=schemas.MatriculaResponse)
def update_matricula(id: int, updated: schemas.MatriculaUpdate, db: Session = Depends(get_db)):
    logger.info(f"Atualizando status da matrícula {id} para {updated.status}")
    matricula = db.query(models.Matricula).filter(models.Matricula.id == id).first()
    if not matricula:
        logger.warning(f"Matrícula {id} não encontrada")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula não encontrada"
        )

    if matricula.status == "cancelada" and updated.status == "cancelada":
        logger.warning(f"Tentativa de cancelar matrícula {id} já cancelada")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta matrícula já se encontra cancelada."
        )

    matricula.status = updated.status
    db.commit()
    db.refresh(matricula)
    return matricula

@app.delete("/matriculas/{id}", response_model=schemas.MatriculaResponse)
def delete_matricula(id: int, db: Session = Depends(get_db)):
    logger.info(f"Deletando matrícula {id} (hard-delete)")
    matricula = db.query(models.Matricula).filter(models.Matricula.id == id).first()
    if not matricula:
        logger.warning(f"Matrícula {id} não encontrada para remoção")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula não encontrada"
        )
    
    db.delete(matricula)
    db.commit()
    return matricula
