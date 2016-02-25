var app = angular.module('malinkaApp',
    ['ngMaterial', 'ngAnimate', 'btford.socket-io', 'md.data.table']);

app.controller('malinkaController', function ($scope, socket) {

    $scope.tail = [];
    $scope.tail1 = [];
    $scope.cpu;

    socket.on('tail', function (data) {
        console.log('tail: ' + data);
        
        if (!data.startsWith('{'))
            return;

		// http://stackoverflow.com/a/8073709/2737684
        $scope.tail.unshift(JSON.parse(data));
        console.log(JSON.parse(data));
        if ($scope.tail.length > 500)
			$scope.tail.pop();
    })

    socket.on('tail1', function (data) {
        console.log('tail1: ' + data);
        
        if (!data.startsWith('{'))
            return;

		// http://stackoverflow.com/a/8073709/2737684
        $scope.tail1.unshift(JSON.parse(data));
        console.log(JSON.parse(data));
        if ($scope.tail1.length > 500)
			$scope.tail1.pop();
    })

    socket.on('cpu', function (data) {
        console.log('cpu: ' + data);

        $scope.cpu = data;
    })
});

app.filter('reverse', function () {
    return function (items) {
        return items.slice().reverse();
    };
});