document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let contadorNovasAlternativas = 0;

    // Função para salvar a edição
    function salvarEdicao(questaoId) {
        const questaoDiv = document.getElementById(`questao_${questaoId}`);
        const inputEnunciado = document.getElementById(`input_enunciado_${questaoId}`);
        const alternativas = questaoDiv.querySelectorAll('.alternativa');

        // Verifica se o enunciado está vazio
        if (inputEnunciado.value.trim() === '') {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "O enunciado não pode estar vazio!",
              });
            return;
        }

        // Verifica se há pelo menos 2 alternativas
        if (alternativas.length < 2) {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "A questão deve ter no mínimo 2 alternativas!",
              });
            return;
        }

        // Verifica se alguma alternativa está vazia
        let alternativaVazia = false;
        alternativas.forEach(alternativa => {
            const textarea = alternativa.querySelector('textarea');
            if (textarea.value.trim() === '') {
                alternativaVazia = true;
            }
        });

        if (alternativaVazia) {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Nenhuma alternativa pode estar vazia!",
              });
            return;
        }
        
        // Verifica se pelo menos uma alternativa está marcada como correta
        const radioCorreta = questaoDiv.querySelector('input[name="alternativa_correta_' + questaoId + '"]:checked');
        if (!radioCorreta) {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Você deve marcar qual é a alternativa correta!",
              });
            return;
        }

        // Mostra o spinner e oculta o ícone de lápis
        const linkSalvar = document.getElementById(`salvar_edicao_${questaoId}`);
        const spinner = linkSalvar.querySelector('.spinner-border');
        const linkEditar = document.getElementById(`editar_enunciado_${questaoId}`);
        const pencilIcon = linkEditar.querySelector('.fa-pencil');

        linkSalvar.disabled = true;
        pencilIcon.style.display = 'none';
        spinner.style.display = 'inline-block';

        // Coleta os dados alterados
        const dadosAlterados = {
            questao_id: questaoId,
            enunciado: inputEnunciado.value,
            alternativas: [],
            alternativa_correta_id: null
        };
        
        // Define qual alternativa está marcada como correta
        if (radioCorreta) {
            dadosAlterados.alternativa_correta_id = radioCorreta.value;
        }

        alternativas.forEach(alternativa => {
            const textarea = alternativa.querySelector('textarea');
            const alternativaId = alternativa.getAttribute('data-alternativa-id');
            
            const alternativaData = {
                texto: textarea.value
            };
            
            // Só adiciona o ID se não for uma nova alternativa
            if (alternativaId && !alternativaId.startsWith('nova_')) {
                alternativaData.id = parseInt(alternativaId);
            } else if (alternativaId && alternativaId.startsWith('nova_')) {
                // Para novas alternativas, adicionar o ID temporário para mapeamento
                alternativaData.temp_id = alternativaId;
            }
            
            dadosAlterados.alternativas.push(alternativaData);
        });

        // Envia os dados para o backend
        fetch(`/avaliacao/${questaoId}/editar-questoes-alternativas/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(dadosAlterados)
        })
        .then(response => {
            if (response.status === 403) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Não é possível editar esta prova pois já foi realizada por alguém.');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const Toast = Swal.mixin({
                    toast: true,
                    position: "bottom-end",
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true,
                    didOpen: (toast) => {
                      toast.onmouseenter = Swal.stopTimer;
                      toast.onmouseleave = Swal.resumeTimer;
                    }
                  });
                  Toast.fire({
                    icon: "success",
                    title: "Questão editada com sucesso"
                  });
                
                // Recarrega a página para refletir as mudanças
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                throw new Error(data.error || 'Erro ao editar a questão');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            Swal.fire({
                icon: "error",
                title: "Erro",
                text: error.message || "Erro ao editar a questão"
              });
        })
        .finally(() => {
            // Restaura o ícone de lápis e oculta o spinner
            pencilIcon.style.display = 'inline-block';
            linkSalvar.disabled = false;
            spinner.style.display = 'none';
        });
    }

    // Função para adicionar nova alternativa
    function adicionarAlternativa(questaoId) {
        const optionList = document.getElementById(`option-list-${questaoId}`);
        const novaAlternativaId = `nova_${contadorNovasAlternativas++}`;
        
        const novaAlternativa = document.createElement('label');
        novaAlternativa.className = 'option-item d-flex align-items-center gap-3 alternativa';
        novaAlternativa.setAttribute('data-alternativa-id', novaAlternativaId);
        novaAlternativa.setAttribute('data-correta', 'false');
        
        novaAlternativa.innerHTML = `
            <div class="option-marker">
                <input type="radio" id="alternativa_${novaAlternativaId}" name="questao_${questaoId}" value="${novaAlternativaId}" disabled>
            </div>
            <div class="option-body w-100">
                <div id="label_alternativa_${novaAlternativaId}" class="option-text d-flex align-items-center gap-2" style="display: none;"></div>
                <textarea id="textarea_alternativa_${novaAlternativaId}" type="text" class="form-control mt-2" rows="1" style="width: 100%; display: block;" placeholder="Digite o texto da alternativa"></textarea>
            </div>
            <div class="d-flex gap-2">
                <input type="radio" 
                       class="form-check-input alternativa-correta-radio" 
                       name="alternativa_correta_${questaoId}"
                       value="${novaAlternativaId}"
                       data-questao-id="${questaoId}"
                       style="display: inline-block; cursor: pointer; width: 20px; height: 20px;"
                       title="Marcar como resposta correta">
                <button type="button" class="btn btn-sm btn-outline-danger btn-excluir-alternativa" data-alternativa-id="${novaAlternativaId}" style="display: inline-block;">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `;
        
        optionList.appendChild(novaAlternativa);
    }

    // Função para excluir alternativa
    function excluirAlternativa(alternativaId, questaoId) {
        const alternativa = document.querySelector(`.alternativa[data-alternativa-id="${alternativaId}"]`);
        const questaoDiv = document.getElementById(`questao_${questaoId}`);
        const alternativasRestantes = questaoDiv.querySelectorAll('.alternativa');
        
        if (alternativasRestantes.length <= 2) {
            Swal.fire({
                icon: "warning",
                title: "Atenção",
                text: "A questão deve ter no mínimo 2 alternativas!",
              });
            return;
        }
        
        Swal.fire({
            title: 'Tem certeza?',
            text: "Esta alternativa será removida!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sim, excluir!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                alternativa.remove();
                Swal.fire({
                    icon: "success",
                    title: "Removida!",
                    text: "A alternativa foi removida. Clique em 'Salvar' para confirmar as alterações.",
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        });
    }

    // Adiciona o evento de clique ao botão "Salvar"
    document.addEventListener('click', function(event) {
        if (event.target && event.target.id.startsWith('salvar_edicao_')) {
            const questaoId = event.target.id.split('_')[2];
            salvarEdicao(questaoId);
        }
        
        // Evento para adicionar alternativa
        if (event.target && event.target.closest('.btn-adicionar-alternativa')) {
            const btn = event.target.closest('.btn-adicionar-alternativa');
            const questaoId = btn.getAttribute('data-questao-id');
            adicionarAlternativa(questaoId);
        }
        
        // Evento para excluir alternativa
        if (event.target && event.target.closest('.btn-excluir-alternativa')) {
            const btn = event.target.closest('.btn-excluir-alternativa');
            const alternativaId = btn.getAttribute('data-alternativa-id');
            // Encontra o questaoId da alternativa
            const alternativa = btn.closest('.alternativa');
            const questaoDiv = alternativa.closest('[id^="questao_"]');
            const questaoId = questaoDiv.id.split('_')[1];
            excluirAlternativa(alternativaId, questaoId);
        }
    });

    // Adiciona o evento de clique ao link de edição
    const editLinks = document.querySelectorAll('[id^="editar_enunciado_"]');
    editLinks.forEach(link => {
        link.addEventListener('click', function() {
            const questaoId = this.id.split('_')[2];
            const questaoDiv = document.getElementById(`questao_${questaoId}`);

            // Oculta o link de edição e exibe os botões de edição
            const linkEditar = document.getElementById(`editar_enunciado_${questaoId}`);
            const botoesEdicao = document.getElementById(`botoes_edicao_${questaoId}`);
            linkEditar.style.display = 'none';
            botoesEdicao.style.display = 'block';

            // Oculta o enunciado e exibe o input do enunciado
            const enunciado = document.getElementById(`enunciado_${questaoId}`);
            const inputEnunciado = document.getElementById(`input_enunciado_${questaoId}`);
            inputEnunciado.style.display = 'block';
            let conteudo = enunciado.innerHTML;
            conteudo = conteudo.replace(/<br\s*\/?>/gi, '\n');
            conteudo = conteudo.replace(/<[^>]+>/g, '');

            inputEnunciado.style.height = 'auto';
            inputEnunciado.style.height = enunciado.scrollHeight + 'px';
            inputEnunciado.value = conteudo;
            enunciado.style.display = 'none';

            // Habilita as alternativas e mostra botões de ação
            const alternativas = questaoDiv.querySelectorAll('.alternativa');
            alternativas.forEach(alternativa => {
                const label = alternativa.querySelector('.option-text');
                const textarea = alternativa.querySelector('textarea');
                const btnExcluir = alternativa.querySelector('.btn-excluir-alternativa');
                const radioCorreta = alternativa.querySelector('.alternativa-correta-radio');
                
                label.style.display = 'none';
                textarea.style.display = 'block';
                
                // Remove o badge de "Correta" do texto antes de colocar no textarea
                let textoLimpo = label.textContent || label.innerText;
                textoLimpo = textoLimpo.replace(/Correta\s*$/i, '').trim();
                textarea.value = textoLimpo;
                
                if (btnExcluir) {
                    btnExcluir.style.display = 'inline-block';
                }
                
                if (radioCorreta) {
                    radioCorreta.style.display = 'inline-block';
                }
            });
            
            // Mostra o botão de adicionar alternativa
            const botoesAlternativa = document.getElementById(`botoes-alternativa-${questaoId}`);
            if (botoesAlternativa) {
                botoesAlternativa.style.display = 'block';
            }

            // Botão de Cancelar
            const botaoCancelar = document.getElementById(`cancelar_edicao_${questaoId}`);
            botaoCancelar.onclick = function() {
                Swal.fire({
                    title: 'Cancelar edição?',
                    text: "As alterações não salvas serão perdidas!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#6c757d',
                    confirmButtonText: 'Sim, cancelar!',
                    cancelButtonText: 'Continuar editando'
                }).then((result) => {
                    if (result.isConfirmed) {
                        location.reload();
                    }
                });
            };
        });
    });
});