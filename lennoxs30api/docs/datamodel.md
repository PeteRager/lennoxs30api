The purpose of this document is to decsribe the data model of the Lenox S30 API


Home
   (homeid, id, name)
   Systems
      System
         (sysid)
         (outdoor temperature)
         (data) - there is a very large system object
         Schedules - a list of the schedules that are configured for this system
         Zones
            (name) <Zone 1>
            (id)   <0>
            (config)  - capabilities of the zone - heating, cooling, dehumidification, min/max setpoints, current active schedule
            Schedules (not sure what the difference is between these and the ones at the system level)
            (sensors)
                            "sensors": [
                            {
                                "hum": 56.81336476924544,
                                "humStatus": "good",
                                "id": 0,
                                "tant": 69.55912714012544,
                                "tempStatus": "good",
                                "tsense": 69.5591815349143
                            }
            (status)
                             status": {
                                "allergenDefender": false,
                                "aux": false,
                                "balancePoint": "none",
                                "coolCoast": false,
                                "damper": 0,
                                "defrost": false,
                                "demand": 0,
                                "fan": false,
                                "heatCoast": false,
                                "humOperation": "off",
                                "humidity": 57,
                                "humidityStatus": "good",
                                "period": {
                                    "csp": 75,
                                    "cspC": 24,
                                    "desp": 55,
                                    "fanMode": "auto",
                                    "hsp": 57,
                                    "hspC": 14,
                                    "humidityMode": "off",
                                    "husp": 40,
                                    "sp": 73,
                                    "spC": 23,
                                    "startTime": 0,
                                    "systemMode": "cool"
                            },

Entity: Homes

The top level is a list of one or more homes.

Attributes:
   homeid - identifier for the home, this is an integer, numbers I see are > 2,000,000
   id - zero based index of the homes for this account
   name - the user configured name of the home
   address - physical address, latitiude / longitude

   Systems - a list of systems in the Home

When Obtained:
   Information is retrieved as part of login

Entity: Systems

Represents an HVAC system within a specific home

Static Attributes:
    sysId - a GUID indentifying the system - this is the ID that is used to subscribe for information
Dynamic Attributes
    presense - indicates if the system is online or offline



    outdoor temperature

            "AdditionalParameters": null,
            "Data": {
                "system": {
                    "publisher": {
                        "publisherName": "lcc"
                    },
                    "status": {
                        "outdoorTemperature": 67,
                        "outdoorTemperatureC": 19,
                        "outdoorTemperatureStatus": "good"
                    }
                }
            },
            "MessageId": "637576290738517589|5fe01439cc69416b9c26f268dee1df0c",
            "MessageType": "PropertyChange",
            "SenderId": "e98d044e-970b-444b-86db-532a09dcc46f",
            "TargetID": "mapp079372367644467046827006_pete.sage@icloud.com"

    system configuration from dynamic
               "system": {
                    "capacityPrognostics": {
                        "alertThreshold": 0,
                        "filterGain": 0,
                        "isValid": false,
                        "persistenceCountThreshold": 0,
                        "persistentThreshold": 0
                    }, .....


When Obtained:
   Information is retrieved as part of login


Entity Zones

   