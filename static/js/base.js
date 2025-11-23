// Объявление переменных
const nav_menu_list = document.querySelectorAll('.nav-menu-item')
const link_now = window.location.href
// Работа меню

for (const li of nav_menu_list) {
    link = li.querySelector('a')
    link_adress = link.href.split('/')[3];
    if (link_now.includes(link_adress)) {

        active_element_now = document.querySelector('li.header-active-menu');
        if (active_element_now) {
            active_element_now.classList.remove('header-active-menu')
        }

        li.classList.add('header-active-menu');
        
    }
}
