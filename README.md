FacMap – Backend

Bem-vindos ao backend do FacMap! 🚀

Este repositório contém a API responsável pelo funcionamento do sistema FacMap, desenvolvida utilizando Python e FastAPI, com persistência de dados através do SQLAlchemy.

O objetivo deste README é orientar todos os integrantes da equipe sobre a organização do projeto, a responsabilidade de cada arquivo e como configurar o ambiente de desenvolvimento.

🛠️ Tecnologias utilizadas
Python 3.13 – Linguagem principal.
FastAPI – Construção da API REST.
SQLAlchemy – ORM para comunicação com o banco de dados.
SQLite – Banco de dados utilizado na configuração atual.
Pydantic – Validação e estruturação dos dados.
Uvicorn – Servidor ASGI.
📁 Estrutura do projeto
text
backend-facMap/
│
├── app/
│   │
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   └── user.py
│   │
│   ├── schemas/
│   │   └── user.py
│   │
│   └── routes/
│       └── users.py
│
├── venv/
│
├── .gitignore
└── README.md

🧩 Organização e responsabilidades
1. app/main.py – Inicialização da API

É o ponto de entrada do backend.

Responsabilidades:

Criar a aplicação FastAPI.
Importar e registrar as rotas.
Inicializar as tabelas do banco de dados.

É nesse arquivo que os novos conjuntos de rotas devem ser registrados na aplicação.

2. app/database.py – Conexão com o banco de dados

Responsável pela configuração e gerenciamento da conexão com o banco.

Contém:

DATABASE_URL: endereço do banco de dados.
engine: mecanismo de conexão do SQLAlchemy.
SessionLocal: criação das sessões do banco.
Base: classe base dos modelos.
get_db(): dependência utilizada pelas rotas para acessar o banco.

Importante: quando uma rota precisar consultar ou modificar informações no banco, deve utilizar a dependência get_db().

3. app/models/ – Modelos do banco de dados

Essa pasta contém as classes que representam as tabelas do banco.

Exemplo:

models/user.py

Define a estrutura da tabela de usuários, incluindo seus campos e tipos de dados.

Sempre que uma nova entidade precisar ser armazenada no banco, seu modelo deverá ser criado nessa pasta.

Exemplos de futuras entidades:

User
Institution
Course
Establishment
4. app/schemas/ – Validação dos dados

Responsável por definir como os dados entram e saem da API.

Utiliza Pydantic para validar as informações recebidas e estruturar as respostas.

Exemplo:

schemas/user.py

Contém:

UserCreate: dados necessários para cadastrar um usuário.
UserResponse: informações que podem ser retornadas pela API.

Diferença importante:

Models representam a estrutura dos dados no banco.
Schemas representam a estrutura dos dados que circulam pela API.

Não confundir os dois!

5. app/routes/ – Rotas e endpoints

É onde ficam os endpoints da API.

Exemplo:

routes/users.py

Responsável pelas operações relacionadas aos usuários.

As rotas recebem as requisições, validam os dados, acessam os serviços necessários e retornam as respostas.

Novos módulos podem ser organizados por funcionalidade, como:

users.py
institutions.py
courses.py
establishments.py
⚙️ Como executar o projeto
1. Clonar o repositório
bash
git clone https://github.com/FacMap-Projeto-Luirys/backend-facMap.git

2. Entrar na pasta
bash
cd backend-facMap

3. Criar o ambiente virtual
bash
python -m venv venv

4. Ativar o ambiente virtual

No Windows PowerShell:

powershell
.\venv\Scripts\Activate.ps1

5. Instalar as dependências

As dependências devem ser instaladas conforme o arquivo de requisitos do projeto.

Caso ainda não exista um requirements.txt, ele deverá ser criado e versionado pela equipe.

6. Executar o servidor
bash
python -m fastapi dev app/main.py

🌐 Documentação da API

Com o servidor iniciado, acesse:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

Essas páginas permitem visualizar e testar os endpoints disponíveis.

👥 Organização do desenvolvimento

Para manter o código organizado, cada integrante deve procurar trabalhar na funcionalidade pela qual ficou responsável.

Recomendações:

Criar modelos na pasta models/.
Criar schemas correspondentes na pasta schemas/.
Criar endpoints na pasta routes/.
Evitar colocar toda a lógica dentro de main.py.
Reutilizar a conexão com o banco através de get_db().
Manter nomes de arquivos e classes claros.
Testar os endpoints antes de enviar alterações.
🌿 Git e colaboração

Antes de começar a trabalhar, atualize seu repositório:

bash
git pull origin main


Recomendamos criar uma branch para cada funcionalidade:

bash
git checkout -b feat/nova-funcionalidade


Depois de concluir:

bash
git add .
git commit -m "feat: descrição da funcionalidade"
git push origin feat/nova-funcionalidade


Em seguida, abra um Pull Request para revisão e integração com a branch principal.

Não enviar para o GitHub:

Pasta venv/.
Arquivos __pycache__/.
Arquivos .env.
Bancos de dados locais.
📌 Observações importantes

Este projeto está em desenvolvimento. A estrutura apresentada representa a organização inicial do backend e poderá crescer conforme novas funcionalidades forem implementadas.

Antes de modificar arquivos compartilhados, como database.py e main.py, conversem com a equipe para evitar conflitos.

Nosso objetivo é construir um backend organizado, escalável e de fácil manutenção para o FacMap.

Bom desenvolvimento a todos! 💙
