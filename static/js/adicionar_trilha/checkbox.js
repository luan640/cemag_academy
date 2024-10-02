// Adiciona event listener para cada checkbox de setor
document.querySelectorAll('.setor-checkbox').forEach(function(setorCheckbox) {
    setorCheckbox.addEventListener('change', function() {
        // Extrai o nome do setor que está dentro do label do checkbox
        const setorNome = this.parentElement.textContent.trim();

        // Seleciona ou desmarca todos os funcionários que possuem o setor associado
        document.querySelectorAll('.funcionario-checkbox').forEach(function(funcionarioCheckbox) {
            // Verifica se o funcionário pertence ao setor marcado
            const funcionarioSetor = funcionarioCheckbox.parentElement.textContent.trim();

            // Se o nome do setor estiver no texto do funcionário, marca/desmarca o checkbox
            if (funcionarioSetor.includes(`(${setorNome})`)) {
                funcionarioCheckbox.checked = setorCheckbox.checked;
            }
        });
    });
});

// Selecionar ou desmarcar todos os setores e funcionários correspondentes com base no switch
document.getElementById('toggle-select-all-switch').addEventListener('click', function() {
    const selectAll = this.checked;

    // Marcar/desmarcar todos os checkboxes de setores e grupos
    let setoresCheckboxes = document.querySelectorAll('.setor-checkbox input, .lider-checkbox');
    setoresCheckboxes.forEach(function(setorCheckbox) {
        setorCheckbox.checked = selectAll;

        // Selecionar/desmarcar todos os funcionários pertencentes ao setor selecionado
        const setorNome = setorCheckbox.parentElement.textContent.trim();
        document.querySelectorAll('.funcionario-checkbox').forEach(function(funcionarioCheckbox) {
            const funcionarioSetor = funcionarioCheckbox.parentElement.textContent.trim();

            // Se o nome do setor estiver no texto do funcionário, marca/desmarca o checkbox
            if (funcionarioSetor.includes(`(${setorNome})`)) {
                funcionarioCheckbox.checked = selectAll;
            }
        });
    });

    // Atualiza o texto do switch
    const label = document.querySelector('label[for="toggle-select-all-switch"]');
    label.textContent = selectAll ? 'Desmarcar Todos' : 'Selecionar Todos';
});

document.getElementById('toggle-show-selected').addEventListener('change', function() {
    const showSelected = this.checked;
    const funcionarios = document.querySelectorAll('.funcionario-checkbox div');

    funcionarios.forEach(function(funcionario) {
        const checkbox = funcionario.querySelector('input.funcionario-checkbox');
        if (showSelected) {
            // Exibe apenas os funcionários que estão com o checkbox marcado
            funcionario.style.display = checkbox.checked ? "" : "none";
        } else {
            // Exibe todos os funcionários
            funcionario.style.display = "";
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const liderCheckbox = document.querySelector('.lider-checkbox');
    const funcionarioCheckboxes = document.querySelectorAll('.funcionario-checkbox');

    liderCheckbox.addEventListener('change', function () {
        // Marca ou desmarca todos os checkboxes de funcionários
        funcionarioCheckboxes.forEach(function (checkbox) {
            // Se o checkbox "Líder" estiver marcado, verifica se o funcionário é um líder
            if (liderCheckbox.checked) {
                if (checkbox.parentElement.innerText.includes('(LÍD)')) {
                    checkbox.checked = true; // Marca o checkbox do funcionário se ele for um líder
                }
            } else {
                // Desmarca todos os checkboxes se o checkbox "Líder" não estiver marcado
                checkbox.checked = false;
            }
        });
    });
});