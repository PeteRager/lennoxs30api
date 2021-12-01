import json
import os
import asyncio

from aiohttp import web
from aiohttp.typedefs import JSONDecoder
from aiohttp.web_request import Request


class AppConnection(object):
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.queue = []


class Simulator(object):
    def __init__(self, configfile: str):
        self.configfile = configfile
        self.appList = {}
        with open(configfile) as f:
            self.config_data = json.load(f)

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
        if app_id in self.appList:
            app: AppConnection = self.appList[app_id]
            for i in range(15):
                if len(app.queue) != 0:
                    message = app.queue.pop()
                    data = '{ "messages": [' + json.dumps(message) + "]}"
                    data = self.perform_substitutions(data)
                    return web.Response(status=200, body=data)
                await asyncio.sleep(1.0)
        return web.Response(status=204)

    async def publish(self, request):
        data = await request.json()
        data["SenderID"] = "LCC"
        data["MessageType"] = "PropertyChange"
        for appName, appObject in self.appList.items():
            appObject.queue.append(data)

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
                    web.post("/Messages/RequestData", simulator.request_data),
                    web.get("/Messages/{app_id}/Retrieve", simulator.retrieve),
                    web.post("/Messages/Publish", simulator.publish),
                ]
            )
    return app
