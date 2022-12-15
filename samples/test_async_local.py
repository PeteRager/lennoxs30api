#!/usr/bin/python

from lennoxs30api.s30exception import S30Exception
from lennoxs30api import lennox_system, lennox_zone, s30api_async

import time
import logging
import sys
import asyncio

###### ENIVRONMENT SETUP #####################
LOG_PATH = "/home/pete"  #  Directoy to stash the log file in
# EMAIL_ADDRESS = "myemail@myemail.com"
# PASSWORD = "mypassword"
IP_ADDRESS = "192.168.1.175"
APP_ID = "test"


logFormatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
)
rootLogger = logging.getLogger()
rootLogger.setLevel(level=logging.DEBUG)

fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_PATH, "log.txt"))
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)

# This task gets messages from Cloud and processes them
async def cloud_message_pump_task(s30api: s30api_async) -> None:
    try:
        # Login and establish connection
        await s30api.serverConnect()
        # For each S30 found, initiate the data subscriptions.
        for lsystem in s30api.system_list:
            await s30api.subscribe(lsystem)
    # Catch errors and exit this task.
    except S30Exception as e:
        print("Failed to connect error " + str(e))
        return
    while True:
        # Checks for new messages and processes them which may update the state of zones, etc.
        try:
            await s30api.messagePump()
            await asyncio.sleep(1)
        # Intermittent errors due to Lennox servers, etc, may occur, log and keep pumping.
        except S30Exception as e:
            print("Message pump error " + str(e))


# This task periodically polls the API for data and prints it.  These calls are just accessing local state, that
# may get updated by the message pump task.  You could also set up a callback on a Zone or System and get notified when the
# entity changes - perhaps in another example!
async def api_poller_task(s30api):
    while True:
        try:
            for lsystem in s30api.systemList:
                for zone in lsystem.zoneList:
                    if zone.getTemperature() != None:
                        message = f"[{zone.name}] Temp [{zone.getTemperature()}] Humidity [{zone.getHumidity()}]"
                        message += f" SystemMode [{zone.getSystemMode()}] FanMode [{zone.getFanMode()}] HumidityMode [{zone.getHumidityMode()}] "
                        message += f"Cool Setpoint [{zone.getCoolSP()}] Heat Setpoint [{zone.getHeatSP()}]"
                        message += f"Outdoor - Temp [{lsystem.outdoorTemperature}]"
                        print(message)
        except Exception as e:
            print("Exception " + str(e))
        await asyncio.sleep(1)


# I found this example of how to read from the command prompt async.
# https://stackoverflow.com/questions/35223896/listen-to-keypress-with-asyncio
import functools


class Prompt:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.q = asyncio.Queue()
        self.loop.add_reader(sys.stdin, self.got_input)

    def got_input(self):
        asyncio.ensure_future(self.q.put(sys.stdin.readline()), loop=self.loop)

    async def __call__(self, msg, end="\n", flush=False):
        print(msg, end=end, flush=flush)
        return (await self.q.get()).rstrip("\n")


prompt = Prompt()
raw_input = functools.partial(prompt, end="", flush=True)

# This task gets input from the command prompt and executes task.
async def command_reader_task(s30api):
    while True:
        try:
            input = await raw_input("enter cmd:")
            splits = input.split(" ")
            res = splits[0]
            print("Result [" + res + "]")
            # By default we'll use Zone_1 on the first S30 found
            zone: lennox_zone = None
            if s30api.system_list != None and len(s30api.system_list) > 0:
                system: lennox_system = s30api.system_list[0]
                zone = system.getZone(0)
                # Zone configuration usually arrives within 5-10 seconds.  In a real program you may wait for it to come in
                # before really starting up.
                if zone == None:
                    print("zone configuration not received, command ignored")
                    continue
            if res == "cool" or res == "off" or res == "heat":
                print("Set HVAC Mode [" + res + "]")
                cmdres = await zone.setHVACMode(res)
                print("Command Result [" + str(cmdres) + "]")
            if res == "circulate" or res == "auto" or res == "on":
                print("Set Fan Mode [" + res + "]")
                cmdres = await zone.setFanMode(res)
                print("Command Result [" + str(cmdres) + "]")
            if res == "csp":
                par = splits[1]
                print("Cool Setpoint [" + par + "]")
                cmdres = await zone.setCoolSPF(par)
                print("Command Result [" + str(cmdres) + "]")
            if res == "hsp":
                par = splits[1]
                print("Heat Setpoint [" + par + "]")
                cmdres = await zone.setHeatSPF(par)
                print("Command Result [" + str(cmdres) + "]")
        except Exception as e:
            print("Exception " + str(e))


async def multiple_tasks(s30api):
    input_coroutines = [
        cloud_message_pump_task(s30api),
        api_poller_task(s30api),
        command_reader_task(s30api),
    ]
    res = await asyncio.gather(*input_coroutines, return_exceptions=True)
    return res


def main():
    s30api = s30api_async("none", "none", APP_ID, IP_ADDRESS)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(multiple_tasks(s30api))


if __name__ == "__main__":
    main()
