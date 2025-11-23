// Объявление переменных

const login_submit_btn = document.querySelector('#login-form-submit-btn');
const login_form = document.querySelector('#login-form');



// Пока не настроена аутентификация, кнопка просто переводит в личный кабинет

login_submit_btn.addEventListener('click', (event)=>{
    event.preventDefault();
    window.location.href = '/tempates/pc/personalCabinet.html'
})