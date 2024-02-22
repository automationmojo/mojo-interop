

class TaskingEvent:
    """
        A :class:`TaskingEvent` object used to report events.
    """

    def __init__(self, tasking_id: str, event_name: str, payload: dict):
        self._tasking_id = tasking_id
        self._event_name = event_name
        self._payload = payload
        return
    
    @property
    def event_name(self) -> str:
        return self._event_name
    
    @property
    def payload(self) -> dict:
        return self._payload

    @property
    def tasking_id(self) -> str:
        return self._tasking_id
        
    @classmethod
    def from_dict(self, data: dict):
        self._tasking_id = data["tasking-id"]
        self._event_name = data["event-name"]
        self._payload = data["payload"]
        return

    def as_dict(self) -> dict:

        rtnval = {
            "event-name": self._event_name,
            "payload": self._payload,
            "tasking-id": self._tasking_id
        }

        return rtnval
    
