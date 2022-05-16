import json
import os
import asyncio
from unittest import async_case

from aiohttp import web
from aiohttp.typedefs import JSONDecoder
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
        with open(configfile) as f:
            self.config_data = json.load(f)

    async def outdoorTempSimulator(self):
        if self.outdoorTempSimRunning == True:
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

    async def zoneSimulator(self):
        if self.zoneSimRunning == True:
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
        if "SenderID" in data:
            app_id = data["SenderID"]
            if app_id in self.appList:
                data = self.loadfile(self.config_data["configFile"])
                app: AppConnection = self.appList[app_id]
                app.queue.append(data)
                data = self.loadfile(self.config_data["deviceFile"])
                app: AppConnection = self.appList[app_id]
                app.queue.append(data)
                asyncio.create_task(self.outdoorTempSimulator())
                asyncio.create_task(self.zoneSimulator())
                return web.Response(text="Simulator Success")
        return web.Response(status=404, text="Simulator Failuer")

    def perform_substitutions(self, message: str) -> str:
        if "substitutions" in self.config_data:
            for substitution in self.config_data["substitutions"]:
                message = message.replace(
                    substitution["old_value"], substitution["new_value"]
                )
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
        return web.Response(status=204)

    def process_message(self, msg):
        if "Data" in msg:
            data = msg["Data"]
            if "systemControl" in data:
                if "diagControl" in data["systemControl"]:
                    if "level" in data["systemControl"]["diagControl"]:
                        level = data["systemControl"]["diagControl"]["level"]
                        msg["Data"] = {
                            "system": {
                                "status": {
                                    "diagLevel": level,
                                }
                            }
                        }
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
                    web.post("/Messages/Publish", simulator.publish),
                ]
            )
    return app
