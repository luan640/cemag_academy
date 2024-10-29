# Cemag Academy

## App de Cadastro

### Estrutura de URLs

| URL Name                                         | View                          | Descrição da View                                             |
|-------------------------------------------------|-------------------------------|--------------------------------------------------------------|
| `funcionario`                                   | `funcionario_cadastro`       | Permite cadastrar novos funcionários.                        |
| `funcionario/<int:pk>/edit`                    | `funcionario_edit`           | Edita os dados de um funcionário existente.                 |
| `funcionario/<int:pk>/delete`                  | `funcionario_delete`         | Exclui um funcionário existente.                             |
| `setor`                                         | `setor_cadastro`             | Permite cadastrar novos setores.                             |
| `setor/<int:pk>/edit`                           | `setor_edit`                 | Edita os dados de um setor existente.                       |
| `setor/<int:pk>/delete`                         | `setor_delete`               | Exclui um setor existente.                                   |
| `area`                                          | `area_cadastro`              | Permite cadastrar novas áreas.                               |
| `area/<int:pk>/edit`                            | `area_edit`                  | Edita os dados de uma área existente.                       |
| `area/<int:pk>/delete`                          | `area_delete`                | Exclui uma área existente.                                   |

### Descrição das Views

1. **funcionario_cadastro**:
   - Permite o cadastro de novos funcionários.
   - Valida os dados e associa o funcionário ao usuário que está criando.
   - Exibe uma lista de funcionários cadastrados.

2. **funcionario_edit**:
   - Carrega os dados de um funcionário existente para edição.
   - Salva as alterações feitas no formulário e redireciona para a lista de funcionários.

3. **funcionario_delete**:
   - Exclui um funcionário específico.
   - Exibe uma mensagem de sucesso após a exclusão.

4. **setor_cadastro**:
   - Permite o cadastro de novos setores.
   - Valida os dados e associa o setor ao usuário que está criando.
   - Exibe uma lista de setores cadastrados.

5. **setor_edit**:
   - Carrega os dados de um setor existente para edição.
   - Salva as alterações feitas no formulário e redireciona para a lista de setores.

6. **setor_delete**:
   - Exclui um setor específico.
   - Exibe uma mensagem de sucesso após a exclusão.

7. **area_cadastro**:
   - Permite o cadastro de novas áreas.
   - Valida os dados e associa a área ao usuário que está criando.
   - Exibe uma lista de áreas cadastradas.

8. **area_edit**:
   - Carrega os dados de uma área existente para edição.
   - Salva as alterações feitas no formulário e redireciona para a lista de áreas.

9. **area_delete**:
   - Exclui uma área específica.
   - Exibe uma mensagem de sucesso após a exclusão.

### Modelos

1. **Area**:
   - Armazena informações sobre áreas, garantindo que cada área tenha um nome único.

2. **Setor**:
   - Relaciona-se com a área, armazenando informações sobre setores que pertencem a uma área específica, garantindo que cada setor tenha um nome único.

3. **Funcionario**:
   - Armazena informações sobre funcionários, incluindo matrícula, nome e o setor ao qual pertencem.
   - Relaciona-se com o modelo `CustomUser` para associar informações do usuário ao funcionário.

4. **AreaTrilha**:
   - Armazena informações sobre áreas de trilha, garantindo que cada área de trilha tenha um nome único.

