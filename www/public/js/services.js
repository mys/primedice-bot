app.factory('socket', function (socketFactory) {
    var mySocket = io.connect();
    
    var socket = socketFactory({
        ioSocket: mySocket
    });

    return socket;
});