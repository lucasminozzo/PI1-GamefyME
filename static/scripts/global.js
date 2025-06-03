function showLoading() {
  document.getElementById("loading-overlay").style.display = "flex";
}

function hideLoading() {
  document.getElementById("loading-overlay").style.display = "none";
}

function toggleUserMenu() {
  var menu = document.getElementById("user-dropdown");
  menu.style.display = menu.style.display === "block" ? "none" : "block";
}

window.addEventListener('click', function (event) {
  const modais = document.querySelectorAll('.modal');
  const dropdowns = document.querySelectorAll('.user-dropdown, .notifications-dropdown');

  dropdowns.forEach(dropdown => {
    if (!dropdown.contains(event.target) && !event.target.closest('.user-menu-btn, .header-btn')) {
      dropdown.style.display = 'none';
    }
  });

  modais.forEach(modal => {
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  });
});


function fecharMsg(elemento) {
  var msg = elemento.closest(".msg-flutuante");
  if (msg) {
    msg.style.animation = "msg-saida 0.4s forwards";
    setTimeout(function () {
      msg.style.display = "none";
    }, 400);
  }
}
let cacheTodasNotificacoes = "";
fetch('/usuarios/ajax/notificacoes/')
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      cacheTodasNotificacoes = data.html;
    }
  });
document.addEventListener("DOMContentLoaded", function () {

  document.addEventListener("click", function (event) {
    const userMenu = document.getElementById("user-dropdown");
    const notificationsDropdown = document.getElementById(
      "notifications-dropdown"
    );
    const notificationsBtn = document.querySelector(".notifications-btn");
    const userMenuBtn = document.querySelector(".user-menu-btn");
    const modal = document.getElementById("notificationModal");

    if (
      userMenu &&
      userMenuBtn &&
      !userMenu.contains(event.target) &&
      !userMenuBtn.contains(event.target)
    ) {
      userMenu.style.display = "none";
    }

    if (
      notificationsDropdown &&
      notificationsBtn &&
      !notificationsDropdown.contains(event.target) &&
      !notificationsBtn.contains(event.target)
    ) {
      notificationsDropdown.style.display = "none";
    }

    if (modal && event.target === modal) {
      fecharModalNotificacao();
    }
  });

  setTimeout(function () {
    var msgs = document.querySelectorAll(".msg-flutuante");
    msgs.forEach(function (msg) {
      msg.style.animation = "msg-saida 0.4s forwards";
      setTimeout(function () {
        msg.style.display = "none";
      }, 400);
    });
  }, 5000);

  window.addEventListener("load", hideLoading);
  window.addEventListener("popstate", hideLoading);
  window.setTimeout(hideLoading, 10000);

  const formRelatorio = document.getElementById("formRelatorio");
  if (formRelatorio) {
    formRelatorio.addEventListener("submit", function (e) {
      e.preventDefault();
      const ini = this.data_inicio.value;
      const fim = this.data_fim.value;
      if (!ini || !fim) {
        alert("Por favor, selecione as duas datas.");
        return;
      }
      const url = `/relatorios/atividades/pdf/?data_inicio=${ini}&data_fim=${fim}`;
      document.getElementById("iframeRelatorio").src = url;
    });
  }
  document.querySelectorAll(".with-loading").forEach(function (el) {
    el.addEventListener("click", function (e) {
      const form = el.closest("form");
  
      if (form) {
        const inputs = form.querySelectorAll("input[required], textarea[required], select[required]");
        let valid = true;
  
        inputs.forEach(function (input) {
          if (!input.value.trim()) {
            valid = false;
          }
        });
  
        if (!valid) {
          e.preventDefault(); // impede o envio
          return; // não mostra loading
        }
      }
  
      showLoading(); // só mostra se todos os required estiverem preenchidos
    });
  });
});

function toggleNotifications(event) {
  event.stopPropagation();
  var dropdown = document.getElementById("notifications-dropdown");
  dropdown.style.display =
    dropdown.style.display === "block" ? "none" : "block";
}

function abrirModalNotificacao(id, mensagem, data, tipo) {
  const modal = document.getElementById("notificationModal");
  const modalMessage = document.getElementById("modalMessage");
  const modalDate = document.getElementById("modalDate");
  const modalIcon = document.getElementById("modalIcon");

  let iconPath = "/static/img/info.png";

  if (tipo === "sucesso") iconPath = "/static/img/gift-box.png";
  else if (tipo === "aviso") iconPath = "/static/img/warning.png";
  else if (tipo === "erro") iconPath = "/static/img/caution.png";
  
  modalIcon.innerHTML = `<img src="${iconPath}" alt="${tipo}" style="width: 50px; height: 50px; vertical-align: middle;" />`;
  modalMessage.innerText  = mensagem;
  modalDate.innerText  = data;
  modal.style.display = "block";

  marcarComoLida(id);
}

function fecharModalNotificacao() {
  const modal = document.getElementById("notificationModal");
  modal.style.display = "none";
}

function marcarComoLida(notificacaoId) {
  fetch(`/usuarios/marcar_notificacao_lida/${notificacaoId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const notificacao = document.querySelector(
          `.notification-item[data-id="${notificacaoId}"]`
        );
        if (notificacao) {
          notificacao.remove();
        
          const restantes = document.querySelectorAll(".notification-item.unread");
          if (restantes.length === 0) {
            const lista = document.querySelector(".notifications-list");
            lista.innerHTML = '<div class="no-notifications">Nenhuma notificação não lida</div>';
          }
        }
        
        atualizarContadorNotificacoes();
      }
    })
    .finally(() => {
      hideLoading();
    });
}

function marcarTodasComoLidas() {
  showLoading();
  fetch("/usuarios/marcar_todas_lidas/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        document.querySelectorAll(".notification-item.unread").forEach((item) => {
          item.remove();
        });

        const badge = document.querySelector(".notification-badge");
        if (badge) badge.remove();

        const lista = document.querySelector(".notifications-list");
        lista.innerHTML = '<div class="no-notifications">Nenhuma notificação não lida</div>';

        const marcarTodasBtn = document.querySelector('.mark-all-read');
        if (marcarTodasBtn) {
          marcarTodasBtn.remove();
        }

        atualizarContadorNotificacoes();
      }
    })
    .finally(() => {
      hideLoading();
    });
}

function atualizarContadorNotificacoes() {
  const badge = document.querySelector(".notification-badge");
  const unreadCount = document.querySelectorAll(
    ".notification-item.unread"
  ).length;

  if (badge) {
    if (unreadCount === 0) {
      badge.remove();
    } else {
      badge.textContent = unreadCount;
    }
  }
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function openRelatorioModal() {
  document.getElementById("relatorioModal").style.display = "block";
}
function closeRelatorioModal() {
  const form = document.getElementById("formRelatorio");
  const iframe = document.getElementById("iframeRelatorio");

  form.reset();
  iframe.src = "";
  document.getElementById("btnGerarPDF").classList.remove("loading");
  document.getElementById("btnGerarPDF").querySelector(".btn-text").style.display = "inline-block";
  document.getElementById("btnGerarPDF").querySelector(".btn-spinner").style.display = "none";

  document.getElementById("relatorioModal").style.display = "none";
}

function limparRelatorio() {
  document.getElementById("formRelatorio").reset();
  document.getElementById("iframeRelatorio").src = "";
}

document.addEventListener("DOMContentLoaded", function () {
  const formRelatorio = document.getElementById("formRelatorio");
  const btnGerarPDF = document.getElementById("btnGerarPDF");

  if (formRelatorio) {
    formRelatorio.addEventListener("submit", function (e) {
      e.preventDefault();
      const ini = this.data_inicio.value;
      const fim = this.data_fim.value;
      if (!ini || !fim) {
        alert("Por favor, selecione as duas datas.");
        return;
      }

      btnGerarPDF.classList.add("loading");
      btnGerarPDF.querySelector(".btn-text").style.display = "none";
      btnGerarPDF.querySelector(".btn-spinner").style.display = "inline-block";

      const url = `/relatorios/atividades/pdf/?data_inicio=${ini}&data_fim=${fim}`;
      document.getElementById("iframeRelatorio").src = url;

      const iframe = document.getElementById("iframeRelatorio");
      iframe.onload = function () {
        btnGerarPDF.classList.remove("loading");
        btnGerarPDF.querySelector(".btn-text").style.display = "inline-block";
        btnGerarPDF.querySelector(".btn-spinner").style.display = "none";
      };
    });
  }
});

function alternarTema() {
  const overlay = document.getElementById("theme-transition-overlay");
  const themeBtn = document.querySelector(".theme-btn");

  if (!themeBtn || !overlay) return;

  overlay.classList.add("active");

  setTimeout(() => {
    const isDark = document.body.classList.toggle("theme-dark");
    localStorage.setItem("tema", isDark ? "dark" : "light");

    overlay.classList.remove("active");

    themeBtn.style.transition = "transform 0.2s ease";
    themeBtn.style.transform = "scale(1.1)";
    setTimeout(() => {
      themeBtn.style.transform = "scale(1)";
    }, 200);
  }, 300);
}

document.addEventListener("DOMContentLoaded", function () {
  if (localStorage.getItem("tema") === "dark") {
    document.body.classList.add("theme-dark");
  }
});

function abrirModalAvatar() {
  document.getElementById("avatarModal").style.display = "block";
}

function fecharModalAvatar() {
  document.getElementById("avatarModal").style.display = "none";
}

let isSelectingAvatar = false;

function selecionarAvatar(nomeAvatar) {
  if (isSelectingAvatar) return;
  isSelectingAvatar = true;

  const imagens = document.querySelectorAll('.avatar-select');
  imagens.forEach(img => {
    img.classList.remove('loading');
    img.style.pointerEvents = 'none';
  });

  const imgSelecionada = Array.from(imagens).find(img => img.src.includes(nomeAvatar));
  if (imgSelecionada) {
    imgSelecionada.classList.add('loading');
  }

  fetch('/usuarios/atualizar_avatar/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ imagem_perfil: nomeAvatar })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      document.querySelector('.avatar-atual').src = `/static/img/avatares/${data.imagem_perfil}`;
      fecharModalAvatar();
    } else {
      alert('Erro ao salvar avatar: ' + data.error);
    }
  })
  .finally(() => {
    imagens.forEach(img => img.style.pointerEvents = 'auto');
    if (imgSelecionada) imgSelecionada.classList.remove('loading');
    isSelectingAvatar = false;
  });
}

function openConfigModal() {
  document.getElementById('configModal').style.display = 'block';
}

function closeConfigModal() {
  document.getElementById('configModal').style.display = 'none';
}

window.addEventListener('click', function(event) {
  const modal = document.getElementById('configModal');
  if (event.target === modal) {
      modal.style.display = 'none';
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("formConfig");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const url = form.getAttribute("action") || "/usuarios/atualizar-config/";
    const formData = new FormData(form);
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

    const botaoSalvar = form.querySelector("button[type='submit']");
    botaoSalvar.disabled = true;
    botaoSalvar.textContent = "Salvando...";
    const container = document.getElementById('container-msg-modal');
    container.innerHTML = ''; // limpa mensagens antigas

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        body: formData,
      });
      
      const data = await response.json();

      botaoSalvar.disabled = false;
      botaoSalvar.textContent = "Salvar Alterações";

      if (response.ok && data.success) {
        exibirMensagemFlutuante('success', 'Perfil atualizado com sucesso!');
        closeConfigModal();

        const nomeSpan = document.querySelector(".user-menu-btn span:nth-child(2)");
        if (nomeSpan) nomeSpan.textContent = data.nmusuario;
        const nomePerfil = document.querySelector(".profile-info h2");
        if (nomePerfil) nomePerfil.textContent = data.nmusuario;
        const dataPerfil = document.querySelector(".profile-info p");
        const dataFormatada = new Date(data.dtnascimento).toLocaleDateString('pt-BR', {timeZone: 'UTC'});
        if (dataPerfil) dataPerfil.textContent = dataFormatada;
      } else {
        const errors = data.errors || data.error;
        console.error(errors);
              
        mensagem = "Erro ao salvar configurações:  ";
        if (typeof errors === "object" && errors !== null) {
          mensagem += "\n\n";
          for (let campo in errors) {
            const nomeCampoFormatado = campo
              .replace("nmusuario", "Nome de usuário")
              .replace("emailusuario", "Email")
              .replace("dtnascimento", "Data de nascimento")
              .replace("senha_atual", "Senha atual")
              .replace("nova_senha", "Nova senha");
              
            const mensagensCampo = Array.isArray(errors[campo])
              ? errors[campo].join(", ")
              : errors[campo];
          
            mensagem += `${mensagensCampo}`;
          }
        }
        const msg = criarMensagemFlutuante(mensagem);
        container.appendChild(msg);
    }
    } catch (error) {
      botaoSalvar.disabled = false;
      botaoSalvar.textContent = "Salvar Alterações";

      console.error("Erro na requisição AJAX:", error);
      criarMensagemFlutuante("Erro inesperado ao salvar as configurações.");
      container.innerHTML = ''; // limpa mensagens antigas
    }
  });
});

function exibirMensagemFlutuante(tipo = sucesso,mensagem) {
  const div = document.createElement('div');
  div.className = `msg-flutuante ${tipo === 'error' || tipo === 'erro' ? 'erro' : 'sucesso'}`;
  div.innerHTML = `
    ${mensagem}
    <span class="fechar" onclick="fecharMsg(this)">×</span>
  `;

  // Insere logo após o header
  const header = document.getElementById('header');
  header.insertAdjacentElement('afterend', div);

  setTimeout(() => {
    div.remove();
  }, 3000);
}
function fecharMsg(elemento) {
  elemento.parentElement.remove();
}

function criarMensagemFlutuante(mensagem, tipo = 'erro') { // Cria a mensagem flutuante para colocar dentro do modal de configurações
  const div = document.createElement('div');
  div.className = `msg-flutuante ${tipo}`;
  div.innerHTML = `
    ${mensagem}
    <span class="fechar" onclick="this.parentElement.remove()">×</span>
  `;
  setTimeout(() => {
    div.remove();
  }, 5000);
  return div;
}


function openCadastroAtividadeModal() {
  document.getElementById("cadastroAtividadeModal").style.display = "block";
}

function closeCadastroAtividadeModal() {
  document.getElementById("formCadastroAtividade").reset();
  document.getElementById("cadastroAtividadeModal").style.display = "none";
}
