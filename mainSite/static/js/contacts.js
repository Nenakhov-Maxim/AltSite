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