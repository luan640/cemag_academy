document.addEventListener('DOMContentLoaded', function() {
    const deleteLinks = document.querySelectorAll('.delete-link, .delete-link-refazer-prova');

    console.log(deleteLinks)

    deleteLinks.forEach(function(deleteLink) {
        deleteLink.addEventListener('click', function(event) {
            let message = 'Você quer mesmo excluir? Processo irreversível.';
            
            if (deleteLink.classList.contains('delete-link-refazer-prova')) {
                message = 'Você quer mesmo desfazer esta prova?';
            }

            const confirmDelete = confirm(message);
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });
});
