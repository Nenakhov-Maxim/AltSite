// Объявление переменных

const popups_close_x_btn = document.querySelectorAll('.popup-close-btn');
const popup_vacancies_more_detail = document.querySelector('.popup-vacancies-more-detail');
const more_detail_btns = document.querySelectorAll('#current-vacancies-card-item-more-info-btn');
const approve_btn = popup_vacancies_more_detail.querySelector('.popup-vacancies-approve-btn');
const poppup_respond = document.querySelector('.popup-respond-vacancy');
const job_application_form = document.getElementById('respond-vacancy-form');
const complete_popup = document.querySelector('.complete-popup');


// Закрытие любого popup по клику на крестик

for (const close_btn of popups_close_x_btn) {
    close_btn.addEventListener('click', (event)=> {
        target_popup = event.target.parentElement.parentElement.parentElement;
        target_popup.classList.add('popup-disable');
    });
};


// Открытие popup просмотра детальной информации о вакансии

for (const btn of more_detail_btns) {
    btn.addEventListener('click', (event)=> {
        event.preventDefault();
        vacancies_id = event.target.dataset.vacanciesid
        csrftoken = event.target.parentElement.parentElement.querySelector('input[name="csrfmiddlewaretoken"]').value
        // Идентификатор нужно отправить на сервер и получить ответ с информацией о вакансии
        fetch(`/job/${vacancies_id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({})
        })
        .then(response => {return response.json()})
        .then(answer => {
            genRequirements(answer.data.requirements.split(';'));
            genResponsibilities(answer.data.responsibilities.split(';'));
            // Меняем заголовок, регион и открываем POPUP
            popup_vacancies_more_detail.querySelector('.popup-vacancies-title').innerHTML = answer.data.title;
            popup_vacancies_more_detail.querySelector('.popup-vacancies-location').innerHTML = answer.data.region;
            popup_vacancies_more_detail.querySelector('.popup-vacancies-approve-btn').dataset.vacanciesid = answer.data.id;
            popup_vacancies_more_detail.classList.remove('popup-disable');
            poppup_respond.querySelector('input[name="vacancies-id"]').value = answer.data.id;
            approve_btn.dataset.vacanciesid = vacancies_id;
        });
    });
}

        
function genRequirements(data){
    // Генерируем требования и добавляем в список
    requiments_list = popup_vacancies_more_detail.querySelector('.popup-vacancies-requirements-list');
    requiments_list.innerHTML = '';
    for (const req of data) {
        let new_li = document.createElement('li');
        new_li.classList.add('popup-vacancies-requirements-item');
        new_li.innerHTML = req.trim(); 
        requiments_list.append(new_li);
    } 
}

function genResponsibilities(data) {
    // Генерируем обязанности и добавляем в список
    duties_list = popup_vacancies_more_detail.querySelector('.popup-vacancies-duties-list');
    duties_list.innerHTML = '';
    for (const resp of data) {
        let new_li = document.createElement('li');
        new_li.classList.add('popup-vacancies-duties-item');
        new_li.innerHTML = resp.trim(); 
        duties_list.append(new_li);
    }
}


// Открытие формы заполнения днных о себе

approve_btn.addEventListener('click', (event)=> {
    event.preventDefault();
    vacancies_id = event.target.dataset.vacanciesid;
    popup_vacancies_more_detail.classList.add('popup-disable');
    poppup_respond.classList.remove('popup-disable');
    
})

job_application_form.addEventListener('submit', (event)=>{
    
    event.preventDefault();
    formData = new FormData(job_application_form);
    csrftoken = formData.get('csrfmiddlewaretoken');
    data = {
        vacancies_id: formData.get('vacancies-id'),
        name: formData.get('respond-vacancy-username'),
        date_point_birthday: formData.get('respond-vacancy-birthday'),
        adress: formData.get('respond-vacancy-adress'),
        education_level: formData.get('respond-vacancy-education-level'),
        additional_education: formData.get('respond-vacancy-subeducation-level'),
        marital_status: formData.get('respond-vacancy-marital-status'),
        desired_salary: formData.get('respond-vacancy-desired-income'),
        email: formData.get('respond-vacancy-email'),
        phone_number: formData.get('respond-vacancy-tel'),
        additional_information: formData.get('respond-vacancy-information'),
        resume_file: formData.get('respond-vacancy-file-upload'),
    }
    // Проверка заполнения нужных полей
    errors = checkInputExeption(data);
    if (errors.length > 0) {
        form_errors_ul = job_application_form.querySelector('.form-errors');
        form_errors_ul.innerHTML = ''
        for (const error of errors) {
            new_li = document.createElement('li');
            new_li.classList.add('error-item');
            new_li.innerHTML = error;
            form_errors_ul.insertAdjacentElement('beforeend', new_li);
        }
        return
    }
    if (data.resume_file.size == 0 || data.resume_file.name=='') {
        if (!confirm('Вы уверены, что хотите отправить отклик без файла резюме?')) {
            return
        }
    }
    
    // Проверка чекбокса, что согласен на обработку ПД

    // Отправка на сервер

    fetch('/job/job-application/', {
        method: 'POST',
        headers: {
            // 'Content-Type': 'multipart/form-data',
            // 'X-CSRFToken': csrftoken
        },
        body: formData
    })
    .then(respose => {return respose.json()})
    .then(data=> {
        if (data.success) {
            data = data.data
            complete_popup.querySelector('.complete-send-email-or-phone').innerHTML = `Мы свяжемся с Вами по Email: ${data.email} или телефону: ${data.tel}`;
            complete_popup.classList.remove('popup-disable');
            completeAnimating();
        }
    });

})

function completeAnimating() {
    timer = complete_popup.querySelector('.complete-timer');
    for (let t = 1; t < 4; t++) {
        setTimeout(()=>{
            timer.innerHTML = `Через ${3 - t} сек. окно закроется...`;
        }, t * 1000);
    }
    setTimeout(()=> {
        window.location.reload();
    }, 4000)
    
}

// Функция проверки правильности заполнения полей в форме

function checkInputExeption(data) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const phoneRegex = /^(8|\+7)[- ]?(\(?\d{3}\)?[- ]?)?[\d-]{7,10}$/;
    error_lib = {
       name: 'Введите, пожалуйста, Ваше ФИО',
       education_level: 'Введите, пожалуйста, Ваш уровень образования',
       marital_status: 'Введите, пожалуйста, Ваше семейное положение',
       email: 'Введите, пожалуйста, Email. <br> Email должен соответствовать шаблону name@domen.ru',
       phone_number: 'Введите, пожалуйста, номер телефона. <br> Телефон должен соответствовать шаблону +7(000)000-00-00 или 8(000)000-00-00',
    }
    errors = []
    for (const key in data) {
        if (!Object.hasOwn(data, key)) continue;
        const value = data[key];
        if ((!value || value == '') && (Object.hasOwn(error_lib, key))) {
            errors.push(error_lib[key])
        } else if (key == 'email') {
            if (!emailRegex.test(data[key])) {
                errors.push(error_lib[key])
            }
        } else if (key == 'phone_number') {
            if(!phoneRegex.test(data[key])) {
                errors.push(error_lib[key])   
            }    
        }

    }
    return errors
}
