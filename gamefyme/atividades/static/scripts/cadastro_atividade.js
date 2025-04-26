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

document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.btn-add').addEventListener('click', function() {
        showLoading();
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