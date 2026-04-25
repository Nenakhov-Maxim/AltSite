document.addEventListener('DOMContentLoaded', () => {
    const galleryItems = Array.from(document.querySelectorAll('.portfolio-gallery-item'));
    const filters = Array.from(document.querySelectorAll('select.select-filter'));

    if (!galleryItems.length || !filters.length) {
        return;
    }

    const normalizeValue = (value) => (value || '')
        .toString()
        .trim()
        .toLowerCase();

    const splitValues = (value) => normalizeValue(value)
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean);

    const matchesCladding = (item, selectedValue) => {
        if (selectedValue === 'all') {
            return true;
        }

        const claddingSystems = splitValues(item.getAttribute('data-cladding-system'));
        return claddingSystems.includes(normalizeValue(selectedValue));
    };

    const matchesObjectType = (item, selectedValue) => {
        if (selectedValue === 'all') {
            return true;
        }

        return normalizeValue(item.getAttribute('data-object-type')) === normalizeValue(selectedValue);
    };

    const matchesLocation = (item, selectedValue) => {
        if (selectedValue === 'all') {
            return true;
        }

        const normalizedSelectedValue = normalizeValue(selectedValue);
        const region = normalizeValue(item.getAttribute('data-region'));
        const city = normalizeValue(item.getAttribute('data-city'));

        return region === normalizedSelectedValue || city === normalizedSelectedValue;
    };

    const matchesYear = (item, selectedValue) => {
        if (selectedValue === 'all') {
            return true;
        }

        return normalizeValue(item.getAttribute('data-year-comlited')) === normalizeValue(selectedValue);
    };

    const applyFilters = () => {
        const claddingValue = document.getElementById('cladding-system-select')?.value || 'all';
        const objectTypeValue = document.getElementById('object-type-select')?.value || 'all';
        const locationValue = document.getElementById('city-region-select')?.value || 'all';
        const yearValue = document.getElementById('year-comlited-select')?.value || 'all';

        galleryItems.forEach((item) => {
            const isVisible = (
                matchesCladding(item, claddingValue)
                && matchesObjectType(item, objectTypeValue)
                && matchesLocation(item, locationValue)
                && matchesYear(item, yearValue)
            );

            item.classList.toggle('portfolio-gallery-item-hidden', !isVisible);
        });
    };

    filters.forEach((filter) => {
        filter.addEventListener('change', applyFilters);
    });

    applyFilters();
});
