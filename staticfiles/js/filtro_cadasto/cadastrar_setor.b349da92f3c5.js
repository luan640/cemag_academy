document.getElementById('filtro_cadastrar_setor').addEventListener('keyup',function() {
    const filtrar = this.value.toLowerCase();
    const setores_cadastradas = document.querySelectorAll('.setores_cadastradas');

    setores_cadastradas.forEach(setor => {
        const texto_setor = setor.querySelector('.setor_area').textContent.toLowerCase();
        if(texto_setor.startsWith(filtrar)){
            setor.style.display = 'flex';
        } else {
            setor.style.display = 'none';
        }
    })
})