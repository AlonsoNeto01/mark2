import time
import requests

def test_api():
    print("Iniciando testes manuais locais...")
    
    # 1. Health check de cada serviço
    print("Health checks:")
    for service, port in [("alunos", 8001), ("disciplinas", 8002), ("matriculas", 8003)]:
        try:
            r = requests.get(f"http://localhost:{port}/health")
            print(f"- {service}: {r.status_code} -> {r.json()}")
        except Exception as e:
            print(f"- {service}: Falhou ({e})")
            
    # 2. Criar Alunos
    print("\nCriando alunos:")
    a1 = {"nome": "Maria Silva", "email": "maria@ufopa.edu.br", "curso": "Sistemas de Informação"}
    a2 = {"nome": "João Souza", "email": "joao@ufopa.edu.br", "curso": "Sistemas de Informação"}
    
    r1 = requests.post("http://localhost:8001/alunos", json=a1)
    print(f"- Criar Maria: {r1.status_code} -> {r1.json()}")
    r2 = requests.post("http://localhost:8001/alunos", json=a2)
    print(f"- Criar João: {r2.status_code} -> {r2.json()}")
    
    # Tentativa de duplicado
    r_dup = requests.post("http://localhost:8001/alunos", json=a1)
    print(f"- Criar Maria (Duplicada): {r_dup.status_code} -> {r_dup.json()}")
    
    # 3. Criar Disciplinas
    print("\nCriando disciplinas:")
    d1 = {"nome": "Sistemas Distribuídos", "codigo": "SD001", "carga_horaria": 60, "vagas": 30}
    d2 = {"nome": "Banco de Dados II", "codigo": "BD002", "carga_horaria": 60, "vagas": 5}
    
    rd1 = requests.post("http://localhost:8002/disciplinas", json=d1)
    print(f"- Criar SD001: {rd1.status_code} -> {rd1.json()}")
    rd2 = requests.post("http://localhost:8002/disciplinas", json=d2)
    print(f"- Criar BD002: {rd2.status_code} -> {rd2.json()}")
    
    # Tentativa de duplicado
    rd_dup = requests.post("http://localhost:8002/disciplinas", json=d1)
    print(f"- Criar SD001 (Duplicada): {rd_dup.status_code} -> {rd_dup.json()}")

    # 4. Criar Matrícula com Sucesso
    print("\nCriando matrícula:")
    m1 = {"aluno_id": 1, "disciplina_id": 1}
    rm1 = requests.post("http://localhost:8003/matriculas", json=m1)
    print(f"- Matricular Aluno 1 na Disc 1: {rm1.status_code} -> {rm1.json()}")
    
    # 5. GET Completa
    print("\nBuscando Matrícula Completa:")
    rc = requests.get("http://localhost:8003/matriculas/1/completa")
    print(f"- GET /matriculas/1/completa: {rc.status_code} -> {rc.json()}")
    
    # 6. Matricular Duplicado
    print("\nMatricular duplicado:")
    rm_dup = requests.post("http://localhost:8003/matriculas", json=m1)
    print(f"- Matricular Aluno 1 na Disc 1 novamente: {rm_dup.status_code} -> {rm_dup.json()}")
    
    # 7. Matricular Aluno inexistente
    print("\nMatricular inexistente:")
    m_inex = {"aluno_id": 99, "disciplina_id": 1}
    rm_inex = requests.post("http://localhost:8003/matriculas", json=m_inex)
    print(f"- Matricular Aluno 99: {rm_inex.status_code} -> {rm_inex.json()}")

if __name__ == "__main__":
    test_api()
