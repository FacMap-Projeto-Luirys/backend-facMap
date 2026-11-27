# Backend – FacMap

## 1. Sobre o projeto

O backend cuida das regras de negócio, da comunicação com o banco de dados e da autenticação dos usuários. Ele também calcula o resultado da avaliação de carreira e disponibiliza tudo por meio de uma API.

## 2. Tecnologias utilizadas

- **Python 3.12+**
- **FastAPI**: criação da API.
- **SQLAlchemy 2**: ORM e comunicação com o banco de dados.
- **PostgreSQL (Supabase)** com o driver **psycopg 3**.
- **Pydantic**: validação e estruturação dos dados.
- **PyJWT**: geração e validação dos tokens JWT.
- **pwdlib (Argon2)**: hash das senhas.
- **Uvicorn/FastAPI CLI**: execução do servidor.
- **Git e GitHub**: versionamento do código.

## 3. Organização das pastas

```
app/
  main.py              Inicializa o FastAPI, CORS, rotas e o /health
  database.py          Conexão com o banco (engine, sessão e dependência DbSession)
  init_db.py           Cria as tabelas que ainda não existem (python -m app.init_db)
  models/              Tabelas do banco (User, Assessment)
  core/
    config.py          Configurações lidas do .env
    security.py        Hash de senha e criação/validação do JWT
    deps.py            Dependência get_current_user (protege rotas)
  schemas/             Schemas Pydantic (entrada e saída da API)
  routes/
    auth.py            /auth/register, /auth/login, /auth/token
    users.py           /users/me
    assessment.py      /assessment/...
  services/
    assessment.py      Cálculo do resultado da avaliação
  data/
    assessment.json    Perguntas, pesos e resultados da avaliação
```

As tabelas ficam em `app/models/`. Os nomes de tabelas e colunas (`hashedPassword`, `createdAt`...) são os mesmos que o Prisma criava, então o banco que já existe continua funcionando. Para usar o banco numa rota, receba a sessão como parâmetro:

```python
from sqlalchemy import select
from app.database import DbSession
from app.models import User

@router.get("/exemplo")
def exemplo(db: DbSession):
    return db.scalars(select(User.email)).all()
```

O `init_db` só cria tabelas que não existem: ele não altera colunas de tabelas que já estão no banco. Se mudar uma coluna, altere a tabela também no Supabase (SQL Editor).

## 4. Como executar o backend

```powershell
cd backend-facMap

# 1. Criar e ativar o ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Criar o .env e preencher DATABASE_URL e JWT_SECRET_KEY
copy .env.example .env

# 4. Criar as tabelas (só na primeira vez, num banco vazio)
python -m app.init_db

# 5. Rodar o servidor
fastapi dev app/main.py
```

A API fica em `http://127.0.0.1:8000`. A documentação interativa está em `http://127.0.0.1:8000/docs`. Para testar as rotas protegidas por ela, clique em **Authorize** e informe o e-mail (no campo `username`) e a senha.

Para conferir se a API está falando com o banco, abra `/health/db`. Se o banco estiver fora do ar ou a `DATABASE_URL` estiver errada, as rotas respondem `503` com a mensagem "Banco de dados indisponível".

### Deploy na Vercel

A Vercel detecta o FastAPI sozinha (`app/main.py`) e instala o `requirements.txt`. Em **Settings → Environment Variables** do projeto do backend, cadastre:

| Variável         | Valor                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| `DATABASE_URL`   | URL do Supabase, "Transaction pooler" (porta 6543)                          |
| `JWT_SECRET_KEY` | Uma chave forte (a mesma de antes, para não derrubar quem já está logado)   |
| `CORS_ORIGINS`   | `https://frontend-fac-map.vercel.app`                                       |

Depois de mudar variáveis, faça um **Redeploy**. No projeto do frontend, `VITE_API_URL` deve apontar para a URL do backend (também com redeploy, porque o valor entra no build).

## 5. Autenticação (JWT)

| Método | Rota             | Protegida | Descrição                                                       |
| ------ | ---------------- | --------- | --------------------------------------------------------------- |
| POST   | `/auth/register` | não       | Cria a conta (`name`, `email`, `password`) e já devolve o token |
| POST   | `/auth/login`    | não       | Login com JSON (`email`, `password`)                            |
| POST   | `/auth/token`    | não       | Login via formulário OAuth2 (usado pelo `/docs`)                |
| GET    | `/users/me`      | **sim**   | Dados do usuário logado                                         |

O login e o cadastro respondem com:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": { "id": 1, "name": "Ana", "email": "ana@exemplo.com" }
}
```

Nas rotas protegidas, envie o header `Authorization: Bearer <access_token>`. Sem o token, ou com um token inválido ou expirado, a API responde `401`.

Para proteger uma rota nova, basta receber o usuário atual como parâmetro:

```python
from app.core.deps import CurrentUser

@router.get("/minha-rota")
async def minha_rota(user: CurrentUser):
    ...
```

## 6. Avaliação (formulário)

A resposta do formulário é calculada de acordo com o arquivo **`app/data/assessment.json`**:

- `areas`: as áreas de TI (título, descrição, ícone, cor).
- `questions`: as perguntas. Cada opção tem `weights`, que são os pontos que ela soma para cada área. O tipo pode ser `single` (uma resposta) ou `multiple` (várias). `exclusive: true` marca uma opção que não pode ser combinada com outras.
- `scoring.base_pct`: afinidade mínima exibida. `scoring.top_n`: quantas áreas são recomendadas.
- `results`: para cada área, os textos de "Por que esse resultado?", a disciplina relacionada e a prévia do PDI.

A afinidade de cada área é calculada assim: `base_pct + (100 - base_pct) × pontos / pontuação máxima possível`. Os textos do resultado vêm da área com maior afinidade.

Para mudar perguntas, pesos ou textos, edite só o JSON. Ele é validado e recarregado automaticamente quando o arquivo muda, sem precisar reiniciar o servidor. Se o `value` de uma opção mudar, atualize o texto correspondente no frontend (`src/data/content.ts`).

| Método | Rota                  | Protegida | Descrição                                       |
| ------ | --------------------- | --------- | ----------------------------------------------- |
| GET    | `/assessment/form`    | não       | Perguntas e opções (sem os pesos)               |
| POST   | `/assessment`         | **sim**   | Envia as respostas, calcula e salva o resultado |
| GET    | `/assessment/latest`  | **sim**   | Último resultado do usuário                     |
| GET    | `/assessment/history` | **sim**   | Todos os resultados do usuário                  |

Exemplo de envio:

```json
{
  "answers": {
    "periodo": "1º período",
    "tempo": "Cerca de 4 horas",
    "atividade": ["Criar sites ou aplicativos"],
    "contatos": ["Git e GitHub"],
    "area": "dev",
    "scenario": "data"
  }
}
```

Respostas que não existem no JSON, perguntas obrigatórias em branco ou uma opção exclusiva combinada com outras retornam `422` com a mensagem do problema.

## 7. Orientações para quem for desenvolver

- Não coloquem todas as funcionalidades dentro do `main.py`.
- Modelem as tabelas em `app/models/`.
- Criem schemas para validar os dados.
- Organizem os endpoints dentro de `routes` e a lógica mais pesada em `services`.
- Evitem duplicar código.
- Usem nomes claros para arquivos, funções e variáveis.
- Antes de criar uma nova funcionalidade, verifiquem se já existe algum arquivo responsável por ela.

## 8. Trabalho em equipe e GitHub

Cada integrante deve trabalhar, de preferência, em uma branch própria. Antes de começar a desenvolver, atualizem o projeto com as alterações mais recentes. Ao terminar uma funcionalidade, façam um commit explicando brevemente o que foi alterado.

Exemplos de commits:

```
feat: criação das rotas de usuários
fix: correção na conexão com banco de dados
refactor: organização dos schemas
docs: atualização da documentação
```

Evitem alterar arquivos de outros módulos sem necessidade e sempre comuniquem mudanças que possam afetar outras funcionalidades.
