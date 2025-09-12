// Função genérica para tratar o submit dos formulários
function handleFormSubmit() {
    let submitButton = document.getElementById('submit-edit');
    submitButton.disabled = true;
    document.querySelector('.spinner-border').classList.remove('d-none');
    document.getElementById('button-text').textContent = "Salvando...";
  }
  
  const formFuncionario = document.getElementById('form-funcionario');
  if (formFuncionario) {
    formFuncionario.addEventListener('submit', handleFormSubmit);
  }
  
  const formSetor = document.getElementById('form-setor');
  if (formSetor) {
    formSetor.addEventListener('submit', handleFormSubmit);
  }
  
  const formArea = document.getElementById('form-area');
  if (formArea) {
    formArea.addEventListener('submit', handleFormSubmit);
  }
  
  const formBook = document.getElementById('form-book');
  if (formBook){
    formBook.addEventListener('submit', handleFormSubmit);
  }

  const realizarProva = document.getElementById('form-realizar-prova');
  if (realizarProva){
    realizarProva.addEventListener('submit', handleFormSubmit);
  }