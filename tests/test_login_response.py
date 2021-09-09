from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home

import json
import os


def test_process_login_message():
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, "login_response.json")
    with open(file_path) as f:
        data = json.load(f)

    api = s30api_async("myemail@email.com", "mypassword")

    api.process_login_response(data)

    lhome: lennox_home = api.getHomeByHomeId("1234567")
    assert lhome != None
    assert lhome.id == "1234567"
    assert lhome.idx == 0
    assert lhome.name == "MoetownHouse"
    assert lhome.json != None

    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.home.id == lhome.id

    lsystem: lennox_system = api.getSystems()[1]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000002"
    assert lsystem.home.id == lhome.id

    assert api.loginBearerToken == "bearer myveryshortversionofthebearertokenfortesting"
    assert api.loginToken == "myveryshortversionofthebearertokenfortesting"
