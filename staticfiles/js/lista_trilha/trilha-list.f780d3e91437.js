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
    const selectedCreatorName = creatorsSelect ? creatorsSelect.options[creatorsSelect.selectedIndex]?.text || '' : '';
    const searchText = (inputSearchEl?.value || '').toLowerCase();
    const onlyMine = filterMineEl ? filterMineEl.checked : false;

    document.querySelectorAll('.trilha-item').forEach(item => {
        const setores = item.getAttribute('data-setores') || '';
        const creatorName = item.querySelector('.creator-name')?.textContent.trim() || '';
        const nome = item.querySelector('.trilha-nome')?.textContent.toLowerCase() || '';
        const criador = creatorName.toLowerCase();
        const destinada = item.getAttribute('data-destinada') === 'true';

        let visible = true;
        if (selectedSector) {
            visible = visible && setores.includes(selectedSector);
        }
        if (selectedCreatorName && selectedCreatorName !== 'Todos os Criadores') {
            visible = visible && creatorName === selectedCreatorName;
        }
        if (onlyMine) {
            visible = visible && destinada;
        }
        if (searchText) {
            visible = visible && (nome.includes(searchText) || criador.includes(searchText));
        }

        item.style.display = visible ? '' : 'none';
    });
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
    if (!filterCategoryEl) return;
    filterCategoryEl.selectedIndex = 0;
    filterButtonTextEl.textContent = 'Filtros';
    this.classList.add('d-none');

    if (filterMineEl) {
        filterMineEl.checked = false;
    }
    if (inputSearchEl) {
        inputSearchEl.value = '';
    }
    const creatorsSelect = document.getElementById('creators');
    if (creatorsSelect) {
        creatorsSelect.selectedIndex = 0;
    }
    applyFilters();
});

filterCategoryEl?.addEventListener('change', applyFilters);

document.getElementById('btnSearch')?.addEventListener('click',function(){
    applyFilters();
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

        } catch (error) {
            console.error('Erro:', error);
            creatorsSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }

    loadCreators();

    creatorsSelect.addEventListener('change', applyFilters);
});

filterMineEl?.addEventListener('change', applyFilters);
