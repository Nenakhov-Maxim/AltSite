// Объявление переменных

const new_order_popup = document.querySelector('.popup-new-order');
const open_new_order_btn = document.querySelector('#pc-content-new-order-btn');


// Открытие формы создания новой заявки

open_new_order_btn.addEventListener('click', (event)=> {
    event.preventDefault();
    new_order_popup.classList.remove('disable-popup');
})