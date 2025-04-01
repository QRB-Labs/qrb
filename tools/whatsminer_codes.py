WHATSMINER_API_MESSAGE_CODES = {
    14: "invalid API command or data",
    23: "invalid json message",
    45: "permission denied",
    131: "command OK",
    132: "command error",
    134: "get token message OK",
    135: "check token error",
    136: "token over max time"
}

def check_response(resp):
    assert resp['Code'] == 131, "API response error"
    assert resp['STATUS'] == 'S', "API response error"


WHATSMINER_ERROR_CODES = {
    70: {
        "message": "Error",
        "description": "Generic error; specific issue may be detailed in logs or additional response fields.",
        "likely_cause": "Unspecified failure (check logs)."
    },
    71: {
        "message": "Invalid Command",
        "description": "The submitted command is not recognized or supported by the API version/firmware.",
        "likely_cause": "Typo or outdated command (e.g., 'foobar')."
    },
    72: {
        "message": "Permission Denied",
        "description": "Command requires authentication or higher privileges, and no valid session/token was provided.",
        "likely_cause": "Missing API token or insufficient rights."
    },
    80: {
        "message": "Fan Error",
        "description": "Fan malfunction detected (e.g., stopped, low RPM, or failure).",
        "likely_cause": "Faulty fan or connection issue."
    },
    81: {
        "message": "Temp Too High",
        "description": "Temperature exceeds safe operational threshold (e.g., hashboard > 80°C).",
        "likely_cause": "Overheating; check cooling or ambient conditions."
    },
    82: {
        "message": "Hashboard Missing",
        "description": "One or more hashboards not detected by the control board.",
        "likely_cause": "Loose connection, dead board, or firmware glitch."
    },
    83: {
        "message": "Power Supply Error",
        "description": "PSU voltage or wattage issue detected, affecting miner operation.",
        "likely_cause": "Unstable PSU or insufficient power."
    },
    84: {
        "message": "Chain Error",
        "description": "Communication failure between control board and hashboard chain.",
        "likely_cause": "Cable issue or hashboard failure."
    },
    710: {
        "message": "Hashrate Low",
        "description": "Hashrate on one or more hashboards is below expected threshold.",
        "likely_cause": "Overheating, faulty board, or power instability."
    },
    711: {
        "message": "Hashrate Zero",
        "description": "No hashrate detected from a hashboard (complete failure).",
        "likely_cause": "Dead hashboard or severe connection issue."
    },
    712: {
        "message": "Overclock Failure",
        "description": "Attempt to overclock (via custom firmware or settings) failed.",
        "likely_cause": "Unsupported hardware or firmware limits exceeded."
    },
    1000: {
        "message": "Busy",
        "description": "Miner is processing another command or temporarily unavailable to respond.",
        "likely_cause": "API overload or miner in reboot cycle."
    },
    1001: {
        "message": "Timeout",
        "description": "Command execution timed out; no response from miner hardware.",
        "likely_cause": "Network issue or miner unresponsive."
    },
    2000: {
        "message": "Firmware Error",
        "description": "Issue during firmware upgrade or validation (e.g., 'NeedUpgradeAgain' state).",
        "likely_cause": "Corrupted firmware file or interrupted update."
    }
}


    

