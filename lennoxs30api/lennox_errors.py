from enum import Enum


class LennoxErrorCodes(Enum):
    lx_alarm_id_Unknown_Device_Detected_DEVICE2 = 10
    lx_alarm_id_Missing_DEVICE2 = 11
    lx_alarm_id_Incomplete_System = 12
    lx_alarm_id_Duplicate_Comfort_Sensor_ID = 13
    lx_alarm_id_Too_Many_Devices_of_the_Same_Type = 14
    lx_alarm_id_Parameter_Missmatch_Detected_for_DEVICE2 = 15
    lx_alarm_id_Low_Ambient_HP_Heat_Lockout = 18
    lx_alarm_id_High_Ambient_Auxiliary_Heat_Lockout = 19
    lx_alarm_id_Protocol_Upgrade_Required_DEVICE2 = 20
    lx_alarm_id_Incompatible_Equipment_Detected = 21
    lx_alarm_id_Over_Temperature_Protection = 29
    lx_alarm_id_Low_Temperature_Protection = 30
    lx_alarm_id_Lost_Communication_with_DEVICE2 = 31
    lx_alarm_id_Asynchronous_Reset_DEVICE2 = 32
    lx_alarm_id_Must_Program_Unit_Capacity_for_DEVICE2 = 34
    lx_alarm_id_Incorrect_Operation_of_DEVICE2 = 35
    lx_alarm_id_Heating_when_Not_Requested_DEVICE2 = 36
    lx_alarm_id_Cooling_when_Not_Requested_DEVICE2 = 37
    lx_alarm_id_Not_Heating_when_Requested_DEVICE2 = 38
    lx_alarm_id_Not_Cooling_when_Requested_DEVICE2 = 39
    lx_alarm_id_HP_Heating_Lockout = 40
    lx_alarm_id_DEVICE2_Control_Board_Replaced = 41
    lx_alarm_id_Communication_Problem = 105
    lx_alarm_id_Low_AC_Line_Voltage = 110
    lx_alarm_id_Line_Polarity_Reversed = 111
    lx_alarm_id_No_Ground_Connection = 112
    lx_alarm_id_High_AC_Line_Voltage = 113
    lx_alarm_id_AC_Line_Frequency_Distortion_Prob = 114
    lx_alarm_id_Low_Secondary_24VAC_Voltage = 115
    lx_alarm_id_High_Secondary_24VAC_Voltage = 116
    lx_alarm_id_Poor_Ground = 117
    lx_alarm_id_Unresponsive_DEVICE2 = 120
    lx_alarm_id_Active_Subnet_Controller_Missing = 124
    lx_alarm_id_Control_Hardware_Problem = 125
    lx_alarm_id_Control_Internal_Communication_Prob = 126
    lx_alarm_id_Configuration_Jumper_Missing = 130
    lx_alarm_id_Corrupted_Control_Parameters = 131
    lx_alarm_id_Failed_Flash_CRC_Check = 132
    lx_alarm_id_reset = 134
    lx_alarm_id_Outdoor_Temperature_Sensor_Problem = 180
    lx_alarm_id_Suction_Pressure_Sensor_Problem = 181
    lx_alarm_id_Suction_Temperature_Sensor_Problem = 182
    lx_alarm_id_Liquid_Pressure_Sensor_Problem = 183
    lx_alarm_id_Liquid_Temperature_Sensor_Problem = 184
    lx_alarm_id_Rollout_Limit_Switch_Open = 200
    lx_alarm_id_Indoor_Blower_Motor_Problem = 201
    lx_alarm_id_ID_Blower_Motor_Unit_Size_Mismatch = 202
    lx_alarm_id_Invalid_Unit_Code = 203
    lx_alarm_id_Gas_Valve_Problem = 204
    lx_alarm_id_Gas_Valve_Relay_Contact_Closed = 205
    lx_alarm_id_Gas_Valve_2nd_Stage_Relay_Failure = 206
    lx_alarm_id_HSI_Sensed_Open = 207
    lx_alarm_id_Low_Pressure_Switch_Open = 223
    lx_alarm_id_Low_Pressure_Switch_Stuck_Closed = 224
    lx_alarm_id_High_Press_Switch_Failed_to_Close = 225
    lx_alarm_id_High_Pressure_Switch_Stuck_Closed = 226
    lx_alarm_id_Lo_Pressure_Switch_Open_in_Run_Mode = 227
    lx_alarm_id_Inducer_Press_Switch_Calib_Failure = 228
    lx_alarm_id_Ignition_on_High_Fire = 229
    lx_alarm_id_Low_Flame_Current_Run_Mode = 240
    lx_alarm_id_Flame_Out_of_Sequence_Still_Present = 241
    lx_alarm_id_Primary_Limit_Switch_Open = 250
    lx_alarm_id_Discharge_Air_Temperature_High = 252
    lx_alarm_id_Watchguard_Flame_Failure_on_Ignite = 270
    lx_alarm_id_Watchguard_Low_Press_Switch_Open = 271
    lx_alarm_id_Watchguard_LoPressSwitchOpenRunMode = 272
    lx_alarm_id_Watchguard_Flame_Fail_in_Run_Mode = 273
    lx_alarm_id_Watchguard_Primary_LimitSwitch_Open = 274
    lx_alarm_id_Watchguard_Flame_OutofSeq_NoFlame = 275
    lx_alarm_id_Watchguard_Calibration_Failure = 276
    lx_alarm_id_Ignition_Circuit_Problem = 290
    lx_alarm_id_Heat_Airflow_Restricted_Below_Min = 291
    lx_alarm_id_Indoor_Blower_Motor_Start_Problem = 292
    lx_alarm_id_Inducer_Motor_Overcurrent = 294
    lx_alarm_id_Indoor_Blower_Over_Temperature = 295
    lx_alarm_id_Discharge_Air_Temp_Sensor_Problem = 310
    lx_alarm_id_Heat_Rate_Reduced_to_Match_Airflow = 311
    lx_alarm_id_ReducedAirflow_IndoorBlower_Cutback = 312
    lx_alarm_id_Indoor_OutdoorUnit_CapacityMismatch = 313
    lx_alarm_id_Link_Relay_Problem = 330
    lx_alarm_id_RSBus_Communication_Link_Problem = 331
    lx_alarm_id_Relay_Y1_Stuck = 344
    lx_alarm_id_Relay_O_Failure = 345
    lx_alarm_id_HP_Jumper_not_Removed = 346
    lx_alarm_id_Relay_Y1_Failure = 347
    lx_alarm_id_Relay_Y2_Failure = 348
    lx_alarm_id_IFC_Error_Check_Jumper_O_to_R = 349
    lx_alarm_id_Electric_Heat_not_Configured = 350
    lx_alarm_id_Electric_Heat_Stage_1_Problem = 351
    lx_alarm_id_Electric_Heat_Stage_2_Problem = 352
    lx_alarm_id_Electric_Heat_Stage_3_Problem = 353
    lx_alarm_id_Electric_Heat_Stage_4_Problem = 354
    lx_alarm_id_Electric_Heat_Stage_5_Problem = 355
    lx_alarm_id_Sequencer_Failed_to_Close = 356
    lx_alarm_id_Sequencer_Stuck_Closed = 357
    lx_alarm_id_Control_Error_Check_Jumper_O_to_R = 358
    lx_alarm_id_Interlock_Switch_Open = 370
    lx_alarm_id_Float_Switch_Sensed_Open = 371
    lx_alarm_id_Interlock_Relay_Failure = 380
    lx_alarm_id_Interlock_Relay_Stuck = 381
    lx_alarm_id_Relay_W1_Failure = 382
    lx_alarm_id_LSOM_Comp_Internal_Overload_Tripped = 400
    lx_alarm_id_Compressor_Long_Run_Cycle = 401
    lx_alarm_id_Outdoor_Unit_System_Pressure_Trip = 402
    lx_alarm_id_Compressor_Short_Cycling = 403
    lx_alarm_id_Compressor_Rotor_Locked = 404
    lx_alarm_id_Compressor_Open_Circuit = 405
    lx_alarm_id_Compressor_Open_Start_Circuit = 406
    lx_alarm_id_Compressor_Open_Run_Circuit = 407
    lx_alarm_id_Compressor_Contactor_Welded = 408
    lx_alarm_id_Compressor_Voltage_Low = 409
    lx_alarm_id_Open_Low_Pressure_Switch = 410
    lx_alarm_id_Low_Pressure_Switch_Strikes_Lockout = 411
    lx_alarm_id_Open_High_Pressure_Switch = 412
    lx_alarm_id_Hi_Pressure_Switch_Strikes_Lockout = 413
    lx_alarm_id_High_Discharge_Line_Temperature = 414
    lx_alarm_id_Hi_Disch_Line_Temp_Strikes_Lockout = 415
    lx_alarm_id_Outdoor_Coil_Sensor_Faulty = 416
    lx_alarm_id_Discharge_Sensor_Faulty = 417
    lx_alarm_id_W_Output_Hardware_Fault = 418
    lx_alarm_id_W_Output_Hardware_Fault_Lockout = 419
    lx_alarm_id_Defrost_Out_of_Control = 420
    lx_alarm_id_W_External_Miswire_Fault = 421
    lx_alarm_id_Compressor_Top_Cap_Switch_Open = 422
    lx_alarm_id_OD_Inverter_CT_Circuit_Problem = 423
    lx_alarm_id_OD_Liquid_Line_Sensor_Faulty = 424
    lx_alarm_id_Compressor_speed_limited_by_OD_temperature = 425
    lx_alarm_id_Excessive_Inverter_Alarms = 426
    lx_alarm_id_OD_Inverter_DC_Peak_Fault = 427
    lx_alarm_id_OD_Inverter_High_Main_Input_Current = 428
    lx_alarm_id_OD_Inverter_DC_Link_Low_Voltage = 429
    lx_alarm_id_OD_Inverter_Compressr_Startup_fail = 430
    lx_alarm_id_OD_Inverter_PFC_Fault = 431
    lx_alarm_id_OD_Inverter_DC_Link_High_Voltage = 432
    lx_alarm_id_OD_Inverter_Compressor_Overcurrent = 433
    lx_alarm_id_OD_Inverter_Comm_Error_to_Main_Control = 434
    lx_alarm_id_OD_Inverter_EEPROM_Checksum_Fault = 435
    lx_alarm_id_OD_Inverter_High_Heat_Sink_Temperature = 436
    lx_alarm_id_OD_Inverter_Heat_Sink_Temp_Sensor_Fault = 437
    lx_alarm_id_OD_Inverter_PFC_Input_Overcurrent = 438
    lx_alarm_id_OD_Inverter_Compressor_Slowdown_High_Input_Current = 439
    lx_alarm_id_OD_Inverter_Compressor_Slowdown_High_Heat_Sink_Temperature = 440
    lx_alarm_id_OD_Inverter_Compressor_Slowdown_High_Compressor_Current = 441
    lx_alarm_id_Compressor_Top_Cap_Switch_Strikes_Lockout = 442
    lx_alarm_id_MUC_Unit_Code_to_Inverter_Model_Mismatch = 443
    lx_alarm_id_Reversing_Valve_Relay_Failed_to_Close = 444
    lx_alarm_id_OD_Low_Suction_Pressure_Fault = 446
    lx_alarm_id_OD_High_Liquid_Line_Temperature = 447
    lx_alarm_id_OD_High_Liquid_Line_Temperature_Strikes_Lockout = 448
    lx_alarm_id_PureAir_Pressure_Sensor_Fault = 500
    lx_alarm_id_PureAir_UV_Sensor_Fault = 501
    lx_alarm_id_PureAir_UV_Lamp_Off = 502
    lx_alarm_id_PureAir_Filter_Life_10 = 503
    lx_alarm_id_PureAir_Filter_Life_0 = 504
    lx_alarm_id_PureAir_Model_Selection_Changed = 505
    lx_alarm_id_PureAir_UV_Lamp_Life_0 = 506
    lx_alarm_id_Filter_Calibration_Fail = 507
    lx_alarm_id_Low_Damper_24VAC_Voltage = 530
    lx_alarm_id_Zoning_Pressure_Switch_Opened_high_pressure = 532
    lx_alarm_id_Zone_1_Temp_Sensor_Problem = 542
    lx_alarm_id_Zone_2_Temp_Sensor_Problem = 543
    lx_alarm_id_Zone_3_Temp_Sensor_Problem = 544
    lx_alarm_id_Zone_4_Temp_Sensor_Problem = 545
    lx_alarm_id_ZS_Parameters_Resetting_From_Restored_Power = 546
    lx_alarm_id_ZS_Parameters_Resetting_From_System_Interruption = 547
    lx_alarm_id_ZS_Humidity_Sensor_Error = 548
    lx_alarm_id_ZS_Zone_Sensor_Lost_Communication = 551
    lx_alarm_id_Load_Shed_Event = 600
    lx_alarm_id_OD_Unit_Low_Ambient_Operational_Lockout = 601
    lx_alarm_id_OD_Unit_High_Ambient_Operational_Lockout = 602
    lx_alarm_id_Service_Alert = 603
    lx_alarm_id_Cooling_Capacity_Degradation = 604
    lx_alarm_id_Low_Room_Temperature_Detected = 610
    lx_alarm_id_High_Room_Temperature_Detected = 611
    lx_alarm_id_Comfort_Sensor_Temp_Sensor_Problem = 700
    lx_alarm_id_TSTAT_Temp_Above_Limit = 701
    lx_alarm_id_TSTAT_Temp_Below_Limit = 702
    lx_alarm_id_Comfort_Sensor_Humid_Sensor_Problem = 703
    lx_alarm_id_TSAT_Indoor_Humidity_Above_Limit = 704
    lx_alarm_id_TSAT_Indoor_Humidity_Below_Limit = 705
    lx_alarm_id_Lost_Communication_with_Server = 801
    lx_alarm_id_Lost_Wireless_Connection_with_WAP = 802
    lx_alarm_id_Temperature_Control_Problem = 900
    lx_alarm_id_Smart = 901
    lx_alarm_id_Ohm_Check = 999
    lx_alarm_id_Missing_Base = 65537
    lx_alarm_id_Missing_Base_1 = 65538
    lx_alarm_id_Missing_TSTAT = 65539
    lx_alarm_id_Missing_HD_Wall_display = 65540
    lx_alarm_id_Download_Failed = 65541
    lx_alarm_id_Update_Failed = 65542
    lx_alarm_id_Firmware_Updated = 65543
    lx_alarm_id_Too_Many_Siblings = 65544
    lx_alarm_id_Cooling_Prognostics_Alert = 65545


lennox_error_messages = {
    LennoxErrorCodes.lx_alarm_id_Unknown_Device_Detected_DEVICE2: "Unknown Device Detected",
    LennoxErrorCodes.lx_alarm_id_Missing_DEVICE2: "Missing Device",
    LennoxErrorCodes.lx_alarm_id_Incomplete_System: "Indoor Unit Not Detected",
    LennoxErrorCodes.lx_alarm_id_Duplicate_Comfort_Sensor_ID: "Duplicate Comfort Sensor ID",
    LennoxErrorCodes.lx_alarm_id_Too_Many_Devices_of_the_Same_Type: "Too Many Devices Of The Same Type",
    LennoxErrorCodes.lx_alarm_id_Parameter_Missmatch_Detected_for_DEVICE2: "Parameter Mismatch Detected For Device",
    LennoxErrorCodes.lx_alarm_id_Low_Ambient_HP_Heat_Lockout: "Low Ambient HP Heat Lockout",
    LennoxErrorCodes.lx_alarm_id_High_Ambient_Auxiliary_Heat_Lockout: "High Ambient Auxiliary Heat Lockout",
    LennoxErrorCodes.lx_alarm_id_Protocol_Upgrade_Required_DEVICE2: "Protocol Upgrade Required",
    LennoxErrorCodes.lx_alarm_id_Incompatible_Equipment_Detected: "Incompatible Equipment Detected",
    LennoxErrorCodes.lx_alarm_id_Over_Temperature_Protection: "Over Temperature Protection",
    LennoxErrorCodes.lx_alarm_id_Low_Temperature_Protection: "Low Temperature Protection",
    LennoxErrorCodes.lx_alarm_id_Lost_Communication_with_DEVICE2: "Lost Communication With Device",
    LennoxErrorCodes.lx_alarm_id_Asynchronous_Reset_DEVICE2: "Device Resetting",
    LennoxErrorCodes.lx_alarm_id_Must_Program_Unit_Capacity_for_DEVICE2: "Must Program Unit Capacity For Device",
    LennoxErrorCodes.lx_alarm_id_Incorrect_Operation_of_DEVICE2: "Incorrect Operation Of Device",
    LennoxErrorCodes.lx_alarm_id_Heating_when_Not_Requested_DEVICE2: "Heating When Not Requested",
    LennoxErrorCodes.lx_alarm_id_Cooling_when_Not_Requested_DEVICE2: "Cooling When Not Requested",
    LennoxErrorCodes.lx_alarm_id_Not_Heating_when_Requested_DEVICE2: "Not Heating When Requested",
    LennoxErrorCodes.lx_alarm_id_Not_Cooling_when_Requested_DEVICE2: "Not Cooling When Requested",
    LennoxErrorCodes.lx_alarm_id_HP_Heating_Lockout: "HP Heating Lockout",
    LennoxErrorCodes.lx_alarm_id_DEVICE2_Control_Board_Replaced: "Device Control Board Replaced",
    LennoxErrorCodes.lx_alarm_id_Communication_Problem: "Communication Error",
    LennoxErrorCodes.lx_alarm_id_Low_AC_Line_Voltage: "GF Low AC Line Voltage",
    LennoxErrorCodes.lx_alarm_id_Line_Polarity_Reversed: "GF Line Polarity Reversed",
    LennoxErrorCodes.lx_alarm_id_No_Ground_Connection: "GF No Ground Connection",
    LennoxErrorCodes.lx_alarm_id_High_AC_Line_Voltage: "GF High AC Line Voltage",
    LennoxErrorCodes.lx_alarm_id_AC_Line_Frequency_Distortion_Prob: "AC Line Frequency/Distortion Error",
    LennoxErrorCodes.lx_alarm_id_Low_Secondary_24VAC_Voltage: "Low Secondary (24VAC) Voltage",
    LennoxErrorCodes.lx_alarm_id_High_Secondary_24VAC_Voltage: "IU High Secondary (24VAC) Voltage",
    LennoxErrorCodes.lx_alarm_id_Poor_Ground: "IU Poor Ground",
    LennoxErrorCodes.lx_alarm_id_Unresponsive_DEVICE2: "Unresponsive Device",
    LennoxErrorCodes.lx_alarm_id_Active_Subnet_Controller_Missing: "Tstat Lost Communication To Smarthub",
    LennoxErrorCodes.lx_alarm_id_Control_Hardware_Problem: "Control Hardware Error",
    LennoxErrorCodes.lx_alarm_id_Control_Internal_Communication_Prob: "Control Internal Communication Error",
    LennoxErrorCodes.lx_alarm_id_Configuration_Jumper_Missing: "Configuration Jumper Missing",
    LennoxErrorCodes.lx_alarm_id_Corrupted_Control_Parameters: "Corrupted Control Parameters",
    LennoxErrorCodes.lx_alarm_id_Failed_Flash_CRC_Check: "Device Control Software Fault",
    LennoxErrorCodes.lx_alarm_id_reset: "Reset",
    LennoxErrorCodes.lx_alarm_id_Outdoor_Temperature_Sensor_Problem: "Outdoor Temperature Sensor Error",
    LennoxErrorCodes.lx_alarm_id_Suction_Pressure_Sensor_Problem: "OU Suction Pressure Transducer Fault",
    LennoxErrorCodes.lx_alarm_id_Suction_Temperature_Sensor_Problem: "OU Suction Temperature Sensor Fault",
    LennoxErrorCodes.lx_alarm_id_Liquid_Pressure_Sensor_Problem: "OU Liquid Pressure Sensor Error",
    LennoxErrorCodes.lx_alarm_id_Liquid_Temperature_Sensor_Problem: "OU Liquid Temperature Sensor Error",
    LennoxErrorCodes.lx_alarm_id_Rollout_Limit_Switch_Open: "GF Rollout Limit Switch Open",
    LennoxErrorCodes.lx_alarm_id_Indoor_Blower_Motor_Problem: "IU Blower Motor Fault",
    LennoxErrorCodes.lx_alarm_id_ID_Blower_Motor_Unit_Size_Mismatch: "IU Blower Motor & Unit Size Mismatch",
    LennoxErrorCodes.lx_alarm_id_Invalid_Unit_Code: "IU Invalid Size Unit Code",
    LennoxErrorCodes.lx_alarm_id_Gas_Valve_Problem: "GF Check Gas Valve",
    LennoxErrorCodes.lx_alarm_id_Gas_Valve_Relay_Contact_Closed: "GF Gas Valve Relay Contact Closed",
    LennoxErrorCodes.lx_alarm_id_Gas_Valve_2nd_Stage_Relay_Failure: "GF Gas Valve 2nd Stage Relay Fault",
    LennoxErrorCodes.lx_alarm_id_HSI_Sensed_Open: "GF HSI Sensed Open",
    LennoxErrorCodes.lx_alarm_id_Low_Pressure_Switch_Open: "GF Low Pressure Switch Open",
    LennoxErrorCodes.lx_alarm_id_Low_Pressure_Switch_Stuck_Closed: "GF Low Pressure Switch Stuck Closed",
    LennoxErrorCodes.lx_alarm_id_High_Press_Switch_Failed_to_Close: "GF High Pressure Switch Failed to Close",
    LennoxErrorCodes.lx_alarm_id_High_Pressure_Switch_Stuck_Closed: "GF High Pressure Switch Stuck Closed",
    LennoxErrorCodes.lx_alarm_id_Lo_Pressure_Switch_Open_in_Run_Mode: "GF Low Pressure Switch Open in Run Mode",
    LennoxErrorCodes.lx_alarm_id_Inducer_Press_Switch_Calib_Failure: "GF Inducer Calibration Issue",
    LennoxErrorCodes.lx_alarm_id_Ignition_on_High_Fire: "GF Ignition On High Fire",
    LennoxErrorCodes.lx_alarm_id_Low_Flame_Current_Run_Mode: "GF Low Flame Current - Run Mode",
    LennoxErrorCodes.lx_alarm_id_Flame_Out_of_Sequence_Still_Present: "GF Flame Out Of Sequence-Still Present",
    LennoxErrorCodes.lx_alarm_id_Primary_Limit_Switch_Open: "GF Primary Limit Switch Open",
    LennoxErrorCodes.lx_alarm_id_Discharge_Air_Temperature_High: "IU Discharge Air Temperature High",
    LennoxErrorCodes.lx_alarm_id_Watchguard_Flame_Failure_on_Ignite: "GF Flame Failed To Ignite",
    LennoxErrorCodes.lx_alarm_id_Watchguard_Low_Press_Switch_Open: "GF Low Press Switch Open",
    LennoxErrorCodes.lx_alarm_id_Watchguard_LoPressSwitchOpenRunMode: "GF Low Press Switch Open Run Mode",
    LennoxErrorCodes.lx_alarm_id_Watchguard_Flame_Fail_in_Run_Mode: "GF Flame Fail In Run Mode",
    LennoxErrorCodes.lx_alarm_id_Watchguard_Primary_LimitSwitch_Open: "GF Primary Limit Switch Open",
    LennoxErrorCodes.lx_alarm_id_Watchguard_Flame_OutofSeq_NoFlame: "GF Flame Out Of Seq. No Flame",
    LennoxErrorCodes.lx_alarm_id_Watchguard_Calibration_Failure: "GF Calibration Failure",
    LennoxErrorCodes.lx_alarm_id_Ignition_Circuit_Problem: "GF Ignition Circuit Fault",
    LennoxErrorCodes.lx_alarm_id_Heat_Airflow_Restricted_Below_Min: "GF Heat Airflow Below Min",
    LennoxErrorCodes.lx_alarm_id_Indoor_Blower_Motor_Start_Problem: "ID Blower Motor Start Fault",
    LennoxErrorCodes.lx_alarm_id_Inducer_Motor_Overcurrent: "GF Inducer Motor Overcurrent",
    LennoxErrorCodes.lx_alarm_id_Indoor_Blower_Over_Temperature: "ID Blower Over Temperature",
    LennoxErrorCodes.lx_alarm_id_Discharge_Air_Temp_Sensor_Problem: "Discharge Air Temp Sensor Error",
    LennoxErrorCodes.lx_alarm_id_Heat_Rate_Reduced_to_Match_Airflow: "GF Heat Rate Reduced To Match Airflow",
    LennoxErrorCodes.lx_alarm_id_ReducedAirflow_IndoorBlower_Cutback: "Reduced Airflow-Indoor Blower Cutback",
    LennoxErrorCodes.lx_alarm_id_Indoor_OutdoorUnit_CapacityMismatch: "Indoor/Outdoor Unit Capacity Mismatch",
    LennoxErrorCodes.lx_alarm_id_Link_Relay_Problem: "Link Relay Problem",
    LennoxErrorCodes.lx_alarm_id_RSBus_Communication_Link_Problem: "RSBus Communication Link Problem",
    LennoxErrorCodes.lx_alarm_id_Relay_Y1_Stuck: "GF IFC Relay Y1 Stuck",
    LennoxErrorCodes.lx_alarm_id_Relay_O_Failure: "Relay O Failure",
    LennoxErrorCodes.lx_alarm_id_HP_Jumper_not_Removed: "AH HP Jumper Not Removed",
    LennoxErrorCodes.lx_alarm_id_Relay_Y1_Failure: "IU or EIM Relay Y1 Fault",
    LennoxErrorCodes.lx_alarm_id_Relay_Y2_Failure: "IU Relay Y2 Fault",
    LennoxErrorCodes.lx_alarm_id_IFC_Error_Check_Jumper_O_to_R: "GF IFC Error Check Jumper O To R",
    LennoxErrorCodes.lx_alarm_id_Electric_Heat_not_Configured: "AH Electric Heat Not Configured",
    LennoxErrorCodes.lx_alarm_id_Electric_Heat_Stage_1_Problem: "AH Electric Heat Stage 1 Fault",
    LennoxErrorCodes.lx_alarm_id_Electric_Heat_Stage_2_Problem: "AH Electric Heat Stage 2 Fault",
    LennoxErrorCodes.lx_alarm_id_Electric_Heat_Stage_3_Problem: "AH Electric Heat Stage 3 Fault",
    LennoxErrorCodes.lx_alarm_id_Electric_Heat_Stage_4_Problem: "AH Electric Heat Stage 4 Fault",
    LennoxErrorCodes.lx_alarm_id_Electric_Heat_Stage_5_Problem: "AH Electric Heat Stage 5 Fault",
    LennoxErrorCodes.lx_alarm_id_Sequencer_Failed_to_Close: "Sequencer Failed to Close",
    LennoxErrorCodes.lx_alarm_id_Sequencer_Stuck_Closed: "Sequencer Stuck Closed",
    LennoxErrorCodes.lx_alarm_id_Control_Error_Check_Jumper_O_to_R: "AH Control Error - Check Jumper O To R",
    LennoxErrorCodes.lx_alarm_id_Interlock_Switch_Open: "GF Interlock Switch Open",
    LennoxErrorCodes.lx_alarm_id_Float_Switch_Sensed_Open: "AH Float Switch Sensed Open",
    LennoxErrorCodes.lx_alarm_id_Interlock_Relay_Failure: "EIM Interlock Relay Fault",
    LennoxErrorCodes.lx_alarm_id_Interlock_Relay_Stuck: "EIM Interlock Relay Stuck",
    LennoxErrorCodes.lx_alarm_id_Relay_W1_Failure: "EIM Relay W1 Fault",
    LennoxErrorCodes.lx_alarm_id_LSOM_Comp_Internal_Overload_Tripped: "OU LSOM Compressor Internal Overload Tripped",
    LennoxErrorCodes.lx_alarm_id_Compressor_Long_Run_Cycle: "OU Compressor Long Run Cycle",
    LennoxErrorCodes.lx_alarm_id_Outdoor_Unit_System_Pressure_Trip: "OU System Pressure Trip",
    LennoxErrorCodes.lx_alarm_id_Compressor_Short_Cycling: "OU Compressor Short-Cycling",
    LennoxErrorCodes.lx_alarm_id_Compressor_Rotor_Locked: "OU Compressor Rotor Locked",
    LennoxErrorCodes.lx_alarm_id_Compressor_Open_Circuit: "OU Compressor Open Circuit",
    LennoxErrorCodes.lx_alarm_id_Compressor_Open_Start_Circuit: "OU Compressor Open Start Circuit",
    LennoxErrorCodes.lx_alarm_id_Compressor_Open_Run_Circuit: "OU Compressor Open Run Circuit",
    LennoxErrorCodes.lx_alarm_id_Compressor_Contactor_Welded: "OU Compressor Contactor Welded",
    LennoxErrorCodes.lx_alarm_id_Compressor_Voltage_Low: "OU Control Board Low 24VAC",
    LennoxErrorCodes.lx_alarm_id_Open_Low_Pressure_Switch: "OU Open Low Pressure Switch",
    LennoxErrorCodes.lx_alarm_id_Low_Pressure_Switch_Strikes_Lockout: "OU Low Pressure Switch Strikes Lockout",
    LennoxErrorCodes.lx_alarm_id_Open_High_Pressure_Switch: "OU Open High Pressure Switch",
    LennoxErrorCodes.lx_alarm_id_Hi_Pressure_Switch_Strikes_Lockout: "OU High Pressure Switch Strikes Lockout",
    LennoxErrorCodes.lx_alarm_id_High_Discharge_Line_Temperature: "OU High Discharge Line Temperature",
    LennoxErrorCodes.lx_alarm_id_Hi_Disch_Line_Temp_Strikes_Lockout: "OU High Discharge Line Temp Strikes Lockout",
    LennoxErrorCodes.lx_alarm_id_Outdoor_Coil_Sensor_Faulty: "OU Coil Sensor Faulty",
    LennoxErrorCodes.lx_alarm_id_Discharge_Sensor_Faulty: "OU Discharge Sensor Faulty",
    LennoxErrorCodes.lx_alarm_id_W_Output_Hardware_Fault: "OU EIM W Output Hardware Fault",
    LennoxErrorCodes.lx_alarm_id_W_Output_Hardware_Fault_Lockout: "OU EIM W Output Hardware Fault Lockout",
    LennoxErrorCodes.lx_alarm_id_Defrost_Out_of_Control: "AH EIM Defrost Out Of Cycle",
    LennoxErrorCodes.lx_alarm_id_W_External_Miswire_Fault: "OU EIM W External Miswiring Fault",
    LennoxErrorCodes.lx_alarm_id_Compressor_Top_Cap_Switch_Open: "OU Compressor Top Cap Switch Open",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_CT_Circuit_Problem: "OU Inverter CT Circuit Fault",
    LennoxErrorCodes.lx_alarm_id_OD_Liquid_Line_Sensor_Faulty: "OU Liquid Line Sensor Faulty",
    LennoxErrorCodes.lx_alarm_id_Compressor_speed_limited_by_OD_temperature: "OU Compressor Speed Limited By OD Temperature",
    LennoxErrorCodes.lx_alarm_id_Excessive_Inverter_Alarms: "OU Excessive Inverter Alarms",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_DC_Peak_Fault: "OU Inverter DC Peak Fault",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_High_Main_Input_Current: "OU Inverter High Main Input Current",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_DC_Link_Low_Voltage: "OU Inverter DC Link Low Voltage",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_Compressr_Startup_fail: "OU Inverter Compressor Startup fail",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_PFC_Fault: "OU Inverter PFC Fault",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_DC_Link_High_Voltage: "OU Inverter DC Link High Voltage",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_Compressor_Overcurrent: "OU Inverter Compressor Overcurrent",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_Comm_Error_to_Main_Control: "OU Inverter Communication Error To Main Control",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_EEPROM_Checksum_Fault: "OU Inverter EEPROM Checksum Fault",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_High_Heat_Sink_Temperature: "OU Inverter High Heat-Sink Temperature",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_Heat_Sink_Temp_Sensor_Fault: "OU Inverter Heat-Sink Temp Sensor Fault",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_PFC_Input_Overcurrent: "OU Inverter PFC Input Overcurrent",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_Compressor_Slowdown_High_Input_Current: "OU Inverter Compressor Slowdown - High Input Current",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_Compressor_Slowdown_High_Heat_Sink_Temperature: "OU Inverter Compressor Slowdown - High Heat-Sink Temperature",
    LennoxErrorCodes.lx_alarm_id_OD_Inverter_Compressor_Slowdown_High_Compressor_Current: "OU Inverter Compressor Slowdown - High Compressor Current",
    LennoxErrorCodes.lx_alarm_id_Compressor_Top_Cap_Switch_Strikes_Lockout: "OU Compressor Top Cap Switch Strikes Lockout",
    LennoxErrorCodes.lx_alarm_id_MUC_Unit_Code_to_Inverter_Model_Mismatch: "OU MUC Unit Code To Inverter Model Mismatch",
    LennoxErrorCodes.lx_alarm_id_Reversing_Valve_Relay_Failed_to_Close: "HP Reversing Valve Relay Or Solenoid Fault",
    LennoxErrorCodes.lx_alarm_id_OD_Low_Suction_Pressure_Fault: "OU Low Suction Pressure Fault",
    LennoxErrorCodes.lx_alarm_id_OD_High_Liquid_Line_Temperature: "OU High Liquid Line Temperature",
    LennoxErrorCodes.lx_alarm_id_OD_High_Liquid_Line_Temperature_Strikes_Lockout: "OU High Liquid Line Temp Strikes Lockout",
    LennoxErrorCodes.lx_alarm_id_PureAir_Pressure_Sensor_Fault: "PA Differential Pressure Sensor Fault",
    LennoxErrorCodes.lx_alarm_id_PureAir_UV_Sensor_Fault: "PA UV Sensor Fault",
    LennoxErrorCodes.lx_alarm_id_PureAir_UV_Lamp_Off: "PA UV Lamp Off",
    LennoxErrorCodes.lx_alarm_id_PureAir_Filter_Life_10: "PA Filter Life At 10%",
    LennoxErrorCodes.lx_alarm_id_PureAir_Filter_Life_0: "PA Filter Life At 0%",
    LennoxErrorCodes.lx_alarm_id_PureAir_Model_Selection_Changed: "PA Model Selection Changed",
    LennoxErrorCodes.lx_alarm_id_PureAir_UV_Lamp_Life_0: "PA Lamp At 0% life",
    LennoxErrorCodes.lx_alarm_id_Filter_Calibration_Fail: "PA Filter Calibration Failure",
    LennoxErrorCodes.lx_alarm_id_Low_Damper_24VAC_Voltage: "ZS Low Damper 24VAC Voltage",
    LennoxErrorCodes.lx_alarm_id_Zoning_Pressure_Switch_Opened_high_pressure: "ZS Zoning Pressure Switch Opened (High Pressure)",
    LennoxErrorCodes.lx_alarm_id_Zone_1_Temp_Sensor_Problem: "ZS Zone 1 Temp Sensor Fault",
    LennoxErrorCodes.lx_alarm_id_Zone_2_Temp_Sensor_Problem: "ZS Zone 2 Temp Sensor Fault",
    LennoxErrorCodes.lx_alarm_id_Zone_3_Temp_Sensor_Problem: "ZS Zone 3 Temp Sensor Fault",
    LennoxErrorCodes.lx_alarm_id_Zone_4_Temp_Sensor_Problem: "ZS Zone 4 Temp Sensor Fault",
    LennoxErrorCodes.lx_alarm_id_ZS_Parameters_Resetting_From_Restored_Power: "ZS Parameters resetting from restored power",
    LennoxErrorCodes.lx_alarm_id_ZS_Parameters_Resetting_From_System_Interruption: "ZS Parameters resetting from system interruption",
    LennoxErrorCodes.lx_alarm_id_ZS_Humidity_Sensor_Error: "ZS Humidity Sensor Error",
    LennoxErrorCodes.lx_alarm_id_ZS_Zone_Sensor_Lost_Communication: "ZS Zone Sensor Lost Communication",
    LennoxErrorCodes.lx_alarm_id_Load_Shed_Event: "Load Shed Event",
    LennoxErrorCodes.lx_alarm_id_OD_Unit_Low_Ambient_Operational_Lockout: "OU Low Ambient Operational Lockout",
    LennoxErrorCodes.lx_alarm_id_OD_Unit_High_Ambient_Operational_Lockout: "OD Unit High Ambient Operational Lockout",
    LennoxErrorCodes.lx_alarm_id_Service_Alert: "Service Alert",
    LennoxErrorCodes.lx_alarm_id_Cooling_Capacity_Degradation: "Cooling Capacity Degradation",
    LennoxErrorCodes.lx_alarm_id_Low_Room_Temperature_Detected: "Low Room Temperature Detected",
    LennoxErrorCodes.lx_alarm_id_High_Room_Temperature_Detected: "High Room Temperature Detected",
    LennoxErrorCodes.lx_alarm_id_Comfort_Sensor_Temp_Sensor_Problem: "Thermostat  Temp Sensor Error",
    LennoxErrorCodes.lx_alarm_id_TSTAT_Temp_Above_Limit: "Thermostat Temp Above Limit",
    LennoxErrorCodes.lx_alarm_id_TSTAT_Temp_Below_Limit: "The thermostat is reading indoor temperatures below the pre-programmed limit",
    LennoxErrorCodes.lx_alarm_id_Comfort_Sensor_Humid_Sensor_Problem: "Thermostat Humid Sensor Error",
    LennoxErrorCodes.lx_alarm_id_TSAT_Indoor_Humidity_Above_Limit: "The thermostat is reading indoor humidity levels above the pre-programmed limit",
    LennoxErrorCodes.lx_alarm_id_TSAT_Indoor_Humidity_Below_Limit: "The thermostat is reading indoor humidity levels below the pre-programmed limit",
    LennoxErrorCodes.lx_alarm_id_Lost_Communication_with_Server: "Lost Communication with Server",
    LennoxErrorCodes.lx_alarm_id_Lost_Wireless_Connection_with_WAP: "Lost Wireless Connection with WAP",
    LennoxErrorCodes.lx_alarm_id_Temperature_Control_Problem: "Temperature Control Error",
    LennoxErrorCodes.lx_alarm_id_Smart: "Inconsistent Indoor Temp",
    LennoxErrorCodes.lx_alarm_id_Ohm_Check: "Ohm check - The ohm reading in the system is either too high or too low",
    LennoxErrorCodes.lx_alarm_id_Missing_Base: "Missing Base",
    LennoxErrorCodes.lx_alarm_id_Missing_Base_1: "Missing Mag Mount Base",
    LennoxErrorCodes.lx_alarm_id_Missing_TSTAT: "Thermostat Lost Connection Or Internal Fault",
    LennoxErrorCodes.lx_alarm_id_Missing_HD_Wall_display: "Missing HD wall display",
    LennoxErrorCodes.lx_alarm_id_Download_Failed: "Download Failed",
    LennoxErrorCodes.lx_alarm_id_Update_Failed: "Update Failed ",
    LennoxErrorCodes.lx_alarm_id_Firmware_Updated: "Firmware Updated",
    LennoxErrorCodes.lx_alarm_id_Too_Many_Siblings: "More Than 8 Tstats In A Group",
    LennoxErrorCodes.lx_alarm_id_Cooling_Prognostics_Alert: "Cooling Capacity Alert",
}

LENNOX_UNKNOWN_ALERT_MESSAGE = "unknown alert code"


def lennox_error_get_message_from_code(code: int):
    try:
        x = LennoxErrorCodes(code)
    except ValueError:
        x = None
    if x is not None:
        return lennox_error_messages.get(x, LENNOX_UNKNOWN_ALERT_MESSAGE)
    else:
        return LENNOX_UNKNOWN_ALERT_MESSAGE
