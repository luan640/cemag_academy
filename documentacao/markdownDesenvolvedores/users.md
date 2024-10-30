# Cemag Academy

## App de Core

Este documento fornece uma visão geral das views e URLs do aplicativo core do projeto Cemag Academy. Abaixo, apresentamos uma tabela com as URLs, suas respectivas views e uma breve descrição de cada uma.

| URL Name          | View                      | Descrição da View                                                                                                                                                                   |
|-------------------|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `login`           | `CustomLoginView`        | Esta view personalizada gerencia o login do usuário. Se o usuário já estiver autenticado, ele será desconectado antes de acessar a página de login. Em caso de erro, uma mensagem de erro é exibida.          |
| `logout`          | `CustomLogoutView`       | Esta view gerencia o logout do usuário, redirecionando para a página de login após a desconexão.                                                                                  |
| `create-user`     | `add_user`               | Esta view permite que um administrador crie um novo usuário. Ela verifica se a matrícula do funcionário existe, associa o usuário ao funcionário e exibe uma mensagem de sucesso ou erro, conforme necessário. |

## Estrutura das Views

### `CustomLoginView`

A classe `CustomLoginView` é responsável pelo processo de autenticação do usuário. Aqui estão suas funcionalidades:

- **Autenticação**: Usa um formulário personalizado (`CustomAuthenticationForm`) para verificar as credenciais do usuário.
- **Logout prévio**: Se o usuário já estiver logado, ele será desconectado ao acessar a página de login.
- **Mensagens de erro**: Caso a matrícula ou a senha estejam incorretas, uma mensagem de erro será exibida.

### `CustomLogoutView`

A classe `CustomLogoutView` gerencia o logout do usuário:

- **Redirecionamento**: Após o logout, o usuário é redirecionado para a página de login.

### `add_user`

A função `add_user` permite ao administrador adicionar novos usuários ao sistema:

- **Verificação de Permissões**: Apenas usuários do tipo 'ADM' podem acessar esta view.
- **Formulário de Criação**: Utiliza o `CustomUserCreationForm` para criar um novo usuário.
- **Validação de Matrícula**: Verifica se a matrícula informada já está associada a um funcionário existente. Se não houver funcionário correspondente, uma mensagem de erro é exibida.
- **Associação de Usuário**: Se a matrícula for válida, o novo usuário é criado e associado ao funcionário correspondente.

### `custom_404`

A função `custom_404` renderiza uma página 404 personalizada quando uma URL não é encontrada.

## Modelos

### `CustomUser`

A classe `CustomUser` estende `AbstractBaseUser` e `PermissionsMixin` para gerenciar usuários personalizados:

- **Campos**: Inclui campos como `matricula`, `first_name`, `last_name`, `email`, `type`, `is_active`, `is_staff` e `is_superuser`.
- **Gerenciador**: Utiliza o `CustomUserManager` para criar usuários e superusuários.

### `CustomUserManager`

O `CustomUserManager` gerencia a criação de usuários e superusuários:

- **Criação de Usuário**: O método `create_user` cria um usuário com a matrícula e senha fornecidas.
- **Criação de Superusuário**: O método `create_superuser` garante que o superusuário tenha as permissões adequadas.