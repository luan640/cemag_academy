document.addEventListener('click', function (event) {
    const collapseElement = document.getElementById('filterSection');
    const toggleButton = document.querySelector('[data-bs-target="#filterSection"]');

    if (
        collapseElement &&
        collapseElement.classList.contains('show') && 
        !collapseElement.contains(event.target) && 
        !toggleButton.contains(event.target)
    ) {
        const collapse = bootstrap.Collapse.getInstance(collapseElement);
        if (collapse) {
            collapse.hide();
        }
    }
});

const filterCategoryEl = document.getElementById('filterCategory');
const clearFilterEl = document.getElementById('clearFilter');
const filterButtonTextEl = document.getElementById('filterButtonText');
const filterMineEl = document.getElementById('filterMine');
const inputSearchEl = document.getElementById('inputSearch');

function applyFilters() {
    const selectedSector = filterCategoryEl ? filterCategoryEl.value : '';
    const creatorsSelect = document.getElementById('creators');
    const selectedCreatorId = creatorsSelect ? creatorsSelect.value : '';
    const searchText = (inputSearchEl?.value || '').trim();
    const onlyMine = filterMineEl ? filterMineEl.checked : false;

    // Construir URL com parâmetros de filtro
    const url = new URL(window.location.href);
    url.searchParams.delete('page'); // Reset para página 1 ao filtrar
    
    if (searchText) {
        url.searchParams.set('search', searchText);
    } else {
        url.searchParams.delete('search');
    }
    
    if (selectedSector) {
        url.searchParams.set('setor', selectedSector);
    } else {
        url.searchParams.delete('setor');
    }
    
    if (selectedCreatorId) {
        url.searchParams.set('criador', selectedCreatorId);
    } else {
        url.searchParams.delete('criador');
    }
    
    if (onlyMine) {
        url.searchParams.set('minhas', 'true');
    } else {
        url.searchParams.delete('minhas');
    }
    
    // Redirecionar para a URL com os filtros
    window.location.href = url.toString();
}

filterCategoryEl?.addEventListener('change', function () {
    const selectedOption = this.options[this.selectedIndex]?.text || '';
    if (selectedOption) {
        filterButtonTextEl.textContent = selectedOption;
        clearFilterEl.classList.remove('d-none');
    }
    applyFilters();
});

clearFilterEl?.addEventListener('click', function () {
    // Redirecionar para a URL base sem filtros
    const url = new URL(window.location.href);
    url.searchParams.delete('page');
    url.searchParams.delete('search');
    url.searchParams.delete('setor');
    url.searchParams.delete('criador');
    url.searchParams.delete('minhas');
    window.location.href = url.pathname;
});

filterCategoryEl?.addEventListener('change', applyFilters);

document.getElementById('btnSearch')?.addEventListener('click',function(){
    applyFilters();
});

// Adicionar evento para Enter no input de busca
inputSearchEl?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        applyFilters();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const creatorsSelect = document.getElementById('creators');
    if (!creatorsSelect) return;

    async function loadCreators() {
        try {
            const response = await fetch("creators/");
            if (!response.ok) throw new Error('Falha ao carregar os criadores.');
            const data = await response.json();

            creatorsSelect.innerHTML = '';
            const defaultOption = document.createElement('option');
            defaultOption.value = "";
            defaultOption.textContent = "Todos os Criadores";
            defaultOption.selected = true;
            creatorsSelect.appendChild(defaultOption);

            data.creators.forEach(creator => {
                const option = document.createElement('option');
                option.value = creator.id;
                option.textContent = creator.name;
                creatorsSelect.appendChild(option);
            });
            
            // Restaurar valor selecionado da URL
            const urlParams = new URLSearchParams(window.location.search);
            const creatorParam = urlParams.get('criador');
            if (creatorParam) {
                creatorsSelect.value = creatorParam;
            }

        } catch (error) {
            console.error('Erro:', error);
            creatorsSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }

    loadCreators();

    creatorsSelect.addEventListener('change', applyFilters);
    
    // Restaurar outros filtros da URL
    const urlParams = new URLSearchParams(window.location.search);
    
    // Restaurar setor
    const setorParam = urlParams.get('setor');
    if (setorParam && filterCategoryEl) {
        filterCategoryEl.value = setorParam;
        const selectedOption = filterCategoryEl.options[filterCategoryEl.selectedIndex]?.text || '';
        if (selectedOption && filterButtonTextEl) {
            filterButtonTextEl.textContent = selectedOption;
        }
        if (clearFilterEl) {
            clearFilterEl.classList.remove('d-none');
        }
    }
    
    // Restaurar checkbox "minhas trilhas"
    const minhasParam = urlParams.get('minhas');
    if (minhasParam === 'true' && filterMineEl) {
        filterMineEl.checked = true;
    }
});

filterMineEl?.addEventListener('change', applyFilters);
