function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function fecharMsg(elemento) {
    var msg = elemento.closest('.msg-flutuante');
    if (msg) {
        msg.style.animation = 'msg-saida 0.4s forwards';
        setTimeout(function() { msg.style.display = 'none'; }, 400);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function() {
            showLoading();
        });
    });
    document.querySelectorAll('header a').forEach(function(link) {
        link.addEventListener('click', function() {
            if (!this.target || this.target !== '_blank') {
                showLoading();
            }
        });
    });
    document.querySelector('.forgot-password').addEventListener('click', function() {
        showLoading();
    });

    var msgs = document.querySelectorAll('.msg-flutuante');
    msgs.forEach(function(msg) {
        setTimeout(function() {
            msg.style.animation = 'msg-saida 0.4s forwards';
            setTimeout(function() { msg.style.display = 'none'; }, 400);
        }, 5000);
    });

    window.addEventListener('load', hideLoading);
    window.addEventListener('popstate', hideLoading);
    window.setTimeout(hideLoading, 10000);
});