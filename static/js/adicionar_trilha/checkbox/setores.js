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

        // Atualiza a exibição dos funcionários
        filtrarFuncionarios();
    });
});