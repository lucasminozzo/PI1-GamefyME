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
    const cards = document.querySelectorAll('.desafio-item');
    cards.forEach(card => {
      const status = card.dataset.status;
      card.style.display = (filtro === 'todos' || filtro === status) ? '' : 'none';
    });
  }
