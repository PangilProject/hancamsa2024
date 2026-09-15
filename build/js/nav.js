/*
[ 상단 네비게이션 ]
사진 히어로 위에서는 투명하게 두고, 스크롤해서 히어로를 벗어나면 흰 배경으로 바꾼다.
*/

(function () {
    'use strict';

    function init() {
        var nav = document.querySelector('.nav');
        if (!nav) return;

        var threshold = 60;
        var ticking = false;

        function update() {
            nav.classList.toggle('is-solid', window.scrollY > threshold);
            ticking = false;
        }

        window.addEventListener('scroll', function () {
            if (ticking) return;
            ticking = true;
            window.requestAnimationFrame(update);
        }, { passive: true });

        update();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
