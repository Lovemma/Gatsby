import './admin';
import UIkit from './base';

let $switcher = $('.uk-switch input');

$switcher.on('click', (event) => {
    let $this = $(event.currentTarget)[0];
    let $url = $($this).data('url');
    let checked = $this.checked;
    $.ajax({
        url: $url,
        type: checked ? 'DELETE' : 'POST',
        data: {},
        success: function (rs) {
            if (rs.r) {
                UIkit.notification({
                    message: 'Ops!',
                    status: 'danger',
                    timeout: 1000
                });
            }
        }
    });
});
