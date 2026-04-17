// Карусель для раздела с примерами систем вентфасадов
$(document).ready(function(){
  $('.owl-carousel').owlCarousel({
    loop:true,
    margin:10,
    dots:true,
    dotsEach: 1,
    items: 1,
    center:true,
    autoplay:true,
    autoplayTimeout:5000,
    autoplayHoverPause:true,
    autoplaySpeed: 1500
    })
});

//Слайдер для раздела с примерами работ
const swiper = new Swiper('.swiper', {
  effect: 'creative',
  creativeEffect: {
    prev: {
      translate: [0,0,-400],
    },
    next: {
      translate: ['100%', 0,0],
    },
  },
  loop: true,
  parallax: true,
  navigation: {
    nextEl: '.swiper-button-next'
  },
  // keyboard: {
  //     enabled: true,
  //     onlyInViewport: true,
  // },
  mousewheel: {
    enabled: true,
    eventsTarget: '.swiper-button-next'
  },
  
});

//Слайдер для новостей
let slides_card_number = 3
let spaces = 30
if (window.innerWidth < 800) {
    slides_card_number = 2
    spaces = 20
}
if (window.innerWidth < 640) {
    slides_card_number = 1
    spaces = 10
}


const news_slider = new Swiper('.news-swiper', {
  
  slidesPerView: slides_card_number,
  spaceBetween: spaces,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  mousewheel: {
    enabled: true,
    eventsTarget: '.news-swiper',
  },
  loop: true,
  keyboard: {
      enabled: true,
      onlyInViewport: true,
  },
})

document.addEventListener('DOMContentLoaded', () => {
  const productButtons = document.querySelectorAll('.top-section-product-btn');
  const alternativeItems = document.querySelectorAll('.alternative-numbers-item');
  const revealItems = [];

  for (const button of productButtons) {
    button.classList.add('scroll-reveal', 'from-left');
    revealItems.push(button);
  }

  alternativeItems.forEach((item, index) => {
    item.classList.add('scroll-reveal', index % 2 === 0 ? 'from-left' : 'from-right');
    revealItems.push(item);
  });

  if (!revealItems.length) {
    return;
  }

  if (!('IntersectionObserver' in window)) {
    for (const item of revealItems) {
      item.classList.add('is-visible');
    }
    return;
  }

  const observer = new IntersectionObserver((entries, currentObserver) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) {
        continue;
      }

      entry.target.classList.add('is-visible');
      currentObserver.unobserve(entry.target);
    }
  }, {
    threshold: 0.18,
    rootMargin: '0px 0px -8% 0px',
  });

  for (const item of revealItems) {
    observer.observe(item);
  }
});
