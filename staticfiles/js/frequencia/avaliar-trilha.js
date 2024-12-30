document.getElementById('avaliacao-trilha-form').addEventListener('submit', function(event) {
    // Desabilita o botão de envio
    const submitButton = document.getElementById('submit-avaliacao-eficacia-trilha');
    submitButton.disabled = true;

    // Exibe o spinner (remove a classe d-none)
    const spinner = submitButton.querySelector('.spinner-border');
    spinner.classList.remove('d-none');

    // Altera o texto do botão para indicar que está processando
    const buttonText = document.getElementById('button-text');
    buttonText.textContent = 'Enviando...';
});