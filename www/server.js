/* global __dirname */
var express = require('express');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io')(server);
var fs = require('fs');

var spawn = require('child_process').spawn;
var tailLog = spawn('tail', ['-f', '/home/pi/log.txt']);
var tailLog1 = spawn('tail', ['-f', '/home/pi/log1.txt']);
var dstat = spawn('dstat', ['-c', '--nocolor']);

// ----------------------------------------------------------------------------
// express
// ----------------------------------------------------------------------------

app.use(express.static(__dirname + '/public'));
app.use('/bower_components', express.static(__dirname + '/bower_components'));

app.get('/', function (req, res) {
    res.sendFile(__dirname + '/index.html');
})

// ----------------------------------------------------------------------------
// socket.io
// ----------------------------------------------------------------------------

io.on('connection', function (socket) {
    console.log('user connected');

    socket.send({ filename: '/home/pi/log.txt' })

    // log.txt
    var logHandler = function (data) {
        socket.emit('tail', data.toString('utf-8'));
    };
    tailLog.stdout.on('data', logHandler);
	
	// log1.txt
    var logHandler1 = function (data) {
        socket.emit('tail1', data.toString('utf-8'));
    };
    tailLog1.stdout.on('data', logHandler1);

    // cpu
    var dstatHandler = function (data) {
        //console.log(data.toString('utf-8'));
        var txt = new Buffer(data).toString('utf-8', 0, data.Length);
        var cpu = (100 - parseInt(txt.split('  ')[3]));
        socket.emit('cpu', cpu);
    }
    dstat.stdout.on('data', dstatHandler);

    // disconnect
    socket.on('disconnect', function () {
        console.log('user disconnected');
        tailLog.stdout.removeListener('data', logHandler);
        tailLog1.stdout.removeListener('data', logHandler1);
        dstat.stdout.removeListener('data', dstatHandler);
    });
})


// ----------------------------------------------------------------------------
// listen:80
// ----------------------------------------------------------------------------


server.listen(80, function () {
    console.log('Server running at localhost:80');
});
