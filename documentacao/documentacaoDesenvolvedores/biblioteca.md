# Biblioteca

Este app é responsável pela gestão de livros, incluindo funcionalidades para listagem, adição, avaliação e registro de visualizações de livros.

## Estrutura do App

- `models.py`: Define os modelos `Livro`, `Rating` e `VisualizacaoLivro`.
- `views.py`: Contém as views para listagem de livros, adição de livros, registro de avaliações e visualizações.
- `urls.py`: Define as rotas específicas do app Biblioteca.

## Endpoints

| URL                    | View                        | Descrição                                                  |
|------------------------|-----------------------------|------------------------------------------------------------|
| `/livros/`             | `list_livro`               | Exibe a lista de livros, incluindo avaliações e visualizações. |
| `/livros/add`          | `livro_add`                | Permite adicionar um novo livro à biblioteca.              |
| `/livros/add-rating/`  | `add_rating`               | Adiciona uma avaliação (rating) para um livro específico.  |
| `/livros/registrar-visualizacao-livro` | `registrar_visualizacao_livro` | Registra a visualização de um livro pelo usuário. |

## Funcionalidades

1. **Listagem de Livros (list_livro)**: Exibe uma lista de livros disponíveis na biblioteca, incluindo média de avaliações de cada livro e avaliações específicas do usuário.

- Recupera todos os livros da base de dados.
- Calcula a média de avaliações de cada livro.
- Verifica quais livros foram visualizados pelo usuário.
- Renderiza a lista de livros com suas respectivas médias e avaliações.

2. **Adicionar Livros (livro_add)**: Permite que usuários com permissão possam adicionar novos livros, incluindo detalhes como título, autor, idioma e ano de publicação.

- Processa o formulário para adicionar um novo livro.
- Realiza a validação dos dados antes de salvar o livro na base de dados.
- Redireciona para a lista de livros após a adição.

3. **Avaliação de Livros (add_rating)**: Os usuários podem avaliar um livro com uma nota (score). A média de avaliações é calculada e exibida junto com a avaliação do usuário, caso já tenha avaliado.

- Permite que um usuário adicione ou atualize a avaliação de um livro.
- Recebe o ID do livro e a pontuação via POST.
- Retorna um JSON com a pontuação atualizada.

4. **Registro de Visualizações (registrar_visualizacao_livro)**: Cada visualização de um livro por um usuário é registrada. Os usuários podem marcar e desmarcar visualizações.

- Registra a visualização de um livro por um usuário.
- Permite que um usuário marque ou desmarque um livro como visualizado.
- Retorna um JSON indicando o status da operação.

## Estrutura do Banco de Dados

### Livro
Armazena informações sobre cada livro, incluindo título, autor, ano de publicação, idioma e arquivos (capa e PDF).

- **Campos**:
  - `titulo` (char)
  - `autor` (char)
  - `arquivo_pdf` (file)
  - `capa` (image)
  - `ano` (int)
  - `idioma` (char)
  - `created_by` (foreign key)
  - `created_at` e `modified_at` (datetime)

### Rating
Armazena as avaliações dos livros feitas pelos usuários.

- **Campos**:
  - `user` (foreign key)
  - `livro` (foreign key)
  - `score` (int)
  - `created_at` (datetime)

### VisualizacaoLivro
Registra quando um usuário visualizou um livro específico.

- **Campos**:
  - `user` (foreign key)
  - `livro` (foreign key)
  - `visualizado_em` (datetime)