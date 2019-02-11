// function do_ajax(endpoint, event_handler, request_text='') {
//     var handler_wrapper = function() {
//       if(this.readyState == XMLHttpRequest.DONE && this.status == 200) {
//         $('#badge-in_progress').hide();
//         event_handler.call(this);
//       } else {
//         $('#badge-in_progress').show();
//       }
//     }
//     var req = new XMLHttpRequest();
//     req.onreadystatechange = handler_wrapper;
//     req.open('POST', endpoint, true);
//     req.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
//     req.send(request_text);
// }

function doCmd(cmd, cb, arg, kwargs) {
    data = {'cmd': cmd};
    data['arg'] = arg;
    data['kwargs'] = kwargs;
    $.ajax({url: '/do_cmd',
            method: 'POST',
            data: JSON.stringify(data, null, '\t'),
            success: cb,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
    });
}