#!/usr/bin/python

from lennoxs30api.s30api_async import *

import time
import logging
import sys
import asyncio

###### ENIVRONMENT SETUP #####################
LOG_PATH = '/home/pete/lennoxs30api'    #  Directoy to stash the log file in
EMAIL_ADDRESS = 'myemail@myemail.com'
PASSWORD = 'mypassword'


logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(level=logging.DEBUG)

fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_PATH, 'log.txt'))
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)


async def runner(s30api):
    if await s30api.serverConnect() == False:
        print("Connection Failed")
        return
    for lsystem in s30api.getSystems():
        if await s30api.subscribe(lsystem) == False:
            print("Data Subscription Failed lsystem [" + str(lsystem) + "]")
            return
    while (True):
        print("Awake")
        await s30api.retrieve()
        await asyncio.sleep(10)

async def poller(s30api):        
    while (True):
        print("Poller Awake")
        try:
            for lsystem in s30api.getSystems():
                print("Outdoor - Temp [" + str(lsystem.outdoorTemperature) + "]")
                for zone in lsystem.getZoneList():
                    if zone.getTemperature() != None:
                        message = "[" + zone.name + "] Temp [" + str(zone.getTemperature()) + "] Humidity [" + str(zone.getHumidity()) + "] "
                        message += "SystemMode [" + str(zone.getSystemMode()) + "] FanMode [" + str(zone.getFanMode()) + "] HumidityMode [" + str(zone.getHumidityMode()) + "] "
                        message += "Cool Setpoint [" + str(zone.getCoolSP()) + "] Heat Setpoint [" + str(zone.getHeatSP()) + "]"
                        print(message)
        except Exception as e:
            print("Exception " + str(e))
        await asyncio.sleep(15)
        
import functools


class Prompt:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.q = asyncio.Queue()
        self.loop.add_reader(sys.stdin, self.got_input)

    def got_input(self):
        asyncio.ensure_future(self.q.put(sys.stdin.readline()), loop=self.loop)

    async def __call__(self, msg, end='\n', flush=False):
        print(msg, end=end, flush=flush)
        return (await self.q.get()).rstrip('\n')

prompt = Prompt()
raw_input = functools.partial(prompt, end='', flush=True)

async def command_reader(s30api):
    while (True):
        try:
            input = await raw_input('enter cmd:')
            splits = input.split(' ')
            res = splits[0]
            print('Result [' + res + ']')
            system = s30api.getSystems()[0]
            if (res == 'cool' or res == 'off' or res or 'heat'):
                print("Set HVAC Mode [" + res + ']')
                cmdres = await system.setHVACMode(res)
                print("Command Result [" + str(cmdres) + ']')
            if (res == 'circulate' or res == 'auto' or res == 'on'):
                print("Set Fan Mode [" + res + ']')
                cmdres = await system.setFanMode(res)
                print("Command Result [" + str(cmdres) + ']')
            if (res == 'csp'):
                par = splits[1]
                print("Cool Setpoint [" + par + ']')
                cmdres = await system.setCoolSPF(par)
                print("Command Result [" + str(cmdres) + ']')
            if (res == 'hsp'):
                par = splits[1]
                print("Heat Setpoint [" + par + ']')
                cmdres = await system.setHeatSPF(par)
                print("Command Result [" + str(cmdres) + ']')
        except Exception as e:
            print("Exception " + str(e))

async def multiple_tasks(s30api):
  input_coroutines = [runner(s30api), poller(s30api), command_reader(s30api)]
  res = await asyncio.gather(*input_coroutines, return_exceptions=True)
  return res        

def main():
    s30api = s30api_async(EMAIL_ADDRESS, PASSWORD, 0, 0, 0,9)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(multiple_tasks(s30api))    


if __name__ == "__main__":
    main()