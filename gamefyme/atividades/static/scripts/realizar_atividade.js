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

function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function fecharMsg(el) {
    el.parentElement.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.form-container');

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            if (this.checkValidity()) {
                showLoading();
                this.submit();
            } else {
                this.reportValidity();
            }
        });
    }

    window.addEventListener('load', hideLoading);
});
