/*
[ 첫 방문 안내 팝업 ]
메인 페이지에서 소개 팝업 창을 띄우고, 팝업 안의 버튼 동작을 처리한다.
*/

function showPopup() {
    // 모바일에서는 새 창 팝업이 차단되거나 별도 탭으로 열려 흐름이 끊긴다
    if (window.innerWidth <= 768) return;
    window.open('popup.html', 'popup', 'width=500, height=560, left=470, top=150');
}

function goMenual() {
    if (window.opener && !window.opener.closed) {
        window.opener.location.href = 'introduce.html';
        window.close();
    } else {
        location.href = 'introduce.html';
    }
}

(function () {
    'use strict';
    function onReady() {
        if (document.body.classList.contains('page-home')) showPopup();
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', onReady);
    } else {
        onReady();
    }
})();
