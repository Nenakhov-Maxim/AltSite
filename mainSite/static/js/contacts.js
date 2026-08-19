const close_success_modal_btn = document.querySelector('.close-button-modal');
if (close_success_modal_btn) {
    close_success_modal_btn.addEventListener('click', (event)=> {
        console.log(close_success_modal_btn)
        modal = document.querySelector('.modal-success');
        if (modal) {
            modal.remove();
        }
    })
}

const captchaRefreshButton = document.querySelector('.feedback-captcha-refresh');
if (captchaRefreshButton) {
    captchaRefreshButton.addEventListener('click', async () => {
        captchaRefreshButton.disabled = true;

        try {
            const response = await fetch(captchaRefreshButton.dataset.refreshUrl, {
                headers: {'X-Requested-With': 'XMLHttpRequest'},
            });
            if (!response.ok) {
                throw new Error('Captcha refresh failed');
            }

            const captcha = await response.json();
            const wrapper = captchaRefreshButton.closest('.feedback-captcha-wrapper');
            const image = wrapper.querySelector('.captcha');
            const keyInput = wrapper.querySelector('input[name="captcha_0"]');
            const answerInput = wrapper.querySelector('input[name="captcha_1"]');

            image.src = captcha.image_url;
            keyInput.value = captcha.key;
            answerInput.value = '';
            answerInput.focus();
        } finally {
            captchaRefreshButton.disabled = false;
        }
    });
}
