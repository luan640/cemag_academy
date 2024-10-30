## Gerenciamento de Acesso às Provas

> Consulte a documentação de [materiais](/documentacao/markdownGestores/materiais.md) para ver como entrar na aba de provas.

### Visualização do Administrador

- Na lista de provas, serão exibidas todas as provas atribuídas a essa trilha, mostrando o [certificado](/documentacao/markdownGestores/certificado.md) somente para colaboradores, supervisores (caso não tenham criado a trilha) e para o diretor.

- Funcionalidades incluem:
  - **Adicionar**: Adicionar novas provas.
  - **Visualizar**: Informações sobre os participantes.
  - **Excluir**: Provas existentes.

  ![Lista de Provas](/documentacao/imgs_documentacao/listaPROVAS.png)

- Ao clicar em visualizar prova, serão exibidas apenas as questões com os campos desabilitados, não sendo possível enviar nada, apenas visualizar a prova.

  ![Visualizar Prova](/documentacao/imgs_documentacao/visualizarPROVA.png)

> **Nota**: Caso seja necessário alterar alguma questão, consulte um dos desenvolvedores. Em versões futuras do sistema, vamos disponibilizar edições para casos de erro.

#### Lista de participantes
- Na lista de participantes, serão exibidos todos os funcionários atribuídos àquela prova.
- Se o funcionário realizou a prova, exibirá o status como ***prova realizada*** e a nota.

- Funcionalidades incluem:
  - **Refazer prova**: Exclui toda a prova realizada pelo colaborador.
  - **Corrigir questões dissertativas**: Direciona o ADM para uma página que permite corrigir a prova do usuário.

  ![Participantes da Prova](/documentacao/imgs_documentacao/participantePROVA.png)

> **Nota 1**: Enquanto o ADM não corrigir a prova dissertativa, ficará exibindo para o usuário "***aguardando correção da dissertativa***".
>
> **Nota 2**: É recomendado clicar em refazer a prova apenas se o usuário não atingiu o resultado esperado e necessitar fazer novamente, pois todas as informações da prova excluída serão perdidas.

### Visualização do Colaborador

- Na lista de provas, serão exibidas todas as provas atribuídas a essa trilha, mostrando o [certificado](/documentacao/markdownGestores/certificado.md) somente para colaboradores, supervisores (caso não tenham criado a trilha) e para o diretor.

- Funcionalidades incluem:
  - **Realizar**: Prova.
  - **Visualizar**: Prova com as respostas marcadas.

  ![Lista de Provas do Colaborador](/documentacao/imgs_documentacao/listcolPROVA.png)

> **Nota**: A opção de visualizar a prova só ficará disponível depois que a prova for realizada.

- Após o colaborador concluir uma prova que possui questões dissertativas, exibirá a mensagem "***aguardando correção da dissertativa***", que só sumirá quando o ADM entrar em "***corrigir questões dissertativas***" e der a nota ao colaborador.
- Esta prova abaixo possui 3 questões (2 objetivas e 1 dissertativa), cada uma valendo 1 ponto. Como o usuário acertou todas as objetivas, a nota exibida será baseada apenas nas questões objetivas, ficando aguardando a correção da dissertativa.
- Se a prova possuir apenas questões objetivas, a nota é imediata.

  ![Exemplo de Prova](/documentacao/imgs_documentacao/exemploPROVA.png)
