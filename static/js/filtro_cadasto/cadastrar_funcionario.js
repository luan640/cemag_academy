document.getElementById('filtrar_funcionario').addEventListener('keyup', function() {
    const filtro = this.value.toLowerCase();  // Captura o valor do input e converte para minúsculo
    const funcionarios = document.querySelectorAll('.funcionarios_cadastrados');  // Seleciona todos os 'li' com a classe 'funcionarios_cadastrados'

    funcionarios.forEach(item => {
        const texto = item.querySelector('.matricula_nome').textContent.toLowerCase();  // Obtém o texto do link e converte para minúsculo
        
        // Verifica se o texto do link contém o filtro digitado
        if (texto.includes(filtro)) {
            item.style.display = '';  // Exibe o item
        } else {
            item.style.display = 'none';  // Esconde o item
        }
    });
});