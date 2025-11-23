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

const news_slider = new Swiper('.news-swiper', {
  slidesPerView: 3,
  spaceBetween: 30,
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