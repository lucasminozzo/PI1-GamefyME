document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("busca-usuarios");
  const usuarios = document.querySelectorAll(".usuario-card");

  input.addEventListener("input", function () {
    const termo = input.value.toLowerCase();

    usuarios.forEach(function (card) {
      const nome = card.dataset.nome;
      card.style.display = nome.includes(termo) ? "block" : "none";
    });
  });
});