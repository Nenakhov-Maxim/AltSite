// Убираем последний значок > в хлебных крошках

const breadCrumbsWrapper = document.querySelector('.bread-crumbs-wrapper');
const spans = breadCrumbsWrapper ? breadCrumbsWrapper.querySelectorAll('span') : [];
if (spans.length) {
    spans[spans.length - 1].style.display = 'none';
}


// Работа меню слева 

const leftSideMenuList = document.querySelector('.left-side-menu-list');
const menuList = leftSideMenuList ? leftSideMenuList.querySelectorAll('a') : [];

for (const menu of menuList) {
    if (menu.href == window.location.href) {
        const activeMenuLeft = leftSideMenuList.querySelector('.menu-active');
        if (activeMenuLeft) {
            activeMenuLeft.classList.remove('menu-active');
        }
        menu.classList.add('menu-active');
    }
}

const leftSideMenuToggle = document.querySelector('.left-side-menu-toggle');
if (leftSideMenuToggle && leftSideMenuList) {
    leftSideMenuToggle.addEventListener('click', () => {
        const isOpen = leftSideMenuList.classList.toggle('left-side-menu-list-open');
        leftSideMenuToggle.setAttribute('aria-expanded', String(isOpen));
    });
}
