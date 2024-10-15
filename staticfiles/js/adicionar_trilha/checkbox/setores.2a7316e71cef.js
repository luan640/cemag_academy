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