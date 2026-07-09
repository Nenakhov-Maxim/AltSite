// Убираем последний значок > в хлебных крошках

const breadCrumbsWrapper = document.querySelector('.bread-crumbs-wrapper');
const spans = breadCrumbsWrapper ? breadCrumbsWrapper.querySelectorAll('span') : [];
if (spans.length) {
    spans[spans.length - 1].style.display = 'none';
}


// Работа меню слева 

const leftSideMenuList = document.querySelector('.left-side-menu-list');
const menuList = leftSideMenuList ? leftSideMenuList.querySelectorAll('a') : [];

for (const menu of menuList) {
    if (menu.href == window.location.href) {
        const activeMenuLeft = leftSideMenuList.querySelector('.menu-active');
        if (activeMenuLeft) {
            activeMenuLeft.classList.remove('menu-active');
        }
        menu.classList.add('menu-active');
    }
}

const leftSideMenuToggle = document.querySelector('.left-side-menu-toggle');
if (leftSideMenuToggle && leftSideMenuList) {
    leftSideMenuToggle.addEventListener('click', () => {
        const isOpen = leftSideMenuList.classList.toggle('left-side-menu-list-open');
        leftSideMenuToggle.setAttribute('aria-expanded', String(isOpen));
    });
}


// Поиск и пагинация продукции

const productSearch = document.querySelector('#production-search');
const productCards = Array.from(document.querySelectorAll('.card-item'));
const productionPagination = document.querySelector('.production-pagination');
const productionEmptyMessage = document.querySelector('.production-empty-message');
const cardsPerPage = 12;
let currentProductPage = 1;

const normalizeSearchText = (value) => value
    .toLowerCase()
    .replaceAll('ё', 'е')
    .replace(/\s+/g, ' ')
    .trim();

const getCardSearchText = (card) => {
    const title = card.querySelector('.card-item-text-block-wrapper')?.textContent || '';
    const description = card.querySelector('.card-item-description-block-wrapper')?.textContent || '';
    return normalizeSearchText(`${title} ${description}`);
};

const indexedProductCards = productCards.map((card) => ({
    card,
    searchText: getCardSearchText(card),
}));

const getFilteredProductCards = () => {
    const query = normalizeSearchText(productSearch?.value || '');

    if (!query) {
        return indexedProductCards;
    }

    return indexedProductCards.filter(({ searchText }) => searchText.includes(query));
};

const renderProductionPagination = (totalPages) => {
    if (!productionPagination) {
        return;
    }

    productionPagination.innerHTML = '';

    if (totalPages <= 1) {
        productionPagination.classList.add('production-hidden');
        return;
    }

    productionPagination.classList.remove('production-hidden');

    const createButton = (label, page, className = '', isDisabled = false) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = label;
        button.className = `production-pagination-button ${className}`.trim();
        button.dataset.page = page;
        button.disabled = isDisabled;

        if (page === currentProductPage) {
            button.classList.add('production-pagination-button-active');
            button.setAttribute('aria-current', 'page');
        }

        return button;
    };

    productionPagination.append(createButton(
        '‹',
        Math.max(currentProductPage - 1, 1),
        'production-pagination-button-nav',
        currentProductPage === 1
    ));

    for (let page = 1; page <= totalPages; page += 1) {
        productionPagination.append(createButton(String(page), page));
    }

    productionPagination.append(createButton(
        '›',
        Math.min(currentProductPage + 1, totalPages),
        'production-pagination-button-nav',
        currentProductPage === totalPages
    ));
};

const renderProducts = () => {
    const filteredCards = getFilteredProductCards();
    const totalPages = Math.ceil(filteredCards.length / cardsPerPage);

    if (currentProductPage > totalPages) {
        currentProductPage = totalPages || 1;
    }

    const pageStart = (currentProductPage - 1) * cardsPerPage;
    const visibleCards = new Set(
        filteredCards
            .slice(pageStart, pageStart + cardsPerPage)
            .map(({ card }) => card)
    );

    productCards.forEach((card) => {
        card.classList.toggle('production-hidden', !visibleCards.has(card));
    });

    if (productionEmptyMessage) {
        productionEmptyMessage.classList.toggle('production-hidden', filteredCards.length > 0);
    }

    renderProductionPagination(totalPages);
};

if (productCards.length) {
    productSearch?.addEventListener('input', () => {
        currentProductPage = 1;
        renderProducts();
    });

    productionPagination?.addEventListener('click', (event) => {
        const button = event.target.closest('.production-pagination-button');

        if (!button) {
            return;
        }

        currentProductPage = Number(button.dataset.page);
        renderProducts();
    });

    renderProducts();
}
