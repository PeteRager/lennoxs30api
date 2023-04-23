"""
Lennox iComfort S30/E30/M30  API.

By Pete Rager

Notes:
  This API currently only supports manual mode (no programs) on the thermostat.

Cloud API Response Notes:

Issues:

Ideas/Future:

Change log:
v0.2.0 - Initial Release

"""
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation
# pylint: disable=logging-not-lazy
# pylint: disable=invalid-name
# pylint: disable=broad-exception-caught
# pylint: disable=protected-access
# pylint: disable=too-many-lines
# pylint: disable=missing-function-docstring
# pylint: disable=consider-using-dict-items

from datetime import datetime
import logging
import json
import uuid
import ssl
from typing import Final, List
from urllib.parse import quote

from aiohttp import ClientTimeout, ClientSession


from .lennox_ble import LennoxBle
from .lennox_errors import lennox_error_get_message_from_code, LennoxErrorCodes
from .lennox_equipment import lennox_equipment, lennox_equipment_diagnostic
from .lennox_home import lennox_home
from .lennox_schedule import lennox_schedule
from .metrics import Metrics
from .message_logger import MessageLogger
from .s30exception import (
    EC_AUTHENTICATE,
    EC_BAD_PARAMETERS,
    EC_COMMS_ERROR,
    EC_EQUIPMENT_DNS,
    EC_HTTP_ERR,
    EC_LOGIN,
    EC_LOGOUT,
    EC_NEGOTIATE,
    EC_NO_SCHEDULE,
    EC_PUBLISH_MESSAGE,
    EC_REQUEST_DATA_HELPER,
    EC_SETMODE_HELPER,
    EC_SUBSCRIBE,
    EC_UNAUTHORIZED,
    S30Exception,
    s30exception_from_comm_exception,
)


_LOGGER = logging.getLogger(__name__)

CLOUD_AUTHENTICATE_URL = "https://ic3messaging.myicomfort.com/v1/mobile/authenticate"
CLOUD_LOGIN_URL = "https://ic3messaging.myicomfort.com/v2/user/login"
CLOUD_NEGOTIATE_URL = "https://icnotificationservice.myicomfort.com/LennoxNotificationServer/negotiate"
CLOUD_RETRIEVE_URL = "https://icretrieveapi.myicomfort.com/v1/messages/retrieve"
CLOUD_REQUESTDATA_URL = "https://icrequestdataapi.myicomfort.com/v1/Messages/RequestData"
CLOUD_PUBLISH_URL = "https://icpublishapi.myicomfort.com/v1/messages/publish"
CLOUD_LOGOUT_URL = "https://ic3messaging.myicomfort.com/v1/user/logout"

# May need to update as the version of API increases
USER_AGENT: str = "lx_ic3_mobile_appstore/3.75.218 (iPad; iOS 14.4.1; Scale/2.00)"

LENNOX_HVAC_OFF: Final = "off"  # validated
LENNOX_HVAC_COOL: Final = "cool"  # validated
LENNOX_HVAC_HEAT: Final = "heat"  # validated
LENNOX_HVAC_HEAT_COOL: Final = "heat and cool"  # validated
LENNOX_HVAC_EMERGENCY_HEAT: Final = "emergency heat"  # validated

HVAC_MODES: Final = {
    LENNOX_HVAC_OFF,
    LENNOX_HVAC_COOL,
    LENNOX_HVAC_HEAT,
    LENNOX_HVAC_HEAT_COOL,
    LENNOX_HVAC_EMERGENCY_HEAT,
}

LENNOX_HUMIDITY_MODE_OFF: Final = "off"
LENNOX_HUMIDITY_MODE_HUMIDIFY: Final = "humidify"
LENNOX_HUMIDITY_MODE_DEHUMIDIFY: Final = "dehumidify"

HUMIDITY_MODES: Final = {
    LENNOX_HUMIDITY_MODE_OFF,
    LENNOX_HUMIDITY_MODE_HUMIDIFY,
    LENNOX_HUMIDITY_MODE_DEHUMIDIFY,
}

LENNOX_HUMID_OPERATION_OFF: Final = "off"
LENNOX_HUMID_OPERATION_DEHUMID: Final = "dehumidifying"  # validated
LENNOX_HUMID_OPERATION_HUMID: Final = "humidifying"  # a guess
LENNOX_HUMID_OPERATION_WAITING: Final = "waiting"

LENNOX_TEMP_OPERATION_OFF: Final = "off"
LENNOX_TEMP_OPERATION_HEATING: Final = "heating"
LENNOX_TEMP_OPERATION_COOLING: Final = "cooling"

LENNOX_HUMIDIFICATION_MODE_BASIC: Final = "basic"

LENNOX_ZONING_MODE_ZONED: Final = "zoned"
LENNOX_ZONING_MODE_CENTRAL: Final = "central"

FAN_MODES: Final = {"on", "auto", "circulate"}
HVAC_MODE_TARGETS: Final = {"fanMode", "systemMode", "humidityMode"}

LENNOX_MANUAL_MODE_SCHEDULE_START_INDEX: int = 16

LENNOX_INDOOR_UNIT_FURNACE: Final = "furnace"
LENNOX_INDOOR_UNIT_AIR_HANDLER: Final = "air handler"
LENNOX_OUTDOOR_UNIT_AC = "air conditioner"
LENNOX_OUTDOOR_UNIT_HP = "heat pump"

LENNOX_SA_STATE_ENABLED_CANCELLED = "enabled cancelled"
LENNOX_SA_STATE_ENABLED_ACTIVE = "enabled active"
LENNOX_SA_STATE_ENABLED_INACTIVE = "enabled inactive"
LENNOX_SA_STATE_DISABLED = "disabled"

LENNOX_SA_SETPOINT_STATE_HOME = "home"
LENNOX_SA_SETPOINT_STATE_TRANSITION = "transition"
LENNOX_SA_SETPOINT_STATE_AWAY = "away"

LENNOX_STATUS_GOOD: Final = "good"
LENNOX_STATUS_NOT_EXIST: Final = "not_exist"
LENNOX_STATUS_NOT_AVAILABLE: Final = "not_available"
LENNOX_STATUS_ERROR: Final = "error"

LENNOX_STATUS: Final = {LENNOX_STATUS_GOOD, LENNOX_STATUS_NOT_EXIST, LENNOX_STATUS_NOT_AVAILABLE, LENNOX_STATUS_ERROR}

LENNOX_BAD_STATUS: Final = {LENNOX_STATUS_NOT_EXIST, LENNOX_STATUS_NOT_AVAILABLE, LENNOX_STATUS_ERROR}

# Alert Modes
LENNOX_ALERT_CRITICAL = "critical"
LENNOX_ALERT_MODERATE = "moderate"
LENNOX_ALERT_MINOR = "minor"
LENNOX_ALERT_NONE = "none"

# Percentage
# Minimum Time in UI is 9 minutes =  9/60 = 15%
LENNOX_CIRCULATE_TIME_MIN: Final = 15
# Maximum Time in UI is 27 minutes =  27/60 = 45%
LENNOX_CIRCULATE_TIME_MAX: Final = 45

LENNOX_DEHUMIDIFICATION_MODE_HIGH: Final = "high"  # Lennox UI - MAX
LENNOX_DEHUMIDIFICATION_MODE_MEDIUM: Final = "medium"  # Lennox UI - Normal
LENNOX_DEHUMIDIFICATION_MODE_AUTO: Final = "auto"  # Lennos UI - Climate IQ
LENNOX_DEHUMIDIFICATION_MODES: Final = {
    LENNOX_DEHUMIDIFICATION_MODE_MEDIUM,
    LENNOX_DEHUMIDIFICATION_MODE_HIGH,
    LENNOX_DEHUMIDIFICATION_MODE_AUTO,
}


LENNOX_FEATURE_UNIT_MODEL_NUMBER: Final = 6
LENNOX_FEATURE_UNIT_SERIAL_NUMBER: Final = 7
LENNOX_FEATURE_EQUIPMENT_TYPE_NAME: Final = 15

LENNOX_PARAMETER_EQUIPMENT_NAME: Final = 18
LENNOX_PARAMETER_SINGLE_SETPOINT_MODE: Final = 525

LENNOX_EQUIPMENT_TYPE_SUBNET_CONTROLLER: Final = 0
LENNOX_EQUIPMENT_TYPE_FURNACE: Final = 16
LENNOX_EQUIPMENT_TYPE_AIR_HANDLER: Final = 17
LENNOX_EQUIPMENT_TYPE_AIR_CONDITIONER: Final = 18
LENNOX_EQUIPMENT_TYPE_HEAT_PUMP: Final = 19
LENNOX_EQUIPMENT_TYPE_ZONING_CONTROLLER: Final = 22

LENNOX_VENTILATION_DAMPER: Final = "ventilation"
LENNOX_VENTILATION_1_SPEED_ERV: Final = "erv"
LENNOX_VENTILATION_2_SPEED_ERV: Final = "2_stage_erv"
LENNOX_VENTILATION_1_SPEED_HRV: Final = "hrv"
LENNOX_VENTILATION_2_SPEED_HRV: Final = "2_stage_hrv"

LENNOX_VENTILATION_CONTROL_MODE_TIMED: Final = "timed"
LENNOX_VENTILATION_CONTROL_MODE_ASHRAE: Final = "ashrae"

# Parameter range for zoneTestControl
PID_ZONE_1_BLOWER_CFM = 256
PID_ZONE_8_HEATING_CFM = 279

# String in lennox JSON representing no value.
LENNOX_NONE_STR: Final = "none"

# BLE Sensor
LENNOX_BLE_COMMSTATUS_AVAILABLE: Final = "active"
LENNOX_BLE_STATUS_INPUT_AVAILABLE: Final = "0"

# NOTE:  This application id is super important and a point of brittleness.  You can find this in the burp logs between the mobile app and the Lennox server.
# If we start getting reports of missesd message, this is the place to look....
# Here is what I do know
#
#  The application id is unique to the mobile app install, so if you install the app on your iphone and ipad you will have two different ids.
#  Uninstalling app on ipad and re-installing created the same app_id; which is also referenced as the device_id in some api calls
#
# If you use the same application_id in both the app and here, then messages will be lost - as there appears to be a SINGLE QUEUE based on <application_id>_<email> -
# so whichever app consumes the message first gets it. The simple test for this - is with the App open and this program running - go to the thermostat and change the mode it will only show up in one place
#
# Arbitrary application_ids do not work, so for example creating a unique id each time this program runs does not seem to work, changing the prefix from MAPP to HA also did not work.
#
# So what I did is made a single change to one of the digits and i am getting data AND i get updates to both phone and this application
# Because the topic also contains e-mail this has a chance to work, but running this program more the once using the same account and email will result in missed messages
#
# So, we do need a mechanism to generate a unique APPLICATION_ID that does work reliably.
APPLICATION_ID = "mapp079372367644467046827099"

# This appears to be a certificate that is installed as part of the App.  The same cert was presented from both Android and IOS apps.  Fortunately it is being passed; rather than used by the app to encrypt a request.
CERTIFICATE = "MIIKXAIBAzCCChgGCSqGSIb3DQEHAaCCCgkEggoFMIIKATCCBfoGCSqGSIb3DQEHAaCCBesEggXnMIIF4zCCBd8GCyqGSIb3DQEMCgECoIIE/jCCBPowHAYKKoZIhvcNAQwBAzAOBAhvt2dVYDpuhgICB9AEggTYM43UVALue2O5a2GqZ6xPFv1ZOGby+M3I/TOYyVwHDBR+UAYNontMWLvUf6xE/3+GUj/3lBcXk/0erw7iQXa/t9q9b8Xk2r7FFuf+XcWvbXcvcPG0uP74Zx7Fj8HcMmD0/8NNcH23JnoHiWLaa1walfjZG6fZtrOjx4OmV6oYMdkRZm9tP5FuJenPIwdDFx5dEKiWdjdJW0lRl7jWpvbU63gragLBHFqtkCSRCQVlUALtO9Uc2W+MYwh658HrbWGsauLKXABuHjWCK8fiLm1Tc6cuNP/hUF+j3kxt2tkXIYlMhWxEAOUicC0m8wBtJJVCDQQLzwN5PebGGXiq04F40IUOccl9RhaZ2PdWLChaqq+CNQdUZ1mDYcdfg5SVMmiMJayRAA7MWY/t4W53yTU0WXCPu3mg0WPhuRUuphaKdyBgOlmBNrXq/uXjcXgTPqKAKHsph3o6K2TWcPdRBswwc6YJ88J21bLD83fT+LkEmCSldPz+nvLIuQIDZcFnTdUJ8MZRh+QMQgRibyjQwBg02XoEVFg9TJenXVtYHN0Jpvr5Bvd8FDMHGW/4kPM4mODo0PfvHj9wgqMMgTqiih8LfmuJQm30BtqRNm3wHCW1wZ0bbVqefvRSUy82LOxQ9443zjzSrBf7/cFk+03iNn6t3s65ubzuW7syo4lnXwm3DYVR32wo/WmpZVJ3NLeWgypGjNA7MaSwZqUas5lY1EbxLXM5WLSXVUyCqGCdKYFUUKDMahZ6xqqlHUuFj6T49HNWXE7lAdSAOq7yoThMYUVvjkibKkji1p1TIAtXPDPVgSMSsWG1aJilrpZsRuipFRLDmOmbeanS+TvX5ctTa1px/wSeHuAYD/t+yeIlZriajAk62p2ZGENRPIBCbLxx1kViXJBOSgEQc8ItnBisti5N9gjOYoZT3hoONd/IalOxcVU9eBTuvMoVCPMTxYvSz6EUaJRoINS6yWfzriEummAuH6mqENWatudlqKzNAH4RujRetKdvToTddIAGYDJdptzzPIu8OlsmZWTv9HxxUEGYXdyqVYDJkY8dfwB1fsa9vlV3H7IBMjx+nG4ESMwi7UYdhFNoBa7bLD4P1yMQdXPGUs1atFHmPrXYGf2kIdvtHiZ149E9ltxHjRsEaXdhcoyiDVdraxM2H46Y8EZNhdCFUTr2vMau3K/GcU5QMyzY0Z1qD7lajQaBIMGJRZQ6xBnQAxkd4xU1RxXOIRkPPiajExENuE9v9sDujKAddJxvNgBp0e8jljt7ztSZ+QoMbleJx7m9s3sqGvPK0eREzsn/2aQBA+W3FVe953f0Bk09nC6CKi7QwM4uTY9x2IWh/nsKPFSD0ElXlJzJ3jWtLpkpwNL4a8CaBAFPBB2QhRf5bi52KxaAD0TXvQPHsaTPhmUN827smTLoW3lbOmshk4ve1dPAyKPl4/tHvto/EGlYnQf0zjs6BATu/4pJFJz+n0duyF1y/F/elBDXPclJvfyZhEFT99txYsSm2GUijXKOHW/sjMalQctiAyg8Y5CzrOJUhKkB/FhaN5wjJLFz7ZCEJBV7Plm3aNPegariTkLCgkFZrFvrIppvRKjR41suXKP/WhdWhu0Ltb+QgC+8OQTC8INq3v1fdDxT2HKNShVTSubmrUniBuF5MDGBzTATBgkqhkiG9w0BCRUxBgQEAQAAADBXBgkqhkiG9w0BCRQxSh5IADAANgAyAGQANQA5ADMANQAtADYAMAA5AGUALQA0ADYAMgA2AC0AOQA2ADUAZAAtADcAMwBlAGQAMQAwAGUAYwAzAGYAYgA4MF0GCSsGAQQBgjcRATFQHk4ATQBpAGMAcgBvAHMAbwBmAHQAIABTAHQAcgBvAG4AZwAgAEMAcgB5AHAAdABvAGcAcgBhAHAAaABpAGMAIABQAHIAbwB2AGkAZABlAHIwggP/BgkqhkiG9w0BBwagggPwMIID7AIBADCCA+UGCSqGSIb3DQEHATAcBgoqhkiG9w0BDAEGMA4ECFK0DO//E1DsAgIH0ICCA7genbD4j1Y4WYXkuFXxnvvlNmFsw3qPiHn99RVfc+QFjaMvTEqk7BlEBMduOopxUAozoDAv0o+no/LNIgKRXdHZW3i0GPbmoj2WjZJW5T6Z0QVlS5YlQgvbSKVee51grg6nyjXymWgEmrzVldDxy/MfhsxNQUfaLm3awnziFb0l6/m9SHj2eZfdB4HOr2r9BXA6oSQ+8tbGHT3dPnCVAUMjht1MNo6u7wTRXIUYMVn+Aj/xyF9uzDRe404yyenNDPqWrVLoP+Nzssocoi+U+WUFCKMBdVXbM/3GYAuxXV+EHAgvVWcP4deC9ukNPJIdA8gtfTH0Bjezwrw+s+nUy72ROBzfQl9t/FHzVfIZput5GcgeiVppQzaXZMBu/LIIQ9u/1Q7xMHd+WsmNsMlV6eekdO4wcCIo/mM+k6Yukf2o8OGjf1TRwbpt3OH8ID5YRIy848GT49JYRbhNiUetYf5s8cPglk/Q4E2oyNN0LuhTAJtXOH2Gt7LsDVxCDwCA+mUJz1SPAVMVY8hz/h8l4B6sXkwOz3YNe/ILAFncS2o+vD3bxZrYec6TqN+fdkLf1PeKH62YjbFweGR1HLq7R1nD76jinE3+lRZZrfOFWaPMBcGroWOVS0ix0h5r8+lM6n+/hfOS8YTF5Uy++AngQR18IJqT7+SmnLuENgyG/9V53Z7q7BwDo7JArx7tosmxmztcubNCbLFFfzx7KBCIjU1PjFTAtdNYDho0CG8QDfvSQHz9SzLYnQXXWLKRseEGQCW59JnJVXW911FRt4Mnrh5PmLMoaxbf43tBR2xdmaCIcZgAVSjV3sOCfJgja6mKFsb7puzYRBLqYkfQQdOlrnHHrLSkjaqyQFBbpfROkRYo9sRejPMFMbw/Orreo+7YELa+ZoOpS/yZAONgQZ6tlZ4VR9TI5LeLH5JnnkpzpRvHoNkWUtKA+YHqY5Fva3e3iV82O4BwwmJdFXP2RiRQDJYVDzUe5KuurMgduHjqnh8r8238pi5iRZOKlrR7YSBdRXEU9R5dx+i4kv0xqoXKcQdMflE+X4YMd7+BpCFS3ilgbb6q1DuVIN5Bnayyeeuij7sR7jk0z6hV8lt8FZ/Eb+Sp0VB4NeXgLbvlWVuq6k+0ghZkaC1YMzXrfM7N+jy2k1L4FqpO/PdvPRXiA7uiH7JsagI0Uf1xbjA3wbCj3nEi3H/xoyWXgWh2P57m1rxjW1earoyc1CWkRgZLnNc1lNTWVA6ghCSMbCh7T79Fr5GEY2zNcOiqLHS3MDswHzAHBgUrDgMCGgQU0GYHy2BCdSQK01QDvBRI797NPvkEFBwzcxzJdqixLTllqxfI9EJ3KSBwAgIH0A=="


class s30api_async(object):

    """Representation of the Lennox S30/E30 thermostat."""

    def __init__(
        self,
        username: str,
        password: str,
        app_id: str,
        ip_address: str = None,
        protocol: str = "https",
        pii_message_logs=True,
        message_debug_logging=True,
        message_logging_file=None,
        timeout: int = None,
    ):
        """Initialize the API interface.
        username: The user name to login with when using a cloud connection
        password: The password of the user to login with when using a cloud connection
        app_id: The unique application id to use to create a message subscription
        ip_address: The ip_address to connect to when using Local Connection.  None if using a Cloud Connection
        protocol: The protocol to use.  Set to http when using the simulator, else should be https
        pii_message_logs: Indicates if personal information should be redacted from the message logs.
        message_debug_logging:  Indicates if messages should be include when debug logging
        message_logging_file:  When specified messages will be logged to this file only.
        """
        self._username = username
        self._password = password
        self._protocol = protocol
        self._pii_message_logs = pii_message_logs
        self.message_log = MessageLogger(_LOGGER, message_debug_logging, message_logging_file)
        self.timeout: int = 300 if timeout is None else timeout
        # Generate a unique app id, following the existing formatting
        if app_id is None:
            dt = datetime.now()
            epoch_time = dt.strftime("%Y%m%d%H%M%S")
            appPrefix = APPLICATION_ID[: len(APPLICATION_ID) - len(epoch_time)]
            app_id = appPrefix + epoch_time
            self._applicationid: str = app_id
            _LOGGER.info(f"__init__  generating unique applicationId [{self._applicationid}]")
        else:
            self._applicationid: str = app_id
            _LOGGER.info(f"__init__ using provided applicationId [{self._applicationid}]")
        if ip_address is None:
            self.isLANConnection = False
            self.ssl = True
            self.initialize_urls_cloud()
        else:
            self.ip = ip_address
            self.isLANConnection = True
            # The certificate on the S30 cannot be validated.  It is self issued by Lennox
            # Default ciphers needed as of python 3.10
            context = ssl.create_default_context()
            context.set_ciphers("DEFAULT")
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self.ssl = context
            self.initialize_urls_local()

        self._publishMessageId: int = 1
        self._session: ClientSession = None
        self.metrics: Metrics = Metrics()
        self.loginBearerToken = None
        self.authBearerToken = None
        self._homeList: List[lennox_home] = []
        self.system_list: List["lennox_system"] = []
        self._badSenderDict: dict = {}
        self.loginToken: str = None
        self._connectionId = None
        self._connectionToken: str = None
        self._tryWebsockets = None
        self._streamURL: str = None

    def initialize_urls_cloud(self):
        self.url_authenticate: str = CLOUD_AUTHENTICATE_URL
        self.url_login: str = CLOUD_LOGIN_URL
        self.url_negotiate: str = CLOUD_NEGOTIATE_URL
        self.url_retrieve: str = CLOUD_RETRIEVE_URL
        self.url_requestdata: str = CLOUD_REQUESTDATA_URL
        self.url_publish: str = CLOUD_PUBLISH_URL
        self.url_logout: str = CLOUD_LOGOUT_URL

    def set_url_protocol(self, url: str) -> str:
        if self._protocol == "https":
            return url
        return url.replace("https:", self._protocol + ":")

    def message_logger(self, msg) -> None:
        self.message_log.log_message(self._pii_message_logs, msg)

    def initialize_urls_local(self):
        self.url_authenticate: str = None
        self.url_login: str = self.set_url_protocol(f"https://{self.ip}/Endpoints/{self._applicationid}/Connect")
        self.url_negotiate: str = None
        self.url_retrieve: str = self.set_url_protocol(f"https://{self.ip}/Messages/{self._applicationid}/Retrieve")
        self.url_requestdata: str = self.set_url_protocol(f"https://{self.ip}/Messages/RequestData")
        self.url_publish: str = self.set_url_protocol(f"https://{self.ip}/Messages/Publish")
        self.url_logout: str = self.set_url_protocol(f"https://{self.ip}/Endpoints/{self._applicationid}/Disconnect")

    def getClientId(self) -> str:
        if self.isLANConnection is True:
            return self._applicationid
        # Cloud appends email address for uniqueness
        return self._applicationid + "_" + self._username

    async def shutdown(self) -> None:
        if self.isLANConnection is True or self.loginBearerToken is not None:
            await self.logout()
        await self._close_session()

    async def logout(self) -> None:
        _LOGGER.info(f"logout - Entering - [{self.url_logout}]")
        url: str = self.url_logout
        headers = {
            "Authorization": self.loginBearerToken,
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "en-US;q=1",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
        }
        try:
            resp = await self.post(url, headers=headers, data=None)
            if resp.status != 200 and resp.status != 204:
                errmsg = f"logout failed response code [{resp.status}] url [{url}]"
                _LOGGER.error(errmsg)
                raise S30Exception(errmsg, EC_LOGOUT, 1)
        except S30Exception as e:
            raise e from e
        except Exception as e:
            s30e = s30exception_from_comm_exception(e, operation="logout", url=url, metrics=self.metrics)
            if s30e is not None:
                raise s30e from e
            _LOGGER.exception("logout exception - please raise an issue")
            raise S30Exception(f"logout failed [{e}]", EC_AUTHENTICATE, 2) from e

    async def _close_session(self) -> None:
        _LOGGER.debug("Closing Session")
        if self._session is not None:
            try:
                await self._session.close()
                self._session = None
            except Exception as e:
                _LOGGER.exception("_close_session - failed to close session [%s]", str(e))
                self._session = None

    def _create_session(self) -> None:
        _LOGGER.debug("Creating Session")
        to = ClientTimeout(total=self.timeout)
        self._session = ClientSession(timeout=to)

    async def serverConnect(self) -> None:
        # On a reconnect we will close down the old session and get a new one
        _LOGGER.debug("serverConnect - Entering")
        await self._close_session()
        self._create_session()
        await self.authenticate()
        await self.login()
        await self.negotiate()
        self.metrics.last_reconnect_time = self.metrics.now()
        _LOGGER.debug("serverConnect - Complete")

    AUTHENTICATE_RETRIES: int = 5

    async def authenticate(self) -> None:
        """Authenticate with Lennox Server by presenting a certificate.  Throws S30Exception on failure"""
        # The only reason this function would fail is if the certificate is no longer valid or the URL is not longer valid.
        _LOGGER.debug("authenticate - Enter")
        if self.isLANConnection is True:
            return
        url = self.url_authenticate
        body = CERTIFICATE
        err_msg: str = None
        try:
            # I did see this fail due to an active directory error on Lennox side.  I saw the same failure in the Burp log for the App and saw that it repeatedly retried
            # until success, so this must be a known / re-occuring issue that they have solved via retries.  When this occurred the call hung for a while, hence there
            # appears to be no reason to sleep between retries.
            for retry in range(0, self.AUTHENTICATE_RETRIES):
                resp = await self.post(url, data=body)
                if resp.status == 200:
                    resp_json = await resp.json()
                    self.message_logger(resp_json)
                    self.authBearerToken = resp_json["serverAssigned"]["security"]["certificateToken"]["encoded"]
                    _LOGGER.info("authenticated with Lennox Cloud")
                    # Success branch - return from here
                    return
                else:
                    # There is often useful diag information in the txt, so grab it and log it
                    txt = await resp.text()
                    err_msg = f"authenticate failed  - retrying [{retry}] of [{self.AUTHENTICATE_RETRIES - 1}] response code [{resp.status}] text [{txt}]"
                    _LOGGER.warning(err_msg)
            raise S30Exception(err_msg, EC_AUTHENTICATE, 1)
        except S30Exception as e:
            raise e
        except KeyError as e:
            raise S30Exception(
                f"authenticate failed - unexpected response - unable to find [{e}] in msg [{resp_json}]",
                EC_AUTHENTICATE,
                2,
            ) from e
        except Exception as e:
            s30e = s30exception_from_comm_exception(e, operation="authenticate", url=url, metrics=self.metrics)
            if s30e is not None:
                raise s30e from e
            _LOGGER.exception("authenticate exception - please raise as issue")
            raise S30Exception("authenticate failed", EC_AUTHENTICATE, 2) from e

    def getHomeByHomeId(self, homeId) -> lennox_home:
        for home in self._homeList:
            if str(home.id) == str(homeId):
                return home
        return None

    def getOrCreateHome(self, homeId) -> lennox_home:
        home = self.getHomeByHomeId(homeId)
        if home is not None:
            return home
        home = lennox_home(homeId)
        self._homeList.append(home)
        return home

    def getHomeByIdx(self, home_id: int) -> lennox_home:
        for home in self._homeList:
            if str(home.idx) == str(home_id):
                return home
        return None

    def getHomes(self) -> List[lennox_home]:
        return self._homeList

    async def post(self, url, headers=None, data=None):
        # LAN Connections do not send headers
        if self.isLANConnection:
            headers = None
        if data is not None:
            self.metrics.inc_send_count(len(data))
        resp = await self._session.post(url, headers=headers, data=data, ssl=self.ssl)
        self.metrics.inc_receive_count()
        self.metrics.process_http_code(resp.status)
        return resp

    async def get(self, url, headers=None, params=None):
        # LAN Connections do not send headers
        if self.isLANConnection:
            headers = None
        resp = await self._session.get(url, headers=headers, params=params, ssl=self.ssl)
        self.metrics.process_http_code(resp.status)
        self.metrics.inc_receive_count()
        return resp

    async def login(self) -> None:
        """Login to Lennox Server using provided email and password.  Throws S30Exception on failure"""
        _LOGGER.debug("login - Enter")
        url: str = self.url_login
        try:
            if self.isLANConnection is True:
                resp = await self.post(url)
                if resp.status != 200 and resp.status != 204:
                    raise S30Exception(
                        f"login local connection failed url [{url}] response code [{resp.status}]",
                        EC_LOGIN,
                        2,
                    )
                self.setup_local_homes()
            else:
                body: str = (
                    "username="
                    + str(self._username)
                    + "&password="
                    + str(self._password)
                    + "&grant_type=password"
                    + "&applicationid="
                    + str(self._applicationid)
                )
                headers = {
                    "Authorization": self.authBearerToken,
                    "Content-Type": "text/plain",
                    "User-Agent": USER_AGENT,
                }
                resp = await self.post(url, headers=headers, data=body)
                if resp.status != 200:
                    txt = await resp.text()
                    raise S30Exception(
                        f"login failed response code [{resp.status}] url [{url}] text [{txt}]",
                        EC_LOGIN,
                        1,
                    )
                resp_json = await resp.json()
                self.message_logger(resp_json)
                self.process_login_response(resp_json)
        except S30Exception as e:
            _LOGGER.error(e.message)
            raise e
        except json.JSONDecodeError as e:
            raise S30Exception(
                f"login - JSONDecodeError unable to decode json response [{e}]",
                EC_LOGIN,
                3,
            ) from e
        except KeyError as e:
            raise S30Exception(
                f"login failed - unexpected response - unable to find [{e}] in msg [{resp_json}]",
                EC_LOGIN,
                2,
            ) from e
        except Exception as e:
            s30e = s30exception_from_comm_exception(e, operation="login", url=url, metrics=self.metrics)
            if s30e is not None:
                raise s30e from e
            _LOGGER.exception(f"login - unexpected exception - please raise an issue to track [{e}]")
            raise S30Exception(f"login failed due to unexpected exception [{e}]", EC_LOGIN, 7) from e
        _LOGGER.info(f"login Success homes [{len(self._homeList)}] systems [{len(self.system_list)}]")

    def process_login_response(self, resp_json: json):
        # Grab the bearer token
        self.loginBearerToken = resp_json["ServerAssignedRoot"]["serverAssigned"]["security"]["userToken"]["encoded"]
        # Split off the "bearer" part of the token, as we need to use just the token part later in the URL.  Format is "Bearer <token>"
        split = self.loginBearerToken.split(" ")
        self.loginToken = split[1]

        # The list of homes and systems(aka S30s) comes back in the response.
        homeList = resp_json["readyHomes"]["homes"]
        for home in homeList:
            lhome: lennox_home = self.getOrCreateHome(home["homeId"])
            lhome.update(home["id"], home["name"], home)
            for system in resp_json["readyHomes"]["homes"][lhome.idx]["systems"]:
                lsystem = self.getOrCreateSystem(system["sysId"])
                lsystem.update(self, lhome, system["id"])

    def setup_local_homes(self):
        # Need to setup a home and system object to represent the local S30.
        lhome: lennox_home = self.getOrCreateHome("local")
        lhome.update("0", "local", "")
        lsystem = self.getOrCreateSystem("LCC")
        lsystem.update(self, lhome, 0)

    async def negotiate(self) -> None:
        _LOGGER.debug("Negotiate - Enter")
        try:
            if self.isLANConnection is True:
                return
            url = self.url_negotiate
            # This sets the version of the client protocol, at some point Lenox could obsolete this version
            url += "?clientProtocol=1.3.0.0"
            # Since these may have special characters, they need to be URI encoded
            url += "&clientId=" + quote(self.getClientId())
            url += "&Authorization=" + quote(self.loginToken)
            resp = await self.get(url)
            if resp.status != 200:
                txt = await resp.text()
                err_msg = f"negotiate failed response code [{resp.status}] text [{txt}] url [{url}]"
                _LOGGER.error(err_msg)
                raise S30Exception(err_msg, EC_NEGOTIATE, 1)
            resp_json = await resp.json()
            self.message_logger(resp_json)
            # So we get these two pieces of information, but they are never used, perhaps these are used by the websockets interface?
            self._connectionId = resp_json["ConnectionId"]
            self._connectionToken = resp_json["ConnectionToken"]
            # The apps do not try to use websockets, instead they periodically poll the data using the retrieve endpoint, would be better
            # to use websockets, so we will stash the info for future use.
            self._tryWebsockets = resp_json["TryWebSockets"]
            self._streamURL = resp_json["Url"]
            _LOGGER.debug(
                "Negotiate Success tryWebSockets [" + str(self._tryWebsockets) + "] streamUrl [" + self._streamURL + "]"
            )
        except S30Exception as e:
            raise e
        except KeyError as e:
            raise S30Exception(
                f"negotiate failed - unexpected response - unable to find [{e}] in msg [{resp_json}]",
                EC_NEGOTIATE,
                2,
            ) from e
        except Exception as e:
            s30e = s30exception_from_comm_exception(e, operation="negotiate", url=url, metrics=self.metrics)
            if s30e is not None:
                raise s30e from e
            _LOGGER.exception("negotiate - unexpected exception - please raise an issue to track")
            raise S30Exception("negotiate failed due to unexpected exception", EC_COMMS_ERROR, 7) from e

    # The topics subscribed to here are based on the topics that the WebApp subscribes to.  We likely don't need to subscribe to all of them
    # These appear to be JSON topics that correspond to the returned JSON.  For now we will do what the web app does.
    async def subscribe(self, lennoxSystem: "lennox_system") -> None:
        if self.isLANConnection is True:
            ref: int = 1
            try:
                await self.requestDataHelper(
                    lennoxSystem.sysId,
                    '"AdditionalParameters":{"JSONPath":"1;/systemControl;/systemController;/reminderSensors;/reminders;/alerts/active;/alerts/meta;/bleProvisionDB;/ble;/indoorAirQuality;/fwm;/rgw;/devices;/zones;/equipments;/schedules;/occupancy;/system"}',
                )
                ref = 2
                await self.requestDataHelper(
                    lennoxSystem.sysId,
                    '"AdditionalParameters":{"JSONPath":"1;/automatedTest;/zoneTestControl;/homes;/reminders;/algorithm;/historyReportFileDetails;/interfaces;/logs"}',
                )

            except S30Exception as e:
                err_msg = f"subscribe fail loca [{ref}] sysId [{lennoxSystem.sysId}] {e.as_string()}"
                _LOGGER.error(err_msg)
                raise e from e
            except Exception as e:
                err_msg = f"subscribe fail locb [{ref}] sysId [{lennoxSystem.sysId}] [{e}] "
                _LOGGER.exception(err_msg)
                raise S30Exception(err_msg, EC_SUBSCRIBE, 3) from e

        else:
            ref: int = 1
            try:
                await lennoxSystem.update_system_online_cloud()
                ref = 2
                await self.requestDataHelper(
                    lennoxSystem.sysId,
                    '"AdditionalParameters":{"JSONPath":"1;/system;/zones;/occupancy;/schedules;"}',
                )
                ref = 3
                await self.requestDataHelper(
                    lennoxSystem.sysId,
                    '"AdditionalParameters":{"JSONPath":"1;/reminderSensors;/reminders;/alerts/active;/alerts/meta;/dealers;/devices;/equipments;/fwm;/ocst;"}',
                )
            except S30Exception as e:
                err_msg = f"subscribe fail locc [{ref}] sysId [{lennoxSystem.sysId}] {e.as_string()}"
                _LOGGER.error(err_msg)
                raise e
            except Exception as e:
                err_msg = f"subscribe fail locd [{ref}] sysId [{lennoxSystem.sysId}] [{e}]"
                _LOGGER.exception(err_msg)
                raise S30Exception(err_msg, EC_SUBSCRIBE, 3) from e

    async def messagePump(self) -> None:
        # This method reads off the queue.
        # Observations:  the clientId is not passed in, they must be mapping the token to the clientId as part of negotiate
        # The long polling is not working for cloud connections, I have tried adjusting the long polling delay.  Long polling seems to work from the IOS App, not sure
        # what the difference is.   https://gist.github.com/rcarmo/3f0772f2cbe0612b699dcbb839edabeb
        # Returns True if messages were received, False if no messages were found, and throws S30Exception for errors
        #        _LOGGER.debug("Request Data - Enter")
        try:
            url = self.url_retrieve
            headers = {
                "Authorization": self.loginBearerToken,
                "User-Agent": USER_AGENT,
                "Accept": "*.*",
                "Accept-Language": "en-US;q=1",
                "Accept-Encoding": "gzip, deflate",
            }
            params = {
                "Direction": "Oldest-to-Newest",
                "MessageCount": "10",
                "StartTime": "1",
            }
            if self.isLANConnection:
                params["LongPollingTimeout"] = "15"
            else:
                params["LongPollingTimeout"] = "0"

            resp = await self.get(url, headers=headers, params=params)
            self.metrics.inc_receive_bytes(resp.content_length)
            if resp.status == 200:
                resp_txt = await resp.text()
                resp_json = json.loads(resp_txt)
                if len(resp_json["messages"]) == 0:
                    return False
                self.message_logger(resp_json)
                for message in resp_json["messages"]:
                    # This method does not throw exceptions.
                    self.processMessage(message)
            elif resp.status == 204:
                return False
            else:
                err_msg = f"messagePump response http_code [{resp.status}]"
                # 502s happen periodically, so this is an expected error and will only be reported as INFO
                _LOGGER.info(err_msg)
                err_code = EC_HTTP_ERR
                if resp.status == 401:
                    err_code = EC_UNAUTHORIZED
                raise S30Exception(err_msg, err_code, resp.status)
            return True
        except S30Exception as e:
            self.metrics.inc_receive_message_error()
            raise e
        except Exception as e:
            self.metrics.inc_receive_message_error()
            s30e = s30exception_from_comm_exception(e, operation="messagePump", url=url, metrics=self.metrics)
            if s30e is not None:
                raise s30e from e
            # should not be here, these are unexpected exceptions that should be handled better
            _LOGGER.exception("messagePump - unexpected exception - please raise an issue to track")
            raise S30Exception("messagePump failed due to unexpected exception", EC_COMMS_ERROR, 7) from e

    def processMessage(self, message):
        self.metrics.inc_message_count()
        # LAN message and cloud message uses different capitalization.
        if "SenderID" in message:
            sysId = message["SenderID"]
        else:
            sysId = message["SenderId"]
        system = self.getSystem(sysId)
        if system is not None:
            system.processMessage(message)
        else:
            system: lennox_system = self.getSystemSibling(sysId)
            if system is None:
                self.metrics.inc_sender_message_drop()
                if sysId in self._badSenderDict:
                    _LOGGER.debug(f"processMessage dropping messages from unknown SenderId/SystemId [{sysId}]")
                else:
                    _LOGGER.error(
                        f"processMessage dropping message from unknown SenderId/SystemId [{sysId}] - please consult https://github.com/PeteRager/lennoxs30/blob/master/docs/sibling.md for configuration assistance"
                    )
                    self._badSenderDict[sysId] = sysId
            else:
                self.metrics.inc_sibling_message_drop()
                if self.metrics.sibling_message_drop == 1:
                    _LOGGER.warning(
                        f"processMessage dropping message from sibling [{sysId}] for system [{system.sysId}] - please consult https://github.com/PeteRager/lennoxs30/blob/master/docs/sibling.md for configuration assistance"
                    )
                else:
                    _LOGGER.debug(f"processMessage dropping message from sibling [{sysId}] for system [{system.sysId}]")

    # Messages seem to use unique GUIDS, here we create one
    def getNewMessageID(self):
        return str(uuid.uuid4())

    async def requestDataHelper(self, sysId: str, additionalParameters: str) -> json:
        _LOGGER.debug("requestDataHelper - Enter")
        try:
            url = self.url_requestdata
            headers = {
                "Authorization": self.loginBearerToken,
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": USER_AGENT,
                "Accept": "*.*",
                "Accept-Language": "en-US;q=1",
                "Accept-Encoding": "gzip, deflate",
            }

            body = "{"
            body += '"MessageType":"RequestData",'
            body += '"SenderID":"' + self.getClientId() + '",'
            body += '"MessageID":"' + self.getNewMessageID() + '",'
            body += '"TargetID":"' + sysId + '",'
            body += additionalParameters
            body += "}"

            jsbody = json.loads(body)
            self.message_logger(jsbody)
            resp = await self.post(url, headers=headers, data=body)
            if resp.status == 200:
                # TODO we should be inspecting the return body?
                if self.isLANConnection is True:
                    txt = await resp.text()
                    _LOGGER.debug(txt)
                    return txt
                else:
                    txt = await resp.json()
                    self.message_logger(txt)
                    return txt
            else:
                txt = await resp.text()
                err_msg = f"requestDataHelper failed response code [{resp.status}] text [{txt}]"
                _LOGGER.error(err_msg)
                raise S30Exception(err_msg, EC_REQUEST_DATA_HELPER, 1)
        except S30Exception as e:
            raise e
        except json.JSONDecodeError as e:
            raise S30Exception(
                f"requestDataHelper failed - JSONDecodeError [{e}] in msg",
                EC_REQUEST_DATA_HELPER,
                3,
            ) from e
        except Exception as e:
            s30e = s30exception_from_comm_exception(e, operation="requestDataHelper", url=url, metrics=self.metrics)
            if s30e is not None:
                raise s30e from e
            _LOGGER.exception("requestDataHelper - unexpected exception - please raise an issue to track")
            raise S30Exception(
                "requestDataHelper failed due to unexpected exception",
                EC_COMMS_ERROR,
                7,
            ) from e

    def getSystem(self, sysId) -> "lennox_system":
        for system in self.system_list:
            if system.sysId == sysId:
                return system
        return None

    def getSystemSibling(self, sysId: str) -> "lennox_system":
        for system in self.system_list:
            if system.sibling_identifier == sysId:
                return system
        return None

    def getOrCreateSystem(self, sysId: str) -> "lennox_system":
        system = self.getSystem(sysId)
        if system is not None:
            return system
        system = lennox_system(sysId)
        self.system_list.append(system)
        return system

    # When publishing data, app uses a GUID that counts up from 1.
    def getNextMessageId(self):
        self._publishMessageId += 1
        messageUUID = uuid.UUID(int=self._publishMessageId)
        return str(messageUUID)

    async def setModeHelper(self, sysId: str, modeTarget: str, mode: str, scheduleId: int) -> None:
        _LOGGER.info(f"setMode modeTarget [{modeTarget}] mode [{mode}] scheduleId [{scheduleId}] sysId [{sysId}]")
        try:
            if modeTarget not in HVAC_MODE_TARGETS:
                err_msg = (
                    f"setModeHelper - invalide mode target [{modeTarget}] requested, must be in [{HVAC_MODE_TARGETS}]"
                )
                _LOGGER.error(err_msg)
                raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
            data = (
                '"Data":{"schedules":[{"schedule":{"periods":[{"id":0,"period":{"'
                + modeTarget
                + '":"'
                + str(mode)
                + '"}'
            )
            data += '}]},"id":' + str(scheduleId) + "}]}"
            _LOGGER.debug("setmode message [" + data + "]")
            await self.publishMessageHelper(sysId, data)
        except S30Exception as e:
            _LOGGER.error(f"setmode - S30Exception {e.as_string()}")
            raise e
        except Exception as e:
            _LOGGER.exception("setmode - Exception ")
            raise S30Exception(str(e), EC_SETMODE_HELPER, 1) from e
        _LOGGER.info(f"setModeHelper success[{mode}] scheduleId [{scheduleId}] sysId [{sysId}]")

    async def publish_message_helper_dict(self, sysId: str, message: dict, additional_parameters=None):
        data = '"Data":' + json.dumps(message)
        await self.publishMessageHelper(sysId, data, additional_parameters=additional_parameters)

    async def publishMessageHelper(self, sysId: str, data: str, additional_parameters=None) -> None:
        _LOGGER.debug(f"publishMessageHelper sysId [{sysId}] data [{data}]")
        try:
            url = self.url_publish
            headers = {
                "Authorization": self.loginBearerToken,
                "User-Agent": USER_AGENT,
                "Accept": "*.*",
                "Content-Type": "application/json",
                "Accept-Language": "en-US;q=1",
                "Accept-Encoding": "gzip, deflate",
            }

            body = "{"
            body += '"MessageType":"Command",'
            body += '"SenderID":"' + self.getClientId() + '",'
            body += '"MessageID":"' + self.getNextMessageId() + '",'
            body += '"TargetID":"' + sysId + '",'
            if additional_parameters is not None:
                body += '"AdditionalParameters":"' + additional_parameters + '",'
            body += data
            body += "}"

            # See if we can parse the JSON, if we can't error will be thrown, no point in sending lennox bad data
            jsbody = json.loads(body)
            self.message_logger(jsbody)
            resp = await self.post(url, headers=headers, data=body)
            resp_txt = await resp.text()
            if resp.status != 200:
                raise S30Exception(
                    f"publishMessageHelper failed response code [{resp.status}] text [{resp_txt}]",
                    EC_PUBLISH_MESSAGE,
                    1,
                )
            resp_json = json.loads(resp_txt)
            _LOGGER.debug(json.dumps(resp_json, indent=4))
            code = resp_json["code"]
            if code != 1:
                raise S30Exception(
                    f"publishMessageHelper failed server returned code [{code}] msg [{resp_txt}]",
                    EC_PUBLISH_MESSAGE,
                    2,
                )
        except json.JSONDecodeError as e:
            raise S30Exception(
                f"publishMessageHelper failed - JSONDecodeError [{e}] in msg [{resp_txt}]",
                EC_PUBLISH_MESSAGE,
                3,
            ) from e
        except KeyError as e:
            raise S30Exception(
                f"publishMessageHelper failed - unexpected response - unable to find [{e}] in msg [{resp_txt}]",
                EC_PUBLISH_MESSAGE,
                4,
            ) from e
        except S30Exception as e:
            _LOGGER.error(e.message)
            raise e
        except Exception as e:
            s30e = s30exception_from_comm_exception(e, operation="publishMessageHelper", url=url, metrics=self.metrics)
            if s30e is not None:
                raise s30e from e
            _LOGGER.exception("publishMessageHelper - unexpected exception - please raise an issue to track")
            raise S30Exception(
                "publishMessageHelper failed due to unexpected exception",
                EC_COMMS_ERROR,
                5,
            ) from e
        _LOGGER.info("publishMessageHelper success sysId [" + str(sysId) + "]")

    async def setHVACMode(self, sysId: str, mode: str, scheduleId: int) -> None:
        _LOGGER.info(f"setHVACMode mode [{mode}] scheduleId [{scheduleId}] sysId [{sysId}]")
        if mode not in HVAC_MODES:
            err_msg = f"setHVACMode - invalide mode [{mode}] requested, must be in [{HVAC_MODES}]"
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        await self.setModeHelper(sysId, "systemMode", mode, scheduleId)

    async def setHumidityMode(self, sysId: str, mode: str, scheduleId: int):
        _LOGGER.info(f"setHumidityMode mode [{mode}] scheduleId [{scheduleId}] sysId [{sysId}]")
        if mode not in HUMIDITY_MODES:
            err_msg = f"setHumidityMode - invalide mode [{mode}] requested, must be in [{HUMIDITY_MODES}]"
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        await self.setModeHelper(sysId, "humidityMode", mode, scheduleId)

    async def setFanMode(self, sysId: str, mode: str, scheduleId: int) -> None:
        _LOGGER.info(f"setFanMode mode [{mode}] scheduleId [{scheduleId}] sysId [{sysId}]")
        if mode not in FAN_MODES:
            err_msg = f"setFanMode - invalide mode [{mode}] requested, must be in [{FAN_MODES}]"
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        await self.setModeHelper(sysId, "fanMode", mode, scheduleId)

    async def setManualAwayMode(self, sysId: str, mode: bool) -> None:
        _LOGGER.info(f"setManualAwayMode mode [{mode}] sysId [{sysId}]")
        mode_str = None
        if mode is True:
            mode_str = "true"
        if mode is False:
            mode_str = "false"
        if mode_str is None:
            err_msg = f"setManualAwayMode - invalid mode [{mode}] requested, must be True or False"
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        data = '"Data":{"occupancy":{"manualAway":' + mode_str + "}" + "}"
        await self.publishMessageHelper(sysId, data)

    async def cancel_smart_away(self, sysId: str) -> None:
        _LOGGER.info(f"cancel_smart_away sysId [{sysId}]")
        command = {"occupancy": {"smartAway": {"config": {"cancel": True}}}}
        data = '"Data":' + json.dumps(command).replace(" ", "")
        await self.publishMessageHelper(sysId, data)

    async def enable_smart_away(self, sysId: str, mode: bool) -> None:
        _LOGGER.info(f"enable_smart_away mode [{mode}] sysId [{sysId}]")
        if mode is not True and mode is not False:
            err_msg = f"enable_smart_away - invalid mode [{mode}] requested, must be True or False"
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        command = {"occupancy": {"smartAway": {"config": {"enabled": mode}}}}
        data = '"Data":' + json.dumps(command).replace(" ", "")
        await self.publishMessageHelper(sysId, data)


class lennox_system(object):
    """Represents a Lennox Control System"""

    def __init__(self, sysId: str):
        self.sysId: str = sysId
        self.api: s30api_async = None
        self.idx: int = None
        self.home: lennox_home = None
        self.zone_list: List["lennox_zone"] = []
        self._schedules: List[lennox_schedule] = []
        self._callbacks = []
        self._diagcallbacks = []
        self._eqParametersCallbacks = []
        self.outdoorTemperature = None
        self.name: str = None
        self.allergenDefender = None
        self.ventilationMode = None
        self.diagPoweredHours = None
        self.diagRuntime = None
        self.diagVentilationRuntime = None
        self.ventilationRemainingTime = None
        self.ventilatingUntilTime = None
        self.ventilationUnitType = None
        self.ventilationControlMode = None
        self.feelsLikeMode = None
        self.manualAwayMode: bool = None
        self.serialNumber: str = None
        self.alert: str = None
        self.active_alerts = []
        self.alerts_num_cleared: int = None
        self.alerts_num_active: int = None
        self.alerts_last_cleared_id: int = None
        self.alerts_num_in_active_array: int = None

        self.heatpump_low_ambient_lockout: bool = False
        self.aux_heat_high_ambient_lockout: bool = False

        # M30 does not send this info, so default to disabled.
        self.single_setpoint_mode: bool = False
        self.temperatureUnit: str = None
        self.indoorUnitType: str = None
        self.productType = None
        self.outdoorUnitType: str = None
        self.humidifierType = None
        self.dehumidifierType = None
        self.outdoorTemperatureC = None
        self.outdoorTemperature = None
        self.outdoorTemperatureStatus = None
        self.numberOfZones = None
        self.sysUpTime = None
        self.diagLevel = None
        self.softwareVersion = None
        self.diagnosticPaths = {}
        self.diagInverterInputVoltage = None
        self.diagInverterInputCurrent = None
        # Smart Away fields
        self.sa_enabled: bool = None
        self.sa_reset: bool = None
        self.sa_cancel: bool = None
        self.sa_state: str = None
        self.sa_setpointState: str = None
        # Sibling data
        self.sibling_self_identifier: str = None
        self.sibling_identifier: str = None
        self.sibling_systemName: str = None
        self.sibling_nodePresent: str = None
        self.sibling_portNumber: str = None
        self.sibling_ipAddress: str = None
        # iHarmony Zoning Mode
        self.centralMode: bool = None
        self.zoningMode: str = None

        self.circulateTime: int = None  # circulation time
        # dehumidification
        self.enhancedDehumidificationOvercoolingC_enable: bool = None
        self.enhancedDehumidificationOvercoolingF_enable: bool = None
        self.enhancedDehumidificationOvercoolingC: float = None
        self.enhancedDehumidificationOvercoolingF: float = None
        self.enhancedDehumidificationOvercoolingF_min: int = None
        self.enhancedDehumidificationOvercoolingF_max: int = None
        self.enhancedDehumidificationOvercoolingF_inc: float = None
        self.enhancedDehumidificationOvercoolingC_min: int = None
        self.enhancedDehumidificationOvercoolingC_max: int = None
        self.enhancedDehumidificationOvercoolingC_inc: float = None
        self.dehumidificationMode: str = None
        # humidification
        self.humidificationMode: str = None
        # Internet status
        self.relayServerConnected: bool = None
        self.internetStatus: bool = None
        # Cloud Connected  "online" or "offline"
        self.cloud_status: str = None

        self._dirty = False
        self._dirtyList = []
        self.message_processing_list = {
            "system": self._processSystemMessage,
            "zones": self._processZonesMessage,
            "schedules": self._processSchedules,
            "occupancy": self._processOccupancy,
            "devices": self._processDevices,
            "equipments": self._processEquipments,
            "systemControl": self._processSystemControl,
            "siblings": self._processSiblings,
            "rgw": self._process_rgw,
            "alerts": self._process_alerts,
            "ble": self._process_ble,
        }

        self.equipment: dict[int, lennox_equipment] = {}
        self.ble_devices: dict[int, LennoxBle] = {}
        _LOGGER.info(f"Creating lennox_system sysId [{self.sysId}]")

    async def update_system_online_cloud(self):
        response = await self.api.requestDataHelper(
            "ic3server",
            '"AdditionalParameters":{"publisherpresence":"true"},"Data":{"presence":[{"id":0,"endpointId":"'
            + self.sysId
            + '"}]}',
        )
        if response is not None:
            message_txt = response.get("message")
            if message_txt is not None:
                try:
                    message = json.loads(message_txt)
                except Exception as e:
                    _LOGGER.warning(
                        f"update_system_online_cloud - Failed to obtain presence status from cloud message [{message_txt}] exception [{e}]"
                    )
                    return
                presence = message.get("presence")
                if presence is not None:
                    sysId = presence[0].get("endpointId")
                    if sysId != self.sysId:
                        _LOGGER.error(
                            f"update_system_online_cloud - get_system_online_cloud sysId [{self.sysId}] received unexpected sysId [{sysId}]"
                        )
                    else:
                        self.attr_updater(presence[0], "status", "cloud_status")
                        self.executeOnUpdateCallbacks()
                else:
                    _LOGGER.warning(f"update_system_online_cloud - No presense element in response [{response}]")
            else:
                _LOGGER.warning(f"update_system_online_cloud - No message element in response [{response}]")
        else:
            _LOGGER.warning("update_system_online_cloud - No Response Received")

    def update(self, api: s30api_async, home: lennox_home, idx: int):
        self.api = api
        self.idx = idx
        self.home = home
        _LOGGER.info(f"Update lennox_system idx [{self.idx}] sysId [{self.sysId}]")

    def processMessage(self, message) -> None:
        try:
            if "Data" in message:
                # By definition if we receive a message for a cloud connected system, it is online.
                if self.api.isLANConnection is False:
                    self.attr_updater({"status": "online"}, "status", "cloud_status")
                data = message["Data"]
                for key in self.message_processing_list:
                    try:
                        if key in data:
                            self.message_processing_list[key](data[key])
                    except Exception:
                        _LOGGER.exception(f"processMessage key [{key}] Exception - Failed Message to Follow")
                        _LOGGER.error(
                            json.dumps(
                                self.api.message_log.remove_redacted_fields(message),
                                indent=4,
                            )
                        )
                _LOGGER.debug(
                    f"processMessage complete system id [{self.sysId}] dirty [{self._dirty}] dirtyList [{self._dirtyList}]"
                )
                self.executeOnUpdateCallbacks()
        except Exception:
            _LOGGER.exception("processMessage - unexpected exception - Failed Message to Follow")
            _LOGGER.error(json.dumps(self.api.message_log.remove_redacted_fields(message), indent=4))

    def getOrCreateSchedule(self, schedule_id):
        schedule = self.getSchedule(schedule_id)
        if schedule is not None:
            return schedule
        schedule = lennox_schedule(schedule_id)
        self._schedules.append(schedule)
        return schedule

    def getSchedule(self, schedule_id):
        for schedule in self._schedules:
            if schedule.id == schedule_id:
                return schedule
        return None

    def getSchedules(self):
        return self._schedules

    def getOrCreateEquipment(self, equipment_id: int) -> lennox_equipment:
        if equipment_id not in self.equipment:
            self.equipment[equipment_id] = lennox_equipment(equipment_id)
        return self.equipment[equipment_id]

    def get_indoor_unit_equipment(self) -> lennox_equipment:
        if self.has_indoor_unit is False:
            return None
        eq: lennox_equipment = None
        # Try to match on the type
        for _, eq in self.equipment.items():
            if (
                eq.equipment_name is not None
                and self.indoorUnitType is not None
                and eq.equipment_type_name.casefold() == self.indoorUnitType.casefold()
            ):
                return eq
        # Otherwise return Eq 2 as this is typically the indoor unit
        return self.equipment.get(2)

    def get_outdoor_unit_equipment(self) -> lennox_equipment:
        if self.has_outdoor_unit is False:
            return None
        eq: lennox_equipment = None
        # Try to match on the type
        for _, eq in self.equipment.items():
            if (
                eq.equipment_name is not None
                and self.outdoorUnitType is not None
                and eq.equipment_type_name.casefold() == self.outdoorUnitType.casefold()
            ):
                return eq
        # Otherwise return Eq 1 as this is typically the indoor unit
        return self.equipment.get(1)

    def _processSystemControl(self, systemControl):
        if "diagControl" in systemControl:
            self.attr_updater(systemControl["diagControl"], "level", "diagLevel")

    def _processSiblings(self, siblings):
        i = len(siblings)
        if i == 0:
            return
        if i > 1:
            _LOGGER.error(f"Encountered system with more than one sibling, please open an issue.  Message: {siblings}")
        # It appears there could be more than one of these, for now lets only process the first one.
        sibling = siblings[0]
        self.attr_updater(sibling, "selfIdentifier", "sibling_self_identifier")
        if "sibling" in sibling:
            self.attr_updater(sibling["sibling"], "identifier", "sibling_identifier")
            self.attr_updater(sibling["sibling"], "systemName", "sibling_systemName")
            self.attr_updater(sibling["sibling"], "portNumber", "sibling_portNumber")
            self.attr_updater(sibling["sibling"], "nodePresent", "sibling_nodePresent")
            self.attr_updater(sibling["sibling"], "ipAddress", "sibling_ipAddress")

    def _process_rgw(self, rgw):
        if "status" in rgw:
            status = rgw["status"]
            self.attr_updater(status, "relayServerConnected")
            self.attr_updater(status, "internetStatus")

    def _process_alerts(self, alerts):
        if "active" in alerts:
            self.active_alerts = []
            for alert in alerts["active"]:
                if (alert1 := alert.get("alert", None)) is not None:
                    t_alert = alert1.copy()
                    # A code of zero indicates a non-alert, lennox seems to put one of these in by default.
                    if (code := t_alert.get("code", None)) is not None and code != 0:
                        t_alert["message"] = lennox_error_get_message_from_code(code)
                        if code == LennoxErrorCodes.lx_alarm_id_Low_Ambient_HP_Heat_Lockout.value:
                            self.attr_updater(t_alert, "isStillActive", "heatpump_low_ambient_lockout")
                        elif code == LennoxErrorCodes.lx_alarm_id_High_Ambient_Auxiliary_Heat_Lockout.value:
                            self.attr_updater(
                                t_alert,
                                "isStillActive",
                                "aux_heat_high_ambient_lockout",
                            )
                        if t_alert.get("isStillActive", True) is not False:
                            self.active_alerts.append(t_alert)
            self._dirty = True
            self._dirtyList.append("active_alerts")
        if "meta" in alerts:
            meta = alerts["meta"]
            self.attr_updater(meta, "numClearedAlerts", "alerts_num_cleared")
            self.attr_updater(meta, "numActiveAlerts", "alerts_num_active")
            self.attr_updater(meta, "lastClearedAlertId", "alerts_last_cleared_id")
            self.attr_updater(meta, "numAlertsInActiveArray", "alerts_num_in_active_array")
            if "numAlertsInActiveArray" in meta and self.alerts_num_in_active_array == 0:
                self.active_alerts = []
                self._dirty = True
                self._dirtyList.append("active_alerts")

    def get_or_create_ble_device(self, ble_id: int) -> LennoxBle:
        if ble_id not in self.ble_devices:
            self.ble_devices[ble_id] = LennoxBle(ble_id)
        return self.ble_devices[ble_id]

    def _process_ble(self, ble):
        for devices in ble.get("devices", {}):
            if "device" in devices:
                device = devices["device"]
                if "wdn" in device and device["wdn"] != 0:
                    ble_device = self.get_or_create_ble_device(device["wdn"])
                    ble_device.update_from_json(device)
                    ble_device.execute_on_update_callbacks()

    def _processSchedules(self, schedules):
        """Processes the schedule messages, throws base exceptions if a problem is encoutered"""
        for schedule in schedules:
            self._dirty = True
            if "schedules" in self._dirtyList is False:
                self._dirtyList.append("schedules")
            schedule_id = schedule["id"]
            if "schedule" in schedule:
                lschedule = self.getSchedule(schedule_id)
                if lschedule is None and "name" in schedule["schedule"]:
                    lschedule = self.getOrCreateSchedule(schedule_id)
                if lschedule is not None:
                    lschedule.update(schedule)
                    # In manual mode, the updates only hit the schedulde rather than the period within the status.
                    # So here, we look for changes to these schedules and route them to the zone but only
                    # if it is in manual mode.
                    if schedule["id"] in (
                        16,
                        17,
                        18,
                        19,
                    ):  # Manual Mode Zones 1 .. 4
                        zone_id = schedule_id - LENNOX_MANUAL_MODE_SCHEDULE_START_INDEX
                        period = schedule["schedule"]["periods"][0]["period"]
                        zone: lennox_zone = self.getZone(zone_id)
                        if zone.isZoneManualMode():
                            zone._processPeriodMessage(period)
                            zone.executeOnUpdateCallbacks()

    def registerOnUpdateCallback(self, callbackfunc, match=None):
        self._callbacks.append({"func": callbackfunc, "match": match})

    def executeOnUpdateCallbacks(self):
        if self._dirty is True:
            for callback in self._callbacks:
                callbackfunc = callback["func"]
                match = callback["match"]
                matches = False
                if match is None:
                    matches = True
                else:
                    for m in match:
                        if m in self._dirtyList:
                            matches = True
                            break
                try:
                    if matches is True:
                        callbackfunc()
                except Exception:
                    # Log and eat this exception so we can process other callbacks
                    _LOGGER.exception("executeOnUpdateCallback - failed ")
        self._dirty = False
        self._dirtyList = []

    def registerOnUpdateCallbackEqParameters(self, callbackfunc, match=None):
        # match is f'{eid}_{pid}'
        self._eqParametersCallbacks.append({"func": callbackfunc, "match": match})

    def executeOnUpdateCallbacksEqParameters(self, pid):
        for callback in self._eqParametersCallbacks:
            callbackfunc = callback["func"]
            match = callback["match"]
            matches = False
            if match is None:
                matches = True
            else:
                for m in match:
                    if m == pid:
                        matches = True
                        break
            try:
                if matches is True:
                    # Adding ID to the callback, since you can pass in an array
                    # of IDs to register for the callback, the callback needs to
                    # know which id the value belongs to.
                    callbackfunc(pid)
            except Exception:
                # Log and eat this exception so we can process other callbacks
                _LOGGER.exception("executeOnUpdateCallbacksEqParameters - failed ")

    def registerOnUpdateCallbackDiag(self, callbackfunc, match=None):
        # match is f'{eid}_{did}'
        self._diagcallbacks.append({"func": callbackfunc, "match": match})

    def executeOnUpdateCallbacksDiag(self, diag_id, newval):
        for callback in self._diagcallbacks:
            callbackfunc = callback["func"]
            match = callback["match"]
            matches = False
            if match is None:
                matches = True
            else:
                for m in match:
                    if m == diag_id:
                        matches = True
                        break
            try:
                if matches is True:
                    # Adding ID to the callback, since you can pass in an array
                    # of IDs to register for the callback, the callback needs to
                    # know which id the value belongs to.
                    callbackfunc(diag_id, newval)
            except Exception:
                # Log and eat this exception so we can process other callbacks
                _LOGGER.exception("executeOnUpdateCallbacksDiag - failed")

    def attr_updater(self, input_set, attr: str, propertyName: str = None) -> bool:
        if attr in input_set:
            attr_val = input_set[attr]
            if propertyName is None:
                propertyName = attr
            if getattr(self, propertyName) != attr_val:
                setattr(self, propertyName, attr_val)
                self._dirty = True
                if propertyName not in self._dirtyList:
                    self._dirtyList.append(propertyName)
                _LOGGER.debug(f"update_attr: system Id [{self.sysId}] attr [{propertyName}] value [{attr_val}]")
                return True
        return False

    def _processSystemMessage(self, message):
        if "config" in message:
            config = message["config"]
            self.attr_updater(config, "temperatureUnit")
            self.attr_updater(config, "dehumidificationMode")
            self.attr_updater(config, "name")
            self.attr_updater(config, "allergenDefender")
            self.attr_updater(config, "ventilationMode")
            self.attr_updater(config, "centralMode")
            self.attr_updater(config, "circulateTime")
            self.attr_updater(config, "humidificationMode")
            self.attr_updater(config, "enhancedDehumidificationOvercoolingC")
            self.attr_updater(config, "enhancedDehumidificationOvercoolingF")
            if "options" in config:
                options = config["options"]
                self.attr_updater(options, "indoorUnitType")
                self.attr_updater(options, "productType")
                self.attr_updater(options, "outdoorUnitType")
                self.attr_updater(options, "humidifierType")
                self.attr_updater(options, "dehumidifierType")
                if "ventilation" in options:
                    ventilation = options["ventilation"]
                    self.attr_updater(ventilation, "unitType", "ventilationUnitType")
                    self.attr_updater(ventilation, "controlMode", "ventilationControlMode")
                if "enhancedDehumidificationOvercoolingF" in options:
                    eoc = options["enhancedDehumidificationOvercoolingF"]
                    if "range" in eoc:
                        dehumid_range = eoc["range"]
                        self.attr_updater(dehumid_range, "min", "enhancedDehumidificationOvercoolingF_min")
                        self.attr_updater(dehumid_range, "max", "enhancedDehumidificationOvercoolingF_max")
                        self.attr_updater(dehumid_range, "inc", "enhancedDehumidificationOvercoolingF_inc")
                        self.attr_updater(
                            dehumid_range,
                            "enable",
                            "enhancedDehumidificationOvercoolingF_enable",
                        )

                if "enhancedDehumidificationOvercoolingC" in options:
                    eoc = options["enhancedDehumidificationOvercoolingC"]
                    if "range" in eoc:
                        dehumid_range = eoc["range"]
                        self.attr_updater(dehumid_range, "min", "enhancedDehumidificationOvercoolingC_min")
                        self.attr_updater(dehumid_range, "max", "enhancedDehumidificationOvercoolingC_max")
                        self.attr_updater(dehumid_range, "inc", "enhancedDehumidificationOvercoolingC_inc")
                        self.attr_updater(
                            dehumid_range,
                            "enable",
                            "enhancedDehumidificationOvercoolingC_enable",
                        )

        if "status" in message:
            status = message["status"]
            self.attr_updater(status, "outdoorTemperature")
            self.attr_updater(status, "outdoorTemperatureC")
            self.attr_updater(status, "outdoorTemperatureStatus")
            self.attr_updater(status, "diagRuntime")
            self.attr_updater(status, "diagPoweredHours")
            self.attr_updater(status, "zoningMode")
            self.attr_updater(status, "numberOfZones")
            self.attr_updater(status, "diagVentilationRuntime")
            self.attr_updater(status, "ventilationRemainingTime")
            self.attr_updater(status, "ventilatingUntilTime")
            self.attr_updater(status, "feelsLikeMode")
            self.attr_updater(status, "alert")

        if "time" in message:
            time = message["time"]
            old = self.sysUpTime
            self.attr_updater(time, "sysUpTime")
            # When uptime become less than what we recorded, it means the S30 has restarted
            if old is not None and old > self.sysUpTime:
                _LOGGER.warning(
                    f"S30 has rebooted sysId [{self.sysId}] old uptime [{old}] new uptime [{self.sysUpTime}]"
                )

    def _processDevices(self, message):
        for device in message:
            if "device" in device:
                if device.get("device", {}).get("deviceType", {}) == 500:
                    for feature in device["device"].get("features", []):
                        if feature.get("feature", {}).get("fid") == 9:
                            self.serialNumber = feature["feature"]["values"][0]["value"]
                            self._dirty = True
                            self._dirtyList.append("serialNumber")
                        if feature.get("feature", {}).get("fid") == 11:
                            self.softwareVersion = feature["feature"]["values"][0]["value"]
                            self._dirty = True
                            self._dirtyList.append("softwareVersion")

    def _processEquipments(self, message):
        for equipment in message:
            equipment_id = equipment.get("id")
            eq = self.getOrCreateEquipment(equipment_id)
            if "equipment" in equipment:
                eq_equipment = equipment["equipment"]
                if "equipType" in eq_equipment:
                    eq.equipType = eq_equipment["equipType"]
            for feature in equipment.get("equipment", {}).get("features", []):
                if feature.get("feature", {}).get("fid") == LENNOX_FEATURE_EQUIPMENT_TYPE_NAME:
                    if "values" in feature["feature"]:
                        eq.equipment_type_name = feature["feature"]["values"][0]["value"]
                if feature.get("feature", {}).get("fid") == LENNOX_FEATURE_UNIT_MODEL_NUMBER:
                    if "values" in feature["feature"]:
                        eq.unit_model_number = feature["feature"]["values"][0]["value"]
                if feature.get("feature", {}).get("fid") == LENNOX_FEATURE_UNIT_SERIAL_NUMBER:
                    if "values" in feature["feature"]:
                        eq.unit_serial_number = feature["feature"]["values"][0]["value"]
            for parameter in equipment.get("equipment", {}).get("parameters", []):
                # 525 is the parameter id for split-setpoint
                if parameter.get("parameter", {}).get("pid") == LENNOX_PARAMETER_SINGLE_SETPOINT_MODE:
                    value = parameter["parameter"]["value"]
                    if value == 1 or value == "1":
                        self.single_setpoint_mode = True
                    else:
                        self.single_setpoint_mode = False
                    self._dirty = True
                    self._dirtyList.append("single_setpoint_mode")
                if parameter.get("parameter", {}).get("pid") == LENNOX_PARAMETER_EQUIPMENT_NAME:
                    # Lennox isn't consistent with capitilization of Subnet Controller
                    eq.equipment_name = parameter["parameter"]["value"]
                if "parameter" in parameter:
                    if "pid" in parameter["parameter"]:
                        pid = parameter["parameter"]["pid"]
                        par = eq.get_or_create_parameter(pid)
                        par.fromJson(parameter["parameter"])
                        self.executeOnUpdateCallbacksEqParameters(f"{equipment_id}_{pid}")

            for diagnostic in equipment.get("equipment", {}).get("diagnostics", []):
                # the diagnostic values sometimes don't have names
                # so remember where we found important keys
                diagnostic_id = diagnostic.get("id")
                diagnostic_data = diagnostic.get("diagnostic", {})
                diagnostic_name = diagnostic_data.get("name")
                diagnostic_path = f"equipment_{equipment_id}:diagnostic_{diagnostic_id}"
                if diagnostic_name == "Inverter Input Voltage":
                    self.diagnosticPaths[diagnostic_path] = "diagInverterInputVoltage"
                if diagnostic_name == "Inverter Input Current":
                    self.diagnosticPaths[diagnostic_path] = "diagInverterInputCurrent"

                if diagnostic_path in self.diagnosticPaths:
                    self.attr_updater(
                        diagnostic_data,
                        "value",
                        self.diagnosticPaths[diagnostic_path],
                    )

            eid = equipment_id
            for diagnostic_data in equipment.get("equipment", {}).get("diagnostics", []):
                did = diagnostic_data["id"]
                diagnostic: lennox_equipment_diagnostic = eq.get_or_create_diagnostic(did)
                if "diagnostic" in diagnostic_data:
                    diags = diagnostic_data["diagnostic"]
                    if "name" in diags:
                        diagnostic.name = diags["name"]
                    if "unit" in diags:
                        diagnostic.unit = diags["unit"]
                    if "valid" in diags:
                        diagnostic.valid = diags["valid"]
                    if "value" in diags:
                        new_value = diags["value"]
                        if new_value != diagnostic.value:
                            diagnostic.value = new_value
                            self.executeOnUpdateCallbacksDiag(f"{eid}_{did}", new_value)

    def has_emergency_heat(self) -> bool:
        """Returns True is the system has emergency heat"""
        # Emergency heat is defined as a system with a heat pump that also has an indoor furnace
        if self.outdoorUnitType == LENNOX_OUTDOOR_UNIT_HP and self.indoorUnitType == LENNOX_INDOOR_UNIT_FURNACE:
            return True
        return False

    @property
    def unique_id(self) -> str:
        # This returns a unique identifier.  When connected ot the cloud we use the sysid which is a GUID; when
        # connected to the LAN the sysid is alway "LCC" - which is not unique - so in this case we use the device serial number.
        if self.sysId == "LCC":
            return self.serialNumber
        return self.sysId

    def config_complete(self) -> bool:
        if self.name is None:
            return False
        if self.api.isLANConnection and self.serialNumber is None:
            return False
        return True

    def _processOccupancy(self, message):
        self.attr_updater(message, "manualAway", "manualAwayMode")
        if "smartAway" in message:
            smart_away = message["smartAway"]
            if "config" in smart_away:
                smart_away_config = smart_away["config"]
                self.attr_updater(smart_away_config, "enabled", "sa_enabled")
                self.attr_updater(smart_away_config, "reset", "sa_reset")
                self.attr_updater(smart_away_config, "cancel", "sa_cancel")
            if "status" in smart_away:
                smart_away_status = smart_away["status"]
                self.attr_updater(smart_away_status, "state", "sa_state")
                self.attr_updater(smart_away_status, "setpointState", "sa_setpointState")

    def get_manual_away_mode(self) -> bool:
        return self.manualAwayMode

    def get_smart_away_mode(self) -> bool:
        if self.sa_enabled is True and (
            self.sa_setpointState == LENNOX_SA_SETPOINT_STATE_TRANSITION
            or self.sa_setpointState == LENNOX_SA_SETPOINT_STATE_AWAY
        ):
            return True
        return False

    def get_away_mode(self) -> bool:
        if self.get_manual_away_mode() is True or self.get_smart_away_mode() is True:
            return True
        return False

    async def set_manual_away_mode(self, mode: bool) -> None:
        await self.api.setManualAwayMode(self.sysId, mode)

    async def cancel_smart_away(self) -> None:
        if self.sa_enabled is not True:
            raise S30Exception(
                f"Unable to cancel smart away, system [{self.sysId}] smart away not enabled [{self.sa_enabled}]",
                EC_BAD_PARAMETERS,
                1,
            )
        await self.api.cancel_smart_away(self.sysId)

    async def enable_smart_away(self, mode: bool) -> None:
        await self.api.enable_smart_away(self.sysId, mode)

    def getZone(self, zone_id):
        for zone in self.zone_list:
            if zone.id == zone_id:
                return zone
        return None

    async def setHVACMode(self, mode, scheduleId):
        return await self.api.setHVACMode(self.sysId, mode, scheduleId)

    async def setHumidityMode(self, mode, scheduleId):
        return await self.api.setHumidityMode(self.sysId, mode, scheduleId)

    async def setFanMode(self, mode, scheduleId):
        return await self.api.setFanMode(self.sysId, mode, scheduleId)

    def convertFtoC(self, tempF: float, noOffset=False) -> float:
        # Lennox allows Celsius to be specified only in 0.5 degree increments
        if noOffset is False:
            float_TempC = (float(tempF) - 32.0) * (5.0 / 9.0)
        else:
            float_TempC = (float(tempF)) * (5.0 / 9.0)
        return self.celsius_round(float_TempC)

    def convertCtoF(self, tempC: float, noOffset=False) -> int:
        # Lennox allows Faren to be specified only in 1 degree increments
        if noOffset is False:
            float_TempF = (float(tempC) * (9.0 / 5.0)) + 32.0
        else:
            float_TempF = float(tempC) * (9.0 / 5.0)
        return self.faren_round(float_TempF)

    def celsius_round(self, c: float) -> float:
        ### Round to nearest 0.5
        return round(c * 2.0) / 2.0

    def faren_round(self, c: float) -> int:
        ### Round to nearest whole number
        return round(c)

    async def setSchedule(self, zoneId: int, scheduleId: int) -> None:
        data = '"Data":{"zones":[{"config":{"scheduleId":' + str(scheduleId) + '},"id":' + str(zoneId) + "}]}"
        await self.api.publishMessageHelper(self.sysId, data)

    async def perform_schedule_setpoint(
        self,
        zoneId,
        scheduleId,
        hsp=None,
        hspC=None,
        csp=None,
        cspC=None,
        sp=None,
        spC=None,
        husp=None,
        desp=None,
    ) -> None:
        _LOGGER.debug(
            f"lennox_system:perform_schedule_setpoint  sysid [{self.sysId}] zoneid [{zoneId}] schedule_id [{scheduleId}] hsp [{hsp}] hspC [{hspC}] csp [{csp}] cspC [{cspC}] sp [{sp}] spC [{spC}] single_setpoint_mode [{self.single_setpoint_mode}] husp [{husp}] desp [{desp}]"
        )
        if (
            hsp is None
            and hspC is None
            and csp is None
            and cspC is None
            and sp is None
            and spC is None
            and husp is None
            and desp is None
        ):
            raise S30Exception(
                f"lennox_system:perform_schedule_setpoint  sysid [{self.sysId}] no setpoints provided - must specify one or more setpoints",
                EC_BAD_PARAMETERS,
                1,
            )

        ### No data validation in this routine, make sure you know what you are setting.
        ### Use the zone.perform_setpoint for error checking
        command = {"schedules": [{"schedule": {"periods": [{"id": 0, "period": {}}]}, "id": scheduleId}]}

        period = command["schedules"][0]["schedule"]["periods"][0]["period"]
        if hsp is not None:
            period["hsp"] = int(hsp)
        if cspC is not None:
            period["cspC"] = float(cspC)
        if hspC is not None:
            period["hspC"] = float(hspC)
        if csp is not None:
            period["csp"] = int(csp)
        if sp is not None:
            period["sp"] = int(sp)
        if spC is not None:
            period["spC"] = float(spC)
        if husp is not None:
            period["husp"] = int(husp)
        if desp is not None:
            period["desp"] = int(desp)

        data = '"Data":' + json.dumps(command).replace(" ", "")
        await self.api.publishMessageHelper(self.sysId, data)

    def getOrCreateZone(self, zone_id):
        zone = self.getZone(zone_id)
        if zone is not None:
            return zone
        zone = lennox_zone(self, zone_id)
        self.zone_list.append(zone)
        return zone

    def _processZonesMessage(self, message):
        for zone in message:
            zone_id = zone["id"]
            lzone = self.getOrCreateZone(zone_id)
            lzone.processMessage(zone)

    def supports_ventilation(self) -> bool:
        return self.is_none(self.ventilationUnitType) is False

    async def ventilation_on(self) -> None:
        _LOGGER.debug(f"ventilation_on sysid [{self.sysId}]")
        if self.supports_ventilation() is False:
            err_msg = f"ventilation_on - attempting to turn ventilation on for non-supported equipment ventilatorUnitType [{self.ventilationUnitType}]"
            raise S30Exception(err_msg, EC_EQUIPMENT_DNS, 1)
        command = {"system": {"config": {"ventilationMode": "on"}}}
        await self.api.publish_message_helper_dict(self.sysId, command)

    async def ventilation_off(self) -> None:
        _LOGGER.debug(f"ventilation_off sysid [{self.sysId}] ")
        if self.supports_ventilation() is False:
            err_msg = f"ventilation_off - attempting to turn ventilation off for non-supported equipment ventilatorUnitType [{self.ventilationUnitType}]"
            raise S30Exception(err_msg, EC_EQUIPMENT_DNS, 1)
        command = {"system": {"config": {"ventilationMode": "off"}}}
        await self.api.publish_message_helper_dict(self.sysId, command)

    async def ventilation_timed(self, durationSecs: int) -> None:
        _LOGGER.debug(f"ventilation_timed sysid [{self.sysId}] durationSecs [{durationSecs}] ")
        try:
            duration_i = int(durationSecs)
        except ValueError as v:
            err_msg = f"ventilation_timed - invalid duration specified must be a positive integer durationSecs [{durationSecs}] valueError [{v}]"
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1) from v
        if self.supports_ventilation() is False:
            err_msg = f"ventilation_timed - attempting to set timed ventilation for non-supported equipment ventilatorUnitType [{self.ventilationUnitType}]"
            raise S30Exception(err_msg, EC_EQUIPMENT_DNS, 1)
        if duration_i < 0:
            err_msg = f"ventilation_timed - invalid duration specified must be a positive integer durationSecs [{durationSecs}]"
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 2)
        command = {"systemController": {"command": f"ventilateNow {duration_i}"}}
        await self.api.publish_message_helper_dict(self.sysId, command)

    async def allergenDefender_on(self) -> None:
        _LOGGER.debug(f"allergenDefender_on sysid [{self.sysId}] ")
        data = '"Data":{"system":{"config":{"allergenDefender":true} } }'
        await self.api.publishMessageHelper(self.sysId, data)

    async def allergenDefender_off(self) -> None:
        _LOGGER.debug(f"allergenDefender_on sysid [{self.sysId}] ")
        data = '"Data":{"system":{"config":{"allergenDefender":false} } }'
        await self.api.publishMessageHelper(self.sysId, data)

    async def centralMode_on(self) -> None:
        _LOGGER.debug(f"centralMode_on sysid [{self.sysId}] ")
        if self.numberOfZones == 1:
            raise S30Exception(
                "Central Mode is not configurable for a system with only one zone",
                EC_BAD_PARAMETERS,
                1,
            )
        data = '"Data":{"system":{"config":{"centralMode":true} } }'
        await self.api.publishMessageHelper(self.sysId, data)

    async def centralMode_off(self) -> None:
        _LOGGER.debug(f"centralMode_off sysid [{self.sysId}] ")
        if self.numberOfZones == 1:
            raise S30Exception(
                "Central Mode is not configurable for a system with only one zone",
                EC_BAD_PARAMETERS,
                1,
            )
        data = '"Data":{"system":{"config":{"centralMode":false} } }'
        await self.api.publishMessageHelper(self.sysId, data)

    async def set_circulateTime(self, minutes: int) -> None:
        _LOGGER.debug(f"set_circulateTime sysid [{self.sysId}] min [{minutes}]")
        try:
            r_min = int(minutes)
        except ValueError as e:
            raise S30Exception(
                f"Circulate Time [{minutes}] must be an integer between [{LENNOX_CIRCULATE_TIME_MIN}] and [{LENNOX_CIRCULATE_TIME_MAX}]",
                EC_BAD_PARAMETERS,
                1,
            ) from e

        if r_min < LENNOX_CIRCULATE_TIME_MIN or r_min > LENNOX_CIRCULATE_TIME_MAX:
            raise S30Exception(
                f"Circulate Time [{minutes}] must be between [{LENNOX_CIRCULATE_TIME_MIN}] and [{LENNOX_CIRCULATE_TIME_MAX}]",
                EC_BAD_PARAMETERS,
                2,
            )
        data = '"Data":{"system":{"config":{"circulateTime":' + str(r_min) + " } } }"
        await self.api.publishMessageHelper(self.sysId, data)

    def is_none(self, s: str) -> bool:
        if s is None or s == LENNOX_NONE_STR:
            return True
        return False

    async def set_dehumidificationMode(self, mode: str) -> None:
        _LOGGER.debug(f"set_dehumificationMode sysid [{self.sysId}] mode [{mode}]")
        if self.is_none(self.dehumidifierType):
            raise S30Exception(
                f"System does not have a dehumidifier, cannot set dehumidification mode[{mode}]",
                EC_EQUIPMENT_DNS,
                1,
            )
        if mode not in LENNOX_DEHUMIDIFICATION_MODES:
            raise S30Exception(
                f"Dehumidification Mode [{mode}] not a valid value, must be in [{LENNOX_DEHUMIDIFICATION_MODES}]",
                EC_BAD_PARAMETERS,
                2,
            )
        data = '"Data":{"system":{"config":{"dehumidificationMode":"' + mode + '" } } }'
        await self.api.publishMessageHelper(self.sysId, data)

    async def set_enhancedDehumidificationOvercooling(self, r_f: int = None, r_c: float = None):
        _LOGGER.debug(f"set_enhancedDehumidificationOvercooling sysid [{self.sysId}] r_f [{r_f}] r_c [{r_c}]")
        if self.is_none(self.dehumidifierType):
            raise S30Exception(
                f"System does not have a dehumidifier, cannot set enhancedDehumidificationOvercooling r_f [{r_f}] r_c [{r_c}]",
                EC_EQUIPMENT_DNS,
                1,
            )
        if (
            self.enhancedDehumidificationOvercoolingF_enable is not True
            or self.enhancedDehumidificationOvercoolingC_enable is not True
        ):
            raise S30Exception(
                f"System does not allow enhancedDehumidificationOvercooling enhancedDehumidificationOvercoolingF_enable [{self.enhancedDehumidificationOvercoolingF_enable}] enhancedDehumidificationOvercoolingC_enable [{self.enhancedDehumidificationOvercoolingC_enable}]",
                EC_EQUIPMENT_DNS,
                2,
            )
        if r_f is None and r_c is None:
            raise S30Exception(
                "enhancedDehumidificationOvercooling must specifcy r_f, r_c or both",
                EC_BAD_PARAMETERS,
                3,
            )
        if r_f is not None:
            try:
                f = int(r_f)
            except ValueError as e:
                raise S30Exception(
                    f"enhancedDehumidificationOvercooling r_f [{r_f}] must be an integer",
                    EC_BAD_PARAMETERS,
                    4,
                ) from e
            if f < self.enhancedDehumidificationOvercoolingF_min or f > self.enhancedDehumidificationOvercoolingF_max:
                raise S30Exception(
                    f"enhancedDehumidificationOvercooling r_f [{r_f}] must be an integer between [{self.enhancedDehumidificationOvercoolingF_min}] and [{self.enhancedDehumidificationOvercoolingF_max}]",
                    EC_BAD_PARAMETERS,
                    5,
                )
        if r_c is not None:
            try:
                c = float(r_c)
            except ValueError as e:
                raise S30Exception(
                    f"enhancedDehumidificationOvercooling r_f [{r_c}] must be an float",
                    EC_BAD_PARAMETERS,
                    6,
                ) from e
            if c < self.enhancedDehumidificationOvercoolingC_min or c > self.enhancedDehumidificationOvercoolingC_max:
                raise S30Exception(
                    f"enhancedDehumidificationOvercooling r_c [{r_c}] must be an floating point between [{self.enhancedDehumidificationOvercoolingC_min}] and [{self.enhancedDehumidificationOvercoolingC_max}]",
                    EC_BAD_PARAMETERS,
                    7,
                )

            if c % self.enhancedDehumidificationOvercoolingC_inc != 0:
                raise S30Exception(
                    f"enhancedDehumidificationOvercooling r_c [{r_c}] must be an floating point multiple of [{self.enhancedDehumidificationOvercoolingC_inc}]",
                    EC_BAD_PARAMETERS,
                    8,
                )

        if r_c is None:
            c = self.convertFtoC(f, noOffset=True)

        if r_f is None:
            f = self.convertCtoF(c, noOffset=True)

        data = (
            '"Data":{"system":{"config":{"enhancedDehumidificationOvercoolingF":'
            + str(f)
            + ' , "enhancedDehumidificationOvercoolingC":'
            + str(c)
            + "} } }"
        )
        await self.api.publishMessageHelper(self.sysId, data)

    async def set_diagnostic_level(self, level: int) -> None:
        level = int(level)
        _LOGGER.debug(f"set_diagnostic_level sysid [{self.sysId}] level[{level}]")
        if level not in (0, 1, 2):
            raise S30Exception(
                f"Invalid diagnostic level [{level}] valid value [0,1,2]",
                EC_BAD_PARAMETERS,
                1,
            )
        data = '"Data":{"systemControl":{"diagControl":{"level":' + str(level) + "} } }"
        await self.api.publishMessageHelper(self.sysId, data)
        # The S30 does not send message when the systemControl parameters are update, but if we re-ask
        # for the systemControl subscription, it will send us the current data.
        await self.api.requestDataHelper(
            self.sysId,
            '"AdditionalParameters":{"JSONPath":"/systemControl"}',
        )

    async def reset_smart_controller(self) -> None:
        _LOGGER.debug("reset_smart_controller sysid [%s]", self.sysId)
        command = {"resetLcc": {"state": "reset"}}
        await self.api.publish_message_helper_dict(self.sysId, command, "/resetLcc")

    async def set_parameter_value(self, et: int, pid: int, value: str):
        _LOGGER.debug(f"set_parameter_value sysid [{self.sysId}] et [{et}] pid [{pid}] value [{value}]")
        command = {"systemControl": {"parameterUpdate": {"et": et, "pid": pid, "value": str(value)}}}
        await self.api.publish_message_helper_dict(self.sysId, command, additional_parameters="/systemControl")

    async def set_equipment_parameter_value(self, equipment_id: int, pid: int, value: str):
        _LOGGER.debug(
            f"set_equipment_parameter_value sysid [{self.sysId}] equipment_id [{equipment_id}] pid [{pid}] value [{value}]"
        )
        equipment = self.equipment.get(equipment_id)
        if equipment is None:
            raise S30Exception(
                f"set_equipment_parameter_value cannot find equipment with equipment_id [{equipment_id}] pid [{pid}] value [{value}]",
                EC_BAD_PARAMETERS,
                1,
            )
        parameter = equipment.parameters.get(pid)
        if parameter is None:
            raise S30Exception(
                f"set_equipment_parameter_value cannot find parameter with equipment_id [{equipment_id}] pid [{pid}] value [{value}]",
                EC_BAD_PARAMETERS,
                2,
            )

        if parameter.enabled is not True:
            raise S30Exception(
                f"set_equipment_parameter_value cannot set disabled parameter equipment_id [{equipment_id}] pid [{pid}] value [{value}]",
                EC_BAD_PARAMETERS,
                3,
            )

        call_value = parameter.validate_and_translate(value)
        await self.set_parameter_value(equipment.equipType, pid, call_value)

    async def _internal_set_zone_test_parameter_value(self, pid: int, value: str, enabled: bool):
        _LOGGER.debug(
            f"_internal_set_zone_test_parameter_value sysid [{self.sysId}] enabled [{enabled}] pid [{pid}] value [{value}]"
        )
        command = {
            "systemControl": {
                "zoneTestControl": {
                    "enable": enabled,
                    "parameterNumber": pid,
                    "value": str(value),
                }
            }
        }
        await self.api.publish_message_helper_dict(self.sysId, command, additional_parameters="/systemControl")

    async def set_zone_test_parameter_value(self, pid: int, value: str, enabled: bool):
        _LOGGER.debug(
            f"set_zone_test_parameter_value sysid [{self.sysId}] pid [{pid}] value [{value}] enabled [{enabled}]"
        )
        equipment = self.equipment.get(0)
        if equipment is None:
            raise S30Exception(
                f"set_zone_test_parameter_value cannot find equipment with equipment_id 0 pid [{pid}] value [{value}]",
                EC_BAD_PARAMETERS,
                1,
            )

        if pid < PID_ZONE_1_BLOWER_CFM or pid > PID_ZONE_8_HEATING_CFM:
            raise S30Exception(
                f"set_zone_test_parameter_value pid [{pid}] must be between {PID_ZONE_1_BLOWER_CFM} and {PID_ZONE_8_HEATING_CFM} value [{value}]",
                EC_BAD_PARAMETERS,
                2,
            )

        parameter = equipment.parameters.get(pid)
        if parameter is None:
            raise S30Exception(
                f"set_zone_test_parameter_value cannot find parameter with equipment_id 0 pid [{pid}] value [{value}]",
                EC_BAD_PARAMETERS,
                3,
            )

        if parameter.enabled is not True:
            raise S30Exception(
                f"set_zone_test_parameter_value cannot set disabled parameter equipment_id 0 pid [{pid}] value [{value}]",
                EC_BAD_PARAMETERS,
                4,
            )

        call_value = parameter.validate_and_translate(value)
        await self._internal_set_zone_test_parameter_value(pid, call_value, enabled)

    @property
    def has_indoor_unit(self) -> bool:
        if self.indoorUnitType is not None and self.indoorUnitType != LENNOX_NONE_STR:
            return True
        return False

    @property
    def has_outdoor_unit(self) -> bool:
        if self.outdoorUnitType is not None and self.outdoorUnitType != LENNOX_NONE_STR:
            return True
        return False


class lennox_zone(object):
    """Represents a lennox zone"""

    def __init__(self, system, zone_id):
        self._callbacks = []

        self.temperature = None
        self.temperatureC = None
        self.temperatureStatus = None
        self.humidity = None
        self.humidityStatus = None
        self.systemMode = None
        self.tempOperation = None

        self.fanMode = None  # The requested fanMode - on, auto, circulate
        self.fan = None  # The current state of fan,  False = not running, True = running
        self.heatCoast = None
        self.defrost = None
        self.balancePoint = None
        self.aux = None
        self.coolCoast = None
        self.ssr = None
        self.allergenDefender = None  # Allergen defender on or off

        self.humidityMode = None
        self.humOperation = None
        self.csp = None
        self.hsp = None

        self.damper = None  # Damper position 0 - 100
        self.demand = None  # Amount of CFM demand from this zone
        self.ventilation = None

        self.heatingOption = None
        self.coolingOption = None
        self.humidificationOption = None
        self.emergencyHeatingOption = None
        self.dehumidificationOption = None

        self.maxCsp = None
        self.maxCspC = None
        self.minCsp = None
        self.minCspC = None

        self.maxHsp = None
        self.maxHspC = None
        self.minHsp = None
        self.minHspC = None

        self.maxHumSp = None
        self.minHumSp = None
        self.maxDehumSp = None
        self.minDehumSp = None

        self.scheduleId = None
        self.scheduleHold = None

        # PERIOD
        self.systemMode = None
        self.fanMode = None
        self.humidityMode = None
        self.csp = None  # Cool Setpoint F
        self.cspC = None  # Cool Setpoint C
        self.hsp = None  # Heat Setpoint F
        self.hspC = None  # Heat Setpoint C
        self.desp = None  # Dehumidify Setpoint %
        self.sp = None  # Perfect Mode Setpoint F
        self.spC = None  # Perfect Mode Setpoint C
        self.husp = None  # Humidity Setpoint
        self.startTime = None
        self.overrideActive = None

        self.id: int = zone_id
        self.name: str = None
        self.system: lennox_system = system
        self._dirty = False
        self._dirtyList = []

        _LOGGER.info(f"Creating lennox_zone id [{self.id}]")

    @property
    def unique_id(self) -> str:
        return (self.system.unique_id + "_" + str(self.id)).replace("-", "") + "_T"

    def registerOnUpdateCallback(self, callbackfunc, match=None):
        self._callbacks.append({"func": callbackfunc, "match": match})

    def executeOnUpdateCallbacks(self):
        if self._dirty is True:
            for callback in self._callbacks:
                callbackfunc = callback["func"]
                match = callback["match"]
                matches = False
                if match is None:
                    matches = True
                else:
                    for m in match:
                        if m in self._dirtyList:
                            matches = True
                            break
                try:
                    if matches is True:
                        callbackfunc()
                except Exception:
                    # Log and eat this exception so we can process other callbacks
                    _LOGGER.exception("executeOnUpdateCallback - failed")
        self._dirty = False
        self._dirtyList = []

    def attr_updater(self, input_set, attr: str) -> bool:
        if attr in input_set:
            attr_val = input_set[attr]
            if getattr(self, attr) != attr_val:
                setattr(self, attr, attr_val)
                self._dirty = True
                if attr not in self._dirtyList:
                    self._dirtyList.append(attr)
                _LOGGER.debug(f"update_attr: zone Id [{self.id}] attr [{attr}] value [{attr_val}]")
                return True
        return False

    @property
    def is_zone_disabled(self):
        # When zoning is disabled, only zone 0 is enabled
        if self.id == 0 or self.system.zoningMode is None or self.system.zoningMode == LENNOX_ZONING_MODE_ZONED:
            return False
        return True

    def processMessage(self, zoneMessage):
        _LOGGER.debug(f"processMessage lennox_zone id [{self.id}]")
        if "config" in zoneMessage:
            config = zoneMessage["config"]
            self.attr_updater(config, "name")
            self.attr_updater(config, "heatingOption")
            self.attr_updater(config, "maxHsp")
            self.attr_updater(config, "maxHspC")
            self.attr_updater(config, "minHsp")
            self.attr_updater(config, "minHspC")
            self.attr_updater(config, "coolingOption")
            self.attr_updater(config, "maxCsp")
            self.attr_updater(config, "maxCspC")
            self.attr_updater(config, "minCsp")
            self.attr_updater(config, "minCspC")
            self.attr_updater(config, "humidificationOption")
            self.attr_updater(config, "emergencyHeatingOption")
            self.attr_updater(config, "dehumidificationOption")
            self.attr_updater(config, "maxHumSp")
            self.attr_updater(config, "minHumSp")
            self.attr_updater(config, "maxDehumSp")
            self.attr_updater(config, "minDehumSp")
            self.attr_updater(config, "scheduleId")
            self.attr_updater(config, "scheduleHold")
            if "scheduleHold" in config:
                scheduleHold = config["scheduleHold"]
                found = False
                if "scheduleId" in scheduleHold:
                    if scheduleHold["scheduleId"] == self.getOverrideScheduleId():
                        if scheduleHold["enabled"] is True:
                            self.overrideActive = True
                            found = True
                if found is False:
                    self.overrideActive = False
                self._dirty = True
                self._dirtyList.append("scheduleHold")

        if "status" in zoneMessage:
            status = zoneMessage["status"]
            self.attr_updater(status, "temperature")
            self.attr_updater(status, "temperatureC")
            self.attr_updater(status, "temperatureStatus")
            self.attr_updater(status, "humidity")
            self.attr_updater(status, "humidityStatus")
            self.attr_updater(status, "tempOperation")
            self.attr_updater(status, "humOperation")
            self.attr_updater(status, "allergenDefender")
            self.attr_updater(status, "damper")
            self.attr_updater(status, "fan")
            self.attr_updater(status, "demand")
            self.attr_updater(status, "ventilation")
            self.attr_updater(status, "heatCoast")
            self.attr_updater(status, "defrost")
            self.attr_updater(status, "balancePoint")
            self.attr_updater(status, "aux")
            self.attr_updater(status, "coolCoast")
            self.attr_updater(status, "ssr")

            if "period" in status:
                period = status["period"]
                self._processPeriodMessage(period)
        _LOGGER.debug(
            f"processMessage complete lennox_zone id [{self.id}] dirty [{self._dirty}] dirtyList [{self._dirtyList}]"
        )
        self.executeOnUpdateCallbacks()

    def _processPeriodMessage(self, period):
        self.attr_updater(period, "systemMode")
        self.attr_updater(period, "fanMode")
        self.attr_updater(period, "humidityMode")
        self.attr_updater(period, "csp")
        self.attr_updater(period, "cspC")
        self.attr_updater(period, "hsp")
        self.attr_updater(period, "hspC")
        self.attr_updater(period, "desp")
        self.attr_updater(period, "sp")
        self.attr_updater(period, "spC")
        self.attr_updater(period, "husp")
        self.attr_updater(period, "startTime")

    def getTemperature(self):
        return self.temperature

    def is_zone_active(self) -> bool:
        return self.temperature is not None

    def getTemperatureC(self):
        return self.temperatureC

    def getHumidity(self):
        return self.humidity

    def getSystemMode(self):
        return self.systemMode

    def getFanMode(self):
        return self.fanMode

    def getHumidityMode(self) -> str:
        return self.humidityMode

    def getCoolSP(self):
        return self.csp

    def getHeatSP(self):
        return self.hsp

    def getTargetTemperatureF(self):
        if self.systemMode == LENNOX_HVAC_OFF:
            return None
        # In single setpoint mode there is only one target.
        if self.system.single_setpoint_mode is True:
            return self.sp

        if self.systemMode == LENNOX_HVAC_COOL:
            return self.csp

        if self.systemMode == LENNOX_HVAC_HEAT or self.systemMode == LENNOX_HVAC_EMERGENCY_HEAT:
            return self.hsp
        # Calling this method in this mode is probably an error TODO
        if self.systemMode == LENNOX_HVAC_HEAT_COOL:
            return None
        return None

    def getTargetTemperatureC(self):
        if self.systemMode == LENNOX_HVAC_OFF:
            return None
        # In single setpoint mode there is only one target.
        if self.system.single_setpoint_mode is True:
            return self.spC

        if self.heatingOption is True and self.coolingOption is True:
            if self.systemMode == "cool":
                return self.cspC
            if self.systemMode == "heat":
                return self.hspC
        elif self.heatingOption is True:
            return self.hspC
        elif self.coolingOption is True:
            return self.cspC
        else:
            return None

    def getHumidifySetpoint(self):
        return self.husp

    def getManualModeScheduleId(self) -> int:
        return 16 + self.id

    def getOverrideScheduleId(self) -> int:
        return 32 + self.id

    def isZoneManualMode(self) -> bool:
        if self.scheduleId == self.getManualModeScheduleId():
            return True
        return False

    def isZoneOveride(self) -> bool:
        if self.scheduleId == self.getOverrideScheduleId():
            return True
        return False

    def validate_setpoints(self, r_hsp=None, r_hspC=None, r_csp=None, r_cspC=None, r_sp=None, r_spC=None):
        if (r_sp is not None or r_spC is not None) and self.system.single_setpoint_mode is False:
            raise S30Exception(
                "validate_setpoints: r_sp or r_spC can only be specified when system is in single setpoint mode",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_sp is None and r_spC is None and self.system.single_setpoint_mode is True:
            raise S30Exception(
                "validate_setpoints: r_sp or r_spC must be specified when system is in single setpoint mode",
                EC_BAD_PARAMETERS,
                2,
            )

        if (
            r_hsp is not None or r_hspC is not None or r_csp is not None or r_cspC is not None
        ) and self.system.single_setpoint_mode is True:
            raise S30Exception(
                "validate_setpoints: r_hsp, r_hspC, r_csp and r_cspC must not be specified when system is in single setpoint mode",
                EC_BAD_PARAMETERS,
                2,
            )

        if (
            r_hsp is None
            and r_hspC is None
            and r_csp is None
            and r_cspC is None
            and self.system.single_setpoint_mode is False
        ):
            raise S30Exception(
                "validate_setpoints: r_hsp, r_hspC, r_csp or r_cspC must be specified when system is in single setpoint mode",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_csp is not None and r_csp < self.minCsp:
            raise S30Exception(
                f"setHeatCoolSPF r_csp [{r_csp}] must be greater than minCsp [{self.minCsp}]",
                EC_BAD_PARAMETERS,
                1,
            )
        if r_csp is not None and r_csp > self.maxCsp:
            raise S30Exception(
                f"setHeatCoolSPF r_csp [{r_csp}] must be less than maxCsp [{self.maxCsp}]",
                EC_BAD_PARAMETERS,
                2,
            )
        if r_hsp is not None and r_hsp < self.minHsp:
            raise S30Exception(
                f"setHeatCoolSPF r_hsp [{r_hsp}] must be greater than minCsp [{self.minHsp}]",
                EC_BAD_PARAMETERS,
                3,
            )
        if r_hsp is not None and r_hsp > self.maxHsp:
            raise S30Exception(
                f"setHeatCoolSPF r_hsp [{r_hsp}] must be less than maxHsp [{self.maxHsp}]",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_cspC is not None and r_cspC < self.minCspC:
            raise S30Exception(
                f"setHeatCoolSPC r_cspC [{r_cspC}] must be greater than minCspC [{self.minCspC}]",
                EC_BAD_PARAMETERS,
                1,
            )
        if r_cspC is not None and r_cspC > self.maxCspC:
            raise S30Exception(
                f"setHeatCoolSPC r_cspC [{r_cspC}] must be less than maxCspC [{self.maxCspC}]",
                EC_BAD_PARAMETERS,
                2,
            )
        if r_hspC is not None and r_hspC < self.minHspC:
            raise S30Exception(
                f"setHeatCoolSPC r_hspC [{r_hspC}] must be greater than minCspC [{self.minHspC}]",
                EC_BAD_PARAMETERS,
                3,
            )
        if r_hspC is not None and r_hspC > self.maxHspC:
            raise S30Exception(
                f"setHeatCoolSPC r_hspC [{r_hspC}] must be less than maxHspC [{self.maxHspC}]",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_sp is not None and (r_sp > self.maxCsp or r_sp < self.minHsp):
            raise S30Exception(
                f"setHeatCoolSPC r_sp [{r_sp}] must be between [{self.minHsp}] and [{self.maxHsp}]",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_spC is not None and (r_spC > self.maxCspC or r_spC < self.minHspC):
            raise S30Exception(
                f"setHeatCoolSPC r_spC [{r_spC}] must be between [{self.minHspC}] and [{self.maxHspC}]",
                EC_BAD_PARAMETERS,
                2,
            )

    async def perform_setpoint(self, r_hsp=None, r_hspC=None, r_csp=None, r_cspC=None, r_sp=None, r_spC=None):
        _LOGGER.debug(
            f"lennox_zone:perform_setpoint  id [{self.id}] hsp [{r_hsp}] hspC [{r_hspC}] csp [{r_csp}] cspC [{r_cspC}] sp [{r_sp}] spC [{r_spC}] single_setpoint_mode [{self.system.single_setpoint_mode}]"
        )

        self.validate_setpoints(
            r_hsp=r_hsp,
            r_hspC=r_hspC,
            r_csp=r_csp,
            r_cspC=r_cspC,
            r_sp=r_sp,
            r_spC=r_spC,
        )

        hsp = hspC = csp = cspC = sp = spC = None

        # When in this mode, the lennox app always sends hsp,hspC,csp and cspC in the message.  The code fills
        # in the parameters by either converting faren to celsius or by copying the current setpoint value from the zone
        if self.system.single_setpoint_mode is False:
            if r_hsp is not None:
                hsp = self.system.faren_round(r_hsp)
            else:
                if r_hspC is not None:
                    hsp = self.system.convertCtoF(r_hspC)
                else:
                    hsp = self.hsp

            if r_hspC is not None:
                hspC = self.system.celsius_round(r_hspC)
            else:
                if r_hsp is not None:
                    hspC = self.system.convertFtoC(r_hsp)
                else:
                    hspC = self.hspC

            if r_csp is not None:
                csp = self.system.faren_round(r_csp)
            else:
                if r_cspC is not None:
                    csp = self.system.convertCtoF(r_cspC)
                else:
                    csp = self.csp

            if r_cspC is not None:
                cspC = self.system.celsius_round(r_cspC)
            else:
                if r_csp is not None:
                    cspC = self.system.convertFtoC(r_csp)
                else:
                    cspC = self.cspC
        else:
            if r_sp is not None:
                sp = self.system.faren_round(r_sp)
            elif r_spC is not None:
                sp = self.system.convertCtoF(r_spC)

            if r_spC is not None:
                spC = self.system.celsius_round(r_spC)
            elif r_sp is not None:
                spC = self.system.convertFtoC(r_sp)

        await self._execute_setpoints(hsp=hsp, hspC=hspC, csp=csp, cspC=cspC, sp=sp, spC=spC)

    async def _execute_setpoints(
        self,
        hsp=None,
        hspC=None,
        csp=None,
        cspC=None,
        sp=None,
        spC=None,
        husp: int = None,
        desp: int = None,
    ):
        info_str = f"zone [{self.id}] hsp [{hsp}] hspC [{hspC}] csp [{csp}] cspC [{cspC}] sp [{sp}] spC [{spC}] husp [{husp}] desp [{desp}]"
        _LOGGER.info(f"_execute_setpoints {info_str}")
        # If the zone is in manual mode, the temperature can just be set.
        if self.isZoneManualMode() is True:
            _LOGGER.info(f"lennox_zone:_execute_setpoints zone already in manual mode id [{self.id}]")
            await self.system.perform_schedule_setpoint(
                zoneId=self.id,
                scheduleId=self.getManualModeScheduleId(),
                hsp=hsp,
                hspC=hspC,
                csp=csp,
                cspC=cspC,
                sp=sp,
                spC=spC,
                husp=husp,
                desp=desp,
            )
            return

        # The zone is following a schedule.  So first check if it's already running
        # the override schedule and we can just set the temperature
        if self.isZoneOveride() is True:
            _LOGGER.info(f"lennox_zone:_execute_setpoints zone already in overridemode id [{self.id}]")
            await self.system.perform_schedule_setpoint(
                zoneId=self.id,
                scheduleId=self.getOverrideScheduleId(),
                hsp=hsp,
                hspC=hspC,
                csp=csp,
                cspC=cspC,
                sp=sp,
                spC=spC,
                husp=husp,
                desp=desp,
            )
            return

        # Otherwise, we are following a schedule and need to switch into manual over-ride
        # Copy all the data over from the current executing period
        _LOGGER.info(_LOGGER.info(f"lennox_zone:_execute_setpoints creating zone override [{self.id}]"))

        if hsp is None:
            hsp = self.hsp
        if hspC is None:
            hspC = self.hspC
        if csp is None:
            csp = self.csp
        if cspC is None:
            cspC = self.cspC
        if sp is None:
            sp = self.sp
        if spC is None:
            spC = self.spC
        if husp is None:
            husp = self.husp
        if desp is None:
            desp = self.desp

        data = '"Data":{"schedules":[{"schedule":{"periods":[{"id":0,"period":'
        data += '{"desp":' + str(desp) + ","
        data += '"hsp":' + str(hsp) + ","
        data += '"cspC":' + str(cspC) + ","
        data += '"sp":' + str(sp) + ","
        data += '"husp":' + str(husp) + ","
        data += '"humidityMode":"' + str(self.humidityMode) + '",'
        data += '"systemMode":"' + str(self.systemMode) + '",'
        data += '"spC":' + str(spC) + ","
        data += '"hspC":' + str(hspC) + ","
        data += '"csp":' + str(csp) + ","
        data += '"startTime":' + str(self.startTime) + ","
        data += '"fanMode":"' + self.fanMode + '"}'
        data += '}]},"id":' + str(self.getOverrideScheduleId()) + "}]}"

        try:
            await self.system.api.publishMessageHelper(self.system.sysId, data)
        except S30Exception as e:
            _LOGGER.error(f"lennox_zone:_execute_setpoints failed to create override {info_str}")
            raise e

        _LOGGER.info(f"lennox_zone:_execute_setpoints placing zone in override hold {info_str}")

        try:
            await self.setScheduleHold(True)
        except S30Exception as e:
            _LOGGER.error("lennox_zone:_execute_setpoints failed to create schedule hold {info_str}")
            raise e

    async def perform_humidify_setpoint(self, r_husp: int = None, r_desp: int = None):
        _LOGGER.debug(f"lennox_zone:perform_humidify_setpoint id [{self.id}] husp [{r_husp}] desp [{r_desp}]")

        husp: int = None
        desp: int = None

        if r_husp is None and r_desp is None:
            raise S30Exception(
                f"perform_humidify_setpoint: r_husp or r_desp must be specified - values [{r_husp}] [{r_desp}]",
                EC_BAD_PARAMETERS,
                1,
            )

        if r_husp is not None:
            husp = int(r_husp)
            if husp > self.maxHumSp or husp < self.minHumSp:
                raise S30Exception(
                    f"perform_humidify_setpoint: r_husp invalid value [{r_husp}] must be between [{self.minHumSp}] and [{self.maxHumSp}]",
                    EC_BAD_PARAMETERS,
                    2,
                )

        if r_desp is not None:
            desp = int(r_desp)
            if desp > self.maxDehumSp or desp < self.minDehumSp:
                raise S30Exception(
                    f"perform_humidify_setpoint: r_desp invalid value [{r_desp}] must be between [{self.minDehumSp}] and [{self.maxDehumSp}]",
                    EC_BAD_PARAMETERS,
                    2,
                )
        await self._execute_setpoints(husp=husp, desp=desp)

    async def setScheduleHold(self, hold: bool) -> bool:
        if hold is True:
            strHold = "true"
        else:
            strHold = "false"

        _LOGGER.info("lennox_zone:setScheduleHold zone [" + str(self.id) + "] hold [" + str(strHold) + "]")
        # Add a schedule hold to the zone, for now all hold will expire on next period
        data = '"Data":{"zones":[{"config":{"scheduleHold":'
        data += '{"scheduleId":' + str(self.getOverrideScheduleId()) + ","
        data += '"exceptionType":"hold","enabled":' + strHold + ","
        data += '"expiresOn":"0","expirationMode":"nextPeriod"}'
        data += '},"id":' + str(self.id) + "}]}"
        try:
            await self.system.api.publishMessageHelper(self.system.sysId, data)
        except S30Exception as e:
            _LOGGER.error("lennox_zone:setScheduleHold failed zone [" + str(self.id) + "] hold [" + str(strHold) + "]")
            raise e

    async def setManualMode(self) -> None:
        await self.system.setSchedule(self.id, self.getManualModeScheduleId())

    async def setSchedule(self, scheduleName: str) -> None:
        scheduleId = None
        for schedule in self.system.getSchedules():
            if schedule.name == scheduleName:
                scheduleId = schedule.id
                break

        if scheduleId is None:
            err_msg = f"setSchedule - unknown schedule [{scheduleName}] zone [{self.name}]"
            raise S30Exception(err_msg, EC_NO_SCHEDULE, 1)

        await self.system.setSchedule(self.id, scheduleId)

    async def setFanMode(self, fan_mode: str) -> None:
        if self.isZoneManualMode() is True:
            await self.system.setFanMode(fan_mode, self.getManualModeScheduleId())
            return

        if self.isZoneOveride() is False:
            data = '"Data":{"schedules":[{"schedule":{"periods":[{"id":0,"period":'
            data += '{"desp":' + str(self.desp) + ","
            data += '"hsp":' + str(self.hsp) + ","
            data += '"cspC":' + str(self.cspC) + ","
            data += '"sp":' + str(self.sp) + ","
            data += '"husp":' + str(self.husp) + ","
            data += '"humidityMode":"' + str(self.humidityMode) + '",'
            data += '"systemMode":"' + str(self.systemMode) + '",'
            data += '"spC":' + str(self.spC) + ","
            data += '"hspC":' + str(self.hspC) + ","
            data += '"csp":' + str(self.csp) + ","
            data += '"startTime":' + str(self.startTime) + ","
            data += '"fanMode":"' + self.fanMode + '"}'
            data += '}]},"id":' + str(self.getOverrideScheduleId()) + "}]}"

            await self.system.api.publishMessageHelper(self.system.sysId, data)
            await self.setScheduleHold(True)
        await self.system.setFanMode(fan_mode, self.getOverrideScheduleId())

    async def setHVACMode(self, hvac_mode: str) -> None:
        # We want to be careful passing modes to the controller that it does not support.  We don't want to brick the controller.
        if hvac_mode == LENNOX_HVAC_COOL:
            if self.coolingOption is False:
                raise S30Exception(
                    f"setHvacMode - invalid hvac mode - zone [{self.id}]  does not support [{hvac_mode}]",
                    EC_BAD_PARAMETERS,
                    1,
                )
        elif hvac_mode == LENNOX_HVAC_HEAT:
            if self.heatingOption is False:
                raise S30Exception(
                    f"setHvacMode - invalid hvac mode - zone [{self.id}]  does not support [{hvac_mode}]",
                    EC_BAD_PARAMETERS,
                    2,
                )
        elif hvac_mode == LENNOX_HVAC_HEAT_COOL:
            if self.heatingOption is False or self.coolingOption is False:
                raise S30Exception(
                    f"setHvacMode - invalid hvac mode - zone [{self.id}]  does not support [{hvac_mode}]",
                    EC_BAD_PARAMETERS,
                    3,
                )
        elif hvac_mode == LENNOX_HVAC_EMERGENCY_HEAT:
            if self.heatingOption is False or self.system.has_emergency_heat() is False:
                raise S30Exception(
                    f"setHvacMode - invalid hvac mode - zone [{self.id}]  does not support [{hvac_mode}]",
                    EC_BAD_PARAMETERS,
                    4,
                )
        elif hvac_mode == LENNOX_HVAC_OFF:
            pass
        else:
            raise S30Exception(
                f"setHvacMode - invalidate hvac mode - zone [{self.id}]  does not recognize [{hvac_mode}]",
                EC_BAD_PARAMETERS,
                4,
            )

        if self.isZoneManualMode() is False:
            await self.system.setSchedule(self.id, self.getManualModeScheduleId())
        await self.system.setHVACMode(hvac_mode, self.getManualModeScheduleId())

    async def setHumidityMode(self, mode: str) -> None:
        # We want to be careful passing modes to the controller that it does not support.  We don't want to brick the controller.
        if mode == LENNOX_HUMIDITY_MODE_HUMIDIFY:
            if self.humidificationOption is False:
                raise S30Exception(
                    f"setHumidityMode - invalid mode - zone [{self.id}]  does not support [{mode}]",
                    EC_BAD_PARAMETERS,
                    1,
                )
        elif mode == LENNOX_HUMIDITY_MODE_DEHUMIDIFY:
            if self.dehumidificationOption is False:
                raise S30Exception(
                    f"setHumidityMode - invalid mode - zone [{self.id}]  does not support [{mode}]",
                    EC_BAD_PARAMETERS,
                    2,
                )
        elif mode == LENNOX_HUMIDITY_MODE_OFF:
            pass
        else:
            raise S30Exception(
                f"setHumidityMode - invalidate mode - zone [{self.id}]  does not recognize [{mode}]",
                EC_BAD_PARAMETERS,
                4,
            )

        if self.isZoneManualMode() is False:
            await self.system.setSchedule(self.id, self.getManualModeScheduleId())
        await self.system.setHumidityMode(mode, self.getManualModeScheduleId())
