# -*- coding: utf-8 -*-
from json import JSONDecodeError

from .api_wrappers.webdav import WebDAVStatusCodes


def map_result_data(what, where):
    def decorator(wrapped):
        def wrapper(* args, ** kwargs)
            ret = wrapped(* args, ** kwargs)
            return ret
        return wrapper
    return decorator


class NextCloudResponse(object):

    def __init__(self, response, json_output=True, data=None):
        self.raw = response
        if not data:
            self.data = response.json() if json_output else response.content.decode("UTF-8")
        else:
            self.data = data


class WebDAVResponse(NextCloudResponse):
    """ Response class for WebDAV api methods """

    METHODS_SUCCESS_CODES = {
        "PROPFIND": [WebDAVStatusCodes.MULTISTATUS_CODE],
        "PROPPATCH": [WebDAVStatusCodes.MULTISTATUS_CODE],
        "REPORT": [WebDAVStatusCodes.MULTISTATUS_CODE],
        "MKCOL": [WebDAVStatusCodes.CREATED_CODE],
        "COPY": [WebDAVStatusCodes.CREATED_CODE, WebDAVStatusCodes.NO_CONTENT_CODE],
        "MOVE": [WebDAVStatusCodes.CREATED_CODE, WebDAVStatusCodes.NO_CONTENT_CODE],
        "PUT": [WebDAVStatusCodes.CREATED_CODE],
        "DELETE": [WebDAVStatusCodes.NO_CONTENT_CODE]
    }

    def __init__(self, response, data=None):
        super(WebDAVResponse, self).__init__(response=response, data=data, json_output=False)
        request_method = response.request.method
        self.is_ok = False
        if request_method in self.METHODS_SUCCESS_CODES:
            self.is_ok = response.status_code in self.METHODS_SUCCESS_CODES[request_method]

    def __repr__(self):
        is_ok_str = "OK" if self.is_ok else "Failed"
        return "<OCSResponse: Status: {}>".format(is_ok_str)


class OCSResponse(NextCloudResponse):
    """ Response class for OCS api methods """

    def __init__(self, response, json_output=True, success_code=None):
        self.raw = response
        self.is_ok = None

        if json_output:
            try:
                self.full_data = response.json()
                self.meta = self.full_data['ocs']['meta']
                self.status_code = self.full_data['ocs']['meta']['statuscode']
                self.data = self.full_data['ocs']['data']
                if success_code:
                    self.is_ok = self.full_data['ocs']['meta']['statuscode'] == success_code
            except JSONDecodeError:
                self.is_ok = False
                self.data = {'message': 'Unable to parse JSON response'}
        else:
            self.data = response.content.decode("UTF-8")

    def __repr__(self):
        is_ok_str = "OK" if self.is_ok else "Failed"
        return "<OCSResponse: Status: {}>".format(is_ok_str)
