let questaoCounter = 1;
let alternativaCounter = 1;

function adicionarQuestao() {
    const questoesContainer = document.getElementById('questoes-container');
    const questaoIndex = questoesContainer.children.length;

    const questaoDiv = document.createElement('div');
    questaoDiv.className = 'questao';
    questaoDiv.innerHTML = `
        <div class="row">
            <h5>Questão</h5>
            <div class="col-sm-6 mb-4">
                <label for="questao-${questaoIndex}-enunciado">Enunciado da Questão:</label>
                <textarea class="form-control" id="questao-${questaoIndex}-enunciado" name="questoes[${questaoIndex}][enunciado]" required></textarea>
            </div>
            <div class="col-sm-5 mb-4">
                <label for="questao-${questaoIndex}-tipo">Tipo:</label>
                <select class="form-control" id="questao-${questaoIndex}-tipo" name="questoes[${questaoIndex}][tipo]" onchange="selecionarTipoQuestao(this, ${questaoIndex})" required>
                    <option value="dissertativa">Dissertativa</option>
                    <option value="objetiva">Objetiva</option>
                </select>
            </div>
        </div>

        <div id="alternativas-container-${questaoIndex}" style="display: none;">
            <h5>Alternativas</h5>
            <button class="btn btn-primary" type="button" onclick="adicionarAlternativa(${questaoIndex})">Adicionar Alternativa</button>
            <button class="btn btn-danger" type="button" onclick="excluirUltimaAlternativa(${questaoIndex})">Excluir Última Alternativa</button>
            <div class="alternativas"></div>
        </div>
        <hr>
    `;
    questoesContainer.appendChild(questaoDiv);
}

function excluirUltimaQuestao() {
    const questoesContainer = document.getElementById('questoes-container');
    const totalQuestoes = questoesContainer.children.length;
    
    if (totalQuestoes > 1) {
        // Remove a última questão criada
        questoesContainer.lastChild.remove();
    } else {
        alert("Não há mais questões para remover.");
    }
}

// Certifique-se de que as alternativas têm IDs e names únicos
function adicionarAlternativa(questaoIndex) {
    const alternativasContainer = document.querySelector(`#alternativas-container-${questaoIndex} .alternativas`);
    const alternativaIndex = alternativasContainer.children.length;

    const alternativaDiv = document.createElement('div');
    alternativaDiv.className = 'alternativa';
    alternativaDiv.innerHTML = `
        <div class="row">
            <div class="col-sm-8 mb-4">
                <label for="questao-${questaoIndex}-alternativa-${alternativaIndex}-texto">Alternativa:</label>
                <input class="form-control" type="text" id="questao-${questaoIndex}-alternativa-${alternativaIndex}-texto" name="questoes[${questaoIndex}][alternativas][${alternativaIndex}][texto]" required>
            </div>
            <div class="col-sm-2 mt-4">
                <label for="questao-${questaoIndex}-alternativa-${alternativaIndex}-correta">Correta:</label>
                <input type="checkbox" id="questao-${questaoIndex}-alternativa-${alternativaIndex}-correta" name="questoes[${questaoIndex}][alternativas][${alternativaIndex}][correta]">
            </div>
        </div>
    `;
    alternativasContainer.appendChild(alternativaDiv);
}

function excluirUltimaAlternativa(questaoIndex) {
    const alternativasContainer = document.querySelector(`#alternativas-container-${questaoIndex} .alternativas`);
    const totalAlternativas = alternativasContainer.children.length;

    if (totalAlternativas > 0) {
        // Remove a última alternativa criada
        alternativasContainer.lastChild.remove();
    } else {
        alert("Não há mais alternativas para remover.");
    }
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
                alert(`Por favor, selecione pelo menos uma alternativa correta na questão ${questaoIndex + 1}.`);
                return false; // Interrompe a validação e impede o envio do formulário
            }
        }
    }
    return true; // Se todas as validações passarem
}

function salvarProva() {
    return new Promise((resolve, reject) => {
        // Primeiro, valide as alternativas
        if (!validarAlternativas()) {
            reject(); // Se a validação falhar, rejeita a promise
            return;
        }

        // Continuação do código de envio do formulário...
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
                    resolve(); // Resolve a promise em caso de sucesso
                    window.location.href = `/avaliacao/${pastaId}/list-provas/`;
                } else {
                    reject(); // Rejeita a promise em caso de erro
                }
            }
        };

        xhr.send(JSON.stringify(provaData));
    });
}
