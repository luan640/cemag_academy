# Cemag Academy

## App de Materiais

Este aplicativo permite gerenciar uma biblioteca de livros, incluindo adição de livros, avaliações e visualizações.

### URL Routes

| URL Name         | View                | Descrição da View |
| ---------------- | ------------------- | ------------------ |
| `list-pasta`     | `pastas_list`       | Lista todas as pastas com opções de filtragem baseadas no tipo de usuário. |
| `detail-pasta`   | `pastas_detail`     | Detalhes de uma pasta específica, incluindo materiais associados e visualizações. |
| `add-pasta`      | `pastas_add`        | Formulário para adicionar uma nova pasta. |
| `edit-pasta`     | `pasta_edit`        | Formulário para editar uma pasta existente. |
| `delete-pasta`   | `pasta_delete`      | Exclui uma pasta específica. |
| `list-material`  | `material_list`     | Lista todos os materiais disponíveis. |
| `detail-material`| `material_detail`   | Detalhes de um material específico. |
| `add-material`   | `material_add`      | Formulário para adicionar um novo material. |
| `add-material-in-pasta` | `material_add_in_pasta` | Formulário para adicionar um material a uma pasta específica. |
| `edit-material`  | `material_edit`     | Formulário para editar um material existente. |

### Funções Principais

## Descrição das Funções

### 1. `extrair_id_youtube(url)`
- **Descrição**: Extrai o ID de um vídeo do YouTube a partir de uma URL.
- **Funcionalidades**:
  - Utiliza uma expressão regular para verificar se a URL é válida e extrair o ID do vídeo.
  - Retorna o ID se a correspondência for encontrada; caso contrário, retorna `None`.

### 2. `is_id_youtube_valido(url)`
- **Descrição**: Verifica se um ID de vídeo do YouTube é válido.
- **Funcionalidades**:
  - Utiliza uma expressão regular para confirmar se o ID tem exatamente 11 caracteres permitidos.
  - Retorna `True` se o ID for válido; caso contrário, retorna `False`.

### 3. `get_filtered_usernames(logged_in_user)`
- **Descrição**: Obtém uma lista de nomes de usuários filtrados com base no tipo de usuário logado.
- **Funcionalidades**:
  - Filtra as avaliações de eficácia com base no tipo de usuário:
    - Para 'LID', filtra avaliações não avaliadas pela chefia.
    - Para 'ADM', filtra avaliações não avaliadas pelo RH.
  - Retorna uma lista formatada com o primeiro nome, sobrenome e matrícula dos usuários.

### 4. `pastas_add(request)`
- **Descrição**: Adiciona uma nova pasta ao sistema.
- **Funcionalidades**:
  - Verifica se a requisição é do tipo POST.
  - Se o formulário for válido, salva a nova pasta associada ao usuário que a criou.
  - Exibe uma mensagem de sucesso e redireciona para a lista de pastas.

### 5. `pastas_list(request)`
- **Descrição**: Renderiza uma lista de pastas com base no tipo de usuário logado.
- **Funcionalidades**:
  - Filtra as pastas que o usuário pode acessar, dependendo do seu tipo:
    - Para 'ADM' e 'DIR', retorna todas as pastas.
    - Para 'LID', retorna pastas criadas pelo usuário, ou associadas ao seu setor.
  - Obtém as avaliações pendentes relacionadas às pastas, dependendo do tipo de usuário.
  - Renderiza o template com as pastas e informações sobre os criadores e avaliações pendentes.

### 6. `funcionarios_avaliaram(request, pk)`
- **Descrição**: Retorna a lista de usuários que avaliaram uma pasta específica.
- **Funcionalidades**:
  - Verifica se a requisição é do tipo GET e se é uma requisição AJAX.
  - Obtém a pasta usando o ID fornecido e filtra as avaliações de eficácia relacionadas a essa pasta.
  - Dependendo do tipo de usuário, retorna os nomes dos usuários que avaliaram a pasta.
  - Retorna uma `JsonResponse` com os usuários avaliados; se a requisição não for válida, retorna um erro 400.

## `pastas_detail(request, pk)`
- **Objetivo:** Exibir os detalhes de uma pasta específica.
- **Processos:**
  - Recupera a pasta correspondente ao ID fornecido (`pk`).
  - Filtra as avaliações de eficácia associadas à pasta e ao usuário logado.
  - Verifica se existem respostas para essas avaliações.
  - Recupera materiais associados à pasta e os ordena por ID.
  - Filtra visualizações de materiais baseadas no funcionário logado.
  - Renderiza o template `pasta_detail.html` com os dados coletados.

## `pasta_edit(request, pk)`
- **Objetivo:** Editar os detalhes de uma pasta existente.
- **Processos:**
  - Recupera a pasta correspondente ao ID fornecido (`pk`).
  - Se o método de requisição for POST:
    - Valida o formulário de edição.
    - Atualiza a pasta e salva os campos ManyToMany.
    - Exibe uma mensagem de sucesso e redireciona para os detalhes da pasta.
  - Se não for POST, inicializa o formulário com os dados da pasta.
  - Renderiza o template `pasta_edit.html`.

## `pasta_delete(request, pk)`
- **Objetivo:** Excluir uma pasta.
- **Processos:**
  - Recupera a pasta correspondente ao ID fornecido (`pk`).
  - Exclui a pasta do banco de dados.
  - Exibe uma mensagem de sucesso.
  - Redireciona para a lista de pastas.

## `material_add(request)`
- **Objetivo:** Adicionar um novo material.
- **Processos:**
  - Se o método de requisição for POST:
    - Valida o formulário de adição.
    - Associa o material ao usuário logado e extrai o ID do vídeo do YouTube se fornecido.
    - Salva o novo material.
    - Redireciona para a lista de materiais.
  - Se não for POST, inicializa um novo formulário.
  - Renderiza o template `material_add.html`.

## `material_add_in_pasta(request, pk)`
- **Objetivo:** Adicionar um material a uma pasta específica.
- **Processos:**
  - Recupera a pasta correspondente ao ID fornecido (`pk`).
  - Se o método de requisição for POST:
    - Valida o formulário de adição.
    - Associa o material à pasta e ao usuário logado, extrai o ID do vídeo do YouTube se necessário.
    - Salva o novo material e redireciona para os detalhes da pasta.
  - Se não for POST, inicializa um novo formulário.
  - Renderiza o template `material_add.html` com dados da pasta.

## `material_list(request)`
- **Objetivo:** Exibir a lista de todos os materiais.
- **Processos:**
  - Recupera todos os materiais do banco de dados.
  - Renderiza o template `material_list.html` com a lista de materiais.

## `material_detail(request, pk)`
- **Objetivo:** Exibir os detalhes de um material específico.
- **Processos:**
  - Recupera o material correspondente ao ID fornecido (`pk`).
  - Renderiza o template `material_detail.html` com os dados do material.

## `material_edit(request, pk_material, pk_pasta)`
- **Objetivo:** Editar os detalhes de um material existente em uma pasta específica.
- **Processos:**
  - Recupera o material e a pasta correspondentes aos IDs fornecidos.
  - Verifica se o material pertence à pasta.
  - Se o método de requisição for POST:
    - Valida o formulário de edição.
    - Atualiza o material, garantindo que a pasta está correta e extrai o ID do vídeo do YouTube se necessário.
    - Salva o material atualizado e redireciona para os detalhes da pasta.
  - Se não for POST, inicializa o formulário com os dados do material.
  - Renderiza o template `material_edit.html`.

## `material_delete(request, pk_material, pk_pasta)`
- **Objetivo:** Excluir um material de uma pasta específica.
- **Processos:**
  - Recupera a pasta e o material correspondentes aos IDs fornecidos.
  - Exclui o material do banco de dados.
  - Exibe uma mensagem de sucesso.
  - Redireciona para os detalhes da pasta.

## `avaliacao(request, pk)`
### Objetivo
Esta função processa a avaliação de uma trilha por um colaborador, enviando emails de notificação aos líderes e administradores, e registra as respostas da avaliação.

### Processos
- **Método `POST`:**
  - Captura os valores do formulário enviados.
  - Converte o valor da qualificação em booleano.
  - Obtém a instância da `Pasta`, `CustomUser`, e `Funcionario` correspondente ao usuário logado.
  - Identifica o líder do setor associado.
  - Prepara o conteúdo do email informando sobre a avaliação da trilha.
  - Envia um email ao líder (LID) se ele existir e não for o avaliador.
  - Envia um email para todos os administradores (ADM) informando sobre a avaliação.
  - Verifica se já existe uma avaliação para a `Pasta` e o usuário. Se não existir, cria uma nova avaliação.
  - Marca a avaliação como realizada pela chefia ou RH, dependendo do tipo de usuário.
  - Cria a resposta da avaliação e a associa à avaliação correspondente.
  - Redireciona o usuário para a página de detalhes da `Pasta`.

- **Método `GET`:**
  - Redireciona para a página de detalhes da `Pasta`.

## `avaliacao_chefia(request, pk)`
### Objetivo
Esta função permite que um líder (chefe) avalie um colaborador em relação a uma trilha.

### Processos
- **Método `GET`:**
  - Recupera o colaborador da requisição.
  - Obtém a instância da `Pasta` correspondente ao `pk`.
  - Busca o funcionário e o usuário associados ao colaborador.
  - Verifica se já existe uma avaliação para o colaborador e a `Pasta`.
  - Retorna a justificativa da avaliação e a eficácia da qualificação como resposta JSON.

- **Método `POST`:**
  - Captura os valores da eficácia e justificativa da avaliação.
  - Verifica se o colaborador existe; se não, busca pelo identificador matricula.
  - Atualiza a avaliação com base no tipo de usuário (ADM ou chefe).
  - Cria uma nova resposta da avaliação.
  - Redireciona para a página de lista de pastas ou para a jornada, dependendo se o colaborador foi filtrado.

## `jornada_detail(request)`
### Objetivo
Renderiza a página com a lista de funcionários, se o usuário for um administrador (ADM).

### Processos
- Verifica o tipo do usuário.
- Se for ADM, recupera todos os funcionários e os ordena por nome.
- Renderiza a página com a lista de funcionários.
- Se não for ADM, redireciona para a página inicial.

## `jornada_detail_unique(request, matricula)`
### Objetivo
Retorna detalhes específicos de um colaborador baseado na matrícula.

### Processos
- Tenta obter o `Funcionario` e `CustomUser` pela matrícula fornecida.
- Se o funcionário ou usuário não existir, retorna um erro em formato JSON.
- Recupera visualizações, provas realizadas e livros visualizados associados ao colaborador.
- Calcula as notas das provas e associa as notas aos títulos das provas.
- Obtém as pastas associadas ao setor do usuário ou pelo seu matrícula.
- Verifica a validade do certificado e retorna dados relevantes.


## `respostas_avaliacao(request, pk_avaliacao)`

**Objetivo:**
Obter e exibir as respostas de avaliação relacionadas a uma avaliação específica.

**Processos:**
- Obtém a avaliação específica pelo ID (`pk_avaliacao`).
- Filtra as respostas relacionadas a essa avaliação.
- Obtém a resposta do usuário correspondente ao tipo de usuário da avaliação.
- Determina o tipo de usuário alternativo ('DIR' ou 'LID') e obtém a resposta correspondente.
- Obtém a resposta do administrador ('ADM').
- Envia os dados da avaliação e das respostas para o template `avaliacao.html`.

## `registrar_visualizacao(request)`

**Objetivo:**
Registrar ou desmarcar a visualização de um material por um funcionário.

**Processos:**
- Verifica se a requisição é do tipo POST.
- Obtém o `material_id` e `pasta_id` do POST.
- Busca o funcionário, pasta e material correspondentes.
- Tenta obter uma visualização existente. Se ela existir, é deletada, retornando status 'desmarcado'.
- Se não existir, uma nova visualização é criada e salva, retornando status 'marcado'.

## `gerar_ficha_frequencia(request, pk)`

**Objetivo:**
Gerar e retornar um PDF da ficha de frequência dos funcionários em relação a uma pasta.

**Processos:**
- Busca a pasta pelo ID (`pk`).
- Conta o total de materiais na pasta.
- Realiza uma subquery para contar os materiais visualizados por cada funcionário.
- Filtra os funcionários que visualizaram todos os materiais.
- Carrega o template HTML `ficha_frequencia.html` com os dados necessários.
- Converte o HTML renderizado em PDF.
- Configura a resposta HTTP para download do PDF gerado.

## `list_participantes(request, pk)`

**Objetivo:**
Listar os participantes de uma prova relacionada a uma pasta específica.

**Processos:**
- Obtém a prova e a pasta associada pelo ID (`pk`).
- Obtém os setores e funcionários relacionados à pasta.
- Cria uma lista de participantes únicos a partir dos funcionários.
- Obtém os usuários correspondentes aos participantes.
- Filtra as provas realizadas para saber quem completou a prova.
- Prepara uma lista final de participantes com status e notas.
- Renderiza a página `participantes_list.html` com a lista final.

## `gerar_certificado(request)`

**Objetivo:**
Criar e exibir um certificado para um funcionário em relação a uma pasta específica.

**Processos:**
- Verifica se a requisição é do tipo POST.
- Obtém o `pasta_id` e `matricula` do POST.
- Busca o funcionário e usuário correspondentes à matrícula.
- Verifica se já existe um certificado para o usuário e a pasta. Se não existir, cria um novo certificado.
- Obtém os materiais da pasta e renderiza a página `certificado1.html` com os dados do funcionário, materiais e certificado.

## `consultar_certificado(request, uuid)`

**Objetivo:**
Consultar e exibir um certificado baseado em um UUID fornecido.

**Processos:**
- Verifica se um `uuid` foi fornecido.
- Tenta consultar o certificado correspondente ao UUID.
- Se o certificado não for encontrado, retorna uma mensagem de erro em JSON.
- Obtém os materiais relacionados ao certificado e o funcionário correspondente.
- Renderiza a página `certificado1.html` com os dados do funcionário, materiais e certificado.
- Retorna mensagens de erro em caso de exceções ou UUID inválido.
