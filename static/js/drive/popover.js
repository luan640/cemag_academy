var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    // Adicionamos um listener para fechar outros popovers quando um novo for aberto
    popoverTriggerEl.addEventListener('show.bs.popover', function () {
    popoverList.forEach(function(popover) {
        if (popover._element !== popoverTriggerEl) {
        popover.hide();
        }
    });
    });
    return new bootstrap.Popover(popoverTriggerEl)
});