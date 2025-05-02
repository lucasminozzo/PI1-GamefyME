function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function toggleUserMenu() {
    var menu = document.getElementById('user-dropdown');
    menu.style.display = (menu.style.display === 'block') ? 'none' : 'block';
}

window.onclick = function(event) {
    if (!event.target.matches('.user-menu-btn') && !event.target.closest('.user-menu-container')) {
        var dropdowns = document.getElementsByClassName("user-dropdown");
        for (var i = 0; i < dropdowns.length; i++) {
            dropdowns[i].style.display = "none";
        }
    }
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

    document.querySelectorAll('a:not(.user-dropdown a)').forEach(function(link) {
        link.addEventListener('click', function() {
            if (!this.target || this.target !== '_blank') {
                showLoading();
            }
        });
    });

    document.querySelectorAll('.task-btn, .action-btn, button:not(.user-menu-btn):not(.fechar)').forEach(function(btn) {
        btn.addEventListener('click', function() {
            if (!btn.closest('.user-dropdown')) {
                showLoading();
            }
        });
    });

    var logoutLink = document.querySelector('.user-dropdown a[href*="logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function() {
            showLoading();
        });
    }

    setTimeout(function() {
        var msgs = document.querySelectorAll('.msg-flutuante');
        msgs.forEach(function(msg) {
            msg.style.animation = 'msg-saida 0.4s forwards';
            setTimeout(function() { msg.style.display = 'none'; }, 400);
        });
    }, 5000);

    window.addEventListener('load', hideLoading);
    window.addEventListener('popstate', hideLoading);
    window.setTimeout(hideLoading, 10000);
});