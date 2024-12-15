
__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Dict, List, Optional, Tuple, Union

import os
import time

from base64 import b64encode
from datetime import datetime, timedelta
from http import HTTPStatus
from pprint import pformat

from requests import session, Response, Session, ConnectionError, ConnectTimeout

from mojo.errors.raising import raise_for_http_status

from mojo.credentials.basecredential import BaseCredential
from mojo.credentials.basiccredential import BasicCredential

from mojo.interop.protocols.rest.restaspects import RestAspects, DEFAULT_REST_ASPECTS

from mojo.xmods.aspects import ActionPattern
from mojo.xmods.xformatting import indent_lines_list


class RestClientBase:
    """
        The :class:`RestClientBase` object is a generic REST client base object that can be inherited from
        in order to implement a REST client that utilizes 'aspects' based APIs
    """

    AUTH_LEAF = ""
    VERIFY_CERTIFICATE = False

    def __init__(self, host: str, credential: BaseCredential, port: Optional[int] = None, scheme: Optional[str] = "https", aspects: RestAspects = DEFAULT_REST_ASPECTS):
        self._host = host
        self._port = port
        self._scheme = scheme
        self._credential = credential
        self._aspects = aspects

        self._host_url = f"{scheme}://{self._host}"
        if port is not None:
            self._host_url = f"{self._host_url}:{port}"

        self._session: Session = None
        return
    
    @property
    def credential(self):
        return self._credential

    @property
    def host(self):
        return self._host
    

    def authenticate(self):
        """
            The `authenticate` method can be overloaded in order to modify the method of authentication
            for the rest client.  The current method of authentication is `Basic` authentication.
        """

        credential: BasicCredential

        username = credential.username
        password = credential.password

        passwd_encoded =  b64encode(password).decode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {username}:{passwd_encoded}"
        }

        auth_leaf = self.AUTH_LEAF.rstrip("/")
        auth_url = f"{self._host_url}/{auth_leaf}"

        session = session()

        resp = session.post(auth_url, headers=headers, verify=self.VERIFY_CERTIFICATE)
        status_code = resp.status_code 
        if status_code != HTTPStatus.OK:
            context = f"Error attempting to authenticate on method=post url={auth_url}."    
            raise_for_http_status(status_code, resp.content, url=auth_url, context=context)

        return

    def format_call_url(self, leaf: str):

        leaf = leaf.rstrip("/")

        call_url = f"{self._host_url}/{leaf}"
        
        return call_url


    def perform_call(self, *, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: Union[int, List[int], Tuple[int]],
                     aspects: Union[RestAspects, None]) -> Response:
        
        if aspects is None:
            aspects = self._aspects

        if isinstance(exp_status, int):
            exp_status = [exp_status]

        response = None

        action_pattern = aspects.action_pattern

        if action_pattern == ActionPattern.SINGLE_CALL:
            response = self._perform_single_call(leaf, method, params, body, exp_status, aspects)
        elif action_pattern == ActionPattern.SINGLE_CONNECTED_CALL:
            response = self._perform_single_connected_call(leaf, method, params, body, exp_status, aspects)
        elif action_pattern == ActionPattern.DO_UNTIL_CONNECTION_FAILURE:
            response = self._perform_call_until_connection_failure(leaf, method, params, body, exp_status, aspects)
        elif action_pattern == ActionPattern.DO_UNTIL_SUCCESS:
            response = self._perform_call_until_success(leaf, method, params, body, exp_status, aspects)
        elif action_pattern == ActionPattern.DO_WHILE_SUCCESS:
            response = self._perform_call_while_success(leaf, method, params, body, exp_status, aspects)
        else:
            errmsg = f"Unsupported action pattern '{action_pattern}'"
            raise RuntimeError(errmsg)

        return response
    

    def _get_session(self, aspects: RestAspects) -> Session:

        session = None

        if aspects.session is not None:
            session = aspects.session
        else:
            if self._session is None:
                self.authenticate()

            session = self._session

        return session


    def _perform_single_call(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: List[int],
                     aspects: RestAspects) -> Response:
        """
            The `_perform_single_call` implements the 'ActionPattern.SINGLE_CALL' action pattern.  This action pattern makes a single
            call to the remote REST API and will raise an exception if the expected response is not 
        """

        logger = aspects.logger

        call_url = self.format_call_url(leaf)

        session: Session = self._get_session()
        resp = session.request(method, call_url, params, body)
        if resp.status_code not in exp_status:
            self._raise_for_status(call_url, method, params, body, exp_status, aspects, resp)

        return resp


    def _perform_single_connected_call(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: List[int],
                     aspects: RestAspects) -> Response:
        """
            The `_perform_single_connected_call` implements the 'ActionPattern.SINGLE_CONNECTED_CALL' action pattern.  This action pattern
            will continue to make attempts to connect with a remote services at a specified interval rate until it successfully makes a connection.
            Once it successfully makes a connection, it will attempt to complet a rest call on the connection.  If the REST call fails, it will not
            re-attempt the call.  It is only persistent in making a connection but not in making a successfull call. 
        """
        
        connection_timeout = aspects.connection_timeout
        connection_interval = aspects.connection_timeout

        logger = aspects.logger

        call_url = self.format_call_url(leaf)
        session: Session = self._get_session()
        resp: Response = None

        now_time = datetime.now()
        start_time = now_time
        conn_end_time = start_time + timedelta(seconds=connection_timeout)

        while True:

            try:
                # We always want to make at least one call
                resp = session.request(method, call_url, params, body, timeout=connection_timeout)

                # If we connected successfully and were able to make the call, do not re-attempt, just break
                break

            except (ConnectTimeout, ConnectionError) as conn_err:

                # If we catch a connection error and we have not been able to connect in time, raise a timeout
                # error
                now_time = datetime.now()
                if now_time > conn_end_time:
                    err_msg_lines = [
                        f"Timeout attempting to connect on url={call_url}",
                        f"    start={start_time} end={conn_end_time} timeout={connection_timeout}"
                    ]
                    err_msg = os.linesep.join(err_msg_lines)
                    raise TimeoutError(err_msg)
                
            # For any exception that is not a ConnectionError or ConnectTimeout, just log and re-raise the exception.
            except Exception as xcpt:
                xcpt_type = type(xcpt).__name__
                err_msg_lines = [
                    f"An {xcpt_type} exception occured calling url={call_url}."
                ]
                err_msg = os.linesep.join(err_msg_lines)
                
                logger.exception(err_msg)
            
            time.sleep(connection_interval)

        # If we get here without an exception being raised, process the response
        if resp.status_code not in exp_status:
            self._raise_for_status(call_url, method, params, body, exp_status, aspects, resp)

        return resp
    
    
    def _perform_call_until_connection_failure(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: List[int],
                     aspects: RestAspects) -> Response:
        """
            Perform a specific API call until a connection error occurs.
        """


        connection_timeout = aspects.connection_timeout
        
        completion_timeout = aspects.completion_timeout
        completion_interval = aspects.completion_interval

        logger = aspects.logger

        call_url = self.format_call_url(leaf)
        session: Session = self._get_session()
        resp: Response = None

        now_time = datetime.now()
        start_time = now_time
        
        comp_end_time = start_time + timedelta(seconds=completion_timeout)
        
        while True:

            try:
                resp = session.request(method, call_url, params, body, timeout=connection_timeout)
            except Exception as xcpt:
                break

            now_time = time.time()
            if now_time > comp_end_time:
                err_msg_lines = [
                    f"Timeout waiting for a connection failure on url={call_url}",
                    f"    start={start_time} end={comp_end_time} timeout={completion_timeout}"
                ]
                err_msg = os.linesep.join(err_msg_lines)
                raise TimeoutError(err_msg)
            
            time.sleep(completion_interval)

        # We don't need to verify the response, this action pattern only waits for a connection failure to occur within
        # a specified completion time

        return resp
    

    def _perform_call_until_success(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: List[int],
                     aspects: RestAspects) -> Response:
        
        connection_timeout = aspects.connection_timeout
        
        completion_timeout = aspects.completion_timeout
        completion_interval = aspects.completion_interval

        logger = aspects.logger

        call_url = self.format_call_url(leaf)
        session: Session = self._get_session()
        resp: Response = None

        now_time = datetime.now()
        start_time = now_time
        
        comp_end_time = start_time + timedelta(seconds=completion_timeout)

        while True:
            resp = None

            try:
                resp = session.request(method, call_url, params, body, timeout=connection_timeout)
            except:
                pass

            if resp is not None:
                pass

            # If we catch a connection error and we have not been able to connect in time, raise a timeout
            # error
            now_time = datetime.now()
            if now_time > comp_end_time:
                err_msg_lines = [
                    f"Timeout attempting to connect on url={call_url}",
                    f"    start={start_time} end={comp_end_time} timeout={connection_timeout}"
                ]
                err_msg = os.linesep.join(err_msg_lines)
                raise TimeoutError(err_msg)

        return
    

    def _perform_call_while_success(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: List[int],
                     aspects: RestAspects) -> Response:
        
        return
    

    def _raise_for_status(self, call_url: str, method: str, params: Union[Dict[str, str]], body: Union[Dict[str, str], None],
                          exp_status: List[int], aspects: RestAspects, resp: Response, call_context: str):
        context_msg_lines = [
            call_context,
            f"CALL: method={method} url={call_url}",
            f"RESPONSE CODE: exp={exp_status} found={status_code}",
        ]

        if params is not None and len(params) > 0:
            context_msg_lines.append("PARAMS:")
            params_lines = pformat(params, indent=4, sort_dicts=True)
            params_lines = indent_lines_list(params_lines, 1, indent=4)
            context_msg_lines.extend(params_lines)
        
        if body is not None and len(body) > 0:
            context_msg_lines.append("BODY:")
            body_lines = pformat(body, indent=4, sort_dicts=True)
            body_lines = indent_lines_list(body_lines, 1, indent=4)
            context_msg_lines.extend(body_lines)

        context_msg = os.linesep.join(context_msg_lines)

        status_code = resp.status_code
        content = resp.content

        raise_for_http_status(status_code, content, url=call_url, context=context_msg)

        return