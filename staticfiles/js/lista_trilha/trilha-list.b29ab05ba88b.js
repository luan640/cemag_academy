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

document.addEventListener('DOMContentLoaded', function() {
    const creatorsSelect = document.getElementById('creators');

    async function loadCreators() {
        try {
            const response = await fetch("creators/");
            
            if (!response.ok) {
                throw new Error('Falha ao carregar os criadores.');
            }
            
            const data = await response.json();
            
            // 1. Limpa completamente o select
            creatorsSelect.innerHTML = '';

            // 2. Adiciona a nova opção padrão (Default)
            // Esta será a opção para "Todos", permitindo limpar o filtro.
            const defaultOption = document.createElement('option');
            defaultOption.value = ""; // Valor vazio
            defaultOption.textContent = "Todos os Criadores"; // Texto descritivo
            defaultOption.selected = true; // Define como selecionada por padrão
            creatorsSelect.appendChild(defaultOption);

            // 3. Adiciona os outros criadores vindos da API
            data.creators.forEach(creator => {
                const option = document.createElement('option');
                option.value = creator.id;
                option.textContent = creator.name;
                creatorsSelect.appendChild(option);
            });

        } catch (error) {
            console.error('Erro:', error);
            creatorsSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }

    loadCreators();

    const allItems = document.querySelectorAll('.list-group-item.trilha-item');

    // 2. Adiciona um "ouvinte" que executa uma função sempre que o filtro de criadores é alterado
    creatorsSelect.addEventListener('change', function() {
        
        // 3. Pega o NOME do criador que foi selecionado no filtro
        // Usamos .text para pegar o texto visível da opção (ex: "Fulano de Tal")
        const selectedCreatorName = this.options[this.selectedIndex].text;

        // 4. Percorre cada item da lista para decidir se deve exibi-lo ou escondê-lo
        allItems.forEach(item => {
            // Pega o elemento que marcamos com a classe 'creator-name' dentro do item atual
            const creatorNameElement = item.querySelector('.creator-name');
            
            if (creatorNameElement) {
                const itemCreatorName = creatorNameElement.textContent.trim();

                // 5. Compara o nome do item com o nome selecionado no filtro
                // A condição é: mostrar se "Todos os Criadores" está selecionado OU se os nomes são iguais
                const shouldBeVisible = (selectedCreatorName === "Todos os Criadores" || itemCreatorName === selectedCreatorName);
                
                // Exibe o item se a condição for verdadeira, senão, oculta
                // Usamos '' para que o item volte ao seu display padrão (definido pelo CSS/Bootstrap)
                item.style.display = shouldBeVisible ? '' : 'none';
            }
        });
    });
});