"""Tests login responses"""
from lennoxs30api.s30api_async import s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home
from tests.conftest import loadfile


def test_process_login_message():
    """Test login message"""
    api = s30api_async("myemail@email.com", "mypassword", None)
    data = loadfile("login_response.json")
    api.process_login_response(data)

    lhome: lennox_home = api.getHomeByHomeId("1234567")
    assert lhome is not None
    assert lhome.id == "1234567"
    assert lhome.idx == 0
    assert lhome.name == "MoetownHouse"
    assert lhome.json is not None

    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.home.id == lhome.id

    lsystem: lennox_system = api.system_list[1]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000002"
    assert lsystem.home.id == lhome.id

    assert api.loginBearerToken == "bearer myveryshortversionofthebearertokenfortesting"
    assert api.loginToken == "myveryshortversionofthebearertokenfortesting"
