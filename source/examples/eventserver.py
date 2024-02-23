
import json
import logging
import traceback
import weakref

from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus


class ServiceClass:

    logger = logging.getLogger()


class Session:

    def post_event(self, event):
        print("Event posted.")
        return

class EventNotificationHandler(BaseHTTPRequestHandler):

    def __init__(self, service_class, session, *args, **kwargs):
        self._service_class = service_class
        self._tasker_session_ref = weakref.ref(session)
        self._logger = self._service_class.logger
        super().__init__(*args, **kwargs)
        return
    
    @property
    def tasker_session(self) -> "TaskerSession":
        return self._tasker_session_ref()

    def do_POST(self):

        if "Content-Type" in self.headers:
            content_type = self.headers["Content-Type"].lower()
            if content_type == "application/json":

                file_length = int(self.headers['Content-Length'])
        
                content = self.rfile.read(file_length)

                try:
                    event = json.loads(content)
                    self.tasker_session.post_event(event)

                    self.send_response(HTTPStatus.ACCEPTED, 'Accepted')
                    self.end_headers()
                except Exception as xcpt:
                    errdetail = traceback.format_exc()
                    self._logger.error(errdetail)
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR, errdetail)
                    self.end_headers()
        return


def event_server():

    session = Session()

    handler_type = partial(EventNotificationHandler, ServiceClass, session)

    localhost =  "127.0.0.1"

    server = HTTPServer((localhost, 0), handler_type)
    server_port = server.server_port

    events_server = server
    events_endpoint = (localhost, server_port)
    
    print(f"Endpoints: {events_endpoint}")

    # After we setup the HTTP server and capture the server endpoint information,
    # set the startgate to allow the thread starting the server to proceed

    server.serve_forever()

if __name__ == "__main__":
    event_server()