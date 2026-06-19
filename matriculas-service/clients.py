import os
import time
import logging
import httpx
from fastapi import HTTPException, status

logger = logging.getLogger("matriculas-service.clients")

# URLs dos microsserviços resolvidas por variáveis de ambiente ou localhost por padrão
ALUNOS_SERVICE_URL = os.getenv("ALUNOS_SERVICE_URL", "http://localhost:8001").rstrip("/")
DISCIPLINAS_SERVICE_URL = os.getenv("DISCIPLINAS_SERVICE_URL", "http://localhost:8002").rstrip("/")

TIMEOUT_LIMIT = 5.0

def get_aluno(aluno_id: int) -> dict:
    url = f"{ALUNOS_SERVICE_URL}/alunos/{aluno_id}"
    logger.info(f"Fazendo chamada GET para {url}")
    start_time = time.time()
    try:
        response = httpx.get(url, timeout=TIMEOUT_LIMIT)
        duration = time.time() - start_time
        logger.info(f"Chamada para {url} concluída em {duration:.4f}s com status {response.status_code}")
        
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aluno com id {aluno_id} não foi encontrado no serviço de alunos."
            )
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        logger.error(f"Timeout na chamada para o serviço de alunos em {url}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de Alunos indisponível (Timeout)."
        )
    except httpx.RequestError as exc:
        logger.error(f"Erro de conexão na chamada para o serviço de alunos em {url}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de Alunos indisponível (Erro de Conexão)."
        )

def get_disciplina(disciplina_id: int) -> dict:
    url = f"{DISCIPLINAS_SERVICE_URL}/disciplinas/{disciplina_id}"
    logger.info(f"Fazendo chamada GET para {url}")
    start_time = time.time()
    try:
        response = httpx.get(url, timeout=TIMEOUT_LIMIT)
        duration = time.time() - start_time
        logger.info(f"Chamada para {url} concluída em {duration:.4f}s com status {response.status_code}")
        
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disciplina com id {disciplina_id} não foi encontrada no serviço de disciplinas."
            )
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        logger.error(f"Timeout na chamada para o serviço de disciplinas em {url}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de Disciplinas indisponível (Timeout)."
        )
    except httpx.RequestError as exc:
        logger.error(f"Erro de conexão na chamada para o serviço de disciplinas em {url}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de Disciplinas indisponível (Erro de Conexão)."
        )
