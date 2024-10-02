// Filtro para setores
document.getElementById('filtrar_setor').addEventListener('input', function() {
    let filtro = this.value.toLowerCase();
    let setores = document.querySelectorAll('#id_setores div');

    setores.forEach(function(setor) {
        let texto = setor.textContent.toLowerCase();
        if (texto.includes(filtro)) {
            setor.style.display = "";
        } else {
            setor.style.display = "none";
        }
    });

    let grupos = document.querySelectorAll("#grupos_setores label");
    grupos.forEach(function (grupo) {
        let texto = grupo.textContent.toLowerCase();
        if(texto.includes(filtro)){
            grupo.style.display = "";
        } else {
            grupo.style.display = "none";
        }
    })
});

// Filtro para funcionários
document.getElementById('filtrar_funcionarios').addEventListener('input', function() {
    let filtro = this.value.toLowerCase();
    let funcionarios = document.querySelectorAll('#id_funcionarios div');

    funcionarios.forEach(function(funcionario) {
        let texto = funcionario.textContent.toLowerCase();
        if (texto.includes(filtro)) {
            funcionario.style.display = "";
        } else {
            funcionario.style.display = "none";
        }
    });
});

let toggleSwitch = document.getElementById('toggle-select-all-switch');

toggleSwitch.addEventListener('change', function() {
    let isChecked = toggleSwitch.checked;

    // Selecionar/desmarcar todos os checkboxes dos setores e grupos
    let checkboxes = document.querySelectorAll('.setor-checkbox input, .lider-checkbox');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = isChecked;
    });

    // Atualizar o texto do switch
    let label = document.querySelector('label[for="toggle-select-all-switch"]');
    label.textContent = isChecked ? 'Desmarcar Todos' : 'Selecionar Todos';
});