"""Provides the backend for a Cudy router"""

from datetime import timedelta
import time
import math
import logging
import urllib.parse
from http.cookies import SimpleCookie
from hashlib import sha256
import requests
import tzlocal

from . import cudy_parser

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=15)
SCAN_INTERVAL = timedelta(seconds=30)
RETRY_INTERVAL = timedelta(seconds=300)


class CudyRouter:
    """Represents a router and provides functions for communication."""

    def __init__(
        self, host: str, username: str, password: str, port: int = 80,
    ) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self.url = f"http://{self.host}:{self.port}/cgi-bin/luci"
        self.auth_cookie = None
        self.username = username
        self.password = password

    def get_cookie_header(self, force_auth: bool) -> str:
        """Returns a cookie header that should be used for authentication."""

        if not force_auth and self.auth_cookie:
            return f"sysauth={self.auth_cookie}"
        if self.authenticate():
            return f"sysauth={self.auth_cookie}"
        else:
            return ""

    def authenticate(self) -> bool:
        """ Test if we can authenticate with the host.
            Extract from Cudy/Luci javascript code:
            $("form").submit(function(e){
                $("input[name='zonename']").val(Intl.DateTimeFormat().resolvedOptions().timeZone);
                $("input[name='timeclock']").val(Math.floor((new Date()).getTime() / 1000));
                $("button[type='submit']").prop("disabled", true);
                if ($("input[name='salt']").length > 0) {
                    $("input[name='luci_password']").val(sha256($('#luci_password2').val() + $("input[name='salt']").val()));
                    if ($("input[name='token']").length > 0) {
                        $("input[name='luci_password']").val(sha256($("input[name='luci_password']").val() + $("input[name='token']").val()));
                    }
                } else {
                    $("input[name='luci_password']").val($('#luci_password2').val());
                }
            });
        """

        headers = {"Content-Type": "application/x-www-form-urlencoded", "Cookie": ""}

        try:
            response = requests.get(self.url, timeout=30, allow_redirects=False)
            if response.status_code == 403 and (data := cudy_parser.get_login_info(response.text)):
                encrypted_password = self._encrypt_password(self.password, data['token'], data['salt'])
                params_list = [
                    f"zonename={tzlocal.get_localzone_name()}",
                    f"timeclock={int(math.floor(time.time()/1000))}",
                    f"luci_username={urllib.parse.quote(self.username)}",
                    f"luci_password={urllib.parse.quote(encrypted_password)}",
                    "luci_language=en"
                ]
                if data.get('_csrf'):
                    params_list.append(f"_csrf={data['_csrf']}")
                if data.get('token'):
                    params_list.append(f"token={data['token']}")
                if data.get('salt'):
                    params_list.append(f"salt={data['salt']}")
                response = requests.post(self.url, timeout=30, headers=headers, data="&".join(params_list), allow_redirects=False)
            else:
                return False
        except requests.exceptions.ConnectionError:
            _LOGGER.debug("Connection error?")
            return False

        if not response.ok:
            return False

        cookie = SimpleCookie()
        cookie.load(response.headers.get("set-cookie"))
        self.auth_cookie = cookie.get("sysauth").value
        return True

    @staticmethod
    def _encrypt_password(clear_password: str, token: str, salt: str) -> str:
        encrypted_password = clear_password
        if salt:
            encrypted_password = sha256((clear_password + salt).encode("utf-8")).hexdigest()
            if token:
                encrypted_password = sha256((encrypted_password + token).encode('utf-8')).hexdigest()
        return encrypted_password

    def get(self, url: str) -> str:
        """Retrieves data from the given URL using an authenticated session."""

        retries = 2
        while retries > 0:
            retries -= 1

            get_url = f"{self.url}/{url}"
            headers = {"Cookie": f"{self.get_cookie_header(False)}"}

            try:
                response = requests.get(
                    get_url, timeout=30, headers=headers, allow_redirects=False
                )
                if response.status_code == 403:
                    if self.authenticate():
                        continue
                    else:
                        _LOGGER.error("Error during authentication to %s", url)
                        break
                if response.ok:
                    return response.text
                else:
                    break
            except Exception:  # pylint: disable=broad-except
                pass

        _LOGGER.error("Error retrieving data from %s", url)
        return ""
