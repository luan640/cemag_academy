# Cemag Academy

## App de Avaliações

O app "Cemag Academy" é destinado a avaliação e certificação de funcionários com funcionalidades como criar, corrigir e visualizar provas, calcular notas e validar certificados.

### Tabela de Views e URLs

| URL Name            | View                               | Descrição da View                                                                                     |
|---------------------|------------------------------------|-------------------------------------------------------------------------------------------------------|
| criar_prova         | `criar_prova`                      | Exibe a interface para criação de uma nova prova em uma pasta específica.                             |
| salvar_prova        | `salvar_prova`                     | Salva os dados de uma nova prova e suas questões no banco de dados.                                   |
| delete_prova        | `delete_prova`                     | Deleta uma prova especificada e redireciona para a lista de provas da pasta.                          |
| calcular_nota       | `calcular_nota`                    | Calcula a nota de um funcionário em uma prova com base em suas respostas.                             |
| validacao_certificado | `validacao_certificado`          | Valida se o funcionário está certificado com base nas provas realizadas e sua pontuação.              |
| list_prova          | `list_prova`                       | Lista todas as provas de uma pasta, exibindo se o funcionário pode baixar o certificado.              |
| realizar_prova      | `realizar_prova`                   | Permite ao funcionário realizar uma prova, salvando suas respostas.                                   |
| visualizar_prova    | `visualizar_prova`                 | Exibe os detalhes de uma prova, incluindo questões, alternativas corretas e respostas selecionadas.   |
| corrigir_questoes_dissertativas | `corrigir_questoes_dissertativas` | Interface para correção das respostas dissertativas das provas realizadas.          |
| refazer_prova       | `refazer_prova`                    | Permite ao administrador solicitar a refação de uma prova para um funcionário específico.             |

## Funcionalidades

### Função: `criar_prova`
- **Objetivo**: Renderizar o template para criar uma nova prova associada a uma pasta específica.
- **Processo**:
  1. Obtém a pasta com base no `pk` fornecido.
  2. Retorna o template `criar-prova.html` com a pasta.

### Função: `salvar_prova`
- **Objetivo**: Salvar uma nova prova e suas questões no banco de dados.
- **Processo**:
  1. Verifica se a requisição é do tipo POST.
  2. Carrega os dados da requisição em formato JSON.
  3. Cria uma nova prova associada à pasta.
  4. Para cada questão, cria a questão e suas alternativas se for do tipo "objetiva".
  5. Retorna um JSON de sucesso ou erro.

### Função: `delete_prova`
- **Objetivo**: Excluir uma prova específica do banco de dados.
- **Processo**:
  1. Obtém a prova a ser excluída pelo `pk`.
  2. Remove a prova do banco de dados.
  3. Redireciona para a lista de provas da pasta associada.

### Função: `calcular_nota`
- **Objetivo**: Calcular a nota total de um funcionário para uma prova específica.
- **Processo**:
  1. Filtra as questões da prova.
  2. Agrega as notas das respostas do funcionário.
  3. Retorna o total de respostas e o número total de questões.

### Função: `validacao_certificado`
- **Objetivo**: Validar se um funcionário pode receber o certificado baseado em suas notas.
- **Processo**:
  1. Para cada prova, verifica se o funcionário realizou a prova.
  2. Calcula a nota do funcionário.
  3. Avalia o percentual de acertos e determina se a pasta está certificada.
  4. Retorna um dicionário com os resultados da validação.

### Função: `list_prova`
- **Objetivo**: Listar todas as provas associadas a uma pasta e verificar a validação de certificados.
- **Processo**:
  1. Obtém a pasta e as provas associadas.
  2. Recupera o funcionário atual.
  3. Chama a função de validação para obter o estado de certificação.
  4. Filtra pastas certificadas e retorna o template `list-prova.html` com os dados.

### Função: `realizar_prova`
- **Objetivo**: Permitir que um funcionário realize uma prova.
- **Processo**:
  1. Verifica se o funcionário já realizou a prova.
  2. Obtém as questões da prova e suas alternativas.
  3. Ao receber uma requisição POST, armazena as respostas no banco.
  4. Registra que a prova foi realizada e redireciona para a lista de provas.

### Função: `visualizar_prova`
- **Objetivo**: Exibir as questões e respostas de uma prova específica para um funcionário.
- **Processo**:
  1. Obtém a prova e suas questões.
  2. Coleta as respostas do funcionário e as alternativas corretas.
  3. Retorna o template `visualizar-prova.html` com as informações.

### Função: `corrigir_questoes_dissertativas`
- **Objetivo**: Permitir que um administrador corrija as respostas dissertativas de um funcionário.
- **Processo**:
  1. Obtém as respostas dissertativas do funcionário para a prova.
  2. Se a requisição for POST, processa as correções.
  3. Retorna o template para correção de questões dissertativas.

### Função: `refazer_prova`
- **Objetivo**: Permitir que um funcionário refaça uma prova que já realizou.
- **Processo**:
  1. Obtém a prova e as respostas anteriores do funcionário.
  2. Calcula a nota final e registra o histórico da prova.
  3. (Processo incompleto no trecho fornecido.)

### Funcionalidades Adicionais

- **Correção de Provas**: Possibilidade de corrigir questões objetivas e dissertativas, com opções para definir respostas corretas.
- **Validação de Certificação**: Determina se o funcionário possui certificação em uma área específica com base na pontuação mínima exigida.
- **Cálculo Automático de Nota**: Através da função `calcular_nota`, a aplicação computa automaticamente as notas das provas.

### Modelos Utilizados

- `Prova`: Representa uma avaliação com título, pasta associada e status.
- `Questao`: Cada prova é composta por múltiplas questões, podendo ser objetivas ou dissertativas.
- `Alternativa`: Opções para questões objetivas, com uma única alternativa correta.
- `Resposta`: Registra as respostas dos funcionários para cada questão.
- `ProvaRealizada`: Guarda as informações sobre quais provas foram realizadas por cada funcionário.
- `HistoricoProva`: Histórico das tentativas de cada funcionário nas provas.

### Formulários Personalizados

- **CorrigirRespostaDissertativaForm**: Formulário para correção de questões dissertativas.
- **CorrigirRespostaDissertativaFormSet**: Formulário em conjunto (FormSet) para correção de várias respostas dissertativas em uma única interface.

