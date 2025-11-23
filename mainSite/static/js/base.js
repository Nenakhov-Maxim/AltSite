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