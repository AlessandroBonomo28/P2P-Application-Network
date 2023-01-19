class HostNotFound(Exception):
    pass
class ConnectionNotFound(Exception):
    pass
class IngoingConnectionException(Exception):
    pass
class OutgoingConnectionException(Exception):
    pass
class SelfConnectNotAllowed(OutgoingConnectionException):
    pass
class FailToConnectToP2PServer(OutgoingConnectionException):
    pass
class TimedOut(Exception):
    pass
class BrokenHost(Exception):
    pass