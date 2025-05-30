function showLoading() {
    document.getElementById("loading-overlay").style.display = "flex";
  }

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.querySelector("form[action*='login']");
    const btnLogin = document.getElementById("btnLogin");
  
    if (loginForm && btnLogin) {
      loginForm.addEventListener("submit", function (e) {
        const email = loginForm.querySelector("#email").value.trim();
        const senha = loginForm.querySelector("#senha").value.trim();
  
        if (!email || !senha) {
          e.preventDefault();
          alert("Preencha o email e a senha.");
          return;
        }
  
        showLoading();
      });
    }
  });
  