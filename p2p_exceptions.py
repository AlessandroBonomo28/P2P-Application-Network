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