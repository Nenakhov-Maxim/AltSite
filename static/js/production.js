// Убираем последний значок > в хлебных крошках

spans = document.querySelector('.bread-crumbs-wrapper').querySelectorAll('span')
spans[spans.length - 1].style.display = 'none';


// Работа меню слева 

menu_list = document.querySelector('.left-side-menu-list').querySelectorAll('a')

for (const menu of menu_list) {
    if (menu.href == window.location.href) {
        active_menu_left = document.querySelector('.left-side-menu-list').querySelector('.menu-active');
        if (active_menu_left) {
            active_menu_left.classList.remove('menu-active');
        }
        menu.classList.add('menu-active');
    }
}