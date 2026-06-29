# 🎤 Roteiro de Apresentação — Sistema Acadêmico Distribuído

> Disciplina: Sistemas Distribuídos — UFOPA
> Tempo estimado: ~15–20 minutos

---

## 📋 Resumo dos Slides

| Slide | Título | Conteúdo Principal |
|-------|--------|---------------------|
| 1 | Capa | Nome do projeto, disciplina, nomes do grupo |
| 2 | O Problema | Por que um sistema distribuído? |
| 3 | Arquitetura Geral | Diagrama dos 3 microsserviços |
| 4 | Tecnologias | Stack usada |
| 5 | Banco por Serviço | Decisão arquitetural chave |
| 6 | Serviço de Alunos | Modelo + endpoints |
| 7 | Serviço de Disciplinas | Modelo + endpoints |
| 8 | Serviço de Matrículas | Modelo + comunicação inter-serviço |
| 9 | Comunicação entre Serviços | Fluxo POST /matriculas |
| 10 | Tolerância a Falhas | Tratamento de 503, timeout |
| 11 | Dashboard Frontend | Interface visual |
| 12 | Demo ao Vivo | Execução prática |
| 13 | Decisões de Design | Tabela resumo |
| 14 | Melhorias Futuras | O que ficou fora do escopo |
| 15 | Encerramento | Perguntas |

---

## 🖥️ Slide 1 — Capa

**O que colocar:**
- Título: **"Sistema Acadêmico Distribuído"**
- Subtítulo: *Projeto Final — Sistemas Distribuídos*
- Logo/nome da UFOPA
- Nomes de todos os integrantes do grupo
- Semestre letivo

**Fala sugerida:**
> "Boa tarde, professor(a). Nosso projeto é um sistema acadêmico construído com arquitetura de microsserviços, onde cada serviço é independente e se comunica via REST."

---

## 🖥️ Slide 2 — O Problema

**O que colocar:**
- Texto curto: *"Sistemas monolíticos tradicionais acoplam toda a lógica em um único processo. Se uma parte falha, tudo cai."*
- Ilustração simples de monolito vs. microsserviços (dois blocos lado a lado)
- Bullet points:
  - ❌ Monolito: falha única derruba tudo
  - ✅ Microsserviços: falha isolada, degradação controlada

**Fala sugerida:**
> "A proposta do projeto é sair do modelo monolítico e construir um sistema onde cada módulo — Alunos, Disciplinas e Matrículas — é um serviço independente, com seu próprio banco de dados e seu próprio processo."

---

## 🖥️ Slide 3 — Arquitetura Geral

**O que colocar:**
- Diagrama da arquitetura (copie ou adapte do README):

```
┌─────────────────────────────────────────────────┐
│          Dashboard (HTML5 / CSS3 / JS)          │
│              index.html                          │
└────────┬──────────────┬──────────────┬──────────┘
         │ API REST     │ API REST     │ API REST
         ▼              ▼              ▼
┌────────────┐  ┌────────────────┐  ┌──────────────┐
│  Alunos    │  │  Disciplinas   │  │  Matrículas  │
│  :8001     │  │  :8002         │  │  :8003       │
│  FastAPI   │  │  FastAPI       │  │  FastAPI     │
│  alunos.db │  │  disciplinas.db│  │  matriculas.db│
└────────────┘  └────────────────┘  └──────┬───────┘
                                           │
                              GET /alunos/{id}
                              GET /disciplinas/{id}
                                           │
                              ┌────────────┴────────────┐
                              ▼                         ▼
                        Alunos :8001            Disciplinas :8002
```

- Destaque as 3 portas: `8001`, `8002`, `8003`
- Setas mostrando que Matrículas consulta os outros dois serviços

> [!TIP]
> **Print para tirar:** Abra o Dashboard (`index.html`) no navegador com os 3 serviços online. A visualização da topologia da rede no Dashboard já mostra a arquitetura de forma visual. **Tire um print/screenshot da área de status cards** mostrando os 3 serviços "Online" com os indicadores verdes.

---

## 🖥️ Slide 4 — Tecnologias Utilizadas

**O que colocar (tabela):**

| Camada | Tecnologia |
|--------|------------|
| **Backend** | Python + FastAPI |
| **ORM** | SQLAlchemy |
| **Banco de Dados** | SQLite (um por serviço) |
| **HTTP Client** | httpx (comunicação entre serviços) |
| **Validação** | Pydantic |
| **Container** | Docker + Docker Compose |
| **Frontend** | HTML5 + CSS3 + JavaScript Vanilla |
| **Design** | Glassmorphism + Dark Theme |

---

## 🖥️ Slide 5 — Banco de Dados por Serviço

**O que colocar:**
- Diagrama mostrando 3 bancos SQLite separados:
  - `alunos.db` → só o Serviço de Alunos acessa
  - `disciplinas.db` → só o Serviço de Disciplinas acessa
  - `matriculas.db` → só o Serviço de Matrículas acessa
- Texto: *"Nenhum serviço acessa o banco de outro diretamente. Toda troca de informação passa pela API REST do dono do dado."*

**Fala sugerida:**
> "Essa é a decisão arquitetural mais importante do projeto. Cada serviço é o dono exclusivo dos seus dados. Se eu preciso saber algo sobre um aluno, faço uma requisição HTTP para o serviço de Alunos — nunca leio direto do banco dele."

> [!IMPORTANT]
> Essa é uma **pergunta provável do professor**: *"Por que bancos separados?"*. Resposta: garante independência real entre os serviços; se fosse um banco só, seria um monolito disfarçado.

---

## 🖥️ Slide 6 — Serviço de Alunos (Porta 8001)

**O que colocar:**
- Modelo de dados:

| Campo | Tipo | Regra |
|-------|------|-------|
| `id` | int | auto |
| `nome` | string | 3–100 chars, obrigatório |
| `email` | string | obrigatório, único, formato email |
| `curso` | string | opcional |
| `ativo` | bool | default `true` |

- Lista de endpoints: `POST`, `GET`, `GET/{id}`, `PUT/{id}`, `DELETE/{id}`, `PATCH/{id}/reativar`, `GET /health`
- Destaque: **DELETE é soft delete** (marca `ativo=false`)

> [!TIP]
> **Print para tirar:** Abra `http://localhost:8001/docs` no navegador. Tire um print da **página do Swagger** mostrando todos os endpoints disponíveis do serviço de Alunos.

---

## 🖥️ Slide 7 — Serviço de Disciplinas (Porta 8002)

**O que colocar:**
- Modelo de dados:

| Campo | Tipo | Regra |
|-------|------|-------|
| `id` | int | auto |
| `nome` | string | 3–100 chars |
| `codigo` | string | único (ex: SD001) |
| `carga_horaria` | int | > 0 |
| `vagas` | int | >= 0 |
| `ativo` | bool | default `true` |

- Mesmos endpoints que Alunos, com `codigo` sendo campo único em vez de `email`
- Destaque: **mesmo padrão do Alunos** (quem entende um, entende o outro)

> [!TIP]
> **Print para tirar:** Abra `http://localhost:8002/docs`. Tire um print do Swagger de Disciplinas.

---

## 🖥️ Slide 8 — Serviço de Matrículas (Porta 8003)

**O que colocar:**
- Modelo de dados:

| Campo | Tipo | Regra |
|-------|------|-------|
| `id` | int | auto |
| `aluno_id` | int | obrigatório |
| `disciplina_id` | int | obrigatório |
| `data_matricula` | datetime | automático |
| `status` | string | `"ativa"` ou `"cancelada"` |

- **Índice único composto** em `(aluno_id, disciplina_id)` para `status = "ativa"` → previne race conditions
- Endpoint especial: `GET /matriculas/{id}/completa` — agrega dados dos 3 serviços

> [!TIP]
> **Print para tirar:** Abra `http://localhost:8003/docs`. Tire um print do Swagger mostrando os endpoints, com destaque para o `/matriculas/{id}/completa`.

---

## 🖥️ Slide 9 — Comunicação entre Serviços (O Coração do Projeto)

**O que colocar:**
- Fluxograma do `POST /matriculas`:

```
Usuário envia POST /matriculas {aluno_id, disciplina_id}
       │
       ▼
[1] GET /alunos/{aluno_id}  ──→ Serviço de Alunos (:8001)
       │
       ├── 404 → "Aluno não encontrado" (rejeita)
       ├── ativo=false → 400 "Aluno inativo" (rejeita)
       ├── Timeout/Erro conexão → 503 "Serviço indisponível"
       │
       ▼
[2] GET /disciplinas/{disc_id}  ──→ Serviço de Disciplinas (:8002)
       │
       ├── (mesmas validações)
       │
       ▼
[3] Verificar duplicata no banco local
       │
       ├── Já existe ativa → 409 "Matrícula duplicada"
       │
       ▼
[4] Cria registro → 201 Created ✅
```

- Trecho do código [clients.py](file:///c:/TRABALHOS/Mark2/matriculas-service/clients.py) mostrando as chamadas HTTP

**Fala sugerida:**
> "Aqui está o ponto central do projeto. Quando uma matrícula é criada, o serviço de Matrículas não confia em nada localmente — ele vai até o serviço de Alunos e até o de Disciplinas confirmar que o aluno e a disciplina existem e estão ativos, antes de gravar qualquer coisa."

> [!TIP]
> **Print para tirar:**
> 1. Abra o código do [clients.py](file:///c:/TRABALHOS/Mark2/matriculas-service/clients.py) — tire print das funções `get_aluno()` e `get_disciplina()` mostrando o tratamento de timeout e erros
> 2. Abra o código do [main.py](file:///c:/TRABALHOS/Mark2/matriculas-service/main.py) — tire print da função `create_matricula()` (linhas 34–78) mostrando o fluxo completo de validação

---

## 🖥️ Slide 10 — Tolerância a Falhas e Resiliência

**O que colocar:**
- Tabela de cenários:

| Cenário | Código HTTP | Comportamento |
|---------|-------------|---------------|
| Aluno não encontrado | `404` | Rejeita com mensagem clara |
| Aluno/disciplina inativo | `400` | Rejeita — existir ≠ estar disponível |
| Matrícula duplicada ativa | `409` | Índice único no banco previne race condition |
| Serviço fora do ar | `503` | Degradação controlada, mensagem informando qual serviço caiu |
| Timeout (> 5s) | `503` | httpx com timeout explícito |

- Trecho de código mostrando o `try/except` com `httpx.TimeoutException` e `httpx.RequestError`

**Fala sugerida:**
> "Se o serviço de Alunos estiver fora do ar, o serviço de Matrículas não trava e não mostra um stack trace genérico. Ele captura o erro de conexão e responde um 503 limpamente, informando que o serviço de Alunos está indisponível. Isso é o que diferencia um sistema distribuído de verdade de três APIs que só por acaso rodam juntas."

> [!TIP]
> **Print para tirar:** Tire um print do trecho `except httpx.TimeoutException` e `except httpx.RequestError` em [clients.py](file:///c:/TRABALHOS/Mark2/matriculas-service/clients.py) (linhas 31–42).

---

## 🖥️ Slide 11 — Dashboard Frontend

**O que colocar:**
- Screenshots do Dashboard em funcionamento (veja abaixo o que printar)
- Bullet points dos recursos:
  - ✅ Status em tempo real dos 3 serviços (Online/Offline)
  - ✅ CRUD completo de Alunos e Disciplinas
  - ✅ Matrícula com visualização de dados agregados
  - ✅ Simulação de Caos (derrubar/subir serviços)
  - ✅ Reativação de registros soft-deleted
  - ✅ Tema escuro com glassmorphism e animações

> [!TIP]
> **Prints para tirar (4 screenshots):**
>
> 1. **Visão geral do Dashboard** — Abra `index.html` com os 3 serviços online. Print da tela inteira mostrando o header, os 3 status cards verdes e a topologia
>
> 2. **Aba de Alunos** — Com a lista de alunos cadastrados aparecendo na tabela e o formulário de cadastro visível. Cadastre 2–3 alunos antes
>
> 3. **Aba de Matrículas** — Com matrículas aparecendo na tabela, mostrando aluno_id e disciplina_id
>
> 4. **Simulação de Caos** — Print do Dashboard com um serviço derrubado (indicador vermelho "Offline") mostrando o alerta no sistema

---

## 🖥️ Slide 12 — Demo ao Vivo 🔴

> [!CAUTION]
> Este é o slide mais importante da apresentação. A demo ao vivo é onde você **ganha ou perde** os 20% de "Comunicação entre Serviços" e impressiona o professor.

**Roteiro da demo (na ordem exata):**

### Passo 1: Subir os serviços
- Abra o terminal e execute `docker-compose up --build`
- **Print/Mostrar:** Os 3 serviços subindo no terminal com logs separados

### Passo 2: Verificar saúde
- No navegador, acesse:
  - `http://localhost:8001/health` → `{"status": "ok", "service": "alunos"}`
  - `http://localhost:8002/health` → `{"status": "ok", "service": "disciplinas"}`
  - `http://localhost:8003/health` → `{"status": "ok", "service": "matriculas"}`
- **Print para tirar:** As 3 respostas de `/health` em abas do navegador

### Passo 3: Criar um aluno (via Swagger ou Dashboard)
- `POST /alunos` com:
```json
{
  "nome": "João Silva",
  "email": "joao@ufopa.edu.br",
  "curso": "Ciência da Computação"
}
```
- **Print:** Resposta `201 Created` com o JSON retornado

### Passo 4: Criar uma disciplina
- `POST /disciplinas` com:
```json
{
  "nome": "Sistemas Distribuídos",
  "codigo": "SD001",
  "carga_horaria": 60,
  "vagas": 40
}
```
- **Print:** Resposta `201 Created`

### Passo 5: Matricular com sucesso ✅
- `POST /matriculas` com:
```json
{
  "aluno_id": 1,
  "disciplina_id": 1
}
```
- **Print:** Resposta `201 Created`
- **Print EXTRA:** Mostre os **logs no terminal** do serviço de Matrículas — vai aparecer as chamadas HTTP para Alunos e Disciplinas com tempo de resposta

### Passo 6: Dados agregados
- `GET /matriculas/1/completa`
- **Print:** Resposta mostrando dados da matrícula + aluno + disciplina juntos (agregação dos 3 serviços)

### Passo 7: Matrícula duplicada (espera 409) ⚠️
- Repita o `POST /matriculas` com os mesmos IDs
- **Print:** Resposta `409 Conflict` com mensagem "O aluno já possui uma matrícula ativa para esta disciplina"

### Passo 8: Aluno inexistente (espera 404) ⚠️
- `POST /matriculas` com `aluno_id: 999`
- **Print:** Resposta `404 Not Found`

### Passo 9: TESTE DE RESILIÊNCIA — Derrubar serviço 💥
- **Derrubar o serviço de Alunos** (via Dashboard/Simulação de Caos ou `docker-compose stop alunos`)
- Tentar `POST /matriculas` novamente
- **Print:** Resposta `503 Service Unavailable` com "Serviço de Alunos indisponível (Erro de Conexão)"
- **Print EXTRA:** O Dashboard mostrando o card de Alunos em vermelho (Offline)

### Passo 10: Religar e confirmar recuperação ✅
- Religar o serviço de Alunos (`docker-compose start alunos`)
- Repetir a matrícula com um par novo — confirmar `201 Created`
- **Print:** Sucesso após o serviço voltar

> [!IMPORTANT]
> O passo 9 (derrubar serviço) é o que mais impressiona o professor. Ele demonstra **tolerância a falhas**, que é a essência de sistemas distribuídos.

---

## 🖥️ Slide 13 — Decisões de Design

**O que colocar (tabela):**

| Decisão | Por quê? |
|---------|----------|
| **Soft delete** em vez de hard delete | Hard delete deixaria matrículas órfãs (Matrículas só guarda o `id`) |
| **Índice único composto** no banco | Validação em código sozinha tem race condition; a garantia real vem do banco |
| **Rejeitamos `400` para inativo**, não `409` | Existir ≠ estar disponível; códigos HTTP devem ser semânticos |
| **URLs por variável de ambiente** | Mudar de `localhost` para nome de container Docker sem mexer no código |
| **Não decrementamos vagas** automaticamente | Evita escrita cross-service e problema de consistência distribuída (fora do escopo) |
| **clients.py separado** do `main.py` | Separação de responsabilidades — lógica de chamada HTTP isolada da lógica de rotas |

**Fala sugerida:**
> "Cada uma dessas decisões foi deliberada. Por exemplo, a gente não decrementa vagas automaticamente quando alguém se matricula. Isso parece natural, mas criaria uma escrita cross-service que pode falhar depois que a matrícula local já foi criada — um problema de consistência distribuída que está fora do escopo da disciplina. A gente deixou isso como melhoria futura, mas a omissão é consciente."

---

## 🖥️ Slide 14 — Limitações e Melhorias Futuras

**O que colocar:**
- 🔒 Autenticação e autorização (JWT, OAuth2)
- 📊 Controle automático de vagas (com transação distribuída ou saga pattern)
- 🔄 Versionamento de API (v1, v2)
- 📡 Comunicação assíncrona com filas (RabbitMQ/Kafka)
- 🐳 Deploy em Kubernetes para escalabilidade
- 📈 Monitoramento com Prometheus + Grafana

**Fala sugerida:**
> "Sabemos das limitações. Não implementamos autenticação porque não era requisito, e o controle de vagas foi uma decisão consciente para evitar complexidade transacional distribuída. Mas temos clareza do que seria o próximo passo."

---

## 🖥️ Slide 15 — Encerramento

**O que colocar:**
- "Obrigado! Dúvidas?"
- Link do repositório GitHub
- QR Code (opcional, para facilitar)

---

## 🛡️ Perguntas Prováveis do Professor (Cole de Apoio)

Tenha estas respostas na ponta da língua:

| Pergunta | Resposta rápida |
|----------|-----------------|
| *"Por que banco separado por serviço?"* | Garante independência real — se fosse banco único, seria monolito disfarçado. Cada serviço é dono exclusivo dos seus dados. |
| *"O que acontece se um serviço cair?"* | Os outros continuam funcionando. Matrículas degrada com 503, informando qual serviço está fora. Demo no passo 9. |
| *"Por que não descontar vagas automaticamente?"* | Escrita cross-service cria problema de consistência distribuída (saga, compensação) fora do escopo. Omissão deliberada. |
| *"Como vocês evitam matrícula duplicada?"* | Índice único composto no banco. Validação em código sozinha tem race condition entre o check e o insert. |
| *"Por que soft delete?"* | Hard delete deixaria matrículas referenciando `aluno_id` que não existe mais — dados órfãos. |
| *"Como o Matrículas descobre a URL dos outros?"* | Variável de ambiente (`ALUNOS_SERVICE_URL`, `DISCIPLINAS_SERVICE_URL`), com fallback para localhost. No Docker, usa o nome do serviço. |
| *"E se os dois serviços caírem ao mesmo tempo?"* | O primeiro erro encontrado já rejeita a requisição. Não precisa agregar múltiplos erros para o escopo. |

---

## 📸 Checklist de Screenshots (Resumo)

Use esta checklist antes da apresentação para garantir que todos os prints estão prontos:

- [ ] Dashboard com 3 serviços online (cards verdes)
- [ ] Dashboard — aba de Alunos com dados
- [ ] Dashboard — aba de Matrículas
- [ ] Dashboard — simulação de caos (serviço offline, card vermelho)
- [ ] Swagger do serviço de Alunos (`localhost:8001/docs`)
- [ ] Swagger do serviço de Disciplinas (`localhost:8002/docs`)
- [ ] Swagger do serviço de Matrículas (`localhost:8003/docs`)
- [ ] Resposta `/health` dos 3 serviços
- [ ] `POST /alunos` → 201 Created
- [ ] `POST /disciplinas` → 201 Created
- [ ] `POST /matriculas` → 201 Created
- [ ] `GET /matriculas/{id}/completa` → dados agregados
- [ ] `POST /matriculas` duplicada → 409 Conflict
- [ ] `POST /matriculas` com aluno inexistente → 404
- [ ] `POST /matriculas` com serviço fora → 503 Service Unavailable
- [ ] Logs no terminal mostrando chamadas HTTP entre serviços
- [ ] Código do `clients.py` (tratamento de erros)
- [ ] Código do `create_matricula()` no `main.py`
- [ ] Docker Compose subindo os 3 contêineres
- [ ] Estrutura do repositório (árvore de pastas)

---

## 🎯 Distribuição de Falas (Adapte ao Grupo)

| Parte | Quem | Slides |
|-------|------|--------|
| Abertura + Arquitetura | Pessoa 1 | Slides 1–5 |
| Alunos + Disciplinas (isolados) | Pessoa 2 | Slides 6–7 |
| Matrículas + Comunicação + Demo ao Vivo | Pessoa 3 | Slides 8–12 |
| Decisões + Perguntas | Todos | Slides 13–15 |

> [!WARNING]
> **Regra de ouro:** Todo mundo precisa falar. O professor pode perguntar individualmente a qualquer integrante.
