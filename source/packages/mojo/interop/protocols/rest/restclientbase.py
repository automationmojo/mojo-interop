
__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Dict, List, Optional, Union

import os

from base64 import b64encode
from http import HTTPStatus

import requests

from mojo.errors.exceptions import HttpForbiddenError

from mojo.credentials.basecredential import BaseCredential
from mojo.credentials.basiccredential import BasicCredential

from mojo.interop.protocols.rest.restaspects import RestAspects, DEFAULT_REST_ASPECTS

from mojo.xmods.aspects import ActionPattern


class RestClientBase:
    """
        The :class:`RestClientBase` object is a generic REST client base object that can be inherited from
        in order to implement a REST client that utilizes 'aspects' based APIs
    """

    AUTH_LEAF = ""
    VERIFY_CERTIFICATE = False

    def __init__(self, host: str, credential: BaseCredential, port: Optional[int] = None, scheme: Optional[str] = "https", aspects: RestAspects = DEFAULT_REST_ASPECTS):
        self._host = host
        self._credential = credential
        self._aspects = aspects

        self._host_url = f"{scheme}://{self._host}"
        if port is not None:
            self._host_url = f"{self._host_url}:{port}"

        self._session: requests.Session = None
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

        session = requests.session()

        resp = session.post(auth_url, headers=headers, verify=self.VERIFY_CERTIFICATE)
        if resp.status_code != HTTPStatus.OK:
            errmsg_lines = [
                f"Error attempting to authenticate on url={auth_url}.",
                f"STATUS: {resp.status_code}"
                "RESPONSE:",
                resp.content
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise HttpForbiddenError(errmsg)

        return
    
    def format_http_response_message(self, resp: requests.Response) -> List[str]:
        return

    def perform_call(self, *, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: Union[int, List[int]],
                     aspects: Union[RestAspects, None]) -> requests.Response:
        
        if aspects is None:
            aspects = self._aspects

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
    

    def _get_session(self, aspects: RestAspects) -> requests.Session:

        session = None

        if aspects.session is not None:
            session = aspects.session
        else:
            if self._session is None:
                self.authenticate()

            session = self._session

        return session

    def _perform_single_call(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: Union[int, List[int]],
                     aspects: RestAspects) -> requests.Response:
        
        logger = aspects.logger

        session = self._get_session()

        return
    
    def _perform_single_connected_call(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: Union[int, List[int]],
                     aspects: RestAspects) -> requests.Response:
        return
    
    def _perform_call_until_connection_failure(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: Union[int, List[int]],
                     aspects: RestAspects) -> requests.Response:
        return
    
    def _perform_call_until_success(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: Union[int, List[int]],
                     aspects: RestAspects) -> requests.Response:
        return
    
    def _perform_call_while_success(self, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, str], None], exp_status: Union[int, List[int]],
                     aspects: RestAspects) -> requests.Response:
        return