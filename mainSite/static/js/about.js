// Убираем последний значок > в хлебных крошках

spans = document.querySelector('.bread-crumbs-wrapper').querySelectorAll('span')
spans[spans.length - 1].style.display = 'none';