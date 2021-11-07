"""
Lennox iComfort Wifi API.

Support added for AirEase MyComfortSync thermostats.

By Pete Sage

Notes:
  This API currently only supports manual mode (no programs) on the thermostat.

Cloud API Response Notes:

Issues:

Ideas/Future:

Change log:
v0.2.0 - Initial Release

"""

from aiohttp.client import ClientSession
from .s30exception import (
    EC_AUTHENTICATE,
    EC_BAD_PARAMETERS,
    EC_COMMS_ERROR,
    EC_HTTP_ERR,
    EC_LOGIN,
    EC_LOGOUT,
    EC_NEGOTIATE,
    EC_NO_SCHEDULE,
    EC_PROCESS_MESSAGE,
    EC_PUBLISH_MESSAGE,
    EC_REQUEST_DATA_HELPER,
    EC_RETRIEVE,
    EC_SETMODE_HELPER,
    EC_SUBSCRIBE,
    EC_UNAUTHORIZED,
    S30Exception,
)
from datetime import datetime
import logging
import json
import uuid
import aiohttp

from urllib.parse import quote
from typing import Final, List
from .lennox_period import lennox_period
from .lennox_schedule import lennox_schedule
from .lennox_home import lennox_home
from .metrics import Metrics

_LOGGER = logging.getLogger(__name__)

CLOUD_AUTHENTICATE_URL = "https://ic3messaging.myicomfort.com/v1/mobile/authenticate"
CLOUD_LOGIN_URL = "https://ic3messaging.myicomfort.com/v2/user/login"
CLOUD_NEGOTIATE_URL = (
    "https://icnotificationservice.myicomfort.com/LennoxNotificationServer/negotiate"
)
CLOUD_RETRIEVE_URL = "https://icretrieveapi.myicomfort.com/v1/messages/retrieve"
CLOUD_REQUESTDATA_URL = (
    "https://icrequestdataapi.myicomfort.com/v1/Messages/RequestData"
)
CLOUD_PUBLISH_URL = "https://icpublishapi.myicomfort.com/v1/messages/publish"
CLOUD_LOGOUT_URL = "https://ic3messaging.myicomfort.com/v1/user/logout"

# May need to update as the version of API increases
USER_AGENT: str = "lx_ic3_mobile_appstore/3.75.218 (iPad; iOS 14.4.1; Scale/2.00)"

LENNOX_HVAC_OFF: Final = "off"
LENNOX_HVAC_COOL: Final = "cool"
LENNOX_HVAC_HEAT: Final = "heat"
LENNOX_HVAC_HEAT_COOL: Final = "heat and cool"  # validated

LENNOX_HUMID_OPERATION_DEHUMID: Final = "dehumidifying"  # validated
LENNOX_HUMID_OPERATION_HUMID: Final = "humidifying"  # a guess
LENNOX_HUMID_OPERATION_WAITING: Final = "waiting"

HVAC_MODES: Final = {
    LENNOX_HVAC_OFF,
    LENNOX_HVAC_COOL,
    LENNOX_HVAC_HEAT,
    LENNOX_HVAC_HEAT_COOL,
}
FAN_MODES: Final = {"on", "auto", "circulate"}
HVAC_MODE_TARGETS: Final = {"fanMode", "systemMode"}

LENNOX_MANUAL_MODE_SCHEDULE_START_INDEX: int = 16

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
CERTIFICATE = "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"


class s30api_async(object):

    """Representation of the Lennox S30/E30 thermostat."""

    def __init__(
        self, username: str, password: str, app_id: str, ip_address: str = None
    ):
        """Initialize the API interface."""
        self._username = username
        self._password = password
        # Generate a unique app id, following the existing formatting
        if app_id is None:
            dt = datetime.now()
            epoch_time = dt.strftime("%Y%m%d%H%M%S")
            appPrefix = APPLICATION_ID[: len(APPLICATION_ID) - len(epoch_time)]
            app_id = appPrefix + epoch_time
            self._applicationid: str = app_id
            _LOGGER.info(
                "__init__  generating unique applicationId ["
                + self._applicationid
                + "]"
            )
        else:
            self._applicationid: str = app_id
            _LOGGER.info(
                "__init__ using provided applicationId [" + self._applicationid + "]"
            )
        if ip_address == None:
            self._isLANConnection = False
            self.ssl = True
            self.initialize_urls_cloud()
        else:
            self.ip = ip_address
            self._isLANConnection = True
            # The certicate on the S30 cannot be validated.  It is self issued by Lennox
            self.ssl = False
            self.initialize_urls_local()

        self._publishMessageId: int = 1
        self._session: ClientSession = None
        self.metrics: Metrics = Metrics()
        self.loginBearerToken = None
        self.authBearerToken = None
        self._homeList: List[lennox_home] = []
        self._systemList: List["lennox_system"] = []

    def initialize_urls_cloud(self):
        self.url_authenticate: str = CLOUD_AUTHENTICATE_URL
        self.url_login: str = CLOUD_LOGIN_URL
        self.url_negotiate: str = CLOUD_NEGOTIATE_URL
        self.url_retrieve: str = CLOUD_RETRIEVE_URL
        self.url_requestdata: str = CLOUD_REQUESTDATA_URL
        self.url_publish: str = CLOUD_PUBLISH_URL
        self.url_logout: str = CLOUD_LOGOUT_URL

    def initialize_urls_local(self):
        self.url_authenticate: str = None
        self.url_login: str = (
            f"https://{self.ip}/Endpoints/{self._applicationid}/Connect"
        )
        self.url_negotiate: str = None
        self.url_retrieve: str = (
            f"https://{self.ip}/Messages/{self._applicationid}/Retrieve"
        )
        self.url_requestdata: str = f"https://{self.ip}/Messages/RequestData"
        self.url_publish: str = f"https://{self.ip}/Messages/Publish"
        self.url_logout: str = (
            f"https://{self.ip}/Endpoints/{self._applicationid}/Disconnect"
        )

    def getClientId(self) -> str:
        if self._isLANConnection == True:
            return self._applicationid
        # Cloud appends email address for uniqueness
        return self._applicationid + "_" + self._username

    async def shutdown(self) -> None:
        if self.loginBearerToken != None:
            await self.logout()
        await self._close_session()

    async def logout(self) -> None:
        url: str = self.url_logout
        headers = {
            "Authorization": self.loginBearerToken,
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "en-US;q=1",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
        }
        resp = await self.post(url, headers=headers, data=None)
        if resp.status != 200:
            errmsg = f"Logout failed response code [{resp.status}]"
            _LOGGER.error(errmsg)
            raise S30Exception(errmsg, EC_LOGOUT, 1)

    async def _close_session(self) -> None:
        if self._session != None:
            try:
                await self._session.close()
                self._sesssion = None
            except Exception as e:
                _LOGGER.error("serverConnect - failed to close session [" + str(e))

    async def serverConnect(self) -> None:
        # On a reconnect we will close down the old session and get a new one
        _LOGGER.debug("serverLogin - Entering")
        await self._close_session()
        self._session = aiohttp.ClientSession()
        await self.authenticate()
        await self.login()
        await self.negotiate()
        self.metrics.last_reconnect_time = datetime.now()
        _LOGGER.debug("serverLogin - Complete")

    AUTHENTICATE_RETRIES: int = 5

    async def authenticate(self) -> None:
        """Authenticate with Lennox Server by presenting a certificate.  Throws S30Exception on failure"""
        # The only reason this function would fail is if the certificate is no longer valid or the URL is not longer valid.
        _LOGGER.debug("authenticate - Enter")
        if self._isLANConnection == True:
            return
        url = self.url_authenticate
        body = CERTIFICATE
        err_msg: str = None
        try:
            # I did see this fail due to an active directory error on Lennox side.  I saw the same failure in the Burp log for the App and saw that it repeatedly retried
            # until success, so this must be a known / re-occuring issue that they have solved via retries.  When this occured the call hung for a while, hence there
            # appears to be no reason to sleep between retries.
            for retry in range(1, self.AUTHENTICATE_RETRIES):
                resp = await self.post(url, data=body)
                if resp.status == 200:
                    resp_json = await resp.json()
                    _LOGGER.debug(json.dumps(resp_json, indent=4))
                    self.authBearerToken = resp_json["serverAssigned"]["security"][
                        "certificateToken"
                    ]["encoded"]
                    _LOGGER.info("authenticated with Lennox Cloud")
                    # Success branch - return from here
                    return
                else:
                    # There is often useful diag information in the txt, so grab it and log it
                    txt = await resp.text()
                    err_msg = f"authenticate failed  - retrying [{retry}] of [{self.AUTHENTICATE_RETRIES}] response code [{resp.status}] text [{txt}]"
                    _LOGGER.warning(err_msg)
            raise S30Exception(err_msg, EC_AUTHENTICATE, 1)
        except Exception as e:
            _LOGGER.error("authenticate exception " + str(e))
            raise S30Exception("Authentication Failed", EC_AUTHENTICATE, 2)

    def getHomeByHomeId(self, homeId) -> lennox_home:
        for home in self._homeList:
            if str(home.id) == str(homeId):
                return home
        return None

    def getOrCreateHome(self, homeId) -> lennox_home:
        home = self.getHomeByHomeId(homeId)
        if home != None:
            return home
        home = lennox_home(homeId)
        self._homeList.append(home)
        return home

    def getHomeByIdx(self, id) -> lennox_home:
        for home in self._homeList:
            if str(home.idx) == str(id):
                return home
        return None

    def getHomes(self) -> List[lennox_home]:
        return self._homeList

    async def post(self, url, headers=None, data=None):
        # LAN Connections do not send headers
        if self._isLANConnection:
            headers = None
        if data != None:
            self.metrics.inc_send_count(len(data))
        resp = await self._session.post(url, headers=headers, data=data, ssl=self.ssl)
        self.metrics.inc_receive_count()
        self.metrics.process_http_code(resp.status)
        return resp

    async def get(self, url, headers=None, params=None):
        # LAN Connections do not send headers
        if self._isLANConnection:
            headers = None
        resp = await self._session.get(
            url, headers=headers, params=params, ssl=self.ssl
        )
        self.metrics.process_http_code(resp.status)
        self.metrics.inc_receive_count()
        return resp

    async def login(self) -> None:
        """Login to Lennox Server using provided email and password.  Throws S30Exception on failure"""
        _LOGGER.debug("login - Enter")
        url: str = self.url_login
        try:
            if self._isLANConnection == True:
                resp = await self.post(url)
                if resp.status != 200 and resp.status != 204:
                    errmsg = f"Local connection failed response code [{resp.status}]"
                    _LOGGER.error(errmsg)
                    raise S30Exception(errmsg, EC_LOGIN, 2)
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
                    errmsg = f"Login failed response code [{resp.status}] text [{txt}]"
                    _LOGGER.error(errmsg)
                    raise S30Exception(errmsg, EC_LOGIN, 1)
                resp_json = await resp.json()
                _LOGGER.debug(json.dumps(resp_json, indent=4))
                self.process_login_response(resp_json)
        except S30Exception as e:
            raise e
        except Exception as e:
            txt = str(e)
            _LOGGER.error("Exception " + str(e))
            raise S30Exception(str(e), EC_COMMS_ERROR, 2)
        _LOGGER.info(
            f"login Success homes [{len(self._homeList)}] systems [{len(self._systemList)}]"
        )

    def process_login_response(self, resp_json: json):
        # Grab the bearer token
        self.loginBearerToken = resp_json["ServerAssignedRoot"]["serverAssigned"][
            "security"
        ]["userToken"]["encoded"]
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
            if self._isLANConnection == True:
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
                err_msg = f"Negotiate failed response code [{resp.status}] text [{txt}]"
                _LOGGER.error(err_msg)
                raise S30Exception(err_msg, EC_NEGOTIATE, 1)
            resp_json = await resp.json()
            _LOGGER.debug(json.dumps(resp_json, indent=4))
            # So we get these two pieces of information, but they are never used, perhaps these are used by the websockets interface?
            self._connectionId = resp_json["ConnectionId"]
            self._connectionToken = resp_json["ConnectionToken"]
            # The apps do not try to use websockets, instead they periodically poll the data using the retrieve endpoint, would be better
            # to use websockets, so we will stash the info for future use.
            self._tryWebsockets = resp_json["TryWebSockets"]
            self._streamURL = resp_json["Url"]
            _LOGGER.info(
                "Negotiate Success connectionId ["
                + self._connectionId
                + "] tryWebSockets ["
                + str(self._tryWebsockets)
                + "] streamUrl ["
                + self._streamURL
                + "]"
            )
        except Exception as e:
            err_msg = "Negotiate - Failed - Exception " + str(e)
            _LOGGER.error(err_msg)
            raise S30Exception(err_msg, EC_NEGOTIATE, 2)

    # The topics subscribed to here are based on the topics that the WebApp subscribes to.  We likely don't need to subscribe to all of them
    # These appear to be JSON topics that correspond to the returned JSON.  For now we will do what the web app does.
    async def subscribe(self, lennoxSystem: "lennox_system") -> None:

        if self._isLANConnection == True:
            ref: int = 1
            try:
                await self.requestDataHelper(
                    lennoxSystem.sysId,
                    '"AdditionalParameters":{"JSONPath":"1;/devices;/zones;/equipments;/schedules;/occupancy;/system"}',
                )
            except S30Exception as e:
                err_msg = f"subsribe fail loca [{ref}] " + str(e)
                _LOGGER.error(err_msg)
                raise e
            except Exception as e:
                err_msg = f"subsribe fail locb [{ref}] " + str(e)
                _LOGGER.error(err_msg)
                raise S30Exception(err_msg, EC_SUBSCRIBE, 3)

        else:
            ref: int = 1
            try:
                await self.requestDataHelper(
                    "ic3server",
                    '"AdditionalParameters":{"publisherpresence":"true"},"Data":{"presence":[{"id":0,"endpointId":"'
                    + lennoxSystem.sysId
                    + '"}]}',
                )
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
                err_msg = f"subsribe fail loca [{ref}] " + str(e)
                _LOGGER.error(err_msg)
                raise e
            except Exception as e:
                err_msg = f"subsribe fail locb [{ref}] " + str(e)
                _LOGGER.error(err_msg)
                raise S30Exception(err_msg, EC_SUBSCRIBE, 3)

    async def messagePump(self) -> None:
        # This method reads off the queue.
        # Observations:  the clientId is not passed in, they must be mapping the token to the clientId as part of negotiate
        # TODO: The long polling is not working, I have tried adjusting the long polling delay.  Long polling seems to work from the IOS App, not sure
        # what the difference is.   https://gist.github.com/rcarmo/3f0772f2cbe0612b699dcbb839edabeb
        # Returns True if messages were received, False if no messages were found, and throws S30Exception for errors
        #        _LOGGER.debug("Request Data - Enter")
        try:
            url = self.url_retrieve
            headers = {
                "Authorization": self.loginBearerToken,
                "User-Agent": USER_AGENT,
                "Accept": "*.*",
                #                'Accept' : '*/*',
                "Accept-Language": "en-US;q=1",
                "Accept-Encoding": "gzip, deflate"
                #                'Accept-Encoding' : 'gzip, deflate'
            }
            params = {
                "Direction": "Oldest-to-Newest",
                "MessageCount": "10",
                "StartTime": "1",
                "LongPollingTimeout": "15",
            }
            resp = await self.get(url, headers=headers, params=params)
            self.metrics.inc_receive_bytes(resp.content_length)
            if resp.status == 200:
                resp_txt = await resp.text()
                resp_json = json.loads(resp_txt)
                _LOGGER.debug(json.dumps(resp_json, indent=4))
                for message in resp_json["messages"]:
                    # TODO if this throws an exception we will miss other messages!
                    self.processMessage(message)
                if len(resp_json["messages"]) == 0:
                    return False
            elif resp.status == 204:
                #                _LOGGER.debug("message pump - 204 received - no data - continuing")
                return False
            else:
                err_msg = f"messagePump failed response http_code [{resp.status}]"
                # 502s happen periodically, so this is an expected error and will only be reported as INFO
                _LOGGER.info(err_msg)
                err_code = EC_HTTP_ERR
                if resp.status == 401:
                    err_code = EC_UNAUTHORIZED
                raise S30Exception(err_msg, err_code, resp.status)
            return True
        except S30Exception as e:
            raise e
        except Exception as e:
            err_msg = "messagePump Failed - Exception " + str(e)
            _LOGGER.error(err_msg)
            raise S30Exception(err_msg, EC_RETRIEVE, 2)

    def processMessage(self, message):
        self.metrics.inc_message_count()
        # LAN message and cloud message uses different capitalization.
        if "SenderID" in message:
            sysId = message["SenderID"]
        else:
            sysId = message["SenderId"]
        system = self.getSystem(sysId)
        if system != None:
            system.processMessage(message)
        else:
            _LOGGER.error("messagePump unknown SenderId/SystemId [" + str(sysId) + "]")

    # Messages seem to use unique GUIDS, here we create one
    def getNewMessageID(self):
        return str(uuid.uuid4())

    async def requestDataHelper(self, sysId: str, additionalParameters: str) -> None:
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

            payload = "{"
            payload += '"MessageType":"RequestData",'
            payload += '"SenderID":"' + self.getClientId() + '",'
            payload += '"MessageID":"' + self.getNewMessageID() + '",'
            payload += '"TargetID":"' + sysId + '",'
            payload += additionalParameters
            payload += "}"
            _LOGGER.debug("requestDataHelper Payload  [" + payload + "]")
            resp = await self.post(url, headers=headers, data=payload)

            if resp.status == 200:
                # TODO we should be inspecting the return body?
                if self._isLANConnection == True:
                    _LOGGER.debug(await resp.text())
                else:
                    _LOGGER.debug(json.dumps(await resp.json(), indent=4))
            else:
                txt = resp.text()
                err_msg = f"requestDataHelper failed response code [{resp.status}] text [{txt}]"
                _LOGGER.error(err_msg)
                raise S30Exception(err_msg, EC_REQUEST_DATA_HELPER, 1)
        except Exception as e:
            err_msg = "requestDataHelper - Exception " + str(e)
            _LOGGER.error(err_msg)
            raise S30Exception(err_msg, EC_REQUEST_DATA_HELPER, 2)

    def getSystems(self) -> List["lennox_system"]:
        return self._systemList

    def getSystem(self, sysId) -> "lennox_system":
        for system in self._systemList:
            if system.sysId == sysId:
                return system
        return None

    def getOrCreateSystem(self, sysId: str) -> "lennox_system":
        system = self.getSystem(sysId)
        if system != None:
            return system
        system = lennox_system(sysId)
        self._systemList.append(system)
        return system

    # When publishing data, app uses a GUID that counts up from 1.
    def getNextMessageId(self):
        self._publishMessageId += 1
        messageUUID = uuid.UUID(int=self._publishMessageId)
        return str(messageUUID)

    async def setModeHelper(
        self, sysId: str, modeTarget: str, mode: str, scheduleId: int
    ) -> None:
        _LOGGER.info(
            f"setMode modeTarget [{modeTarget}] mode [{mode}] scheduleId [{scheduleId}] sysId [{sysId}]"
        )
        try:
            if modeTarget not in HVAC_MODE_TARGETS:
                err_msg = f"setModeHelper - invalide mode target [{modeTarget}] requested, must be in [{HVAC_MODE_TARGETS}]"
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
            _LOGGER.error("setmode - S30Exception " + str(e))
            raise e
        except Exception as e:
            _LOGGER.error("setmode - Exception " + str(e))
            raise S30Exception(str(e), EC_SETMODE_HELPER, 1)
        _LOGGER.info(
            f"setModeHelper success[{mode}] scheduleId [{scheduleId}] sysId [{sysId}]"
        )

    async def publishMessageHelper(self, sysId: str, data: str) -> None:
        _LOGGER.debug(f"publishMessageHelper sysId [{sysId}] data [{data}]")
        try:
            body = "{"
            body += '"MessageType":"Command",'
            body += '"SenderID":"' + self.getClientId() + '",'
            body += '"MessageID":"' + self.getNextMessageId() + '",'
            body += '"TargetID":"' + sysId + '",'
            body += data
            body += "}"

            # See if we can parse the JSON, if we can't error will be thrown, no point in sending lennox bad data
            jsbody = json.loads(body)
            _LOGGER.debug(
                "publishMessageHelper message [" + json.dumps(jsbody, indent=4) + "]"
            )

            url = self.url_publish
            headers = {
                "Authorization": self.loginBearerToken,
                "User-Agent": USER_AGENT,
                "Accept": "*.*",
                "Content-Type": "application/json",
                "Accept-Language": "en-US;q=1",
                "Accept-Encoding": "gzip, deflate",
            }
            resp = await self.post(url, headers=headers, data=body)
            if resp.status != 200:
                txt = await resp.text()
                err_msg = f"publishMessageHelper failed response code [{resp.status}] text [{txt}]"
                _LOGGER.error(err_msg)
                raise S30Exception(err_msg, EC_PUBLISH_MESSAGE, 1)
            resp_txt = await resp.text()
            resp_json = json.loads(resp_txt)
            _LOGGER.debug(json.dumps(resp_json, indent=4))
        except Exception as e:
            _LOGGER.error("publishMessageHelper - Exception " + str(e))
            raise S30Exception(str(e), EC_PUBLISH_MESSAGE, 2)
        _LOGGER.info("publishMessageHelper success sysId [" + str(sysId) + "]")

    async def setHVACMode(self, sysId: str, mode: str, scheduleId: int) -> None:
        _LOGGER.info(
            f"setHVACMode mode [{mode}] scheduleId [{scheduleId}] sysId [{sysId}]"
        )
        if mode not in HVAC_MODES:
            err_msg = (
                f"setMode - invalide mode [{mode}] requested, must be in [{HVAC_MODES}]"
            )
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        await self.setModeHelper(sysId, "systemMode", mode, scheduleId)

    async def setFanMode(self, sysId: str, mode: str, scheduleId: int) -> None:
        _LOGGER.info(
            f"setFanMode mode [{mode}] scheduleId [{scheduleId}] sysId [{sysId}]"
        )
        if mode not in FAN_MODES:
            err_msg = f"setFanMode - invalide mode [{mode}] requested, must be in [{FAN_MODES}]"
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        await self.setModeHelper(sysId, "fanMode", mode, scheduleId)

    async def setManualAwayMode(self, sysId: str, mode: bool) -> None:
        _LOGGER.info(f"setManualAwayMode mode [{mode}] sysId [{sysId}]")
        str = None
        if mode == True:
            str = "true"
        if mode == False:
            str = "false"
        if str is None:
            err_msg = f"setManualAwayMode - invalid mode [{mode}] requested, must be True or False"
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        data = '"Data":{"occupancy":{"manualAway":' + str + "}" + "}"
        await self.publishMessageHelper(sysId, data)


class lennox_system(object):
    def __init__(self, sysId: str):
        self.sysId: str = sysId
        self.api: s30api_async = None
        self.idx: int = None
        self.home: lennox_home = None
        self._zoneList: List["lennox_zone"] = []
        self._schedules: List[lennox_schedule] = []
        self._callbacks = []
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
        self.manualAwayMode = None
        self.serialNumber: str = None
        self.single_setpoint_mode: bool = None
        self.temperatureUnit: str = None
        self.dehumidificationMode = None
        self.indoorUnitType = None
        self.productType = None
        self.outdoorUnitType = None
        self.humidifierType = None
        self.dehumidifierType = None
        self.outdoorTemperatureC = None
        self.outdoorTemperature = None
        self.numberOfZones = None
        self.sysUpTime = None
        self.diagLevel = None
        self.softwareVersion = None
        self.diagnosticPaths = {}
        self.diagInverterInputVoltage = None
        self.diagInverterInputCurrent = None
        self._dirty = False
        self._dirtyList = []
        _LOGGER.info(f"Creating lennox_system sysId [{self.sysId}]")

    def update(self, api: s30api_async, home: lennox_home, idx: int):
        self.api = api
        self.idx = idx
        self.home = home
        _LOGGER.info(f"Update lennox_system idx [{self.idx}] sysId [{self.sysId}]")

    def processMessage(self, message) -> None:
        try:
            if "Data" in message:
                data = message["Data"]
                if "system" in data:
                    self.processSystemMessage(data["system"])
                if "zones" in data:
                    self.processZonesMessage(data["zones"])
                if "schedules" in data:
                    self.processSchedules(data["schedules"])
                if "occupancy" in data:
                    self.processOccupancy(data["occupancy"])
                if "devices" in data:
                    self.processDevices(data["devices"])
                if "equipments" in data:
                    self.processEquipments(data["equipments"])
                _LOGGER.debug(
                    f"processMessage complete system id [{self.sysId}] dirty [{self._dirty}] dirtyList [{self._dirtyList}]"
                )
                self.executeOnUpdateCallbacks()
        except Exception as e:
            _LOGGER.error("processMessage - Exception " + str(e))
            raise S30Exception(str(e), EC_PROCESS_MESSAGE, 1)

    def getOrCreateSchedule(self, id):
        schedule = self.getSchedule(id)
        if schedule != None:
            return schedule
        schedule = lennox_schedule(id)
        self._schedules.append(schedule)
        return schedule

    def getSchedule(self, id):
        for schedule in self._schedules:
            if schedule.id == id:
                return schedule
        return None

    def getSchedules(self):
        return self._schedules

    def processSchedules(self, schedules):
        try:
            for schedule in schedules:
                self._dirty = True
                self._dirtyList.append("schedules")
                id = schedule["id"]
                if "schedule" in schedule:
                    lschedule = self.getSchedule(id)
                    if lschedule is None and "name" in schedule["schedule"]:
                        lschedule = self.getOrCreateSchedule(id)
                    if lschedule != None:
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
                            zone_id = id - LENNOX_MANUAL_MODE_SCHEDULE_START_INDEX
                            period = schedule["schedule"]["periods"][0]["period"]
                            zone: lennox_zone = self.getZone(zone_id)
                            if zone.isZoneManualMode():
                                zone.processPeriodMessage(period)
                                zone.executeOnUpdateCallbacks()
        except Exception as e:
            _LOGGER.error("processSchedules - failed " + str(e))
            raise S30Exception(str(e), EC_PROCESS_MESSAGE, 2)

    def registerOnUpdateCallback(self, callbackfunc, match=None):
        self._callbacks.append({"func": callbackfunc, "match": match})

    def executeOnUpdateCallbacks(self):
        if self._dirty == True:
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
                    if matches == True:
                        callbackfunc()
                except Exception as e:
                    # Log and eat this exception so we can process other callbacks
                    _LOGGER.error("executeOnUpdateCallback - failed " + str(e))
        self._dirty = False
        self._dirtyList = []

    def attr_updater(self, set, attr: str, propertyName: str = None) -> bool:
        if attr in set:
            attr_val = set[attr]
            if propertyName is None:
                propertyName = attr
            if getattr(self, propertyName) != attr_val:
                setattr(self, propertyName, attr_val)
                self._dirty = True
                self._dirtyList.append(propertyName)
                _LOGGER.debug(
                    f"update_attr: system Id [{self.sysId}] attr [{propertyName}]"
                )
                return True
        return False

    def processSystemMessage(self, message):
        try:
            if "config" in message:
                config = message["config"]
                self.attr_updater(config, "temperatureUnit")
                self.attr_updater(config, "dehumidificationMode")
                self.attr_updater(config, "name")
                self.attr_updater(config, "allergenDefender")
                self.attr_updater(config, "ventilationMode")
                if "options" in config:
                    options = config["options"]
                    self.attr_updater(options, "indoorUnitType")
                    self.attr_updater(options, "productType")
                    self.attr_updater(options, "outdoorUnitType")
                    self.attr_updater(options, "humidifierType")
                    self.attr_updater(options, "dehumidifierType")
                    if "ventilation" in options:
                        ventilation = options["ventilation"]
                        self.attr_updater(
                            ventilation, "unitType", "ventilationUnitType"
                        )
                        self.attr_updater(
                            ventilation, "controlMode", "ventilationControlMode"
                        )

            if "status" in message:
                status = message["status"]
                self.attr_updater(status, "outdoorTemperature")
                self.attr_updater(status, "outdoorTemperatureC")
                self.attr_updater(status, "diagLevel")
                self.attr_updater(status, "diagRuntime")
                self.attr_updater(status, "diagPoweredHours")
                self.attr_updater(status, "numberOfZones")
                self.attr_updater(status, "diagVentilationRuntime")
                self.attr_updater(status, "ventilationRemainingTime")
                self.attr_updater(status, "ventilatingUntilTime")
                self.attr_updater(status, "feelsLikeMode")

            if "time" in message:
                time = message["time"]
                old = self.sysUpTime
                self.attr_updater(time, "sysUpTime")
                # When uptime become less than what we recorded, it means the S30 has restarted
                if old is not None and old > self.sysUpTime:
                    _LOGGER.warning(
                        f"S30 has rebooted sysId [{self.sysId}] old uptime [{old}] new uptime [{self.sysUpTime}]"
                    )

        except Exception as e:
            _LOGGER.error("processSystemMessage - Exception " + str(e))
            raise S30Exception(str(e), EC_PROCESS_MESSAGE, 3)
        return

    def processDevices(self, message):
        try:
            for device in message:
                if "device" in device:
                    if device.get("device", {}).get("deviceType", {}) == 500:
                        for feature in device["device"].get("features", []):
                            if feature.get("feature", {}).get("fid") == 9:
                                self.serialNumber = feature["feature"]["values"][0][
                                    "value"
                                ]
                                self._dirty = True
                                self._dirtyList.append("serialNumber")
                            if feature.get("feature", {}).get("fid") == 11:
                                self.softwareVersion = feature["feature"]["values"][0][
                                    "value"
                                ]
                                self._dirty = True
                                self._dirtyList.append("softwareVersion")

        except Exception as e:
            _LOGGER.error("processDevices - Exception " + str(e))
            raise S30Exception(str(e), EC_PROCESS_MESSAGE, 1)

    def processEquipments(self, message) -> bool:
        update = False
        try:
            for equipment in message:
                equipment_id = equipment.get("id")
                for parameter in equipment.get("equipment", {}).get("parameters", []):
                    # 525 is the parameter id for split-setpoint
                    if parameter.get("parameter", {}).get("pid") == 525:
                        value = parameter["parameter"]["value"]
                        if value == 1 or value == "1":
                            self.single_setpoint_mode = True
                        else:
                            self.single_setpoint_mode = False
                        self._dirty = True
                        self._dirtyList.append("single_setpoint_mode")
                for diagnostic in equipment.get("equipment", {}).get("diagnostics", []):
                    # the diagnostic values sometimes don't have names
                    # so remember where we found important keys
                    diagnostic_id = diagnostic.get("id")
                    diagnostic_data = diagnostic.get("diagnostic", {})
                    diagnostic_name = diagnostic_data.get("name")
                    diagnostic_path = (
                        f"equipment_{equipment_id}:diagnostic_{diagnostic_id}"
                    )
                    if diagnostic_name == "Inverter Input Voltage":
                        self.diagnosticPaths[
                            diagnostic_path
                        ] = "diagInverterInputVoltage"
                    if diagnostic_name == "Inverter Input Current":
                        self.diagnosticPaths[
                            diagnostic_path
                        ] = "diagInverterInputCurrent"

                    if diagnostic_path in self.diagnosticPaths:
                        self.attr_updater(
                            diagnostic_data,
                            "value",
                            self.diagnosticPaths[diagnostic_path],
                        )
        except Exception as e:
            _LOGGER.error("processDevices - Exception " + str(e))
            raise S30Exception(str(e), EC_PROCESS_MESSAGE, 1)
        return update

    def unique_id(self) -> str:
        # This returns a unique identifier.  When connected ot the cloud we use the sysid which is a GUID; when
        # connected to the LAN the sysid is alway "LCC" - which is not unique - so in this case we use the device serial number.
        if self.api._isLANConnection == True:
            return self.serialNumber
        return self.sysId

    def config_complete(self) -> bool:
        if self.name is None:
            return False
        if self.api._isLANConnection and self.serialNumber is None:
            return False
        return True

    def processOccupancy(self, message):
        try:
            self.attr_updater(message, "manualAway", "manualAwayMode")

        except Exception as e:
            _LOGGER.error("processOccupancy - Exception " + str(e))
            raise S30Exception(str(e), EC_PROCESS_MESSAGE, 1)

    def get_manual_away_mode(self):
        return self.manualAwayMode

    async def set_manual_away_mode(self, mode: bool) -> None:
        await self.api.setManualAwayMode(self.sysId, mode)

    def getZone(self, id):
        for zone in self._zoneList:
            if zone.id == id:
                return zone
        return None

    def getZones(self):
        return self._zoneList

    def getZoneList(self):
        return self._zoneList

    async def setHVACMode(self, mode, scheduleId):
        return await self.api.setHVACMode(self.sysId, mode, scheduleId)

    async def setFanMode(self, mode, scheduleId):
        return await self.api.setFanMode(self.sysId, mode, scheduleId)

    def convertFtoC(self, tempF: float) -> float:
        # Lennox allows Celsius to be specified only in 0.5 degree increments
        float_TempC = (float(tempF) - 32.0) * (5.0 / 9.0)
        return self.celsius_round(float_TempC)

    def convertCtoF(self, tempC: float) -> int:
        # Lennox allows Faren to be specified only in 1 degree increments
        float_TempF = (float(tempC) * (9.0 / 5.0)) + 32.0
        return self.faren_round(float_TempF)

    def celsius_round(self, c: float) -> float:
        ### Round to nearest 0.5
        return round(c * 2.0) / 2.0

    def faren_round(self, c: float) -> int:
        ### Round to nearest whole number
        return round(c)

    async def setSchedule(self, zoneId: int, scheduleId: int) -> None:
        data = (
            '"Data":{"zones":[{"config":{"scheduleId":'
            + str(scheduleId)
            + '},"id":'
            + str(zoneId)
            + "}]}"
        )
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
    ) -> None:
        ### No data validation in this routine, make sure you know what you are setting.
        ### Use the zone.perform_setpoint for error checking
        command = {
            "schedules": [
                {"schedule": {"periods": [{"id": 0, "period": {}}]}, "id": scheduleId}
            ]
        }

        period = command["schedules"][0]["schedule"]["periods"][0]["period"]
        if hsp != None:
            period["hsp"] = int(hsp)
        if cspC != None:
            period["cspC"] = float(cspC)
        if hspC != None:
            period["hspC"] = float(hspC)
        if csp != None:
            period["csp"] = int(csp)
        if sp != None:
            period["sp"] = int(sp)
        if spC != None:
            period["spC"] = float(spC)

        data = '"Data":' + json.dumps(command).replace(" ", "")
        await self.api.publishMessageHelper(self.sysId, data)

    def getOrCreateZone(self, id):
        zone = self.getZone(id)
        if zone != None:
            return zone
        zone = lennox_zone(self, id)
        self._zoneList.append(zone)
        return zone

    def processZonesMessage(self, message):
        try:
            for zone in message:
                id = zone["id"]
                lzone = self.getOrCreateZone(id)
                lzone.processMessage(zone)
        except Exception as e:
            err_msg = "processZonesMessage - Exception " + str(e)
            _LOGGER.error(err_msg)
            raise S30Exception(err_msg, EC_PROCESS_MESSAGE, 1)

    def supports_ventilation(self) -> bool:
        return self.ventilationUnitType == "ventilator"

    async def ventilation_on(self) -> None:
        _LOGGER.debug(f"ventilation_on sysid [{self.sysId}]")
        if self.supports_ventilation() == False:
            err_msg = f"ventilation_on - attempting to turn ventilation on for non-supported equipment ventilatorUnitType [{self.ventilationUnitType}]"
            _LOGGER.error(err_msg)
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        data = '"Data":{"system":{"config":{"ventilationMode":"on"} } }'
        await self.api.publishMessageHelper(self.sysId, data)

    async def ventilation_off(self) -> None:
        _LOGGER.debug(f"ventilation_off sysid [{self.sysId}] ")
        if self.ventilationUnitType != "ventilator":
            err_msg = f"ventilation_off - attempting to turn ventilation off for non-supported equipment ventilatorUnitType [{self.ventilationUnitType}]"
            _LOGGER.error(err_msg)
            raise S30Exception(err_msg, EC_BAD_PARAMETERS, 1)
        data = '"Data":{"system":{"config":{"ventilationMode":"off"} } }'
        await self.api.publishMessageHelper(self.sysId, data)

    async def allergenDefender_on(self) -> None:
        _LOGGER.debug(f"allergenDefender_on sysid [{self.sysId}] ")
        data = '"Data":{"system":{"config":{"allergenDefender":true} } }'
        await self.api.publishMessageHelper(self.sysId, data)

    async def allergenDefender_off(self) -> None:
        _LOGGER.debug(f"allergenDefender_on sysid [{self.sysId}] ")
        data = '"Data":{"system":{"config":{"allergenDefender":false} } }'
        await self.api.publishMessageHelper(self.sysId, data)


class lennox_zone(object):
    def __init__(self, system, id):
        self._callbacks = []

        self.temperature = None
        self.temperatureC = None
        self.humidity = None
        self.systemMode = None
        self.tempOperation = None

        self.fanMode = None  # The requested fanMode - on, auto, circulate
        self.fan = (
            None  # The current state of fan,  False = not running, True = running
        )
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
        self.maxDehumSp = None
        self.minDehumSp = None

        self.scheduleId = None
        self.scheduleHold = None

        # PERIOD
        self.systemMode = None
        self.fanMode = None
        self.humidityMode = None
        self.csp = None
        self.cspC = None
        self.hsp = None
        self.hspC = None
        self.desp = None
        self.sp = None
        self.spC = None
        self.husp = None
        self.startTime = None
        self.overrideActive = None

        self.id: int = id
        self.name: str = None
        self._system: lennox_system = system
        self._dirty = False
        self._dirtyList = []

        _LOGGER.info(f"Creating lennox_zone id [{self.id}]")

    def registerOnUpdateCallback(self, callbackfunc, match=None):
        self._callbacks.append({"func": callbackfunc, "match": match})

    def executeOnUpdateCallbacks(self):
        if self._dirty == True:
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
                    if matches == True:
                        callbackfunc()
                except Exception as e:
                    # Log and eat this exception so we can process other callbacks
                    _LOGGER.error("executeOnUpdateCallback - failed " + str(e))
        self._dirty = False
        self._dirtyList = []

    def attr_updater(self, set, attr: str) -> bool:
        if attr in set:
            attr_val = set[attr]
            if getattr(self, attr) != attr_val:
                setattr(self, attr, attr_val)
                self._dirty = True
                self._dirtyList.append(attr)
                _LOGGER.debug(f"update_attr: zone Id [{self.id}] attr [{attr}]")
                return True
        return False

    def processMessage(self, zoneMessage) -> bool:
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
            self.attr_updater(config, "maxHumSp")
            self.attr_updater(config, "emergencyHeatingOption")
            self.attr_updater(config, "dehumidificationOption")
            self.attr_updater(config, "maxDehumSp")
            self.attr_updater(config, "minDehumSp")
            self.attr_updater(config, "scheduleId")
            self.attr_updater(config, "scheduleHold")
            if "scheduleHold" in config:
                scheduleHold = config["scheduleHold"]
                found = False
                if "scheduleId" in scheduleHold:
                    if scheduleHold["scheduleId"] == self.getOverrideScheduleId():
                        if scheduleHold["enabled"] == True:
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
            self.attr_updater(status, "humidity")
            self.attr_updater(status, "tempOperation")
            self.attr_updater(status, "humOperation")
            self.attr_updater(status, "allergenDefender")
            self.attr_updater(status, "damper")
            self.attr_updater(status, "fan")
            self.attr_updater(status, "demand")
            self.attr_updater(status, "ventilation")

            if "period" in status:
                period = status["period"]
                self.processPeriodMessage(period)
        _LOGGER.debug(
            f"processMessage complete lennox_zone id [{self.id}] dirty [{self._dirty}] dirtyList [{self._dirtyList}]"
        )
        self.executeOnUpdateCallbacks()
        return self._dirty

    def processPeriodMessage(self, period):
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
        return self.temperature != None

    def getTemperatureC(self):
        return self.temperatureC

    def getHumidity(self):
        return self.humidity

    def getSystemMode(self):
        return self.systemMode

    def getFanMode(self):
        return self.fanMode

    def getHumidityMode(self):
        return self.humidityMode

    def getCoolSP(self):
        return self.csp

    def getHeatSP(self):
        return self.hsp

    def getTargetTemperatureF(self):
        if self.systemMode == LENNOX_HVAC_OFF:
            return None
        # In single setpoint mode there is only one target.
        if self._system.single_setpoint_mode == True:
            return self.sp

        if self.systemMode == LENNOX_HVAC_COOL:
            return self.csp

        if self.systemMode == LENNOX_HVAC_HEAT:
            return self.hsp
        # Calling this method in this mode is probably an error TODO
        if self.systemMode == LENNOX_HVAC_HEAT_COOL:
            return None
        return None

    def getTargetTemperatureC(self):
        if self.systemMode == LENNOX_HVAC_OFF:
            return None
        # In single setpoint mode there is only one target.
        if self._system.single_setpoint_mode == True:
            return self.spC

        if self.heatingOption == True and self.coolingOption == True:
            if self.systemMode == "cool":
                return self.cspC
            if self.systemMode == "heat":
                return self.hspC
        elif self.heatingOption == True:
            return self.hspC
        elif self.coolingOption == True:
            return self.cspC
        else:
            return None

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

    def validate_setpoints(
        self, r_hsp=None, r_hspC=None, r_csp=None, r_cspC=None, r_sp=None, r_spC=None
    ):

        if (
            r_sp != None or r_spC != None
        ) and self._system.single_setpoint_mode == False:
            raise S30Exception(
                f"validate_setpoints: r_sp or r_spC can only be specified when system is in single setpoint mode",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_sp == None and r_spC == None and self._system.single_setpoint_mode == True:
            raise S30Exception(
                f"validate_setpoints: r_sp or r_spC must be specified when system is in single setpoint mode",
                EC_BAD_PARAMETERS,
                2,
            )

        if (
            r_hsp != None or r_hspC != None or r_csp != None or r_cspC != None
        ) and self._system.single_setpoint_mode == True:
            raise S30Exception(
                f"validate_setpoints: r_hsp, r_hspC, r_csp and r_cspC must not be specified when system is in single setpoint mode",
                EC_BAD_PARAMETERS,
                2,
            )

        if (
            r_hsp == None
            and r_hspC == None
            and r_csp == None
            and r_cspC == None
            and self._system.single_setpoint_mode == False
        ):
            raise S30Exception(
                f"validate_setpoints: r_hsp, r_hspC, r_csp or r_cspC must be specified when system is in single setpoint mode",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_csp != None and r_csp < self.minCsp:
            raise S30Exception(
                f"setHeatCoolSPF r_csp [{r_csp}] must be greater than minCsp [{self.minCsp}]",
                EC_BAD_PARAMETERS,
                1,
            )
        if r_csp != None and r_csp > self.maxCsp:
            raise S30Exception(
                f"setHeatCoolSPF r_csp [{r_csp}] must be less than maxCsp [{self.maxCsp}]",
                EC_BAD_PARAMETERS,
                2,
            )
        if r_hsp != None and r_hsp < self.minHsp:
            raise S30Exception(
                f"setHeatCoolSPF r_hsp [{r_hsp}] must be greater than minCsp [{self.minHsp}]",
                EC_BAD_PARAMETERS,
                3,
            )
        if r_hsp != None and r_hsp > self.maxHsp:
            raise S30Exception(
                f"setHeatCoolSPF r_hsp [{r_hsp}] must be less than maxHsp [{self.maxHsp}]",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_cspC != None and r_cspC < self.minCspC:
            raise S30Exception(
                f"setHeatCoolSPC r_cspC [{r_cspC}] must be greater than minCspC [{self.minCspC}]",
                EC_BAD_PARAMETERS,
                1,
            )
        if r_cspC != None and r_cspC > self.maxCspC:
            raise S30Exception(
                f"setHeatCoolSPC r_cspC [{r_cspC}] must be less than maxCspC [{self.maxCspC}]",
                EC_BAD_PARAMETERS,
                2,
            )
        if r_hspC != None and r_hspC < self.minHspC:
            raise S30Exception(
                f"setHeatCoolSPC r_hspC [{r_hspC}] must be greater than minCspC [{self.minHspC}]",
                EC_BAD_PARAMETERS,
                3,
            )
        if r_hspC != None and r_hspC > self.maxHspC:
            raise S30Exception(
                f"setHeatCoolSPC r_hspC [{r_hspC}] must be less than maxHspC [{self.maxHspC}]",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_sp != None and (r_sp > self.maxCsp or r_sp < self.minHsp):
            raise S30Exception(
                f"setHeatCoolSPC r_sp [{r_sp}] must be between [{self.minHsp}] and [{self.maxHsp}]",
                EC_BAD_PARAMETERS,
                2,
            )

        if r_spC != None and (r_spC > self.maxCspC or r_spC < self.minHspC):
            raise S30Exception(
                f"setHeatCoolSPC r_spC [{r_spC}] must be between [{self.minHspC}] and [{self.maxHspC}]",
                EC_BAD_PARAMETERS,
                2,
            )

    async def perform_setpoint(
        self, r_hsp=None, r_hspC=None, r_csp=None, r_cspC=None, r_sp=None, r_spC=None
    ):
        _LOGGER.debug(
            f"lennox_zone:setpoint_helper  id [{self.id}] hsp [{r_hsp}] hspC [{r_hspC}] csp [{r_csp}] cspC [{r_cspC}] sp [{r_sp}] spC [{r_spC}]"
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
        if self._system.single_setpoint_mode == False:
            if r_hsp != None:
                hsp = self._system.faren_round(r_hsp)
            else:
                if r_hspC != None:
                    hsp = self._system.convertCtoF(r_hspC)
                else:
                    hsp = self.hsp

            if r_hspC != None:
                hspC = self._system.celsius_round(r_hspC)
            else:
                if r_hsp != None:
                    hspC = self._system.convertFtoC(r_hsp)
                else:
                    hspC = self.hspC

            if r_csp != None:
                csp = self._system.faren_round(r_csp)
            else:
                if r_cspC != None:
                    csp = self._system.convertCtoF(r_cspC)
                else:
                    csp = self.csp

            if r_cspC != None:
                cspC = self._system.celsius_round(r_cspC)
            else:
                if r_csp != None:
                    cspC = self._system.convertFtoC(r_csp)
                else:
                    cspC = self.cspC
        else:
            if r_sp != None:
                sp = self._system.faren_round(r_sp)
            elif r_spC != None:
                sp = self._system.convertCtoF(r_spC)

            if r_spC != None:
                spC = self._system.celsius_round(r_spC)
            elif r_sp != None:
                spC = self._system.convertFtoC(r_sp)

        # If the zone is in manual mode, the temperature can just be set.
        if self.isZoneManualMode() == True:
            _LOGGER.info(
                f"lennox_zone:setHeatCoolSPF zone already in manual mode id [{self.id}]"
            )
            await self._system.perform_schedule_setpoint(
                zoneId=self.id,
                scheduleId=self.getManualModeScheduleId(),
                hsp=hsp,
                hspC=hspC,
                csp=csp,
                cspC=cspC,
                sp=sp,
                spC=spC,
            )
            return

        # The zone is following a schedule.  So first check if it's already running
        # the override schedule and we can just set the temperature
        if self.isZoneOveride() == True:
            _LOGGER.info(
                f"lennox_zone:setHeatCoolSPF zone already in overridemode id [{self.id}]"
            )
            await self._system.perform_schedule_setpoint(
                zoneId=self.id,
                scheduleId=self.getOverrideScheduleId(),
                hsp=hsp,
                hspC=hspC,
                csp=csp,
                cspC=cspC,
                sp=sp,
                spC=spC,
            )
            return

        # Otherwise, we are following a schedule and need to switch into manual over-ride
        # Copy all the data over from the current executing period
        _LOGGER.info(
            _LOGGER.info(
                f"lennox_zone:setHeatCoolSPF creating zone override [{self.id}]"
            )
        )

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

        data = '"Data":{"schedules":[{"schedule":{"periods":[{"id":0,"period":'
        data += '{"desp":' + str(self.desp) + ","
        data += '"hsp":' + str(hsp) + ","
        data += '"cspC":' + str(cspC) + ","
        data += '"sp":' + str(sp) + ","
        data += '"husp":' + str(self.husp) + ","
        data += '"humidityMode":"' + str(self.humidityMode) + '",'
        data += '"systemMode":"' + str(self.systemMode) + '",'
        data += '"spC":' + str(spC) + ","
        data += '"hspC":' + str(hspC) + ","
        data += '"csp":' + str(csp) + ","
        data += '"startTime":' + str(self.startTime) + ","
        data += '"fanMode":"' + self.fanMode + '"}'
        data += '}]},"id":' + str(self.getOverrideScheduleId()) + "}]}"

        try:
            await self._system.api.publishMessageHelper(self._system.sysId, data)
        except S30Exception as e:
            _LOGGER.error(
                "lennox_zone:setHeatCoolSPF failed to create override - zone ["
                + str(self.id)
                + "] hsp ["
                + str(r_hsp)
                + "] csp ["
                + str(r_csp)
                + "]"
            )
            raise e

        _LOGGER.info(
            "lennox_zone:setHeatCoolSPF placing zone in override hold - zone ["
            + str(self.id)
            + "] hsp ["
            + str(r_hsp)
            + "] csp ["
            + str(r_csp)
            + "]"
        )

        try:
            await self.setScheduleHold(True)
        except S30Exception as e:
            _LOGGER.error(
                "lennox_zone:setHeatCoolSPF failed to create schedule hold - zone ["
                + str(self.id)
                + "] hsp ["
                + str(r_hsp)
                + "] csp ["
                + str(r_csp)
                + "]"
            )
            raise e

    async def setScheduleHold(self, hold: bool) -> bool:
        if hold == True:
            strHold = "true"
        else:
            strHold = "false"

        _LOGGER.info(
            "lennox_zone:setScheduleHold zone ["
            + str(self.id)
            + "] hold ["
            + str(strHold)
            + "]"
        )
        # Add a schedule hold to the zone, for now all hold will expire on next period
        data = '"Data":{"zones":[{"config":{"scheduleHold":'
        data += '{"scheduleId":' + str(self.getOverrideScheduleId()) + ","
        data += '"exceptionType":"hold","enabled":' + strHold + ","
        data += '"expiresOn":"0","expirationMode":"nextPeriod"}'
        data += '},"id":' + str(self.id) + "}]}"
        try:
            await self._system.api.publishMessageHelper(self._system.sysId, data)
        except S30Exception as e:
            _LOGGER.error(
                "lennox_zone:setScheduleHold failed zone ["
                + str(self.id)
                + "] hold ["
                + str(strHold)
                + "]"
            )
            raise e

    async def setManualMode(self) -> None:
        await self._system.setSchedule(self.id, self.getManualModeScheduleId())

    async def setSchedule(self, scheduleName: str) -> None:
        scheduleId = None
        for schedule in self._system.getSchedules():
            if schedule.name == scheduleName:
                scheduleId = schedule.id
                break

        if scheduleId == None:
            err_msg = (
                f"setSchedule - unknown schedule [{scheduleName}] zone [{self.name}]"
            )
            _LOGGER.error(err_msg)
            raise S30Exception(err_msg, EC_NO_SCHEDULE, 1)

        await self._system.setSchedule(self.id, scheduleId)

    async def setFanMode(self, fan_mode: str) -> None:
        if self.isZoneManualMode() == True:
            await self._system.setFanMode(fan_mode, self.getManualModeScheduleId())
            return

        if self.isZoneOveride() == False:
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

            await self._system.api.publishMessageHelper(self._system.sysId, data)
            await self.setScheduleHold(True)
        await self._system.setFanMode(fan_mode, self.getOverrideScheduleId())

    async def setHVACMode(self, hvac_mode: str) -> None:
        # We want to be careful passing modes to the controller that it does not support.  We don't want to brick the controller.
        if hvac_mode == LENNOX_HVAC_COOL:
            if self.coolingOption == False:
                raise S30Exception(
                    f"setHvacMode - invalid hvac mode - zone [{self.id}]  does not support [{hvac_mode}]",
                    EC_BAD_PARAMETERS,
                    1,
                )
        elif hvac_mode == LENNOX_HVAC_HEAT:
            if self.heatingOption == False:
                raise S30Exception(
                    f"setHvacMode - invalid hvac mode - zone [{self.id}]  does not support [{hvac_mode}]",
                    EC_BAD_PARAMETERS,
                    2,
                )
        elif hvac_mode == LENNOX_HVAC_HEAT_COOL:
            if self.heatingOption == False or self.coolingOption == False:
                raise S30Exception(
                    f"setHvacMode - invalid hvac mode - zone [{self.id}]  does not support [{hvac_mode}]",
                    EC_BAD_PARAMETERS,
                    3,
                )
        elif hvac_mode == LENNOX_HVAC_OFF:
            pass
        else:
            raise S30Exception(
                f"setHvacMode - invalidate hvac mode - zone [{self.id}]  does not recognize [{hvac_mode}]",
                EC_BAD_PARAMETERS,
                4,
            )

        if self.isZoneManualMode() == False:
            await self._system.setSchedule(self.id, self.getManualModeScheduleId())
        await self._system.setHVACMode(hvac_mode, self.getManualModeScheduleId())
