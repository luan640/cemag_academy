// Filtro para setores
document.getElementById('filtrar_setor_editar_trilha').addEventListener('input', function() {
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
});

document.getElementById('filtrar_funcionarios_editar_trilha').addEventListener('input', function() {
    let filtro = this.value.toLowerCase();
    let funcionarios = document.querySelectorAll('#id_funcionarios div');
    document.getElementById('toggle-show-selected').checked = false;

    funcionarios.forEach(function(funcionario) {
        let texto = funcionario.textContent.toLowerCase();
        if (texto.includes(filtro)) {
            funcionario.style.display = "";
        } else {
            funcionario.style.display = "none";
        }
    });
});