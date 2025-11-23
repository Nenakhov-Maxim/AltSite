// Объявление переменных
const popup = document.querySelector('.popup-new-order');
const close_popup_x_btn = popup.querySelectorAll('.popup-close-x');
const close_popup_btn = popup.querySelector('#new-order-form-close-form');
const submit_btn = popup.querySelector('#new-order-form-submit-form');
const logger = popup.querySelector('.logger-wrapper');

//Закрытие POPUP по клику на крестик (всех)

for (const btn_x of close_popup_x_btn) {
    btn_x.addEventListener('click', (event)=> {
        parent_popup = event.target.parentElement.parentElement.parentElement;
        parent_popup.classList.add('disable-popup');
    })
}

// Закрытие POPUP создания новой заявки по клику по кнопке "отмена"

close_popup_btn.addEventListener('click', ()=> {
    popup.classList.add('disable-popup');
})

// Отправка формы на сервер

submit_btn.addEventListener('click', (event)=>{
    event.preventDefault();
    // Собираем данные из формы
    form = popup.querySelector('#new-order-form');
    form_data = form.elements

    data = {
        'order_name': form_data[0].value,
        'organization_name': form_data[1].value,
        'consumer_name': form_data[2].value,
        'consumer_phone': form_data[3].value,
        'consumer_email': form_data[4].value,
        'product_name': form_data[5].value,
        'product_count': form_data[6].value,
    };
   
    // Отправляем данные на сервер
    openLogger();

    fetch('/create-new-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'data': data
            })
        })
        .then(response => response.json())
        .then(data => {
            closeLogger();
            // Продолжаем код тут
            // Пример возвращаемого значения
            data = {
                'order_id': 1,
                'order_name': 'Заявка № 1',
                'organization_name': 'ООО "Северсталь"',
                'consumer_name': 'Щавелев Николай Александрович',
                'consumer_phone': '+7(951)777-66-55',
                'consumer_email': 'shavelev@mail.ru',
                'product_name': 'Изготовление фасадной системы АЛЬФА',
                'product_count': '1500',    
            }
        })
        .catch(error => {
            popup.querySelector('.logger-inner').innerHTML = 'Ошибка на сервере: <br>' + error
            setTimeout(() => {
                closeLogger();    
            }, 3000);
        });


})

function create_new_order(data) {
    sendAjaxQuery(data)
    return {}
    
}

function sendAjaxQuery(data) {
    setTimeout(closeLogger, 5000)
}

function openLogger(){
    logger.classList.remove('disable-popup');
}

function closeLogger(){
    logger.classList.add('disable-popup');
}