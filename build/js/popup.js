function showPopup() {
    // 모바일에서는 새 창 팝업이 탭으로 열리거나 차단되므로 띄우지 않는다
    if (window.innerWidth <= 768) {
        return;
    }
    open("popup.html", "popup", "width=500, height=560, left=470, top=150");
}

function goMenual() {

    if (window.opener && !window.opener.closed) {
        window.opener.location.href = 'introduce.html';
        window.close();
    } else {
        location.href = 'introduce.html';
    }

}
