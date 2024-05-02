
__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

from requests import Response

from mojo.interop.protocols.rest.restaspects import RestAspects


CT = TypeVar('CT')


class PreCannedRequest(Generic[CT]):

    def __init__(self, *, leaf: str, method: str, params: Union[Dict[str, str], None],
                     body: Union[Dict[str, Any], None], exp_status: Union[int, List[int]],
                     aspects: Union[RestAspects, None], perform_call: Callable, package_result: Callable):
        
        self._leaf = leaf
        self._method = method
        self._params = params
        self._body = body
        self._exp_status = exp_status
        self._aspects = aspects
        self._perform_call = perform_call
        self._package_result = package_result
        return

    def perform_call(self) -> "ItemsResult[CT]":

        resp: Response = self._perform_call(leaf=self.leaf, method=self._method, params=self._params, body=self._body, exp_status=self._exp_status, aspects=self._aspects)
        result = self._package_result(resp)

        return result


class Paging:
    """
        The :class:`Paging` object combines a the collection of parameters that are necessary to preform paging opertions
        on the results of a REST API call for a collection.
    """
    def __init__(self, *, page: int, count: int, total_count: int, per_page: int, first_page: int, last_page: int,
                 request_next: Optional[PreCannedRequest] = None, request_prev: Optional[PreCannedRequest] = None):
        self._page = page
        self._count = count
        self._total_count = total_count
        self._per_page = per_page
        self._first_page = first_page
        self._last_page = last_page

        self._request_next = request_next
        self._request_prev = request_prev 
        return
    
    @property
    def count(self) -> int:
        return self._count
    
    @property
    def first_page(self) -> int:
        return self._first_page
    
    @property
    def last_page(self) -> int:
        return self._last_page

    @property
    def page(self) -> int:
        return self._page
    
    @property
    def per_page(self) -> int:
        return self._per_page

    @property
    def request_next(self) -> Union[PreCannedRequest, None]:
        return self._request_next
        
    @property
    def request_prev(self) -> Union[PreCannedRequest, None]:
        return self._request_prev

    @property
    def total_count(self) -> int:
        return self._total_count



class ItemsResult(Generic[CT]):

    def __init__(self, items: List[CT], paging: Optional[Paging] = None):
        self._items = items
        self._paging = paging
        return
    
    @property
    def is_paged(self):
        """
            Returns a value indicating if this items result is paged.
        """
        rtnval = True if self._paging is not None else False
        return rtnval
    
    @property
    def items(self) -> List[CT]:
        """
            Returns a list of items.  This could be a complete list of items or the items from a page depending
            on the results of the API call.
        """
        return self._items
    
    @property
    def paging(self) -> Union[Paging, None]:
        """
            Returns the paging details for this result.
        """
        return self._paging

    def next_page_result(self) -> "ItemsResult[CT]":
        """
            Retrieve the next page of results if there is one.
        """

        result = None

        if self._paging.request_next is not None:
            result = self._paging.request_next.perform_call()

        return result
    
    def prev_page_result(self) -> "ItemsResult[CT]":
        """
            Retrieve the next page of results if there is one.
        """

        result = None

        if self._paging.request_prev is not None:
            result = self._paging.request_prev.perform_call()

        return result


