let questaoCounter = 1;
let alternativaCounter = 1;

function adicionarQuestao() {
    const questoesContainer = document.getElementById('questoes-container');
    const questaoIndex = questoesContainer.children.length;

    const questaoDiv = document.createElement('div');
    questaoDiv.className = 'questao exam-question-card';
    questaoDiv.setAttribute('data-questao-index', questaoIndex);
    questaoDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-3">
            <h5 class="mb-0">Questão ${questaoIndex + 1}</h5>
            <button class="btn btn-outline-danger btn-sm" type="button" onclick="excluirQuestao(this)" title="Excluir esta questão">
                <i class="fa-solid fa-trash"></i>
            </button>
        </div>
        <div class="row">
            <div class="col-sm-6 mb-4">
                <label for="questao-${questaoIndex}-enunciado">Enunciado da questão</label>
                <textarea class="form-control" id="questao-${questaoIndex}-enunciado" name="questoes[${questaoIndex}][enunciado]" required></textarea>
            </div>
            <div class="col-sm-5 mb-4">
                <label for="questao-${questaoIndex}-tipo">Tipo</label>
                <select class="form-control" id="questao-${questaoIndex}-tipo" name="questoes[${questaoIndex}][tipo]" onchange="selecionarTipoQuestao(this, ${questaoIndex})" required>
                    <option value="dissertativa">Dissertativa</option>
                    <option value="objetiva">Objetiva</option>
                </select>
            </div>
        </div>

        <div id="alternativas-container-${questaoIndex}" style="display: none;">
            <h5>Alternativas</h5>
            <div class="d-flex flex-wrap gap-2 mb-3">
                <button class="btn btn-outline-secondary btn-sm" type="button" onclick="adicionarAlternativa(${questaoIndex})">Adicionar alternativa</button>
                <button class="btn btn-outline-danger btn-sm" type="button" onclick="excluirUltimaAlternativa(${questaoIndex})">Excluir última alternativa</button>
            </div>
            <div class="alternativas"></div>
        </div>
        <hr>
    `;
    questoesContainer.appendChild(questaoDiv);
    atualizarNumeracaoQuestoes();
}

function excluirQuestao(botaoElement) {
    const questoesContainer = document.getElementById('questoes-container');
    const totalQuestoes = questoesContainer.children.length;
    
    if (totalQuestoes > 1) {
        // Confirmação antes de excluir
        if (confirm('Tem certeza que deseja excluir esta questão?')) {
            // Remove a questão específica
            const questaoDiv = botaoElement.closest('.questao');
            questaoDiv.remove();
            
            // Atualiza a numeração e os índices
            atualizarNumeracaoQuestoes();
        }
    } else {
        alert("É necessário ter pelo menos uma questão na prova.");
    }
}

function excluirUltimaQuestao() {
    const questoesContainer = document.getElementById('questoes-container');
    const totalQuestoes = questoesContainer.children.length;
    
    if (totalQuestoes > 1) {
        if (confirm('Tem certeza que deseja excluir a última questão?')) {
            questoesContainer.lastChild.remove();
            atualizarNumeracaoQuestoes();
        }
    } else {
        alert("É necessário ter pelo menos uma questão na prova.");
    }
}

function atualizarNumeracaoQuestoes() {
    const questoesContainer = document.getElementById('questoes-container');
    const questoes = questoesContainer.querySelectorAll('.questao');
    
    questoes.forEach((questaoDiv, novoIndex) => {
        // Atualiza o atributo data
        questaoDiv.setAttribute('data-questao-index', novoIndex);
        
        // Atualiza o título da questão
        const tituloQuestao = questaoDiv.querySelector('h5');
        if (tituloQuestao) {
            tituloQuestao.textContent = `Questão ${novoIndex + 1}`;
        }
        
        // Atualiza os IDs e names dos elementos
        const enunciado = questaoDiv.querySelector('textarea');
        if (enunciado) {
            enunciado.id = `questao-${novoIndex}-enunciado`;
            enunciado.name = `questoes[${novoIndex}][enunciado]`;
        }
        
        const tipoSelect = questaoDiv.querySelector('select');
        if (tipoSelect) {
            tipoSelect.id = `questao-${novoIndex}-tipo`;
            tipoSelect.name = `questoes[${novoIndex}][tipo]`;
            tipoSelect.setAttribute('onchange', `selecionarTipoQuestao(this, ${novoIndex})`);
        }
        
        // Atualiza o container de alternativas
        const alternativasContainer = questaoDiv.querySelector('[id^="alternativas-container-"]');
        if (alternativasContainer) {
            alternativasContainer.id = `alternativas-container-${novoIndex}`;
            
            // Atualiza os botões de adicionar/excluir alternativas
            const btnAdicionar = alternativasContainer.querySelector('button[onclick*="adicionarAlternativa"]');
            if (btnAdicionar) {
                btnAdicionar.setAttribute('onclick', `adicionarAlternativa(${novoIndex})`);
            }
            
            const btnExcluir = alternativasContainer.querySelector('button[onclick*="excluirUltimaAlternativa"]');
            if (btnExcluir) {
                btnExcluir.setAttribute('onclick', `excluirUltimaAlternativa(${novoIndex})`);
            }
            
            // Atualiza as alternativas existentes
            const alternativas = alternativasContainer.querySelectorAll('.alternativa');
            alternativas.forEach((alt, altIndex) => {
                const inputTexto = alt.querySelector('input[type="text"]');
                const inputCheckbox = alt.querySelector('input[type="checkbox"]');
                const labelTexto = alt.querySelector('label[for*="texto"]');
                const labelCheckbox = alt.querySelector('label[for*="correta"]');
                
                if (inputTexto) {
                    inputTexto.id = `questao-${novoIndex}-alternativa-${altIndex}-texto`;
                    inputTexto.name = `questoes[${novoIndex}][alternativas][${altIndex}][texto]`;
                }
                
                if (inputCheckbox) {
                    inputCheckbox.id = `questao-${novoIndex}-alternativa-${altIndex}-correta`;
                    inputCheckbox.name = `questoes[${novoIndex}][alternativas][${altIndex}][correta]`;
                }
                
                if (labelTexto) {
                    labelTexto.setAttribute('for', `questao-${novoIndex}-alternativa-${altIndex}-texto`);
                }
                
                if (labelCheckbox) {
                    labelCheckbox.setAttribute('for', `questao-${novoIndex}-alternativa-${altIndex}-correta`);
                }
            });
        }
    });
}

// Certifique-se de que as alternativas têm IDs e names únicos
function adicionarAlternativa(questaoIndex) {
    const alternativasContainer = document.querySelector(`#alternativas-container-${questaoIndex} .alternativas`);
    const alternativaIndex = alternativasContainer.children.length;

    const alternativaDiv = document.createElement('div');
    alternativaDiv.className = 'alternativa mb-3';
    alternativaDiv.innerHTML = `
        <div class="row align-items-center">
            <div class="col-sm-8 mb-2">
                <label for="questao-${questaoIndex}-alternativa-${alternativaIndex}-texto">Alternativa ${alternativaIndex + 1}</label>
                <input class="form-control" type="text" id="questao-${questaoIndex}-alternativa-${alternativaIndex}-texto" name="questoes[${questaoIndex}][alternativas][${alternativaIndex}][texto]" required>
            </div>
            <div class="col-sm-2 mb-2">
                <label for="questao-${questaoIndex}-alternativa-${alternativaIndex}-correta">Correta</label>
                <input type="checkbox" class="form-check-input" id="questao-${questaoIndex}-alternativa-${alternativaIndex}-correta" name="questoes[${questaoIndex}][alternativas][${alternativaIndex}][correta]">
            </div>
            <div class="col-sm-2 mb-2">
                <button class="btn btn-outline-danger btn-sm w-100" type="button" onclick="excluirAlternativa(this, ${questaoIndex})" title="Excluir esta alternativa">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    alternativasContainer.appendChild(alternativaDiv);
    atualizarNumeracaoAlternativas(questaoIndex);
}

function excluirAlternativa(botaoElement, questaoIndex) {
    const alternativasContainer = document.querySelector(`#alternativas-container-${questaoIndex} .alternativas`);
    const totalAlternativas = alternativasContainer.children.length;

    if (totalAlternativas > 0) {
        if (confirm('Tem certeza que deseja excluir esta alternativa?')) {
            const alternativaDiv = botaoElement.closest('.alternativa');
            alternativaDiv.remove();
            atualizarNumeracaoAlternativas(questaoIndex);
        }
    }
}

function excluirUltimaAlternativa(questaoIndex) {
    const alternativasContainer = document.querySelector(`#alternativas-container-${questaoIndex} .alternativas`);
    const totalAlternativas = alternativasContainer.children.length;

    if (totalAlternativas > 0) {
        if (confirm('Tem certeza que deseja excluir a última alternativa?')) {
            alternativasContainer.lastChild.remove();
            atualizarNumeracaoAlternativas(questaoIndex);
        }
    } else {
        alert("Não há mais alternativas para remover.");
    }
}

function atualizarNumeracaoAlternativas(questaoIndex) {
    const alternativasContainer = document.querySelector(`#alternativas-container-${questaoIndex} .alternativas`);
    const alternativas = alternativasContainer.querySelectorAll('.alternativa');
    
    alternativas.forEach((alt, altIndex) => {
        const inputTexto = alt.querySelector('input[type="text"]');
        const inputCheckbox = alt.querySelector('input[type="checkbox"]');
        const labelTexto = alt.querySelector('label[for*="texto"]');
        const labelCheckbox = alt.querySelector('label[for*="correta"]');
        const btnExcluir = alt.querySelector('button[onclick*="excluirAlternativa"]');
        
        if (inputTexto) {
            inputTexto.id = `questao-${questaoIndex}-alternativa-${altIndex}-texto`;
            inputTexto.name = `questoes[${questaoIndex}][alternativas][${altIndex}][texto]`;
        }
        
        if (inputCheckbox) {
            inputCheckbox.id = `questao-${questaoIndex}-alternativa-${altIndex}-correta`;
            inputCheckbox.name = `questoes[${questaoIndex}][alternativas][${altIndex}][correta]`;
        }
        
        if (labelTexto) {
            labelTexto.textContent = `Alternativa ${altIndex + 1}`;
            labelTexto.setAttribute('for', `questao-${questaoIndex}-alternativa-${altIndex}-texto`);
        }
        
        if (labelCheckbox) {
            labelCheckbox.setAttribute('for', `questao-${questaoIndex}-alternativa-${altIndex}-correta`);
        }
        
        if (btnExcluir) {
            btnExcluir.setAttribute('onclick', `excluirAlternativa(this, ${questaoIndex})`);
        }
    });
}

function selecionarTipoQuestao(selectElement, questaoIndex) {
    const alternativasContainer = document.getElementById(`alternativas-container-${questaoIndex}`);
    if (selectElement.value === 'objetiva') {
        alternativasContainer.style.display = 'block';
    } else {
        alternativasContainer.style.display = 'none';
    }
}

function validarAlternativas() {
    const questoesContainer = document.getElementById('questoes-container');
    const questoes = questoesContainer.querySelectorAll('.questao');

    for (let questaoIndex = 0; questaoIndex < questoes.length; questaoIndex++) {
        const tipoQuestao = document.getElementById(`questao-${questaoIndex}-tipo`).value;

        if (tipoQuestao === 'objetiva') {
            const alternativasContainer = document.querySelector(`#alternativas-container-${questaoIndex} .alternativas`);
            const checkboxes = alternativasContainer.querySelectorAll(`input[type="checkbox"]`);

            let algumaAlternativaCorreta = false;

            checkboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    algumaAlternativaCorreta = true;
                }
            });

            if (!algumaAlternativaCorreta) {
                alert(`Por favor, selecione pelo menos uma alternativa correta na questao ${questaoIndex + 1}.`);
                return false; // Interrompe a validacao e impede o envio do formulario
            }
        }
    }
    return true; // Se todas as validacoes passarem
}

function salvarProva() {
    return new Promise((resolve, reject) => {
        // Primeiro, valide as alternativas
        if (!validarAlternativas()) {
            reject(); // Se a validacao falhar, rejeita a promise
            return;
        }

        const form = document.getElementById('prova-form');
        const formData = new FormData(form);
        const provaData = {};

        provaData.titulo = formData.get('titulo');
        provaData.questoes = [];

        const questoesContainer = document.getElementById('questoes-container');
        questoesContainer.querySelectorAll('.questao').forEach((questaoDiv, questaoIndex) => {
            const questao = {
                enunciado: formData.get(`questoes[${questaoIndex}][enunciado]`),
                tipo: formData.get(`questoes[${questaoIndex}][tipo]`),
                alternativas: []
            };

            if (questao.tipo === 'objetiva') {
                const alternativasContainer = questaoDiv.querySelector('.alternativas');
                alternativasContainer.querySelectorAll('.alternativa').forEach((alternativaDiv, alternativaIndex) => {
                    const alternativa = {
                        texto: formData.get(`questoes[${questaoIndex}][alternativas][${alternativaIndex}][texto]`),
                        correta: formData.get(`questoes[${questaoIndex}][alternativas][${alternativaIndex}][correta]`) ? true : false
                    };
                    questao.alternativas.push(alternativa);
                });
            }
            provaData.questoes.push(questao);
        });

        const xhr = new XMLHttpRequest();
        const pastaId = document.getElementById('idTrilha').innerText;
        xhr.open('POST', `/avaliacao/${pastaId}/salvar-prova/`);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    resolve();
                    window.location.href = `/avaliacao/${pastaId}/list-provas/`;
                } else {
                    reject();
                }
            }
        };

        xhr.send(JSON.stringify(provaData));
    });
}
