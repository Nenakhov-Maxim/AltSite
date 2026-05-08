const RF_MAP_NAME = 'russia_subjects_custom';
const RF_MAP_COLORS = {
    base: '#dbe7ef',
    active: '#fe855b',
    current: '#1d4567',
    stroke: '#ffffff',
    hover: '#ff9a76'
};
const RF_MAP_OVERLAY_LAYERS = [
    {
        codes: ['BEL-BEL', 'MOL-MOL', 'ARM-ARM'],
        transform: 'matrix(1.1808 -0.1281 0.1935 1.1264 -99.4653 59.5897)'
    },
    {
        codes: ['KZH-KAZ', 'YZK-YZB', 'KRS-KYR', 'TYD-TYD'],
        transform: 'matrix(1.1808 0.0041 0.1538 1.0308 -89.1134 60.4977)'
    }
];
const RF_MAP_CONFIG = {
    regionLinks: {},
    cityMarkers: [],
    titlesByCode: {}
};

function getRfMapRoot() {
    return document.querySelector('.rf-map');
}

function loadRfMapConfig() {
    const configNode = document.getElementById('rf-map-config');
    if (!configNode) {
        return;
    }

    try {
        const config = JSON.parse(configNode.textContent);
        RF_MAP_CONFIG.regionLinks = config.regionLinks || {};
        RF_MAP_CONFIG.cityMarkers = config.cityMarkers || [];
        RF_MAP_CONFIG.titlesByCode = config.titlesByCode || {};
    } catch (error) {
        RF_MAP_CONFIG.regionLinks = {};
        RF_MAP_CONFIG.cityMarkers = [];
        RF_MAP_CONFIG.titlesByCode = {};
    }
}

function getLinkedCodes(code) {
    if (!code) {
        return new Set();
    }

    const linkedCodes = new Set(RF_MAP_CONFIG.regionLinks[code] || []);

    Object.entries(RF_MAP_CONFIG.regionLinks).forEach(([sourceCode, pairCodes]) => {
        if (pairCodes.includes(code)) {
            linkedCodes.add(sourceCode);
        }
    });

    return linkedCodes;
}

function getHighlightedCodes(code) {
    const highlightedCodes = getLinkedCodes(code);

    if (code) {
        highlightedCodes.add(code);
    }

    return highlightedCodes;
}

function getActiveCodes(root) {
    return new Set(
        Array.from(root.querySelectorAll('.district-text[id]'))
            .filter((district) => district.textContent.trim())
            .map((district) => district.id)
    );
}

function getDistrictTitle(root, titleByCode, code) {
    const region = root.querySelector(`[data-code="${code}"]`);
    return RF_MAP_CONFIG.titlesByCode[code] || region?.getAttribute('data-title') || titleByCode.get(code) || code;
}

function getDistrictBlock(root, code) {
    return root.querySelector(`.district-text[id="${code}"]`);
}

function hideDistrictPanel(root) {
    const district = root.querySelector('.district');
    if (!district) {
        return;
    }

    district.style.display = 'none';
}

function showDistrictPanel(root, title) {
    const district = root.querySelector('.district');
    const titleNode = district?.querySelector('span');

    if (!district || !titleNode) {
        return;
    }

    titleNode.textContent = title;
    district.style.display = 'block';
}

function hideAllDistrictTexts(root) {
    root.querySelectorAll('.district-text').forEach((district) => {
        district.style.display = 'none';
    });
}

function buildDistrictLinks(root, titleByCode, activeCodes) {
    const links = root.querySelector('.district-links');
    if (!links) {
        return;
    }

    links.innerHTML = '';

    Array.from(activeCodes)
        .sort((left, right) => getDistrictTitle(root, titleByCode, left).localeCompare(getDistrictTitle(root, titleByCode, right), 'ru'))
        .forEach((code) => {
            const link = document.createElement('div');
            link.dataset.code = code;
            link.dataset.title = getDistrictTitle(root, titleByCode, code);
            link.textContent = link.dataset.title;
            links.appendChild(link);
        });
}

function applyLegacyRegionState(root, activeCodes, currentCode, hoverCode = null) {
    const highlightedCodes = getHighlightedCodes(currentCode || hoverCode);

    root.querySelectorAll('[data-code]').forEach((region) => {
        const code = region.getAttribute('data-code');
        region.classList.toggle('region-active', highlightedCodes.has(code) && code !== currentCode);
        region.classList.toggle('region-current', code === currentCode);
    });
}

function applyVectorRegionState(mapInstance, activeCodes, currentCode, hoverCode = null) {
    const highlightedCodes = getHighlightedCodes(currentCode || hoverCode);

    Object.entries(mapInstance.regions).forEach(([code, region]) => {
        const fill = code === currentCode
            ? RF_MAP_COLORS.current
            : highlightedCodes.has(code)
                ? RF_MAP_COLORS.hover
                : RF_MAP_COLORS.base;

        region.element.setStyle({
            fill,
            stroke: RF_MAP_COLORS.stroke,
            strokeWidth: 1.2,
            strokeOpacity: 1
        });

        const node = region.element.shape.node;
        node.classList.toggle('region-active', highlightedCodes.has(code) && code !== currentCode);
        node.classList.toggle('region-current', code === currentCode);
    });
}

function applyOverlayRegionState(root, activeCodes, currentCode, hoverCode = null) {
    const highlightedCodes = getHighlightedCodes(currentCode || hoverCode);

    root.querySelectorAll('.rf-map__overlay [data-code]').forEach((region) => {
        const code = region.getAttribute('data-code');
        region.classList.toggle('region-active', highlightedCodes.has(code) && code !== currentCode);
        region.classList.toggle('region-current', code === currentCode);
    });
}

function applyVectorMapState(root, mapInstance, activeCodes, currentCode, hoverCode = null) {
    applyVectorRegionState(mapInstance, activeCodes, currentCode, hoverCode);
    applyOverlayRegionState(root, activeCodes, currentCode, hoverCode);
}

function closeDistrict(root, activeCodes, mapInstance) {
    root.classList.remove('open');
    hideAllDistrictTexts(root);
    hideDistrictPanel(root);

    if (mapInstance) {
        applyVectorMapState(root, mapInstance, activeCodes, null);
        return;
    }

    applyLegacyRegionState(root, activeCodes, null);
}

function openDistrict(root, titleByCode, activeCodes, code, mapInstance) {
    const district = getDistrictBlock(root, code);

    if (!district || !district.textContent.trim()) {
        return false;
    }

    root.classList.add('open');
    hideAllDistrictTexts(root);
    district.style.display = 'block';
    showDistrictPanel(root, getDistrictTitle(root, titleByCode, code));

    if (mapInstance) {
        applyVectorMapState(root, mapInstance, activeCodes, code);
    } else {
        applyLegacyRegionState(root, activeCodes, code);
    }

    return true;
}

function bindDistrictInteractions(root, titleByCode, activeCodes, mapInstance) {
    const $root = $(root);
    $root.off('.rfMap');

    $root.on('mouseenter.rfMap', '[data-code]', function() {
        if (root.classList.contains('open')) {
            return;
        }

        const code = this.getAttribute('data-code');

        if (mapInstance) {
            applyVectorMapState(root, mapInstance, activeCodes, null, code);
        } else {
            applyLegacyRegionState(root, activeCodes, null, code);
        }

        showDistrictPanel(root, getDistrictTitle(root, titleByCode, this.getAttribute('data-code')));
    });

    $root.on('mouseleave.rfMap', '[data-code]', function() {
        if (!root.classList.contains('open')) {
            if (mapInstance) {
                applyVectorMapState(root, mapInstance, activeCodes, null);
            } else {
                applyLegacyRegionState(root, activeCodes, null);
            }

            hideDistrictPanel(root);
        }
    });

    $root.on('click.rfMap', '[data-code], .district-links div', function(event) {
        const code = this.getAttribute('data-code');
        if (!code) {
            return;
        }

        const opened = openDistrict(root, titleByCode, activeCodes, code, mapInstance);
        if (!opened && !root.classList.contains('open')) {
            hideDistrictPanel(root);
        }

        event.preventDefault();
    });

    const closeButton = root.querySelector('.close-district');
    if (closeButton) {
        closeButton.addEventListener('click', () => closeDistrict(root, activeCodes, mapInstance));
    }
}

function initLegacyMap(root, activeCodes) {
    const titleByCode = new Map();

    root.querySelectorAll('[data-code][data-title]').forEach((region) => {
        const code = region.getAttribute('data-code');
        if (!titleByCode.has(code)) {
            titleByCode.set(code, region.getAttribute('data-title'));
        }
    });

    applyLegacyRegionState(root, activeCodes, null);
    buildDistrictLinks(root, titleByCode, activeCodes);
    bindDistrictInteractions(root, titleByCode, activeCodes, null);
    bindCityMarkers(root, null);
    bindCoordinatePicker(root, null);
}

function createVectorContainer(root) {
    const existingCanvas = root.querySelector('.rf-map__canvas');
    if (existingCanvas) {
        return existingCanvas;
    }

    const canvas = document.createElement('div');
    canvas.className = 'rf-map__canvas';

    const links = root.querySelector('.district-links');
    if (links) {
        root.insertBefore(canvas, links);
    } else {
        root.appendChild(canvas);
    }

    return canvas;
}

function createOverlayElement(tagName) {
    return document.createElementNS('http://www.w3.org/2000/svg', tagName);
}

function getVectorRegionLayer(mapInstance) {
    const firstRegion = Object.values(mapInstance?.regions || {})[0];
    const regionNode = firstRegion?.element?.shape?.node;

    return regionNode?.parentNode || null;
}

function createVectorOverlay(root, mapInstance, sourceSvg) {
    const regionLayer = getVectorRegionLayer(mapInstance);
    if (!sourceSvg || !regionLayer || regionLayer.querySelector('.rf-map__overlay')) {
        return;
    }

    root.querySelectorAll('.rf-map__canvas > .rf-map__overlay').forEach((legacyOverlay) => {
        legacyOverlay.remove();
    });

    const overlay = createOverlayElement('g');
    overlay.classList.add('rf-map__overlay');
    overlay.setAttribute('aria-hidden', 'true');

    RF_MAP_OVERLAY_LAYERS.forEach((layer, index) => {
        const group = createOverlayElement('g');
        group.classList.add('rf-map__overlay-group');
        group.dataset.layer = String(index + 1);
        group.setAttribute('transform', layer.transform);

        layer.codes.forEach((code) => {
            const sourceNode = sourceSvg.querySelector(`[data-code="${code}"]`);
            if (!sourceNode) {
                return;
            }

            const clone = sourceNode.cloneNode(true);
            clone.removeAttribute('class');
            clone.removeAttribute('style');
            group.appendChild(clone);
        });

        if (group.childNodes.length) {
            overlay.appendChild(group);
        }
    });

    if (overlay.childNodes.length) {
        regionLayer.appendChild(overlay);
    }
}

function getRegionNode(root, mapInstance, code) {
    if (mapInstance?.regions?.[code]) {
        return mapInstance.regions[code].element.shape.node;
    }

    return root.querySelector(`.rf-map__overlay [data-code="${code}"], svg [data-code="${code}"]`);
}

function getMapSvg(root, mapInstance) {
    if (mapInstance) {
        return root.querySelector('.rf-map__canvas svg');
    }

    return root.querySelector('svg');
}

function getCityLayerParent(root, mapInstance) {
    if (mapInstance) {
        return getVectorRegionLayer(mapInstance) || getMapSvg(root, mapInstance);
    }

    return getMapSvg(root, mapInstance);
}

function createSvgPoint(svg, x, y) {
    const point = svg.createSVGPoint();
    point.x = x;
    point.y = y;

    return point;
}

function getSvgPoint(svg, node, targetNode, x, y) {
    const nodeMatrix = node.getCTM();
    const targetMatrix = targetNode.getCTM();
    if (!nodeMatrix || !targetMatrix) {
        return null;
    }

    return createSvgPoint(svg, x, y)
        .matrixTransform(nodeMatrix)
        .matrixTransform(targetMatrix.inverse());
}

function getRegionCenterPoint(svg, regionNode, cityLayerParent) {
    if (!regionNode.getBBox) {
        return null;
    }

    const regionBox = regionNode.getBBox();
    if (!regionBox.width && !regionBox.height) {
        return null;
    }

    return getSvgPoint(
        svg,
        regionNode,
        cityLayerParent,
        regionBox.x + (regionBox.width / 2),
        regionBox.y + (regionBox.height / 2)
    );
}

function createCityLayer(root, mapInstance) {
    const cityLayerParent = getCityLayerParent(root, mapInstance);
    if (!cityLayerParent) {
        return null;
    }

    let cityLayer = Array.from(cityLayerParent.children)
        .find((child) => child.classList.contains('rf-map__cities'));

    if (!cityLayer) {
        cityLayer = createOverlayElement('g');
        cityLayer.classList.add('rf-map__cities');
        cityLayerParent.appendChild(cityLayer);
    }

    root.querySelectorAll('.rf-map__canvas > .rf-map__cities, .rf-map > .rf-map__cities').forEach((legacyLayer) => {
        legacyLayer.remove();
    });

    return cityLayer;
}

function getCityMarkerPoints(root, mapInstance) {
    if (root._rfMapCityMarkerPoints) {
        return root._rfMapCityMarkerPoints;
    }

    const svg = getMapSvg(root, mapInstance);
    const cityLayerParent = getCityLayerParent(root, mapInstance);
    if (!svg || !cityLayerParent) {
        return [];
    }

    root._rfMapCityMarkerPoints = RF_MAP_CONFIG.cityMarkers.reduce((points, cityMarker) => {
        const cityX = Number(cityMarker.x);
        const cityY = Number(cityMarker.y);

        if (Number.isFinite(cityX) && Number.isFinite(cityY)) {
            points.push({
                x: cityX,
                y: cityY,
                label: cityMarker.label
            });

            return points;
        }

        const regionNode = getRegionNode(root, mapInstance, cityMarker.code);
        if (!regionNode) {
            return points;
        }

        const regionCenter = getRegionCenterPoint(svg, regionNode, cityLayerParent);
        if (!regionCenter) {
            return points;
        }

        points.push({
            x: regionCenter.x + (cityMarker.offsetX || 0),
            y: regionCenter.y + (cityMarker.offsetY || 0),
            label: cityMarker.label
        });

        return points;
    }, []);

    return root._rfMapCityMarkerPoints;
}

function renderCityMarkers(root, mapInstance) {
    const cityLayer = createCityLayer(root, mapInstance);
    if (!cityLayer) {
        return;
    }

    cityLayer.innerHTML = '';

    getCityMarkerPoints(root, mapInstance).forEach((cityMarker) => {
        const cityItem = createOverlayElement('g');
        const cityDot = createOverlayElement('circle');
        const cityLabel = createOverlayElement('text');

        cityItem.classList.add('rf-map__city-marker');
        cityItem.setAttribute('transform', `translate(${cityMarker.x} ${cityMarker.y})`);

        cityDot.classList.add('rf-map__city-marker-dot');
        cityDot.setAttribute('r', '2.5');
        cityDot.setAttribute('cx', '0');
        cityDot.setAttribute('cy', '0');

        cityLabel.classList.add('rf-map__city-marker-label');
        cityLabel.setAttribute('x', '6');
        cityLabel.setAttribute('y', '-4');
        cityLabel.textContent = cityMarker.label;

        cityItem.appendChild(cityDot);
        cityItem.appendChild(cityLabel);
        cityLayer.appendChild(cityItem);
    });
}

function bindCityMarkers(root, mapInstance) {
    const renderMarkers = () => renderCityMarkers(root, mapInstance);

    window.requestAnimationFrame(renderMarkers);

    if (root._rfMapResizeHandler) {
        window.removeEventListener('resize', root._rfMapResizeHandler);
    }

    if (root._rfMapResizeObserver) {
        root._rfMapResizeObserver.disconnect();
    }

    root._rfMapResizeHandler = () => {
        window.requestAnimationFrame(renderMarkers);
    };

    window.addEventListener('resize', root._rfMapResizeHandler);
}

function bindVectorMapResize(root, canvas, mapInstance) {
    let resizeFrame = null;

    const resizeMap = () => {
        if (resizeFrame) {
            window.cancelAnimationFrame(resizeFrame);
        }

        resizeFrame = window.requestAnimationFrame(() => {
            resizeFrame = null;

            if (typeof mapInstance.updateSize === 'function') {
                mapInstance.updateSize();
            }

            root._rfMapCityMarkerPoints = null;
            renderCityMarkers(root, mapInstance);
        });
    };

    if (root._rfMapMapResizeHandler) {
        window.removeEventListener('resize', root._rfMapMapResizeHandler);
    }

    if (root._rfMapMapResizeObserver) {
        root._rfMapMapResizeObserver.disconnect();
    }

    root._rfMapMapResizeHandler = resizeMap;
    window.addEventListener('resize', root._rfMapMapResizeHandler);

    if (typeof ResizeObserver !== 'undefined') {
        root._rfMapMapResizeObserver = new ResizeObserver(resizeMap);
        root._rfMapMapResizeObserver.observe(canvas);
    }

    resizeMap();
}

function bindCoordinatePicker(root, mapInstance) {
    const params = new URLSearchParams(window.location.search);
    if (!params.has('rfMapCoords')) {
        return;
    }

    const svg = getMapSvg(root, mapInstance);
    const cityLayerParent = getCityLayerParent(root, mapInstance);
    if (!svg || !cityLayerParent) {
        return;
    }

    svg.addEventListener('click', (event) => {
        const matrix = cityLayerParent.getScreenCTM();
        if (!matrix) {
            return;
        }

        const svgPoint = createSvgPoint(svg, event.clientX, event.clientY)
            .matrixTransform(matrix.inverse());
        const x = Number(svgPoint.x.toFixed(2));
        const y = Number(svgPoint.y.toFixed(2));

        console.info(`rfMap city coordinates: x=${x}, y=${y}`, { x, y });
    });
}

function initVectorMap(root, activeCodes) {
    if (typeof jsVectorMap === 'undefined' || !window.rfRussiaMapDefinitionLoaded) {
        return false;
    }

    const canvas = createVectorContainer(root);
    let mapInstance;

    try {
        mapInstance = new jsVectorMap({
            selector: canvas,
            map: RF_MAP_NAME,
            showTooltip: false,
            zoomButtons: false,
            zoomOnScroll: false,
            regionStyle: {
                initial: {
                    fill: RF_MAP_COLORS.base,
                    stroke: RF_MAP_COLORS.stroke,
                    strokeWidth: 1.2,
                    fillOpacity: 1
                },
                hover: {
                    fill: RF_MAP_COLORS.hover,
                    cursor: 'pointer'
                },
                selected: {
                    fill: RF_MAP_COLORS.current
                },
                selectedHover: {
                    fill: RF_MAP_COLORS.current
                }
            }
        });
    } catch (error) {
        canvas.remove();
        return false;
    }

    const legacySvg = root.querySelector('svg');
    createVectorOverlay(root, mapInstance, legacySvg);

    if (legacySvg) {
        legacySvg.style.display = 'none';
    }

    const titleByCode = new Map(
        Object.entries(mapInstance._mapData.paths).map(([code, config]) => [code, config.name || code])
    );

    Object.entries(mapInstance.regions).forEach(([code, region]) => {
        const node = region.element.shape.node;
        node.dataset.title = titleByCode.get(code) || code;
    });

    applyVectorMapState(root, mapInstance, activeCodes, null);
    buildDistrictLinks(root, titleByCode, activeCodes);
    bindDistrictInteractions(root, titleByCode, activeCodes, mapInstance);
    bindVectorMapResize(root, canvas, mapInstance);
    bindCityMarkers(root, mapInstance);
    bindCoordinatePicker(root, mapInstance);

    return true;
}

document.addEventListener('DOMContentLoaded', () => {
    loadRfMapConfig();

    const root = getRfMapRoot();
    if (!root) {
        return;
    }

    const activeCodes = getActiveCodes(root);
    if (!initVectorMap(root, activeCodes)) {
        initLegacyMap(root, activeCodes);
    }
});
