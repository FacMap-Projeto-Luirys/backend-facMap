README – Backend FacMap
1. Sobre o projeto

O FacMap é um projeto desenvolvido para facilitar a localização e o acesso a informações relacionadas às faculdades.

O backend é responsável por gerenciar as regras de negócio, comunicação com o banco de dados, autenticação dos usuários e disponibilização das informações por meio de uma API.

2. Tecnologias utilizadas
Python
FastAPI – criação da API.
SQLAlchemy – comunicação com o banco de dados.
Pydantic – validação e estruturação dos dados.
Uvicorn/FastAPI CLI – execução do servidor.
Git e GitHub – versionamento do código.
3. Organização das pastas

O backend está organizado para separar as responsabilidades de cada parte do sistema.

app/

É a pasta principal da aplicação. Todo o código do backend fica dentro dela.

app/main.py

É o arquivo principal da aplicação. Nele fica a inicialização do FastAPI, a configuração das rotas e a integração dos módulos principais.

app/database.py

Responsável pela conexão com o banco de dados, criação da configuração do SQLAlchemy e gerenciamento das sessões utilizadas pela aplicação.

app/models/

Contém os modelos das tabelas do banco de dados.

Cada arquivo representa uma entidade que será armazenada no banco.

Exemplo: user.py representa o modelo de usuário.

app/schemas/

Contém os schemas responsáveis pela validação dos dados recebidos e enviados pela API.

Por exemplo, no cadastro de usuários, podemos ter:

UserCreate: dados necessários para criar um usuário.
UserResponse: informações que serão retornadas pela API.
app/routes/

Contém as rotas da API, separadas por funcionalidade.

Cada arquivo é responsável por um conjunto de endpoints.

Exemplo: users.py contém as rotas relacionadas aos usuários, como cadastro, consulta e outras operações.

4. Como funciona a comunicação entre as partes?

O funcionamento segue esta organização:

O usuário realiza uma requisição à API.
A rota correspondente recebe essa requisição.
O schema valida os dados recebidos.
A rota utiliza o model para interagir com o banco.
O database gerencia a conexão e a sessão.
A API retorna uma resposta ao usuário.

Essa separação ajuda a manter o código organizado e facilita a manutenção e o desenvolvimento em equipe.

5. Como executar o backend?

Primeiro, entre na pasta do projeto:

bash
cd backend-facMap


Ative o ambiente virtual:

Windows PowerShell:

powershell
.\venv\Scripts\Activate


Instale as dependências:

bash
pip install -r requirements.txt


Execute o servidor:

bash
python -m fastapi dev app/main.py


Após iniciar, a API ficará disponível localmente.

A documentação interativa do FastAPI poderá ser acessada em:

http://127.0.0.1:8000/docs

6. Orientações para quem for desenvolver

Para manter o projeto organizado, sigam algumas recomendações:

Não coloquem todas as funcionalidades dentro do main.py.
Criem models para representar as tabelas do banco.
Criem schemas para validar os dados.
Organizem os endpoints dentro de routes.
Evitem duplicar código.
Utilizem nomes claros para arquivos, funções e variáveis.
Antes de criar uma nova funcionalidade, verifiquem se já existe algum arquivo responsável por ela.
7. Trabalho em equipe e GitHub

Cada integrante deve trabalhar preferencialmente em uma branch própria.

Antes de começar a desenvolver, atualizem o projeto com as alterações mais recentes.

Ao finalizar uma funcionalidade, façam um commit explicando brevemente o que foi alterado.

Exemplos de commits:

feat: criação das rotas de usuários
fix: correção na conexão com banco de dados
refactor: organização dos schemas
docs: atualização da documentação

Evitem alterar arquivos de outros módulos sem necessidade e sempre comuniquem mudanças que possam afetar outras funcionalidades.

8. Importante

A estrutura do backend foi pensada para permitir que várias pessoas desenvolvam funcionalidades diferentes sem precisar concentrar tudo em um único arquivo.

O objetivo é manter o projeto modular, organizado e fácil de expandir conforme novas funcionalidades do FacMap forem implementadas.

Cada integrante deve respeitar a separação de responsabilidades para evitar conflitos e facilitar a integração do código.
