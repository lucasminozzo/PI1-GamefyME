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

function validarTempo(input) {
    const feedback = document.getElementById('tempo-feedback');
    const valor = input.value === "" ? null : parseInt(input.value);

    input.value = input.value.replace(/[^0-9]/g, '');

    if (input.value === "") {
        input.classList.remove('invalido');
        feedback.classList.remove('erro');
        feedback.textContent = 'Máximo 240 minutos (4 horas)';
        return;
    }

    if (valor < 1) {
        input.classList.add('invalido');
        feedback.classList.add('erro');
        feedback.textContent = 'Mínimo 1 minuto';
        return;
    }

    if (valor > 240) {
        input.classList.add('invalido');
        feedback.classList.add('erro');
        feedback.textContent = 'Máximo 240 minutos (4 horas)';
        return;
    }

    input.classList.remove('invalido');
    feedback.classList.remove('erro');
    feedback.textContent = `${valor} minutos`;
}

function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.form-container');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (this.checkValidity()) {
            showLoading();
            this.submit();
        } else {
            this.reportValidity();
        }
    });

    document.querySelectorAll('a.btn-cancel, a.action-btn').forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (!this.target || this.target !== '_blank') {
                showLoading();
            }
        });
    });

    var logoutLink = document.querySelector('.user-dropdown a[href*="logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            showLoading();
        });
    }

    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (typeof bootstrap !== 'undefined') {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.display = 'none';
            }
        });
    }, 5000);

    window.addEventListener('load', hideLoading);
    window.addEventListener('popstate', hideLoading);
    window.setTimeout(hideLoading, 10000);
});