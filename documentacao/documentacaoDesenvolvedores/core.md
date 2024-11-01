# Cemag Academy

### App de Core

|   URL Name     |    View     | Descrição da View |
| -------------- | ----------- | ----------------- |
| `home` | `painel_home` | Redireciona para o painel principal do usuário, exibindo informações relevantes sobre trilhas e progresso. |
| `painel_home_superuser` | `painel_home_superuser` | Painel exclusivo para usuários do tipo superusuário, apresentando informações administrativas. |
| `load_trilhas_finalizadas` | `load_trilhas_finalizadas` | Carrega e retorna as trilhas finalizadas pelo usuário. |
| `load_progresso_geral_individual` | `load_progresso_geral_individual` | Retorna o progresso geral individual do usuário. |
| `load_progresso_funcionarios` | `load_progresso_funcionarios` | Carrega e retorna o progresso dos funcionários de um setor. |
| `ultimas_trilhas` | `ultimas_trilhas` | Retorna as últimas trilhas criadas no sistema. |
| `ultimos_acessos` | `ultimos_acessos` | Exibe os últimos acessos de usuários, dependendo do tipo de usuário. |

## Descrição das Funções na View

### 1. `painel_home(request)`
- **Descrição**: Renderiza a página inicial do painel para usuários comuns.
- **Funcionalidades**:
  - Redireciona usuários do tipo 'ADM', 'LID', 'DIR' para a página de superusuário.
  - Obtém ou cria um objeto `Funcionario` baseado na matrícula do usuário.
  - Filtra as `Pastas` que o usuário tem acesso com base em seu setor.
  - Calcula o progresso das trilhas e o progresso geral do usuário.
  - Renderiza o template `home.html` com as informações de progresso do usuário.

### 2. `painel_home_superuser(request)`
- **Descrição**: Renderiza a página inicial do painel para superusuários.
- **Funcionalidades**:
  - Obtém ou cria um objeto `Funcionario` para o usuário atual, se não existir.
  - Renderiza o template `home-superuser.html`.

### 3. `ultimas_trilhas(request)`
- **Descrição**: Retorna as últimas trilhas criadas.
- **Funcionalidades**:
  - Obtém as últimas 5 `Pastas` criadas e renderiza o conteúdo HTML da lista.
  - Retorna uma resposta JSON com o HTML renderizado.

### 4. `ultimos_acessos(request)`
- **Descrição**: Retorna os últimos acessos dos usuários.
- **Funcionalidades**:
  - Filtra os últimos acessos de usuários com base no tipo do usuário logado (ADM ou funcionário de um setor específico).
  - Renderiza o conteúdo HTML da lista de últimos acessos.
  - Retorna uma resposta JSON com o HTML renderizado.

### 5. `load_trilhas_finalizadas(request)`
- **Descrição**: Carrega e retorna as trilhas finalizadas pelo usuário.
- **Funcionalidades**:
  - Obtém o setor do usuário e as pastas associadas.
  - Calcula o progresso das trilhas e quantas foram finalizadas.
  - Renderiza o conteúdo HTML da lista de trilhas finalizadas.
  - Retorna uma resposta JSON com o HTML renderizado.

### 6. `load_progresso_geral_individual(request)`
- **Descrição**: Carrega e retorna o progresso geral individual do usuário.
- **Funcionalidades**:
  - Obtém o setor do usuário e as pastas associadas.
  - Calcula o progresso geral do usuário nas trilhas.
  - Renderiza o conteúdo HTML do progresso geral.
  - Retorna uma resposta JSON com o HTML renderizado.

### 7. `load_progresso_funcionarios(request)`
- **Descrição**: Carrega e retorna o progresso dos funcionários sob a liderança do usuário.
- **Funcionalidades**:
  - Obtém os dados de progresso dos funcionários no setor do usuário.
  - Renderiza o conteúdo HTML do progresso dos funcionários.
  - Retorna uma resposta JSON com o HTML renderizado.

### 8. `get_setor_do_usuario(user)`
- **Descrição**: Obtém o setor do usuário atual.
- **Funcionalidades**:
  - Retorna o setor associado ao funcionário do usuário logado.

### 9. `get_pastas(setor_do_usuario, matricula)`
- **Descrição**: Obtém as pastas acessíveis ao usuário.
- **Funcionalidades**:
  - Filtra as pastas que o usuário pode acessar com base em seu setor e matrícula.

### 10. `calcular_progresso_trilha_individual(user, pastas)`
- **Descrição**: Calcula o progresso individual do usuário nas trilhas.
- **Funcionalidades**:
  - Usa cache para armazenar o progresso e evitar cálculos repetidos.
  - Retorna um dicionário com as pastas e o progresso individual do usuário.

### 11. `calcular_trilhas_finalizadas(pastas, progresso_pasta)`
- **Descrição**: Calcula quantas trilhas foram finalizadas pelo usuário.
- **Funcionalidades**:
  - Conta as pastas finalizadas (100% de progresso) e retorna uma string com o total.

### 12. `calcular_media_progresso_area_trilha(user, pastas, progresso_pasta)`
- **Descrição**: Calcula a média de progresso das trilhas por área.
- **Funcionalidades**:
  - Usa a classe `ProgressoTrilha` para calcular a média de progresso nas trilhas.

### 13. `get_leader_data(user)`
- **Descrição**: Obtém os dados de progresso dos funcionários sob a liderança do usuário.
- **Funcionalidades**:
  - Filtra funcionários no mesmo setor do usuário, excluindo administradores.
  - Retorna os dados de progresso dos funcionários.
