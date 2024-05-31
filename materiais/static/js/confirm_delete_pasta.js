document.addEventListener('DOMContentLoaded', function() {
    const deleteLink = document.querySelector('.delete-link');
    
    if (deleteLink) {
        deleteLink.addEventListener('click', function(event) {
            const confirmDelete = confirm('Você quer mesmo excluir essa trilha? Processo irreversível.');
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    }
});