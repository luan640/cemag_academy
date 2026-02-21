document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.material-visualizado');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const materialId = this.dataset.materialId;
            const pastaId = this.dataset.pastaId;

            fetch(this.dataset.url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'material_id': materialId,
                    'pasta_id': pastaId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'marcado') {
                    // Checkbox marcado, faça algo se necessário
                } else {
                    // Checkbox desmarcado, faça algo se necessário
                }
            })
            .catch(error => {
                console.error('Erro na requisição:', error);
            });
        });
    });
});