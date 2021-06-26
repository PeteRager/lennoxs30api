# PyPI - lennoxs30api

pip install lennoxs30api

## API Wrapper for www.lennoxicomfort.com

By Pete Rager  

This asyncio module connects to the Lennox Cloud API to retrieve data from S30 / E30 thermostats.  This API does not work for older models that use a different API.  Those models are supported by this project:  https://github.com/thevoltagesource/myicomfort

Prerequistes:

1. Python version 3.8.6 or later

2. A Lennox sign-on (email address and password)

3. You may need to install aiohttp https://docs.aiohttp.org/en/stable/

Sample program Instructions:

1. Grab the repo

2. Edit the test_async.py program to supply the following
 
    LOG_PATH = '/home/pete/lennoxs30api'    #  Directoy to stash the log file in

    EMAIL_ADDRESS = 'myemail@myemail.com'

    PASSWORD = 'mypassword'

Command Line Program Instructions:

The command line program uses asyncio and runs 3 different tasks

- Task 1 (runner) - this task connects to the cloud API and periodically polls it at a 10 second interval

- Task 2 (poller) - this task runs on a 15 second interval and prints out information from all active Zones

- Task 3 (prompt) - this task reads from the command line and executes commands on behalf of the user to enabling API testing.  Cmd List

        cool, heat, off - sets the HVAC mode to cool, heat or off.  usage - just type the word followed by enter eg cool

        auto, on, circulate - sets the Fan mocde to auto, on, or ciruclate

        csp <TempF> - sets the cool setpoint in F.  example  csp 76

        hsp <TempF> - sets the heat setpoint in F.  example hsp 65

To exit the program hit crtl-c

## Reporting Bugs

Please enabled debug logging when reporting bugs and provide sample code.  Do not publicly post the debug logs as they contain Personally Identifiable Information that is part of the communication protocol.  Your password IS NOT in the logs, but other information such as email, home address, etc., that is part of the lennox communications is.

## Enhancements

Submit enhancement requests as issues or better yet send a pull request.


