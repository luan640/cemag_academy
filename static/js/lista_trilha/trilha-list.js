document.addEventListener('click', function (event) {
    // Elementos relevantes
    const collapseElement = document.getElementById('filterSection');
    const toggleButton = document.querySelector('[data-bs-target="#filterSection"]');

    // Verifica se o colapso está aberto e o clique foi fora do botão ou do colapso
    if (
        collapseElement.classList.contains('show') && 
        !collapseElement.contains(event.target) && 
        !toggleButton.contains(event.target)
    ) {
        // Fecha o colapso
        const collapse = bootstrap.Collapse.getInstance(collapseElement); // Obtém a instância Bootstrap
        if (collapse) {
            collapse.hide();
        }
    }
});

document.getElementById('filterCategory').addEventListener('change', function () {
    const selectedOption = this.options[this.selectedIndex].text; // Obtém o texto do setor selecionado
    const filterButtonText = document.getElementById('filterButtonText'); // Elemento de texto no botão
    const clearFilter = document.getElementById('clearFilter'); // Elemento "x" para remover o filtro

    if (selectedOption) {
        filterButtonText.textContent = selectedOption; // Altera o texto do botão
        clearFilter.style.display = 'inline'; // Exibe o "x"
    }
});

// Clique no "x" para limpar o filtro
document.getElementById('clearFilter').addEventListener('click', function () {
    const filterCategory = document.getElementById('filterCategory'); // Select de setores
    const filterButtonText = document.getElementById('filterButtonText'); // Elemento de texto no botão

    // Redefine o select e o botão
    filterCategory.selectedIndex = 0; // Volta para a opção inicial
    filterButtonText.textContent = 'Filtros'; // Texto padrão do botão

    // Oculta o "x"
    this.style.display = 'none';

    // Mostra todos os itens
    const items = document.querySelectorAll('.trilha-item');
    items.forEach(item => {
        item.style.display = 'flex'; // Restaura a exibição
    });
});

// Captura o select de setores e adiciona o evento
document.getElementById('filterCategory').addEventListener('change', function () {
    const filteredSector = this.value; // Nome do setor selecionado
    const items = document.querySelectorAll('.trilha-item'); // Todos os itens da lista

    items.forEach(item => {
        // Verifica se o setor filtrado está incluído nos setores do item
        const setores = item.getAttribute('data-setores'); // Obtém os setores do atributo data
        if (setores && setores.includes(filteredSector)) {
            item.style.display = 'flex'; // Mostra o item
        } else {
            item.style.display = 'none'; // Oculta o item
        }
    });
});

document.getElementById('btnSearch').addEventListener('click',function(){
    const inputSearch = document.getElementById('inputSearch').value.toLowerCase();
    const itemTrilha = document.querySelectorAll('.trilha-item');

    itemTrilha.forEach(function(item) {
        const nome = item.querySelector('.trilha-nome').textContent.toLowerCase();
        if(nome.includes(inputSearch)){
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    })
})