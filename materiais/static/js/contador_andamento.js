document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.material-visualizado');
    const andamentoVisualizacoes = document.getElementById('andamentoVisualizacoes');

    function updatePercentage() {
      const totalCheckboxes = checkboxes.length;
      let checkboxesMarcados = 0;

      checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
          checkboxesMarcados++;
        }
      });

      const percentage = totalCheckboxes > 0 ? (checkboxesMarcados / totalCheckboxes) * 100 : 0;
      andamentoVisualizacoes.textContent = `Andamento da trilha: ${percentage.toFixed(2)}%`;
    }

    // Atualiza o percentual ao carregar a página
    updatePercentage();

    // Adiciona event listener para atualizar o percentual quando checkboxes são alterados
    checkboxes.forEach(checkbox => {
      checkbox.addEventListener('change', updatePercentage);
    });
  });