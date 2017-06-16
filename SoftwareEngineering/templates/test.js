/**
 * Created by duxinlu on 2017/5/31.
 */
function alert_msg() {
    alert('?');
    p = document.getElementById('msg');

    if (p.innerHTML == null || p.innerHTML == '') {
        return;
    } else {
        p.style.color = 'red';
    }

}