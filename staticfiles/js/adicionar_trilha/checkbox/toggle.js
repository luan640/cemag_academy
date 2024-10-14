// Listener para marcar/desmarcar todos os setores e funcionários correspondentes com base no switch
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

    // Atualiza a exibição dos funcionários
    filtrarFuncionarios();
});

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

        // Atualiza a exibição dos funcionários
        filtrarFuncionarios();
    });
});

function filtrarFuncionarios() {
    const showSelected = document.getElementById('toggle-show-selected').checked;
    const funcionarios = document.querySelectorAll('.funcionario-checkbox div');

    funcionarios.forEach(function(funcionario) {
        const checkbox = funcionario.querySelector('input.funcionario-checkbox');
        if (showSelected) {
            funcionario.style.display = checkbox.checked ? "" : "none";
        } else {
            funcionario.style.display = "";
        }
    });
}

document.getElementById('toggle-show-selected').addEventListener('change',filtrarFuncionarios);

filtrarFuncionarios();