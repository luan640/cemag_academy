document.getElementById('prova-form').addEventListener('submit', function(event) {
    event.preventDefault();
    salvarProva();
});

function adicionarQuestao() {
    const questoesContainer = document.getElementById('questoes-container');
    const questaoIndex = questoesContainer.children.length;

    const questaoDiv = document.createElement('div');
    questaoDiv.className = 'questao';
    questaoDiv.innerHTML = `
        <label for="questao-${questaoIndex}-enunciado">Enunciado da Questão:</label>
        <textarea class="form-control" id="questao-${questaoIndex}-enunciado" name="questoes[${questaoIndex}][enunciado]" required></textarea>
        
        <label for="questao-${questaoIndex}-tipo">Tipo:</label>
        <select class="form-control" id="questao-${questaoIndex}-tipo" name="questoes[${questaoIndex}][tipo]" onchange="selecionarTipoQuestao(this, ${questaoIndex})" required>
            <option value="dissertativa">Dissertativa</option>
            <option value="objetiva">Objetiva</option>
        </select>

        <div id="alternativas-container-${questaoIndex}" style="display: none;">
            <h4>Alternativas</h4>
            <button class="btn btn-primary" type="button" onclick="adicionarAlternativa(${questaoIndex})">Adicionar Alternativa</button>
            <div class="alternativas"></div>
        </div>
    `;
    questoesContainer.appendChild(questaoDiv);
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
    const alternativaIndex = alternativasContainer.children.length;

    const alternativaDiv = document.createElement('div');
    alternativaDiv.className = 'alternativa';
    alternativaDiv.innerHTML = `
        <label for="questao-${questaoIndex}-alternativa-${alternativaIndex}-texto">Alternativa:</label>
        <input class="form-control" type="text" id="questao-${questaoIndex}-alternativa-${alternativaIndex}-texto" name="questoes[${questaoIndex}][alternativas][${alternativaIndex}][texto]" required>
        
        <label for="questao-${questaoIndex}-alternativa-${alternativaIndex}-correta">Correta:</label>
        <input class="form-control" type="checkbox" id="questao-${questaoIndex}-alternativa-${alternativaIndex}-correta" name="questoes[${questaoIndex}][alternativas][${alternativaIndex}][correta]">
    `;
    alternativasContainer.appendChild(alternativaDiv);
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