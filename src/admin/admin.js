import UIkit from './base';

let $error = $('meta[name=error]').attr('content');
let $switcher = $('.uk-switch input');
let $switchInput = $('.switch-input');

if ($error) {
    UIkit.notification({
        message: $error,
        status: 'danger',
        timeout: 1000
    });
}

$('.uk-tab a').on('click', (event) => {
    let $this = $(event.currentTarget)[0];
    window.location.replace($this.href);
});

$switcher.on('click', (event) => {
    let $this = $(event.currentTarget)[0];
    let checked = $this.checked;
    if (checked) {
        $this.setAttribute('value', 'on');
        $switchInput.attr('value', 'on');
    } else {
        $this.setAttribute('value', 'off');
        $switchInput.attr('value', 'off');
    }
});