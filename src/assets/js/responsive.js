/*
[ 반응형 이미지맵 ]
usemap 의 coords 는 픽셀 고정값이라 이미지가 줄어들면 클릭 영역이 어긋난다.
원본 coords 를 data-coords 에 보관해 두고, 이미지가 실제로 그려진 크기에 맞춰 다시 계산한다.

기준 크기는 img 의 data-map-basew / data-map-baseh 로 지정한다.
(coords 를 작성할 당시 이미지가 그려지던 크기)
*/

(function () {
    'use strict';

    function areasOf(img) {
        var name = (img.getAttribute('usemap') || '').replace('#', '');
        if (!name) return [];
        var map = document.querySelector('map[name="' + name + '"]');
        return map ? map.getElementsByTagName('area') : [];
    }

    function resizeImageMap(img) {
        var baseW = parseFloat(img.getAttribute('data-map-basew')) || img.naturalWidth;
        var baseH = parseFloat(img.getAttribute('data-map-baseh')) || img.naturalHeight;
        var w = img.clientWidth;
        var h = img.clientHeight;
        if (!baseW || !baseH || !w || !h) return;

        var ratioX = w / baseW;
        var ratioY = h / baseH;
        var areas = areasOf(img);

        for (var i = 0; i < areas.length; i++) {
            var area = areas[i];
            if (!area.getAttribute('data-coords')) {
                area.setAttribute('data-coords', area.getAttribute('coords') || '');
            }
            var origin = area.getAttribute('data-coords');
            if (!origin) continue;

            var scaled = origin.trim().split(/[\s,]+/).map(function (v, idx) {
                var n = parseFloat(v);
                if (isNaN(n)) return v;
                return Math.round(n * (idx % 2 === 0 ? ratioX : ratioY));
            });
            area.setAttribute('coords', scaled.join(','));
        }
    }

    function resizeAll() {
        var imgs = document.querySelectorAll('img[usemap]');
        for (var i = 0; i < imgs.length; i++) {
            resizeImageMap(imgs[i]);
        }
    }

    function onReady() {
        resizeAll();
        var imgs = document.querySelectorAll('img[usemap]');
        for (var i = 0; i < imgs.length; i++) {
            if (!imgs[i].complete) {
                imgs[i].addEventListener('load', resizeAll);
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', onReady);
    } else {
        onReady();
    }

    window.addEventListener('load', resizeAll);

    var timer = null;
    window.addEventListener('resize', function () {
        clearTimeout(timer);
        timer = setTimeout(resizeAll, 100);
    });
    window.addEventListener('orientationchange', function () {
        setTimeout(resizeAll, 200);
    });
})();
