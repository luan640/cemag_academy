  document.getElementById('filtrar_funcionario').addEventListener('click', function() {
    const inputElement = document.getElementById('filterInput');
    const funcionarioNome = inputElement.value;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Recupera todas as opções do datalist
    const options = Array.from(document.querySelectorAll('#encodings option'));
    // Encontra a opção que corresponde ao nome digitado
    const option = options.find(opt => opt.value === funcionarioNome);

    if (option) {
      const funcionarioMatricula = option.getAttribute('data-matricula');

    // Envia uma requisição para o backend com o id do funcionário
    fetch(`/materiais/jornada/detail/${funcionarioMatricula}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': '{{ csrf_token }}', // CSRF Token se necessário
      }
    })
    .then(response => response.json())
    .then(data => {
      const listGroupOne = document.querySelector('#collapseOne .list-group');
      listGroupOne.innerHTML = ''; // Limpa a lista existente
      const notificationOne = document.getElementById("notificationOne")
      notificationOne.textContent = data.lista_livros_visualizados.length;

      if (data.lista_livros_visualizados.length > 0) {
        data.lista_livros_visualizados.forEach(livro => {
          const listItem = document.createElement('li');
          listItem.className = 'list-group-item';
          listItem.innerHTML =`<div class="row">
                                  <div class="col-sm-10">
                                    ${livro.livro_titulo} 
                                  </div>
                                  <div class="col-sm-2">
                                    <strong>${livro.rating}/5</strong>
                                  </div>
                                </div>` ;
          listGroupOne.appendChild(listItem);
        });
      } else {
        listGroupOne.innerHTML = '<li class="list-group-item">Nenhum livro visualizado.</li>';
      }
      const listGroupFour = document.querySelector('#collapseFour .list-group');
      listGroupFour.innerHTML = ''; // Limpa a lista existente
      const notificationFour = document.getElementById("notificationFour");
      notificationFour.textContent = data.lista_provas_realizadas.length;

      const getClassForNota = (nota) => {
        if (nota >= 7) return 'bg-success';   // Verde
        if (nota >= 5) return 'bg-warning';   // Amarelo
        return 'bg-danger';                   // Vermelho
      };

      if (data.lista_provas_realizadas.length > 0) {
        data.lista_provas_realizadas.forEach(prova => {
          console.log(prova)
          const listItem = document.createElement('form');
          listItem.method = 'POST';
          listItem.action = `/avaliacao/${prova.id}/visualizar-prova/${funcionarioMatricula}/`;  // Nova rota sem parâmetros na URL

          // Adiciona o CSRF token ao formulário
          const csrfTokenInput = document.createElement('input');
          csrfTokenInput.type = 'hidden';
          csrfTokenInput.name = 'csrfmiddlewaretoken';
          csrfTokenInput.value = csrfToken;  // Usa o token obtido da meta tag
          listItem.appendChild(csrfTokenInput);

          const notaClass = getClassForNota(prova.nota_final);

          // Adiciona um botão ao formulário que pode ser estilizado como um link ou botão
          const submitButton = document.createElement('button');
          submitButton.type = 'submit';
          submitButton.className = 'list-group-item list-group-item-action';
          submitButton.innerHTML =  `<div class="d-flex justify-content-between align-items-center">
                                        <h5>${prova.prova_titulo}</h5>
                                        <span class="rounded-circle d-inline-block text-white text-center ${notaClass}" style="width: 30px; height: 30px; line-height: 30px; font-size: 14px; font-weight: bold;">${prova.nota_final}</span>
                                    </div>`;

          listItem.appendChild(submitButton)
          listGroupFour.appendChild(listItem);
        });
      } else {
        const noItem = document.createElement('a');
        noItem.className = 'list-group-item list-group-item-action';
        noItem.href = '#';
        noItem.textContent = 'Nenhuma prova realizada.';
        listGroupFour.appendChild(noItem);
      }
      // Atualize a página ou faça algo com os dados retornados
      const listGroupFive = document.querySelector('#collapseFive .list-group');
      listGroupFive.innerHTML = ''; // Limpa a lista existente
      const notificationFive = document.getElementById("notificationFive")
      notificationFive.textContent = data.lista_materiais_visualizados.length

      if (data.lista_materiais_visualizados.length > 0) {
        data.lista_materiais_visualizados.forEach(material => {
          const listItem = document.createElement('li');
          listItem.className = 'list-group-item';
          listItem.textContent = material;
          listGroupFive.appendChild(listItem);
        });
      } else {
        listGroupFive.innerHTML = '<li class="list-group-item">Nenhum material visualizado.</li>';
      }
      const listGroupCertificado = document.querySelector('#collapseCertificado .list-group');
      listGroupCertificado.innerHTML = ''; // Limpa a lista existente
      const notificationCertificado = document.getElementById("notificationCertificado");

      // Filtra apenas as pastas certificadas com valor True
      const pastasCertificadasTrue = Object.keys(data.pastas_certificadas).filter(pasta => data.pastas_certificadas[pasta].certificado === true);

      notificationCertificado.textContent = pastasCertificadasTrue.length;

      if (pastasCertificadasTrue.length > 0) {
        pastasCertificadasTrue.forEach(pasta => {
          const certificadoInfo = data.pastas_certificadas[pasta];
          const provaId = certificadoInfo.provas[0];  // Assumindo que você passa o ID da prova no JSON
          const pastaId = certificadoInfo.pasta_id;

          const listItem = document.createElement('form');
          listItem.method = 'POST';
          listItem.action = '/materiais/pasta/certificado/';  // Nova rota sem parâmetros na URL
          listItem.target = '_blank';  // Para abrir em uma nova aba, como antes

          // Adiciona o CSRF token ao formulário
          const csrfTokenInput = document.createElement('input');
          csrfTokenInput.type = 'hidden';
          csrfTokenInput.name = 'csrfmiddlewaretoken';
          csrfTokenInput.value = csrfToken;  // Usa o token obtido da meta tag
          listItem.appendChild(csrfTokenInput);

          // Adiciona os dados ocultos (prova_id, pasta_id e matricula)
          const provaIdInput = document.createElement('input');
          provaIdInput.type = 'hidden';
          provaIdInput.name = 'prova_id';
          provaIdInput.value = provaId;
          listItem.appendChild(provaIdInput);

          const pastaIdInput = document.createElement('input');
          pastaIdInput.type = 'hidden';
          pastaIdInput.name = 'pasta_id';
          pastaIdInput.value = pastaId;
          listItem.appendChild(pastaIdInput);

          const matriculaInput = document.createElement('input');
          matriculaInput.type = 'hidden';
          matriculaInput.name = 'matricula';
          matriculaInput.value = funcionarioMatricula;
          listItem.appendChild(matriculaInput);

          // Adiciona um botão ao formulário que pode ser estilizado como um link ou botão
          const submitButton = document.createElement('button');
          submitButton.type = 'submit';
          submitButton.className = 'list-group-item list-group-item-action btn btn-link';
          submitButton.innerHTML = `<strong>Trilha: </strong>${pasta}`;

          listItem.appendChild(submitButton);
          listGroupCertificado.appendChild(listItem);
        });
      } else {
        listGroupCertificado.innerHTML = '<li class="list-group-item">Nenhuma pasta certificada.</li>';
      }

      const listGroupSix = document.querySelector('#collapseSix .list-group');
      listGroupSix.innerHTML = ''; // Limpa a lista existente
      const notificationSix = document.getElementById("notificationSix");
      const notification_dot = document.getElementById("notification-dot");
      notificationSix.textContent = data.dict_avaliacao_eficacia.trilhas.length;
      const hasFalseRH = data.dict_avaliacao_eficacia.avaliacoes_rh.some(avaliacao => avaliacao === false);
      if (hasFalseRH) {
          notification_dot.style.display = 'block';
      } else {
          notification_dot.style.display = 'none';
      }

      if (data.dict_avaliacao_eficacia.trilhas.length > 0) {
        data.dict_avaliacao_eficacia.trilhas.forEach((trilha, index) => {
          const listItem = document.createElement('form');
          listItem.method = 'POST';
          listItem.action = `/materiais/avaliacao/respostas-avaliacao/${data.dict_avaliacao_eficacia.avaliacoes_id[index]}/`;  // Nova rota sem parâmetros na URL

          // Adiciona o CSRF token ao formulário
          const csrfTokenInput = document.createElement('input');
          csrfTokenInput.type = 'hidden';
          csrfTokenInput.name = 'csrfmiddlewaretoken';
          csrfTokenInput.value = csrfToken;  // Usa o token obtido da meta tag
          listItem.appendChild(csrfTokenInput);

          // Adiciona um botão ao formulário que pode ser estilizado como um link ou botão
          const submitButton = document.createElement('button');
          submitButton.type = 'submit';
          submitButton.className = 'list-group-item list-group-item-action';
          submitButton.innerHTML = `<strong>${trilha}</strong><br>Avaliado pelo Supervisor: ${data.dict_avaliacao_eficacia.avaliacoes_supervisor[index] ? 
          '<i class="fa-solid fa-circle-check" style="color: #63E6BE;"></i>' : '<i class="fa-solid fa-circle-xmark" style="color: #ff4242;"></i>'}<br>Avaliado pelo RH  : ${data.dict_avaliacao_eficacia.avaliacoes_rh[index] 
          ? '<i class="fa-solid fa-circle-check" style="color: #63E6BE;"></i>' : '<i class="fa-solid fa-circle-xmark" style="color: #ff4242;"></i>'}`;

          listItem.appendChild(submitButton)
          listGroupSix.appendChild(listItem);
        });
      } else {
        listGroupSix.innerHTML = '<li class="list-group-item">Nenhuma trilha avaliada.</li>';
      }
    }).catch(error => {
      console.error('Erro:', error)
      alert("Usuário não encontrado.");
    });
  } else {
    alert("Funcionário não encontrado.");
  }
});