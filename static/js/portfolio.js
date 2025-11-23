// Галлерея

const open_gallery_btns = document.querySelectorAll('.portfolio-gallery-item-open-gal');
for (const btn of open_gallery_btns) {
    btn.addEventListener('click', (event)=> {
        event.preventDefault();
        portfolio_id = event.target.dataset.portfolioid //Забираем идетификатор портфолио
        link = event.target.href + '/';
        csrf_token = event.target.parentElement.querySelector('input[name="csrfmiddlewaretoken"]').value
        fetch(link, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            body: JSON.stringify({ 'portfolio_id': portfolio_id })
            })
            .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
            })
            .then(data => {
            
                if (data.success) {
                    galleryData = {
                        title: 'Портфолио № ' + portfolio_id,
                        images: []
                    }
                    for (const img of data.data) {
                        img_data = {
                            src: img.src,
                            thumb: img.src,
                            width: 600,
                            height: 400,
                            caption: img.caption
                        }
                        galleryData.images.push(img_data);
                    }
                    let myGallery = new Bizon(galleryData);
                    myGallery.show()
                } else {
                    console.log('Ошибка на сервере:', data.error);
                }
            })
            .catch(error => {
            console.error('Произошла ошибка:', error);
        });  
    })
}