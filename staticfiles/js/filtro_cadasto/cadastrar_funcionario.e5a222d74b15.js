document.getElementById('filtrar_funcionario').addEventListener('keyup', function() {
    const filtro = this.value.toLowerCase();
    const funcionarios = document.querySelectorAll('.funcionarios_cadastrados');

    funcionarios.forEach(item => {
        const texto = item.querySelector('.matricula_nome').textContent.toLowerCase();
        // Exibe ou oculta a linha conforme o filtro
        item.style.display = texto.includes(filtro) ? '' : 'none';
    });
});
