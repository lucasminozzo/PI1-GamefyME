function abrirModalCadastroDesafio() {
    document.getElementById('modalCadastroDesafio').style.display = 'block';
  }
  function fecharModalCadastroDesafio() {
    document.getElementById('modalCadastroDesafio').style.display = 'none';
  }
  function abrirModalEditarDesafio(id, nome, descricao, tipo, inicio, fim, xp, logica, parametro) {
    document.getElementById('editar_iddesafio').value = id;
    document.getElementById('editar_nmdesafio').value = nome;
    document.getElementById('editar_dsdesafio').value = descricao;
    document.getElementById('editar_tipo').value = tipo;
    document.getElementById('editar_dtinicio').value = inicio;
    document.getElementById('editar_dtfim').value = fim;
    document.getElementById('editar_expdesafio').value = xp;
    document.getElementById('editar_tipo_logica').value = logica;
    document.getElementById('editar_parametro').value = parametro;
  
    document.getElementById('modalEditarDesafio').style.display = 'block';
    document.body.style.overflow = 'hidden';
  }
  function fecharModalEditarDesafio() {
    document.getElementById('modalEditarDesafio').style.display = 'none';
    document.body.style.overflow = '';
  }
  window.onclick = function(event) {
    const cadastro = document.getElementById('modalCadastroDesafio');
    const editar = document.getElementById('modalEditarDesafio');
    if (event.target === cadastro) fecharModalCadastroDesafio();
    if (event.target === editar) fecharModalEditarDesafio();
  };

  function filtrarDesafios() {
    const filtro = document.getElementById('filtro-status').value;
    const todosOsCards = document.querySelectorAll('.desafio-item');
    let algumCardVisivelNoTotal = false;

    todosOsCards.forEach(card => {
        const status = card.getAttribute('data-status');

        if (filtro === 'todos' || filtro === status) {
            card.style.display = 'block';
            algumCardVisivelNoTotal = true;
        } else {
            card.style.display = 'none';
        }
    });

    const todosOsGrupos = document.querySelectorAll('.desafio-grupo');
    todosOsGrupos.forEach(grupo => {
        const cardsVisiveisNoGrupo = grupo.querySelectorAll('.desafio-item[style*="display: block"]');

        if (cardsVisiveisNoGrupo.length > 0) {
            grupo.style.display = 'block';
        } else {
            grupo.style.display = 'none';
        }
    });

    const mensagemVazio = document.getElementById('nenhum-desafio-encontrado');
    if (algumCardVisivelNoTotal) {
        mensagemVazio.style.display = 'none';
    } else {
        mensagemVazio.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const filtroSelect = document.getElementById('filtro-status');
    if (filtroSelect) {
        filtroSelect.value = 'todos';
    }
    
    filtrarDesafios();
});