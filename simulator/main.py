import json
import os
import asyncio

from aiohttp import web
from aiohttp.web_request import Request

from lennoxs30api.s30api_async import LENNOX_STATUS_GOOD, LENNOX_STATUS_NOT_AVAILABLE


class AppConnection(object):
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.queue = []


class Simulator(object):
    def __init__(self, configfile: str):
        self.configfile = configfile
        self.appList = {}
        self.zoneSimRunning = False
        self.outdoorTempSimRunning = False
        self.diagSimRunning = False
        self.siblingSimRunning = False
        self.outdoorTempSim = False
        self.heatpumpLockoutSim = None
        self.zoneSim = False
        self.siblingSim = False
        self.diagSim = False
        self.equipment = None
        self.productType = None
        self.wifiSim = False
        self.wifiSimRunning = False
        with open(configfile) as f:
            self.config_data = json.load(f)
            if "outdoorTempSim" in self.config_data:
                self.outdoorTempSim = self.config_data["outdoorTempSim"]
            if "zoneSim" in self.config_data:
                self.zoneSim = self.config_data["zoneSim"]
            if "siblingSim" in self.config_data:
                self.siblingSim = self.config_data["siblingSim"]
            if "diagSim" in self.config_data:
                self.diagSim = self.config_data["diagSim"]
            if "heatpumpLockoutSim" in self.config_data:
                self.heatpumpLockoutSim = self.config_data["heatpumpLockoutSim"]
            if "productType" in self.config_data:
                self.productType = self.config_data["productType"]
            if "wifiSim" in self.config_data:
                self.wifiSim = self.config_data["wifiSim"]

    async def heatpumpLockoutSimulator(self):
        if self.heatpumpLockoutSim is None:
            return
        active: bool = False
        while True:
            message = self.loadfile(self.heatpumpLockoutSim)
            await asyncio.sleep(15.0)
            message["Data"]["alerts"]["active"][0]["alert"]["isStillActive"] = active
            message["Data"]["alerts"]["active"][1]["alert"]["isStillActive"] = active
            if not active:
                message["Data"]["alerts"]["meta"]["numActiveAlerts"] = 0
            else:
                message["Data"]["alerts"]["meta"]["numActiveAlerts"] = 2

            active = not active
            for _, appObject in self.appList.items():
                appObject.queue.append(message)

    async def outdoorTempSimulator(self):
        if self.outdoorTempSim == False or self.outdoorTempSimRunning == True:
            return
        self.outdoorTempSimRunning = True
        await asyncio.sleep(15.0)
        temperature = 10
        while True:
            if temperature == 100:
                status = LENNOX_STATUS_NOT_AVAILABLE
            else:
                status = LENNOX_STATUS_GOOD
            message = {
                "MessageId": "637594500464320381|95a6cacebd94459dbe7538161628bdb6",
                "SenderId": "LCC",
                "TargetID": "mapp079372367644467046827098_myemail@email.com",
                "MessageType": "PropertyChange",
                "Data": {
                    "system": {
                        "status": {
                            "outdoorTemperatureStatus": status,
                            "outdoorTemperature": temperature,
                            "outdoorTemperatureC": 13.5,
                        },
                        "publisher": {"publisherName": "lcc"},
                    }
                },
            }
            for appName, appObject in self.appList.items():
                appObject.queue.append(message)
            if temperature == 100:
                temperature = 10
            else:
                temperature = temperature + 10
            await asyncio.sleep(5.0)

    async def wifiSimulator(self):
        if self.wifiSim is False or self.wifiSimRunning:
            return
        self.wifiSimRunning = True
        message = self.loadfile("tests/messages/wifi_interface_status.json")

        await asyncio.sleep(15.0)
        value: int = -100
        while True:
            message["Data"]["interfaces"][0]["Info"]["status"]["rssi"] = str(value)
            value += 1
            if value > 0:
                value = 100

            for _, appObject in self.appList.items():
                appObject.queue.append(message)
            await asyncio.sleep(1.0)


    async def diagSimulator(self):
        if self.diagSim == False or self.diagSimRunning == True:
            return
        self.diagSimRunning = True
        message = self.loadfile("tests/messages/equipments_diag_update.json")

        await asyncio.sleep(15.0)
        value: float = 0.0
        while True:
            message["Data"]["equipments"][0]["equipment"]["diagnostics"][1]["diagnostic"]["value"] = str(value)
            value += 1.2
            if value > 300:
                value = 0.0

            if message["Data"]["equipments"][0]["equipment"]["diagnostics"][0]["diagnostic"]["value"] == "Yes":
                message["Data"]["equipments"][0]["equipment"]["diagnostics"][0]["diagnostic"]["value"] = "No"
            else:
                message["Data"]["equipments"][0]["equipment"]["diagnostics"][0]["diagnostic"]["value"] = "Yes"

            for appName, appObject in self.appList.items():
                appObject.queue.append(message)
            await asyncio.sleep(1.0)

    async def parameterUpdate(self, pu: dict) -> None:
        await asyncio.sleep(8.0)
        message = {
            "MessageId": 0,
            "SenderID": "LCC",
            "TargetID": "ha_dev",
            "MessageType": "PropertyChange",
            "Data": {
                "system": {
                    "status": {"rsbusMode": "commissioning"},
                    "publisher": {"publisherName": "lcc"},
                }
            },
        }
        for appName, appObject in self.appList.items():
            appObject.queue.append(message)
        await asyncio.sleep(0.5)
        for eq in self.equipment["Data"]["equipments"]:
            equip = eq["equipment"]
            if pu["et"] == equip["equipType"]:
                message = {
                    "MessageId": 0,
                    "SenderID": "LCC",
                    "TargetID": "ha_dev",
                    "MessageType": "PropertyChange",
                    "Data": {
                        "equipments": [
                            {
                                "publisher": {"publisherName": "lcc"},
                                "equipment": {
                                    "parameters": [
                                        {
                                            "parameter": {
                                                "pid": pu["pid"],
                                                "enabled": True,
                                                "value": pu["value"],
                                            },
                                        }
                                    ],
                                    "equipType": pu["et"],
                                },
                                "id": eq["id"],
                            }
                        ]
                    },
                }
                for appName, appObject in self.appList.items():
                    appObject.queue.append(message)
                break

    async def zoneSimulator(self):
        if self.zoneSim == False or self.zoneSimRunning == True:
            return
        self.zoneSimRunning = True
        await asyncio.sleep(15.0)
        temperature = 10
        humidity = 50
        while True:
            if temperature == 100:
                status = LENNOX_STATUS_NOT_AVAILABLE
            else:
                status = LENNOX_STATUS_GOOD
            message = {
                "MessageId": "637594500464319661|7df1361acd764dce83fcbc776ae3f8dd",
                "SenderId": "LCC",
                "TargetID": "mapp079372367644467046827098_myemail@email.com",
                "MessageType": "PropertyChange",
                "Data": {
                    "zones": [
                        {
                            "publisher": {"publisherName": "lcc"},
                            "status": {
                                "fan": False,
                                "allergenDefender": False,
                                "humidity": humidity,
                                "humidityStatus": status,
                                "temperature": temperature,
                                "temperatureStatus": status,
                                "temperatureC": 26,
                            },
                            "id": 0,
                        }
                    ]
                },
                "AdditionalParameters": None,
            }
            for appName, appObject in self.appList.items():
                appObject.queue.append(message)
            if temperature == 100:
                temperature = 10
                humidity = 50
            else:
                temperature = temperature + 10
                humidity = humidity + 1
            await asyncio.sleep(5.0)

    async def siblingSimulator(self):
        if self.siblingSim == False or self.siblingSimRunning == True:
            return
        self.siblingSimRunning = True
        message = {
            "MessageId": 0,
            "SenderID": "LCC",
            "TargetID": "homeassistant",
            "MessageType": "PropertyChange",
            "Data": {
                "siblings": [
                    {
                        "publisher": {"publisherName": "lcc"},
                        "id": 0,
                        "selfIdentifier": "KL21J00001",
                        "sibling": {
                            "identifier": "KL21J00002",
                            "systemName": '"Bedrooms"',
                            "nodePresent": True,
                            "portNumber": 443,
                            "groupCountTracker": True,
                            "ipAddress": "10.0.0.2",
                        },
                    }
                ]
            },
        }
        for appName, appObject in self.appList.items():
            appObject.queue.append(message)
        await asyncio.sleep(15.0)

        temperature = 100
        while True:
            if temperature == 100:
                status = LENNOX_STATUS_NOT_AVAILABLE
            else:
                status = LENNOX_STATUS_GOOD
            message = {
                "MessageId": "637594500464320381|95a6cacebd94459dbe7538161628bdb6",
                "SenderId": "KL21J00002",
                "TargetID": "mapp079372367644467046827098_myemail@email.com",
                "MessageType": "PropertyChange",
                "Data": {
                    "system": {
                        "status": {
                            "outdoorTemperatureStatus": status,
                            "outdoorTemperature": temperature,
                            "outdoorTemperatureC": 13.5,
                        },
                        "publisher": {"publisherName": "lcc"},
                    }
                },
            }
            for appName, appObject in self.appList.items():
                appObject.queue.append(message)
            if temperature == 200:
                temperature = 100
            else:
                temperature = temperature + 10
            await asyncio.sleep(5.0)

    def loadfile(self, name) -> json:
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, "../" + name)
        with open(file_path) as f:
            data = json.load(f)
        if "SenderId" in data:
            data["SenderId"] = "LCC"
        if "SenderID" in data:
            data["SenderID"] = "LCC"
        return data

    async def connect(self, request: Request):
        app_id = request.match_info["app_id"]
        if app_id in self.appList:
            pass
        else:
            self.appList[app_id] = AppConnection(app_id)
        return web.Response(text="Simulator Success")

    async def disconnect(self, request: Request):
        app_id = request.match_info["app_id"]
        self.appList.pop(app_id)
        return web.Response(text="Simulator Success")

    async def request_data(self, request: Request):
        data = await request.json()
        return self.process_request_data(data)

    def process_request_data(self, data):
        if "SenderID" in data:
            app_id = data["SenderID"]
            if app_id in self.appList:
                app: AppConnection = self.appList[app_id]
                if "configFile" in self.config_data:
                    data = self.loadfile(self.config_data["configFile"])
                    if self.productType != None:
                        data["Data"]["system"]["config"]["options"]["productType"] = self.productType
                    app.queue.append(data)
                if "rgwFile" in self.config_data:
                    data = self.loadfile(self.config_data["rgwFile"])
                    app.queue.append(data)
                if "zonesFile" in self.config_data:
                    data = self.loadfile(self.config_data["zonesFile"])
                    app.queue.append(data)
                if "equipmentFile" in self.config_data:
                    data = self.loadfile(self.config_data["equipmentFile"])
                    self.equipment = data
                    app.queue.append(data)
                if "deviceFile" in self.config_data:
                    data = self.loadfile(self.config_data["deviceFile"])
                    app.queue.append(data)
                if "bleFile" in self.config_data:
                    data = self.loadfile(self.config_data["bleFile"])
                    app.queue.append(data)
                if "iaqFile" in self.config_data:
                    data = self.loadfile(self.config_data["iaqFile"])
                    app.queue.append(data)
                if "systemFile" in self.config_data:
                    data = self.loadfile(self.config_data["systemFile"])
                    app.queue.append(data)
                if "alertFile" in self.config_data:
                    data = self.loadfile(self.config_data["alertFile"])
                    app.queue.append(data)
                if "weatherFile" in self.config_data:
                    data = self.loadfile(self.config_data["weatherFile"])
                    app.queue.append(data)
                if "wifiInterfaceFile" in self.config_data:
                    data = self.loadfile(self.config_data["wifiInterfaceFile"])
                    app.queue.append(data)

                asyncio.create_task(self.outdoorTempSimulator())
                asyncio.create_task(self.zoneSimulator())
                asyncio.create_task(self.siblingSimulator())
                asyncio.create_task(self.diagSimulator())
                asyncio.create_task(self.heatpumpLockoutSimulator())
                asyncio.create_task(self.wifiSimulator())
                return web.Response(text="Simulator Success")
        return web.Response(status=404, text="Simulator Failuer")

    def perform_substitutions(self, message: str) -> str:
        if "substitutions" in self.config_data:
            for substitution in self.config_data["substitutions"]:
                message = message.replace(substitution["old_value"], substitution["new_value"])
        return message

    async def retrieve(self, request):
        app_id = request.match_info["app_id"]
        delay = 15
        if app_id in self.appList:
            app: AppConnection = self.appList[app_id]
            for i in range(delay):
                if len(app.queue) != 0:
                    message = app.queue.pop()
                    data = '{ "messages": [' + json.dumps(message) + "]}"
                    data = self.perform_substitutions(data)
                    return web.Response(status=200, body=data)
                await asyncio.sleep(1.0)
        else:
            data = {}
            self.appList[app_id] = AppConnection(app_id)
            data["SenderID"] = app_id
            self.process_request_data(data)
        return web.Response(status=204)

    def process_message(self, msg):
        if "Data" in msg:
            data = msg["Data"]
            if "system" in data:
                if "config" in data["system"]:
                    if "centralMode" in data["system"]["config"]:
                        mode = data["system"]["config"]["centralMode"]
                        if mode == True:
                            zm = "central"
                        else:
                            zm = "zoned"
                        msg["Data"] = {
                            "system": {
                                "status": {
                                    "zoningMode": zm,
                                },
                                "config": {"centralMode": mode},
                            }
                        }
            if "systemControl" in data:
                if "parameterUpdate" in data["systemControl"]:
                    parameterUpdate = data["systemControl"]["parameterUpdate"]
                    asyncio.create_task(self.parameterUpdate(parameterUpdate))
        return msg

    async def publish(self, request):
        data = await request.json()
        data["SenderID"] = "LCC"
        data["MessageType"] = "PropertyChange"
        message_to_send = self.process_message(data)
        for appName, appObject in self.appList.items():
            appObject.queue.append(message_to_send)

        body_json = {"code": 1, "message": "", "retry_after": 0}
        body_txt = json.dumps(body_json)
        return web.Response(status=200, body=body_txt)


def init_func(argv):
    if len(argv) == 2:
        if argv[0] == "-c":
            fileName = argv[1]
            simulator = Simulator(fileName)
            app = web.Application()
            app.add_routes(
                [
                    web.post("/Endpoints/{app_id}/Connect", simulator.connect),
                    web.post("/Endpoints/{app_id}/Disconnect", simulator.disconnect),
                    web.post("/Messages/RequestData", simulator.request_data),
                    web.get("/Messages/{app_id}/Retrieve", simulator.retrieve),
                    web.get("/v1/Messages/{app_id}/Retrieve", simulator.retrieve),
                    web.post("/Messages/Publish", simulator.publish),
                    web.post("/v1/messages/publish", simulator.publish),
                ]
            )
    return app
