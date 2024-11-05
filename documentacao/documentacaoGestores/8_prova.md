## Gerenciamento de Acesso às Provas

### Visualização do Administrador ou Supervisor que criou a trilha

#### Acesso a prova
 - Para ter acesso a área de provas deverá clicar em visualizar provas.

![alt text](/documentacao/imgs_documentacao/entraradmPROVA.png)

#### Criar prova

- O botão de Add Prova vai encaminhar para uma página de criação de prova.
- Poderá adicionar quantas questões quiser, sendo elas objetiva e dissertativa.
- Ao clicar em **➕**, será adicionada uma nova questão e ao clicar em 🗑️, a última questão criada será removida.
- Como mensionado anteriormente, terá dois tipos de questões, dissertativa e objetiva, ao selecionar objetiva em "**Tipo**", exibirá dois botões, ***Adicionar alternativa*** e ***Excluir alternativa*** (para remover a última alternativa criada).
- Ao clicar em ✅, será encaminhado para a lista de provas e vai criar a nova prova. 

![alt text](/documentacao/imgs_documentacao/criarPROVA.png)

![alt text](/documentacao/imgs_documentacao/adicionarALTERNATIVA.png)

>**Nota**: Fiquem atentos na hora de criar a prova, por enquanto não tem nenhuma área para administradores editarem as questões, mas caso aconteça qualquer tipo de erro, entrar em contato com um dos desenvolvedores para aplicar essas edições.

#### Lista de provas

- Na lista de provas, serão exibidas todas as provas atribuídas a essa trilha, mostrando o [certificado](/documentacao/documentacaoGestores/certificado.md) somente para colaboradores, supervisores (caso não tenham criado a trilha) e para o diretor.

- Funcionalidades incluem:
  - **Visualizar**: provas criadas. 
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

#### Acesso a prova
 - Para ter acesso a área de provas deverá clicar em Provas disponíveis, esse botão só estará disponível se todos os campos de ***Marcar como visualizado*** estiverem marcados.

![alt text](/documentacao/imgs_documentacao/entrarcolPROVA.png)

#### Lista de provas

- Na lista de provas, serão exibidas todas as provas atribuídas a essa trilha, mostrando o [certificado](/documentacao/documentacaoGestores/certificado.md) somente para colaboradores, supervisores (caso não tenham criado a trilha) e para o diretor.

- Funcionalidades incluem:
  - **Realizar**: Prova.
  - **Visualizar**: Prova com as respostas marcadas.

  ![Lista de Provas do Colaborador](/documentacao/imgs_documentacao/listcolPROVA.png)

> **Nota**: A opção de visualizar a prova só ficará disponível depois que a prova for realizada.

- Após o colaborador concluir uma prova que possui questões dissertativas, exibirá a mensagem "***aguardando correção da dissertativa***", que só sumirá quando o ADM entrar em "***corrigir questões dissertativas***" e der a nota ao colaborador.
- Esta prova abaixo possui 3 questões (2 objetivas e 1 dissertativa), cada uma valendo 1 ponto. Como o usuário acertou todas as objetivas, a nota exibida será baseada apenas nas questões objetivas, ficando aguardando a correção da dissertativa.
- Se a prova possuir apenas questões objetivas, a nota é imediata.

  ![Exemplo de Prova](/documentacao/imgs_documentacao/exemploPROVA.png)

---

[Página anterior](/documentacao/documentacaoGestores/7_jornada.md) --- [Próxima Página](/documentacao/documentacaoGestores/9_certificado.md)