import json
from enum import Enum

class MessageType(Enum):
    REQUEST = "REQUEST" #hostname
    RESPONSE = "RESPONSE"
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
    ERROR = "ERROR"
    INFO = "INFO"
    WARNING = "WARNING"
    PUBLISH = "PUBLISH"
    FETCH = "FETCH"
    CONNECT = "CONNECT"
    DISCOVER = "DISCOVER"
    PING = "PING"
    SELECT = "SELECT"
    SELECTFROM = "SELECTFROM"
    NOTIFY = "NOTIFY"
    SEND = "SEND"

class StatusCode(Enum):
    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

class Message:
    def __init__(self, type, content, status=StatusCode.OK):
        self.type = type.name
        self.content = content
        self.status = status.value

    def serialize_message(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def deserialize_message(json_str):
        msg_dict = json.loads(json_str)
        msg_type = MessageType[msg_dict['type']]  # Convert the string back into an enum member
        msg_status = StatusCode(msg_dict['status'])  # Convert the integer back into an enum member
        msg = Message(msg_type, msg_dict['content'], msg_status)
        return msg
        # msg_dict = json.loads(json_str)
        # msg = Message(msg_dict['type'], msg_dict['content'], msg_dict['status'])
        # return msg

# Example usage:
# request_message = Message(MessageType.REQUEST, "Request for resource")
# response_message = Message(MessageType.RESPONSE, "Response with resource")
# ack_message = Message(MessageType.ACKNOWLEDGEMENT, "Acknowledgement of request")
# error_message = Message(MessageType.ERROR, "An error occurred")
# info_message = Message(MessageType.INFO, "System is running smoothly")
# warning_message = Message(MessageType.WARNING, "Potential problem detected")
# publish_message = Message(MessageType.PUBLISH, "Publishing file")
# fetch_message = Message(MessageType.FETCH, "Fetching file")

# print(request_message)
# print(response_message)
# print(ack_message)
# print(error_message)
# print(info_message)
# print(warning_message)