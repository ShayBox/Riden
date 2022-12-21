class Register:
    # Init
    ID = 0
    SN_H = 1
    SN_L = 2
    FW = 3
    # Info
    INT_C_S = 4
    INT_C = 5
    INT_F_S = 6
    INT_F = 7
    V_SET = 8
    I_SET = 9
    V_OUT = 10
    I_OUT = 11
    AH = 12
    P_OUT = 13
    V_IN = 14
    KEYPAD = 15
    OVP_OCP = 16
    CV_CC = 17
    OUTPUT = 18
    PRESET = 19
    I_RANGE = 20  # Used on RD6012p
    # Unused/Unknown 21-31
    BAT_MODE = 32
    V_BAT = 33
    EXT_C_S = 34
    EXT_C = 35
    EXT_F_S = 36
    EXT_F = 37
    AH_H = 38
    AH_L = 39
    WH_H = 40
    WH_L = 41
    # Unused/Unknown 42-47
    # Date
    YEAR = 48
    MONTH = 49
    DAY = 50
    # Time
    HOUR = 51
    MINUTE = 52
    SECOND = 53
    # Unused/Unknown 54
    # Calibration
    # DO NOT CHANGE Unless you know what you're doing!
    V_OUT_ZERO = 55
    V_OUT_SCALE = 56
    V_BACK_ZERO = 57
    V_BACK_SCALE = 58
    I_OUT_ZERO = 59
    I_OUT_SCALE = 60
    I_BACK_ZERO = 61
    I_BACK_SCALE = 62
    # Unused/Unknown 63-65
    # Settings/Options
    OPT_TAKE_OK = 66
    OPT_TAKE_OUT = 67
    OPT_BOOT_POW = 68
    OPT_BUZZ = 69
    OPT_LOGO = 70
    OPT_LANG = 71
    OPT_LIGHT = 72
    # Unused/Unknown 73-79
    # Presets
    M0_V = 80
    M0_I = 81
    M0_OVP = 82
    M0_OCP = 83
    M1_V = 84
    M1_I = 85
    M1_OVP = 86
    M1_OCP = 87
    M2_V = 88
    M2_I = 89
    M2_OVP = 90
    M2_OCP = 91
    M3_V = 92
    M3_I = 93
    M3_OVP = 94
    M3_OCP = 95
    M4_V = 96
    M4_I = 97
    M4_OVP = 98
    M4_OCP = 99
    M5_V = 100
    M5_I = 101
    M5_OVP = 102
    M5_OCP = 103
    M6_V = 104
    M6_I = 105
    M6_OVP = 106
    M6_OCP = 107
    M7_V = 108
    M7_I = 109
    M7_OVP = 110
    M7_OCP = 111
    M8_V = 112
    M8_I = 113
    M8_OVP = 114
    M8_OCP = 115
    M9_V = 116
    M9_I = 117
    M9_OVP = 118
    M9_OCP = 119
    # Unused/Unknown 120-255
    SYSTEM = 256
    # NOT REGISTERS - Magic numbers for the registers
    BOOTLOADER = 5633
