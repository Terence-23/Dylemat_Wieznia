var socket = io.connect('https://' + document.domain + ':' + location.port);

socket.on('connect', function () {
    console.log('Connected to server');
});

socket.on('redirect', function (data) {
    var newUrl = data.url;
    window.location.href = newUrl;
});
