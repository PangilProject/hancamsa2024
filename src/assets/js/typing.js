/*
[ 타이핑 효과 ]
.typing-txt 의 문구를 .typing 안에 한 글자씩 찍는다. (제이쿼리 없이)
*/

(function () {
    'use strict';

    function init() {
        var source = document.querySelector('.typing-txt');
        var target = document.querySelector('.typing');
        if (!source || !target) return;

        // 모션을 줄이도록 설정했다면 한 번에 보여준다
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            target.textContent += source.textContent;
            return;
        }

        var chars = Array.from(source.textContent);
        var i = 0;
        var tick = setInterval(function () {
            if (i >= chars.length) { clearInterval(tick); return; }
            target.textContent += chars[i++];
        }, 100);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
