# https://www.whatsminer.com/file/WhatsminerAPI%20V2.0.3.pdf
WHATSMINER_API_MESSAGE_CODES = {
    14: "invalid API command or data",
    23: "invalid json message",
    45: "permission denied",
    131: "command OK",
    132: "command error",
    134: "get token message OK",
    135: "check token error",
    136: "token over max time",
    137: "Base64 decode error"
}


# https://auradine.com/wp-content/uploads/2025/02/TeraFlux-Miner-API-Reference.pdf
TERAFLUX_API_MESSAGE_CODES = {
    7: "pools",
    9: "devs",
    11: "summary",
    69: "devdetails",
}


# https://whatsminer.net/wp-content/uploads/2021/07/Error-Code-Descriptions-20210406.pdf
# https://whatsminer.net/wp-content/uploads/2021/11/Whatsminer-Error-Code-Description-20210930.pdf
# https://www.zeusbtc.com/articles/asic-miner-troubleshooting/1688-how-to-deal-with-fault-codes-of-whatsminer-series
# https://aryaminer.com/blogs/artical/whatsminer-error-code
WHATSMINER_ERROR_CODES = {
    110: {"message": "Fanin detect speed error",
          "action": "Check whether the fan connection is normal, or replace the power supply, or replace the fan"
    },
    111: {"message": "Fanout detect speed error",
          "action": "Check whether the fan connection is normal, or replace the power supply, or replace the fan"
    },
    120: {"message": "Inlet fan speed error (Deviation 2000+)",
          "action": "Check fan connection, replace if necessary"
    },
    121: {"message": "Outlet fan speed error (Deviation 2000+)",
          "action": "Replace the fan"
    },
    130: {"message": "Fanin speed error",
          "action": "Check whether the fan connection is normal, or replace the power supply, or replace the fan"
    },
    131: {"message": "Fanout speed error",
          "action": "Check whether the fan connection is normal, or replace the power supply, or replace the fan"
    },
    140: {"message": "Fan speed is too high",
          "action": "Please check the environment temperature"
    },
    200: {"message": "Power probing error, no power found",
          "action": "Detecting power output wiring, updating the latest firmware, or replacing power supply"
    },
    201: {"message": "Power supply and configuration file mismatch",
          "action": "Replace the correct PSU"
    },
    202: {"message": "Power vout error, set: 1050, get: 0",
          "action": ''
    },
    203: {"message": "Power protecting",
          "action": "Please check the environment temperature"
    },
    204: {"message": "Power current protecting",
          "action": "Please check the environment temperature"
    },
    205: {"message": "Power current error",
          "action": "Inspection of power supply in power grid"
    },
    206: {"message": "Power input voltage is low",
          "action": "Improve power supply conditions and input voltage"
    },
    207: {"message": "Power input current protecting",
          "action": "Improve power supply conditions and input voltage"
    },
    208: {"message": "PSU changes too much",
          "action": "Replace the power supply"
    },
    210: {"message": "Power error status",
          "action": "Check power failure code",
    },
    213: {"message": "Power input voltage and current do not match the power",
          "action": "Replace the PSU"
    },
    217: {"message": "Power set enable error. set: 1, get: 0",
          "action": ""
    },
    233: {"message": "Power output over temperature protection",
          "action": "Please check the environment temperature"
    },
    234: {"message": "Power output over temperature protection",
          "action": "Please check the environment temperature"
    },
    235: {"message": "Power output over temperature protection",
          "action": "Please check the environment temperature"
    },
    236: {"message": "Power output over-current protection 0. code: 0x40008",
          "action": "Please check the environment temperature，check copper row screw"
    },
    237: {"message": "Overcurrent Protection of Power Output",
          "action": "Please check the environment temperature，check copper row screw"
    },
    238: {"message": "Overcurrent Protection of Power Output",
          "action":  "Please check the environment temperature，check copper row screw"
    },
    239: {"message": "Overvoltage Protection of Power Output",
          "action": "Inspection of power supply in power grid"
    },
    240: {"message": "Low Voltage Protection for Power Output",
          "action": "Inspection of power supply in power grid"
    },
    241: {"message": "Power output current imbalance",
          "action": "Replace the power"
    },
    243: {"message": "Over-temperature Protection for Power Input",
          "action": "Please check the environment temperature"
    },
    244: {"message": "Over-temperature Protection for Power Input",
          "action": "Please check the environment temperature"
    },
    245: {"message": "Over-temperature Protection for Power Input",
          "action": "Please check the environment temperature"
    },
    246: {"message": "Overcurrent Protection for Power Input",
          "action": "Please check the environment temperature"
    },
    247: {"message": "Overcurrent Protection for Power Input",
          "action": "Please check the environment temperature"
    },
    248: {"message": "Overvoltage Protection for Power Input",
          "action": "Inspection of input voltage in powergrid"
    },
    249: {"message": "Overvoltage Protection for Power Input",
          "action": "Inspection of input voltage in powergrid"
    },
    250: {"message": "Undervoltage Protection for Power Input",
          "action": "Inspection of input voltage in powergrid"
    },
    251: {"message": "Undervoltage Protection for Power Input",
          "action": "Inspection of input voltage in power grid"
    },
    253: {"message": "Power Fan Error",
          "action": "Replace the PSU"
    },
    254: {"message": "Power Fan Error",
          "action": "Replace the PSU"
    },
    255: {"message": "Protection of over power output",
          "action": "Please check the environment temperature"
    },
    256: {"message": "Protection of over power output",
          "action": "Please check the environment temperature"
    },
    257: {"message": "Input over current protection of power supply primary side",
          "action": "Try to power off and restart, no effect to replace the power supply"
    },
    263: {"message": "Power communication warning",
          "action": "Check whether the screws of the control board are locked"
    },
    264: {"message": "Power communication error",
          "action": "Check whether the screws of the control board are locked"
    },
    267: {"message": "Power watchdog protection",
          "action": "Contact the technician in time"
    },
    268: {"message": "Power output over-current protection",
          "action": "Check the ambient temperature, check the copper bar screw"
    },
    269: {"message": "Power input over-current protection",
          "action": "Improve power supply conditions and input voltage"
    },
    270: {"message": "Power input over-voltage protection",
          "action": "Inspection of input voltage in power grid"
    },
    271: {"message":
          "Power input under-voltage protection",
          "action": "Inspection of input voltage in power grid"
    },
    272: {"message": "Warning of excessive power output of power supply",
          "action": "Please check the environment temperature"
    },
    273: {"message": "Power input power too high warning",
          "action": "Please check the environment temperature"
    },
    274: {"message": "Power fan warning",
          "action": "Check if the power fan is blocked andmayneed to be replaced"
    },
    275: {"message": "Power over temperature warning",
          "action": "Please check the environment temperature"
    },
    300: {"message": "SM0 temperature sensor detection error",
          "action": "Check the connection of the hashboard"
    },
    301: {"message": "SM1 temperature sensor detection error",
          "action": "Check the connection of the hashboard"
    },
    302: {"message": "SM2 temperature sensor detection error",
          "action": "Check the connection of the hashboard"
    },
    309: {"message": "All temperature sensor detection errors",
          "action": "Check the connection of the hashboard"
    },
    320: {"message": "SM0 temperature reading error",
          "action": "Check whether the control board screwislocked properly, check the connection board and the arrangement contact"
    },
    321: {"message": "SM1 temperature reading error",
          "action": "Check whether the control board screwislocked properly, check the connectionboardand the arrangement contact"
    },
    322: {"message": "SM2 temperature reading error",
          "action": "Check whether the control board screwislocked properly, check the connectionboardand the arrangement contact"
    },
    329: {"message": "Control board temperature sensor communication error",
          "action": "Replace the power supply"
    },
    350: {"message": "SM0 temperature protecting",
          "action": "Please check the environment temperature"
    },
    351: {"message": "SM1 temperature protecting",
          "action": "Please check the environment temperature"
    },
    352: {"message": "SM2 temperature protecting",
          "action": "Please check the environment temperature"
    },
    360: {"message": "The temperature of the hashboard is overheating",
          "action": "Replace the thermal interface of the boards."
    },
    370: {"message": "The environment temperature fluctuates too much.",
          "action": "Check the environment temperature, or check the environment wind direction and wind speed."
    },
    410: {"message": "SM0 detect eeprom error",
          "action": "Check adapter board and wiring contact"
    },
    411: {"message": "SM1 detect eeprom error",
          "action": "Check adapter board and wiring contact"
    },
    412: {"message": "SM2 detect eeprom error",
          "action": "Check adapter board and wiring contact"
    },
    420: {"message": "SM0 parser eeprom error",
          "action": "Contact the technician in time"
    },
    421: {"message": "SM1 parser eeprom error",
          "action": "Contact the technician in time"
    },
    422: {"message": "SM2 parser eeprom error",
          "action": "Contact the technician in time"
    },
    430: {"message": "SM0 chip bin type error",
          "action": "Contact the technician in time"
    },
    431: {"message": "SM1 chip bin type error",
          "action": "Contact the technician in time"
    },
    432: {"message": "SM2 chip bin type error",
          "action": "Contact the technician in time"
    },
    440: {"message": "SM0 eeprom chip num X error",
          "action": "Contact the technician in time"
    },
    441: {"message": "SM1 eeprom chip num X error",
          "action": "Contact the technician in time"
    },
    442: {"message": "SM2 eeprom chip num X error",
          "action": "Contact the technician in time"
    },
    510: {"message": "SM0 miner type error",
          "action": "The version and type of hashboard areinconsistent, replace the correct hashboard"
    },
    511: {"message": "SM1 miner type error",
          "action": "The version and type of hashboard areinconsistent, replace the correct hashboard"
    },
    512: {"message": "SM2 miner type error",
          "action": "The version and type of hashboard areinconsistent, replace the correct hashboard"
    },
    530: {"message": "SM0 not found",
          "action": "Check the connection and arrangement oftheadapter board, or replace the controlboard, check whether the hash boardconnector is empty welded"
    },
    531: {"message": "SM1 not found",
          "action": "Check the connection and arrangement oftheadapter board, or replace the controlboard, check whether the hash boardconnector is empty welded"
    },
    532: {"message": "SM2 not found",
          "action": "Check the connection and arrangement oftheadapter board, or replace the controlboard, check whether the hash boardconnector is empty welded"
    },
    540: {"message": "SM0 reading chip id error",
          "action": "Check adapter board and wiring contact，Clean the dust on the hashboard"
    },
    541: {"message": "SM1 reading chip id error",
          "action": "Check adapter board and wiring contact，Clean the dust on the hashboard"
    },
    542: {"message": "SM2 reading chip id error",
          "action": "Check adapter board and wiring contact，Clean the dust on the hashboard"
    },
    550: {"message": "SM0 have bad chips",
          "action": "Replacement of bad chips"
    },
    551: {"message": "SM1 have bad chips",
          "action": "Replacement of bad chips"
    },
    552: {"message": "SM2 have bad chips",
          "action": "Replacement of bad chips"
    },
    560: {"message": "SM0 loss balance",
          "action": "Plug in the adapter plate, and then screwin the power connection hashboard again"
    },
    561: {"message": "SM1 loss balance",
          "action": "Plug in the adapter plate, and then screwin the power connection hashboard again"
    },
    562: {"message": "SM2 loss balance",
          "action": "Plug in the adapter plate, and then screwin the power connection hashboard again"
    },
    600: {"message":
          "Environment temperature is high",
          "action": "Please check the environment temperature"
    },
    610: {"message": "If the ambient temperature is too high in high performance mode, return to normal mode",
          "action": "Check the ambient temperature, high performance mode needs to be controlled below 30 ℃"
    },
    701: {"message": "Control board no support chip",
          "action:": "Upgrade the corresponding type of firmware"
    },
    702: {"message": "Control board version unknown",
          "action": "Contact after-sales"
    },
    710: {"message": "Control board rebooted as exception",
          "action": "Updating the latest firmware. Check whether the control board screw is locked properly"
    },
    712: {"message": "Control board rebooted as exception",
          "action": "Updating the latest firmware. Check whether the control board screw is locked properly"
    },
    714: {"message": "The network connection is seriously unstable",
          "action": "Check the network cable connection or replace the control board"
    },
    800: {"message": "cgminer checksum error",
          "action": "Re-upgrade firmware"
    },
    801: {"message": "system-monitor checksum error",
          "action": "Re-upgrade firmware"
    },
    802: {"message":
          "remote-daemon checksum error",
          "action": "Re-upgrade firmware"
    },
    2000: {"message": "No pool information configured",
           "action": "Check pool configuration"
    },
    2010: {"message": "All pools are disable",
           "action": "Please check the network or pools configure"
    },
    2020: {"message": "Pool0 connect failed",
           "action": "Please check the network or pools configure"
    },
    2021: {"message": "Pool1 connect failed",
           "action": "Please check the network or pools configure"
    },
    2022: {"message": "Pool2 connect failed",
           "action": "Please check the network or pools configure"
    },
    2030: {"message": "High rejection rate of pool",
           "action": "Please check the network or pools configure. Setting of mining currency"
    },
    2040: {"message": "The pool does not support the asicboost mode",
           "action": "Check pool configuration"
    },
    2050: {"message": "Failed to switch to new pool",
           "action": "check the network or pools configure"
    },
    2310: {"message": "Hash rate is too low",
           "action": "Check input voltage, network environment, and ambient temperature"
    },
    2320: {"message": "Hash rate is too low",
           "action": "Check input voltage, network environment, and ambient temperature"
    },
    2340: {"message": "The loss of hash rate is too high",
           "action": "Check input voltage, network environment, and ambient temperature"
    },
    2350: {"message": "The loss of hash rate is too high",
           "action": "Check input voltage, network environment, and ambient temperature"
    },
    5110: {"message": "SM0 Frequency Up Timeout",
           "action": "reboot"
    },
    5111: {"message": "SM1 Frequency Up Timeout",
           "action": "reboot"
    },
    5112: {"message": "SM2 Frequency Up Timeout",
           "action": "reboot"
    },
    8000: {"message": "WhatsMinerTool version too low",
           "action": "Download and install the latest WhatsMinerTool"
    },
    8010: {"message": "Frequency not up to standard",
           "action": "Upgrade to the latest software"
    },
    8020: {"message": "Hashrate not up to standard",
           "action": "Ensure proper cooling and update software"
    },
    8400: {"message": "Wrong software version installed",
           "action": "Upgrade to the correct version"
    },
    8410: {"message": "Incorrect firmware version for miner model",
           "action": "Flash the correct firmware"
    },
    8700: {"message": "Miner and PSU model mismatch",
           "action": "Replace with the correct PSU"
    },
    9100: {"message": "Process blocked",
           "action": ""
    },
    9110: {"message": "Process blocked",
           "action": ""
    },
    100001: {"message":  "/antiv/signature Illegal",
             "action":  "Flash the ASIC with SD card, then with WhatsMinerTool."
    },
    100002: {"message": "/antiv/dig/initd.dig Illegal",
             "action": "Flash the ASIC with SD card, then with WhatsMinerTool."
    },
    100003: {"message": "/antiv/dig/pf_partial.dig Illegal",
             "action": "Flash the ASIC with SD card, then with WhatsMinerTool."
    },
    
    # PSU error codes

    0x0001: {"message": "Input undervoltage",
             "action": "Check the power supply"
    },
    0x0002: {"message": "Temperature sampling over temperature protection of power radiator",
             "action": "Power on again after 10 minutes of power failure. If it occurs again, replace the power supply"
    },
    0x0004: {"message":
             "Temperature sampling over temperature protection of power radiator",
             "action": "Power on again after 10 minutes of powerfailure. If it occurs again, replace the power supply"
    },
    0x0008: {"message": "Over temperature protection of environmental temperature sampling in power supply",
             "action": "Power on again after 10 minutes of power failure. If it occurs again, replace the power supply"
    },
    0x0010: {"message": "Primary side over current",
             "action": "Power on again after 10 minutes of power failure. If it occurs again, replace the power supply"
    },
    0x0020: {"message": "Output undervoltage" ,
             "action": "Check the power supply",
    },
    0x0040: {"message": "Output over current (continuous load 320A for more than 2S)",
             "action": "Tighten the copper bar screw again"
    },
    0x0080: {"message": "Primary side over current",
             "action": "Power on again after 10 minutes of powerfailure. If it occurs again, replace the power supply"
    },
    0x0100: {"message": "Single circuit overcurrent (protection point 120a)",
             "action": "Check the PSU"
    },
    0x0200: {"message": "Single circuit overcurrent (protection point 120a)",
             "action": "Check the PSU"
    },
    0x0400: {"message": "Single circuit overcurrent (protection point 120a)",
             "action": "Check the PSU"
    },
    0x0800: {"message": "Fan failure",
             "action": "Replace the PSU"
    },
    0x1000: {"message": "Output over current (continuous load of 310A for more than 5min)",
             "action": "Check the PSU"
    },
    0x2000: {"message": "Output over current (continuous load 295A for more than 10min)",
             "action": "Check the PSU"
    }
}
