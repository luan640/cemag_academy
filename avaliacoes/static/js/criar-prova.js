document.getElementById('prova-form').addEventListener('submit', function(event) {
    event.preventDefault();
    salvarProva();
});

let questaoCounter = 0;
let alternativaCounter = 0;

function adicionarQuestao() {
    const questoesContainer = document.getElementById('questoes-container');
    const questaoIndex = questaoCounter++;

    const questaoDiv = document.createElement('div');
    questaoDiv.className = 'questao';
    questaoDiv.innerHTML = `
        <div class="row">
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
            <div class="col-sm-1 mt-4">
                <a id="excluir-questao-${questaoIndex}" class="btn btn-danger">
                    <i class="fa-solid fa-trash"></i>
                </a>
            </div>
        </div>

        <div id="alternativas-container-${questaoIndex}" style="display: none;">
            <h4>Alternativas</h4>
            <button class="btn btn-primary" type="button" onclick="adicionarAlternativa(${questaoIndex})">Adicionar Alternativa</button>
            <div class="alternativas"></div>
        </div>
        <hr>
    `;
    questoesContainer.appendChild(questaoDiv);

    // Adicionar o manipulador de eventos de exclusão
    document.getElementById(`excluir-questao-${questaoIndex}`).addEventListener('click', function() {
        excluirQuestao(questaoIndex);
    });
}

function excluirQuestao(index) {
    const questaoDiv = document.getElementById(`questao-${index}-enunciado`).closest('.questao');
    questaoDiv.remove();
}

function excluirAlternativa(questaoIndex, alternativaIndex) {
    const alternativaDiv = document.getElementById(`questao-${questaoIndex}-alternativa-${alternativaIndex}-texto`).closest('.alternativa');
    alternativaDiv.remove();
}


function selecionarTipoQuestao(selectElement, questaoIndex) {
    const alternativasContainer = document.getElementById(`alternativas-container-${questaoIndex}`);
    if (selectElement.value === 'objetiva') {
        alternativasContainer.style.display = 'block';
    } else {
        alternativasContainer.style.display = 'none';
    }
}

function adicionarAlternativa(questaoIndex) {
    const alternativasContainer = document.querySelector(`#alternativas-container-${questaoIndex} .alternativas`);
    const alternativaIndex = alternativaCounter++;
    

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
            <div class="col-sm-2 mt-4">
                <a id="excluir-alternativa-${questaoIndex}-${alternativaIndex}" class="btn btn-danger">
                    <i class="fa-solid fa-trash"></i>
                </a>
            </div>
        </div>
    `;
    alternativasContainer.appendChild(alternativaDiv);

    // Adicionar o manipulador de eventos de exclusão
    document.getElementById(`excluir-alternativa-${questaoIndex}-${alternativaIndex}`).addEventListener('click', function() {
        excluirAlternativa(questaoIndex, alternativaIndex);
    });
}


function salvarProva() {
    const form = document.getElementById('prova-form');
    const formData = new FormData(form);
    const provaData = {};

    provaData.titulo = formData.get('titulo');
    provaData.descricao = formData.get('descricao');
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

    
    // Enviar provaData para o servidor usando AJAX
    const xhr = new XMLHttpRequest();
    const pastaId = document.getElementById('idTrilha').innerText;
    xhr.open('POST', `/avaliacao/${pastaId}/salvar-prova/`);  // Corrigindo a URL
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                alert('Prova salva com sucesso!');
            } else {
                alert('Erro ao salvar a prova.');
            }
        }
    };
    xhr.send(JSON.stringify(provaData));
}