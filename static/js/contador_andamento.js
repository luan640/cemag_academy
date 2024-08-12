document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('.material-visualizado');
    const andamentoVisualizacoes = document.getElementById('andamentoVisualizacoes');
    const botaoProvas = document.getElementById('provaDisponivel'); // Seleciona o botão
    const progressBar = document.getElementById('progressBar'); // Seleciona a barra de progresso
    const statusIconCheck = document.getElementById('statusIconCheck'); // Ícone de check
    const statusIconXmark = document.getElementById('statusIconXmark'); // Ícone de xmark

    function updatePercentage() {
        const totalCheckboxes = checkboxes.length;
        let checkboxesMarcados = 0;

        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                checkboxesMarcados++;
            }
        });

        const percentage = totalCheckboxes > 0 ? (checkboxesMarcados / totalCheckboxes) * 100 : 0;
        andamentoVisualizacoes.textContent = percentage.toFixed(2) + '%';

        // Atualiza o estilo da barra de progresso e o texto dentro dela
        progressBar.style.width = percentage + '%';
        botaoProvas.style.textDecoration = 'none'
        progressBar.textContent = percentage.toFixed(2) + '%';
        progressBar.setAttribute('aria-valuenow', percentage.toFixed(2));

        // Remove as classes bg-success, bg-warning, bg-danger
        progressBar.classList.remove('bg-success', 'bg-warning', 'bg-danger');

        console.log(percentage)
        // Adiciona a classe correta com base na porcentagem
        if (percentage >= 80 && percentage <= 100) {
            progressBar.classList.add('bg-success');
        } else if (percentage > 25 && percentage < 80) {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-danger');
        }

        // Atualiza os ícones e o estado do botão com base no progresso
        if (percentage === 100) {
            statusIconCheck.style.display = 'block';
            statusIconXmark.style.display = 'none';
            botaoProvas.removeAttribute('disabled');
            botaoProvas.textContent = 'Provas disponíveis'
            botaoProvas.style.color = '#0d6efd';
            botaoProvas.style.pointerEvents = 'auto'; // Habilita o botão
        } else {
            statusIconCheck.style.display = 'none';
            statusIconXmark.style.display = 'block';
            botaoProvas.setAttribute('disabled', 'true');
            botaoProvas.textContent = 'Provas indisponíveis'
            botaoProvas.style.color = 'gray';
            botaoProvas.style.pointerEvents = 'none'; // Desabilita o botão
        }
    }

    updatePercentage(); // Atualiza ao carregar a página

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updatePercentage);
    });
});
