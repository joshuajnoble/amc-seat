from socketIO_client import SocketIO, LoggingNamespace

with SocketIO('192.168.42.1', 5000, LoggingNamespace) as socketIO:
    dict = {'data':'josh'}
    socketIO.emit('test', dict)
    socketIO.wait(seconds=1)