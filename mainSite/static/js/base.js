const menu_item_where_pay = document.querySelector('.footer-menu-wehere-pay-inner').querySelector('a');

// Прокрутка при клике по меню, где купить продукцию

menu_item_where_pay.addEventListener('click', (event)=> {
    let element = document.querySelector('.geography-of-sales-block');
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    } else {
        location.replace('/')
        element = document.querySelector('.geography-of-sales-block');
        element.scrollIntoView({ behavior: 'smooth' });
    }
})

// ========================================
// МОБИЛЬНОЕ МЕНЮ
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const headerNavMenu = document.querySelector('.header-nav-menu');
    const headerSocial = document.querySelector('.header-social');
    const body = document.body;

    // Проверка наличия элементов
    if (!mobileMenuToggle) return;

    // Открытие/закрытие мобильного меню
    mobileMenuToggle.addEventListener('click', function() {
        // Переключение класса active для кнопки
        this.classList.toggle('active');
        
        // Переключение класса active для меню
        if (headerNavMenu) {
            headerNavMenu.classList.toggle('active');
        }
        
        // Переключение класса active для социальных сетей
        if (headerSocial) {
            headerSocial.classList.toggle('active');
        }
        
        // Блокировка прокрутки страницы когда меню открыто
        if (this.classList.contains('active')) {
            body.style.overflow = 'hidden';
        } else {
            body.style.overflow = '';
        }
    });

    // Закрытие меню при клике на пункт меню
    if (headerNavMenu) {
        const menuItems = headerNavMenu.querySelectorAll('.nav-menu-item a');
        menuItems.forEach(item => {
            item.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                headerNavMenu.classList.remove('active');
                if (headerSocial) {
                    headerSocial.classList.remove('active');
                }
                body.style.overflow = '';
            });
        });
    }

    // Закрытие меню при изменении размера окна (если переключились на десктоп)
    window.addEventListener('resize', function() {
        if (window.innerWidth > 680) {
            if (mobileMenuToggle.classList.contains('active')) {
                mobileMenuToggle.classList.remove('active');
                if (headerNavMenu) {
                    headerNavMenu.classList.remove('active');
                }
                if (headerSocial) {
                    headerSocial.classList.remove('active');
                }
                body.style.overflow = '';
            }
        }
    });

    // Закрытие меню при клике вне меню
    document.addEventListener('click', function(event) {
        const isClickInsideMenu = headerNavMenu && headerNavMenu.contains(event.target);
        const isClickOnToggle = mobileMenuToggle.contains(event.target);
        
        if (!isClickInsideMenu && !isClickOnToggle && mobileMenuToggle.classList.contains('active')) {
            mobileMenuToggle.classList.remove('active');
            if (headerNavMenu) {
                headerNavMenu.classList.remove('active');
            }
            if (headerSocial) {
                headerSocial.classList.remove('active');
            }
            body.style.overflow = '';
        }
    });
});
