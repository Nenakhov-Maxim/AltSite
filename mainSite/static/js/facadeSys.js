const allTypeFacadeSys = document.querySelectorAll('.facade-menu-list');
const openSystemBtns = document.querySelectorAll('.facade-menu-item-text');
const LIST_STAGGER_DELAY = 90;
const LIST_ANIMATION_DURATION = 320;

// Реализация раскрывающихся списков при загрузке страницы

document.addEventListener('DOMContentLoaded', ()=> {
    if (!allTypeFacadeSys.length) {
        return;
    }

    allTypeFacadeSys.forEach((typeFacadeSys)=> {
        const innerSysList = Array.from(typeFacadeSys.querySelectorAll('.subitem'));
        const menuToggle = typeFacadeSys.querySelector('.facade-menu-item-text');

        if (!menuToggle || !innerSysList.length) {
            return;
        }

        const hasActiveLink = Boolean(typeFacadeSys.querySelector('.active-nav-facade'));

        if (hasActiveLink) {
            menuToggle.classList.remove('close-facade-menu-item');
            menuToggle.classList.add('open-facade-menu-item');
            innerSysList.forEach((sys)=> {
                setOpenedListState(sys);
            });
            return;
        }

        menuToggle.classList.remove('open-facade-menu-item');
        menuToggle.classList.add('close-facade-menu-item');
        innerSysList.forEach((sys)=> {
            setClosedListState(sys);
        });
    });
});

// Нажатие на кнопку + или -

if (openSystemBtns) {
    openSystemBtns.forEach((openCloseBtn) => {
        openCloseBtn.addEventListener('click', (event)=> {
            // event.preventDefault();
            const targetMenuItem = event.currentTarget;
            const parentBlock = targetMenuItem.closest('.facade-menu-list');
            const facadeItems = parentBlock ? Array.from(parentBlock.querySelectorAll('.subitem')) : [];

            if (!facadeItems.length) {
                return;
            }

            // Открытие списка
            if (targetMenuItem.classList.contains('close-facade-menu-item')) {
                facadeItems.forEach((sysItem, index)=> {
                    animateOpenList(sysItem, 'open', index * LIST_STAGGER_DELAY);
                });
                targetMenuItem.classList.remove('close-facade-menu-item');
                targetMenuItem.classList.add('open-facade-menu-item');
            // Закрытие списка
            } else if (targetMenuItem.classList.contains('open-facade-menu-item')) {
                facadeItems.reverse().forEach((sysItem, index)=> {
                    animateOpenList(sysItem, 'close', index * LIST_STAGGER_DELAY);
                });
                targetMenuItem.classList.remove('open-facade-menu-item');
                targetMenuItem.classList.add('close-facade-menu-item');
            }
        })
    })
}

function clearListAnimation(elem) {
    if (elem.openCloseTimeout) {
        clearTimeout(elem.openCloseTimeout);
        elem.openCloseTimeout = null;
    }

    if (elem.transitionHandler) {
        elem.removeEventListener('transitionend', elem.transitionHandler);
        elem.transitionHandler = null;
    }
}

function setClosedListState(elem) {
    clearListAnimation(elem);
    elem.style.display = 'none';
    elem.style.maxHeight = '0px';
    elem.style.opacity = '0';
    elem.style.transform = 'translateY(-8px)';
    elem.style.overflow = 'hidden';
}

function setOpenedListState(elem) {
    clearListAnimation(elem);
    elem.style.display = 'block';
    elem.style.maxHeight = 'none';
    elem.style.opacity = '1';
    elem.style.transform = 'translateY(0)';
    elem.style.overflow = 'visible';
}

function animateOpenList(elem, param, delay = 0) {
    clearListAnimation(elem);

    elem.openCloseTimeout = setTimeout(() => {
        const isOpenAction = param === 'open';

        elem.style.transition = 'none';
        elem.style.overflow = 'hidden';

        if (isOpenAction) {
            elem.style.display = 'block';
            elem.style.maxHeight = '0px';
            elem.style.opacity = '0';
            elem.style.transform = 'translateY(-8px)';

            requestAnimationFrame(() => {
                const targetHeight = `${elem.scrollHeight}px`;
                elem.style.transition = `max-height ${LIST_ANIMATION_DURATION}ms ease, opacity ${LIST_ANIMATION_DURATION}ms ease, transform ${LIST_ANIMATION_DURATION}ms ease`;
                elem.style.maxHeight = targetHeight;
                elem.style.opacity = '1';
                elem.style.transform = 'translateY(0)';

                elem.transitionHandler = () => {
                    elem.style.maxHeight = 'none';
                    elem.style.overflow = 'visible';
                    elem.removeEventListener('transitionend', elem.transitionHandler);
                    elem.transitionHandler = null;
                };

                elem.addEventListener('transitionend', elem.transitionHandler, { once: true });
            });
        } else {
            if (getComputedStyle(elem).display === 'none') {
                setClosedListState(elem);
                return;
            }

            elem.style.display = 'block';
            elem.style.maxHeight = `${elem.scrollHeight}px`;
            elem.style.opacity = '1';
            elem.style.transform = 'translateY(0)';

            requestAnimationFrame(() => {
                elem.style.transition = `max-height ${LIST_ANIMATION_DURATION}ms ease, opacity ${LIST_ANIMATION_DURATION}ms ease, transform ${LIST_ANIMATION_DURATION}ms ease`;
                elem.style.maxHeight = '0px';
                elem.style.opacity = '0';
                elem.style.transform = 'translateY(-8px)';

                elem.transitionHandler = () => {
                    setClosedListState(elem);
                };

                elem.addEventListener('transitionend', elem.transitionHandler, { once: true });
            });
        }
    }, delay);
}
