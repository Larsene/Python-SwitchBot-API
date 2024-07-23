"""
This module provides a simple python wrapper over the Switchbot API.
It simple handles requesting credential.
"""

import hashlib
import keyword
import time
from decouple import config as decoupleconfig
from requests import Session
from uuid import uuid4
import base64
import hmac

from exceptions import APIError

ENDPOINT = 'https://api.switch-bot.com'
VERSION = 'v1.1'
TIMEOUT = 60

class SwitchBot:
    """
    Low level SwitchBot Client. It abstracts the authentication
    """
    def __init__(
        self,
        endpoint=None,
        api_version=None, 
        application_token=None,
        application_secret=None,
        timeout=TIMEOUT,
    ):
        
        """
                Creates a new Switchbot API client.
                
                 The ``endpoint`` identifies the switchbot api endpoint
                 ``application_token`` is the token provided by the app in developper mode
                 ``application_secret``authenticates it
                 ``timeout`` is the request timeout
        
                 if the values are not provided, we will to load them from the .env file
                 or environnement variables, or use defaults values ENDPOINT, VERSION, TIMEOUT
                 
                 :param str endpoint: API endpoint to connect
                 :param str api_version: the version of the API to connect
                 :param str application_token: the token provided by switchbot
                 :param str application_secret: API secret as provided by Switchbot
        
        """
        # load endpoint
        if endpoint is None:
            endpoint = decoupleconfig('ENDPOINT', cast=str, default=ENDPOINT)
        self.endpoint = endpoint
        
        # load version
        if api_version is None:
            api_version = decoupleconfig('API_VERSION', cast=str, default=VERSION)
        self.api_version = api_version
                
        # load token
        if application_token is None:
            application_token = decoupleconfig('TOKEN', cast=str)
        self.application_token =  application_token
        
        # load secret
        if application_secret is None:
            application_secret = decoupleconfig('SECRET', cast=str)
        self.application_secret = application_secret
        
        # timeout
        if timeout is None:
            timeout = decoupleconfig('TIMEOUT', cast=str, default=TIMEOUT)
        self.timeout = timeout        
        
        # use a requests session
        self._session = Session()
       
        
    def get(self, _target, **kwargs):
        """ 'GET' wrapper
        
        :param string _target: API method to call
        """
        if kwargs:
            query_string = kwargs
            if query_string != "":
                if "?" in _target:
                    _target = "%s&%s" % (_target, query_string)
                else:
                    _target = "%s?%s" % (_target, query_string)
        return self.call("GET", _target, None)
    
    
    def post(self, _target, **kwargs):
        """ 'POST' wrapper
        
        :param string _target: API method to call
        """
        if not kwargs:
            kwargs = None
        
        return self.call("POST", _target, None)    
    

    def call(self, method, path, data=None):
        """
        Low level call helper.
    
        :param str method: HTTP verb. Usually one of GET, POST, PUT, DELETE
        :param str path: api entrypoint to call, relative to endpoint base path
        :param data: any json serializable data to send as request's body
        :raises APIError: when request failed
        """
        # attempt request
        try:
            result = self.raw_call(method=method, path=path, data=data)
        except Exception as error:
            raise APIError("Low HTTP request failed error", error)
    
        status = result.status_code
    
        # attempt to decode and return the response
        try:
            if status != 204:
                json_result = result.json()
            else:
                json_result = None
        except ValueError as error:
            raise APIError("Failed to decode API response", error)
    
        # error check
        if status >= 100 and status < 300:
            return json_result
        elif status == 400:
            raise APIError("Bad Request", error)
        elif status == 401:
            raise APIError("Unauthorized", error)
        elif status == 403:
            raise APIError("Forbidden", error)
        elif status == 404:
            raise APIError("Not Found", error)
        elif status == 406:
            raise APIError("Not Acceptable", error)
        elif status == 415:
            raise APIError("Unsupported Media Type", error)
        elif status == 422:
            raise APIError("Unprocessable Entity", error)
        elif status == 429:
            raise APIError("Too Many Requests", error)
        elif status == 500:
            raise APIError("Internal Server Error", error)                                                
        else:
            raise APIError(json_result.get("message"), response=result)


    def raw_call(self, method, path, data=None):
        """ low level call helper, include headers authentication
        
        :param str method: GET, POST, PUT, DELETE
        :param str path: api entrypoint relative to endpoint base path
        :param data: any json serializable data to send as request's body
        """
        target = self.endpoint + '/' + self.api_version +'/' + path
        
        # generation headers params
        nonce = uuid4()
        t = int(round(time.time() * 1000))
        string_to_sign = '{}{}{}'.format(self.application_token, t, nonce)
        string_to_sign = bytes(string_to_sign, 'utf-8')
        secret = bytes(self.application_secret, 'utf-8')
        sign = base64.b64encode(hmac.new(secret,
                                         msg=string_to_sign,
                                         digestmod=hashlib.sha256
                                         ).digest())
        
        #API header JSON
        apiHeader = {
            'Authorization': self.application_token,
            'Content-Type': 'application/json',
            'charset':'utf8',
            't': str(t),
            'sign': str(sign, 'utf-8'),
            'nonce': str(nonce),
        }
                
        return self._session.request(method, target, headers=apiHeader, timeout=self.timeout)