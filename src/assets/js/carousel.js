/*
[ 메인 히어로 캐러셀 ]
외부 라이브러리 없이 동작한다. 슬라이드에 is-active 를 옮겨 붙이는 것이 전부다.
*/

(function () {
    'use strict';

    var INTERVAL = 5000;

    function init() {
        var root = document.getElementById('carousel');
        if (!root) return;

        var slides = root.querySelectorAll('.hero__slide');
        var dots = root.querySelectorAll('.hero__dot');
        if (!slides.length) return;

        var current = 0;
        var timer = null;
        var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        function show(i) {
            current = (i + slides.length) % slides.length;
            for (var n = 0; n < slides.length; n++) {
                slides[n].classList.toggle('is-active', n === current);
            }
            for (var d = 0; d < dots.length; d++) {
                dots[d].classList.toggle('is-active', d === current);
                dots[d].setAttribute('aria-selected', d === current ? 'true' : 'false');
            }
        }

        function start() {
            if (reduced) return;
            stop();
            timer = setInterval(function () { show(current + 1); }, INTERVAL);
        }

        function stop() {
            if (timer) { clearInterval(timer); timer = null; }
        }

        for (var d = 0; d < dots.length; d++) {
            dots[d].addEventListener('click', function () {
                show(parseInt(this.getAttribute('data-index'), 10));
                start();
            });
        }

        // 탭이 보이지 않을 때는 굳이 돌리지 않는다
        document.addEventListener('visibilitychange', function () {
            document.hidden ? stop() : start();
        });
        root.addEventListener('mouseenter', stop);
        root.addEventListener('mouseleave', start);

        show(0);
        start();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
