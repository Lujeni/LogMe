var txt = document.getElementById("log-list");

$(function() {
	WEB_SOCKET_SWF_LOCATION = "/static/flashsocket/WebSocketMain.swf";
	var socket = io.connect();

	socket.on('connect',    function()    { socket.emit('get_logs'); feeding(); });
	socket.on('reset',      function()    { reset();                              });
	socket.on('disconnect', function()    { socket = io.connect(); oops();        });

	socket.on('logs', function (json) {
		var data = JSON.parse(json);
		txt.innerHTML = '<div><span class="label label-info">'+data['host']+'</span><div><span class="label label-succes">'+data['logfile']+'</span> '+data['text']+'</div>' + txt.innerHTML;
    });
});
