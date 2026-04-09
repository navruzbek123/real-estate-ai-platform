$(document).ready(function() {
    initFavorites();
    initDarkMode();
    initNavbarScroll();
    
    if (typeof isAuthenticated !== 'undefined' && isAuthenticated) {
        initNotifications();
    }
});

function initFavorites() {
    $('.favorite-btn').off('click').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        var btn = $(this);
        var id = btn.data('id');
        var icon = btn.find('i');
        
        $.ajax({
            url: '/favorites/toggle/',
            method: 'POST',
            data: {
                listing_id: id,
                csrfmiddlewaretoken: getCookie('csrftoken')
            },
            success: function(res) {
                if (res.success) {
                    if (res.action === 'added') {
                        btn.addClass('active');
                        icon.removeClass('far').addClass('fas');
                        showNotification('Добавлено в избранное', 'success');
                    } else {
                        btn.removeClass('active');
                        icon.removeClass('fas').addClass('far');
                        showNotification('Удалено из избранного', 'info');
                        
                        if (btn.closest('.listing-card').length) {
                            btn.closest('.listing-card').fadeOut(300, function() {
                                $(this).remove();
                            });
                        }
                    }
                }
            },
            error: function() {
                showNotification('Войдите для добавления в избранное', 'error');
            }
        });
    });
}

function initDarkMode() {
    var stored = localStorage.getItem('darkMode');
    if (stored === 'true') {
        $('body').addClass('dark-mode');
    }
    
    $('#darkModeToggle').off('click').on('click', function() {
        var isDark = $('body').toggleClass('dark-mode').hasClass('dark-mode');
        localStorage.setItem('darkMode', isDark);
        
        var icon = $(this).find('i');
        if (isDark) {
            icon.removeClass('fa-moon').addClass('fa-sun');
        } else {
            icon.removeClass('fa-sun').addClass('fa-moon');
        }
        
        $.ajax({
            url: '/accounts/dark-mode/',
            method: 'POST',
            data: {
                dark_mode: isDark,
                csrfmiddlewaretoken: getCookie('csrftoken')
            }
        });
    });
}

function initNotifications() {
    updateNotificationsCount();
    
    setInterval(function() {
        updateNotificationsCount();
    }, 30000);
}

function updateNotificationsCount() {
    $.ajax({
        url: '/accounts/api/profile/',
        method: 'GET',
        success: function(data) {
            if (data.profile && data.profile.dark_mode) {
                $('body').addClass('dark-mode');
            }
        },
        error: function() {}
    });
}

function initNavbarScroll() {
    $(window).scroll(function() {
        if ($(this).scrollTop() > 50) {
            $('.navbar').addClass('scrolled');
        } else {
            $('.navbar').removeClass('scrolled');
        }
    });
}

function showNotification(message, type) {
    var icon = 'info-circle';
    var bgClass = 'alert-info';
    
    switch(type) {
        case 'success':
            icon = 'check-circle';
            bgClass = 'alert-success';
            break;
        case 'error':
            icon = 'exclamation-circle';
            bgClass = 'alert-error';
            break;
        case 'warning':
            icon = 'exclamation-triangle';
            bgClass = 'alert-warning';
            break;
    }
    
    var html = '<div class="alert ' + bgClass + '">' +
                '<i class="fas fa-' + icon + '"></i> ' + message +
                '</div>';
    
    var container = $('.messages-container');
    if (!container.length) {
        container = $('<div class="messages-container"></div>').prependTo('body');
    }
    
    container.html(html).show();
    
    setTimeout(function() {
        container.fadeOut();
    }, 3000);
}

function formatPrice(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function debounce(func, wait) {
    var timeout;
    return function() {
        var context = this;
        var args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}

function sanitizeHTML(str) {
    var temp = document.createElement('div');
    temp.textContent = str;
    return temp.innerHTML;
}
