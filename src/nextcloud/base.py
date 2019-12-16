# -*- coding: utf-8 -*-
import enum


class WithRequester(object):

    API_URL = NotImplementedError

    def __init__(self, requester):
        self._requester = requester

    @property
    def requester(self):
        """ Get requester instance """
        # dynamically set API_URL for requester
        self._requester.API_URL = self.API_URL
        self._requester.SUCCESS_CODE = getattr(self, 'SUCCESS_CODE', None)
        return self._requester


class NextcloudError(RuntimeError):
    def __init__(self, msg, code=None):
        super().__init__(msg)
        self.code = code


class MapResultData:
    def __init__(self, where=None, what=None):
        """
        Args:
            where: To which attribute to map the result
            what: How to get the result
        """
        self.where = where
        self.what = what

    def _get_error(self, result):
        raise NotImplementedError()

    def _map_result(self, result):
        raise NotImplementedError()

    def __call__(self, wrapped):
        def wrapper(* args, ** kwargs):
            res = wrapped(* args, ** kwargs)
            if res.is_ok:
                if self.where:
                    self._map_result(res)
            else:
                raise self._get_error(res)
            return res
            wrapped.__doc__ = self._update_doc(wrapped.__doc__)
        return wrapper

    def _update_doc(self, original_doc):
        return original_doc


class WebDavMRD(MapResultData):
    def _get_error(self, result):
        exc = NextcloudError(result.raw.reason, result.raw.status_code)
        return exc


class OCSMRD(MapResultData):
    def _map_result(self, result):
        if self.what:
            setattr(result, self.where, result.data[self.what])
        else:
            setattr(result, self.where, result.data)

    def _result_doc_string(self):
        ret = ""
        if self.what:
            ret = "The result is available as .data[XXX] key, or the .YYY attribute"
        return ret

    def _update_doc(self, original_doc):
        if ":return:" in original_doc:
            doc = original_doc + "\n" + self._result_doc_string()
        return doc

    def _get_error(self, result):
        exc = NextcloudError(result.meta['message'], result.meta['statuscode'])
        return exc


class OCSCode(enum.IntEnum):
    OK = 100
    SERVER_ERROR = 996
    NOT_AUTHORIZED = 997
    NOT_FOUND = 998
    UNKNOWN_ERROR = 999


class ShareType(enum.IntEnum):
    USER = 0
    GROUP = 1
    PUBLIC_LINK = 3
    FEDERATED_CLOUD_SHARE = 6


class Permission(enum.IntEnum):
    """ Permission for Share have to be sum of selected permissions """
    READ = 1
    UPDATE = 2
    CREATE = 4
    DELETE = 8
    SHARE = 16
    ALL = 31


QUOTA_UNLIMITED = -3


def datetime_to_expire_date(date):
    return date.strftime("%Y-%m-%d")
