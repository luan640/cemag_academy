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
});