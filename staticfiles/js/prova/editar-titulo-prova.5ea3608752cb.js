document.addEventListener('DOMContentLoaded', () => {
    const buttonEditTitle = document.getElementById("button-edit-title");
    const inputEditTitle = document.getElementById("input-edit-title");
    const containerEditTitle = document.getElementById("container-edit-title")
    const titleTest = document.getElementById("title"); 

    buttonEditTitle.addEventListener("click", function() {
        const contentTitle = titleTest.textContent;
        inputEditTitle.value = contentTitle;
        inputEditTitle.style.display = "block";
        titleTest.style.display = "none";
        this.style.display = "none";

        const buttonSubmitNewTitle = document.createElement('button');
        buttonSubmitNewTitle.classList.add("btn", "btn-success");
        buttonSubmitNewTitle.style.width = "70px";
        buttonSubmitNewTitle.textContent = "Editar";
        buttonSubmitNewTitle.id = "submit-edit-title";

        const buttonCancelNewTitle = document.createElement('button');
        buttonCancelNewTitle.classList.add("btn", "btn-danger");
        buttonCancelNewTitle.style.width = "70px";
        buttonCancelNewTitle.innerHTML = `<i class="fa-solid fa-xmark"></i>`;
        buttonCancelNewTitle.id = "cancel-edit-title";

        containerEditTitle.append(buttonSubmitNewTitle, buttonCancelNewTitle);

        buttonCancelNewTitle.addEventListener("click", () => {
            inputEditTitle.style.display = "none";
            titleTest.style.display = "block";
            this.style.display = "block";
            containerEditTitle.removeChild(buttonSubmitNewTitle)
            containerEditTitle.removeChild(buttonCancelNewTitle)
        })

        buttonSubmitNewTitle.addEventListener("click", function() {
            const span = document.createElement("span");
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            buttonCancelNewTitle.disabled = true;
            this.disabled = true;
            this.textContent = "";
            span.classList.add("spinner-border", "spinner-border-sm");
            buttonSubmitNewTitle.appendChild(span);

            if (inputEditTitle.value === "") {
                Swal.fire({
                    icon: "error",
                    title: "Oops...",
                    text: "O título da prova não pode ser vazio",
                });
                this.disabled = false;
                buttonCancelNewTitle.disabled = false;
                buttonSubmitNewTitle.textContent = "Editar";
                buttonSubmitNewTitle.removeChild(span);
                return 
            } else if (inputEditTitle.value === contentTitle) {
                Swal.fire({
                    icon: "error",
                    title: "Oops...",
                    text: "Não houve alterações no título da prova",
                });
                this.disabled = false;
                buttonCancelNewTitle.disabled = false;
                buttonSubmitNewTitle.innerHTML = "Editar";
                return 
            } 

            // A rota está vazia pois o POST é na mesma rota que no GET
            fetch("", {
                method: "POST",
                headers: {
                    "Content-Ttype": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({"titulo":inputEditTitle.value})
            })
            .then((response) => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.message || "Erro desconhecido na requisição");
                    });
                }
                return response.json();
            })
            .then((data) => {
                const Toast = Swal.mixin({
                    toast: true,
                    position: "bottom-end",
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true,
                    didOpen: (toast) => {
                      toast.onmouseenter = Swal.stopTimer;
                      toast.onmouseleave = Swal.resumeTimer;
                    }
                  });
                  Toast.fire({
                    icon: "success",
                    title: "Sucesso ao editar o título da prova"
                  });
                containerEditTitle.removeChild(buttonSubmitNewTitle)
                containerEditTitle.removeChild(buttonCancelNewTitle)
                titleTest.textContent = inputEditTitle.value;

                inputEditTitle.style.display = "none";
                titleTest.style.display = "block";
                buttonEditTitle.style.display = "block";
            })
            .catch((error) => {
                console.error(error)
                const Toast = Swal.mixin({
                    toast: true,
                    position: "bottom-end",
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true,
                    didOpen: (toast) => {
                      toast.onmouseenter = Swal.stopTimer;
                      toast.onmouseleave = Swal.resumeTimer;
                    }
                  });
                  Toast.fire({
                    icon: "error",
                    title: "Erro ao editar o título da prova"
                  });
            })
        })
    })
})