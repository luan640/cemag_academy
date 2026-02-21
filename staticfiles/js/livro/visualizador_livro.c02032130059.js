document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.livro-visualizado');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const livroId = this.dataset.livroId;

            fetch(this.dataset.url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'livro_id': livroId
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