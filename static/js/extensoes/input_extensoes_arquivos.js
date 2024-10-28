const videoInput = document.getElementById('id_video');
const arquivoInput = document.getElementById('id_arquivo');
const fotosInput = document.getElementById('id_fotos');
videoInput.setAttribute('accept', '.mp4');
arquivoInput.setAttribute('accept', '.pdf, .doc, .docx');
fotosInput.setAttribute('accept', '.png, .jpeg, .jpg');

videoInput.addEventListener('change', function() {
const file = this.files[0];
const allowedExtensions = /(\.mp4)$/i;

if (!allowedExtensions.exec(file.name)) {
    alert('Por favor, selecione um arquivo de vídeo com a extensão .mp4');
    this.value = ''; // Limpa o input
}
});

arquivoInput.addEventListener('change', function() {
const file = this.files[0];
const allowedExtensions = /(\.pdf|\.doc|\.docx)$/i;

if (!allowedExtensions.exec(file.name)) {
    alert('Por favor, selecione um arquivo com uma das seguintes extensões: .pdf, .doc, .docx, .txt');
    this.value = '';
}
});

fotosInput.addEventListener('change', function() {
const file = this.files[0];
const allowedExtensions = /(\.png|\.jpeg|\.jpg)$/i;

if (!allowedExtensions.exec(file.name)) {
    alert('Por favor, selecione uma imagem com uma das seguintes extensões: .png, .jpeg, .jpg');
    this.value = '';
}
});