document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

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
            return; // Interrompe a execução da função
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
                text: "O enunciado não pode estar vazio!",
              });
            return; // Interrompe a execução da função
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
            alternativas: []
        };

        alternativas.forEach(alternativa => {
            const textarea = alternativa.querySelector('textarea');
            dadosAlterados.alternativas.push({
                id: alternativa.querySelector('input').id.split('_')[1],
                texto: textarea.value
            });
        });

        // Envia os dados para o backend
        fetch(`/avaliacao/${questaoId}/editar-questoes-alternativas/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Adiciona o token CSRF
            },
            body: JSON.stringify(dadosAlterados)
        })
        .then(response => response.json())
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
                // Atualiza a interface se necessário
                const enunciado = document.getElementById(`enunciado_${questaoId}`);
                enunciado.innerText = inputEnunciado.value;
                alternativas.forEach((alternativa, index) => {
                    const label = alternativa.querySelector('label');
                    label.innerText = dadosAlterados.alternativas[index].texto;
                });
                // Restaura o estado original
                document.getElementById(`editar_enunciado_${questaoId}`).style.display = 'inline';
                document.getElementById(`botoes_edicao_${questaoId}`).style.display = 'none';
                enunciado.style.display = 'block';
                inputEnunciado.style.display = 'none';
                alternativas.forEach(alternativa => {
                    const label = alternativa.querySelector('label');
                    const textarea = alternativa.querySelector('textarea');
                    label.style.display = 'block';
                    textarea.style.display = 'none';
                });
            } else {
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
                    icon: "error",
                    title: "Erro ao editar a questão"
                  });
            }
        })
        .catch(error => {
            console.error('Erro:', error);
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
                icon: "error",
                title: "Erro ao editar a a questão"
              });
        })
        .finally(() => {
            // Restaura o ícone de lápis e oculta o spinner
            pencilIcon.style.display = 'inline-block';
            linkSalvar.disabled = false;
            spinner.style.display = 'none';
        });
    }

    // Adiciona o evento de clique ao botão "Salvar" apenas uma vez
    document.addEventListener('click', function(event) {
        if (event.target && event.target.id.startsWith('salvar_edicao_')) {
            const questaoId = event.target.id.split('_')[2];
            salvarEdicao(questaoId);
        }
    });

    // Adiciona o evento de clique ao link de edição
    const editLinks = document.querySelectorAll('[id^="editar_enunciado_"]');
    editLinks.forEach(link => {
        link.addEventListener('click', function() {
            const questaoId = this.id.split('_')[2]; // Extrai o ID da questão
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

            inputEnunciado.style.height = 'auto'; // Redefine a altura para recalcular
            inputEnunciado.style.height = enunciado.scrollHeight + 'px';
            // Define o valor do textarea com o conteúdo ajustado
            inputEnunciado.value = conteudo;

            enunciado.style.display = 'none';

            // Habilita apenas as alternativas da questão selecionada
            const alternativas = questaoDiv.querySelectorAll('.alternativa');
            alternativas.forEach(alternativa => {
                const label = alternativa.querySelector('label');
                const textarea = alternativa.querySelector('textarea');
                label.style.display = 'none';
                textarea.style.display = 'block';
                textarea.value = label.innerText; // Preenche o textarea com o texto da alternativa
            });

            // Botão de Cancelar
            const botaoCancelar = document.getElementById(`cancelar_edicao_${questaoId}`);
            botaoCancelar.addEventListener('click', function() {
                // Restaura o estado original
                linkEditar.style.display = 'inline';
                botoesEdicao.style.display = 'none';
                enunciado.style.display = 'block';
                inputEnunciado.style.display = 'none';
                alternativas.forEach(alternativa => {
                    const label = alternativa.querySelector('label');
                    const textarea = alternativa.querySelector('textarea');
                    label.style.display = 'block';
                    textarea.style.display = 'none';
                });
            });
        });
    });
});