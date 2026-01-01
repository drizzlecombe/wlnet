#!/usr/bin/env python

# -----------------------------------------------------------------------------
# A module for attempting to determine what transport mode has been supplied
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Constants used in this module
# -----------------------------------------------------------------------------

# The known HF transport modes
_HF_modes = {'ARDOP', 'PACTOR', 'VARA'}

# The known internet modes. Note that MESH could be considered an RF mode, but
# it also can be an internet mode. Since it isn't being treated differently
# (i.e. we can't tell if the check-in was done over the air), we'll just assume
# it is an internet mode.
_inet_modes = {'MESH', 'SMTP', 'TELNET', 'WEBMAIL'}

# The known modes for VHF and above
_VHF_modes = {'APRS', 'PACKET', 'VARA FM'}

# Canonical transport mode names 
_expected_modes = _HF_modes.union(_inet_modes.union(_VHF_modes))

# This is the thresholds for HF frequencies. Any 
HF_FREQUENCY_UPPER_BOUNDARY = 50.0
HF_FREQUENCY_LOWER_BOUNDARY = 1.8
# -----------------------------------------------------------------------------
def mode_validator(raw_mode: str, frequency: float) -> str:
    if not isinstance(raw_mode, str):
        return None
    return  mode_best_guess((raw_mode.strip()).upper(), frequency)

# -----------------------------------------------------------------------------
def is_mode_hf(mode: str, frequency: float) -> bool:
    """
    Given a validated mode and frequency, makes the determination if this was an
    HF check-in. 
    """
    if frequency > HF_FREQUENCY_LOWER_BOUNDARY and \
        frequency < HF_FREQUENCY_UPPER_BOUNDARY:
        if mode in _HF_modes:
            return True
        else:
            raise ValueError(f'Frequency is HF ({frequency}) but mode ' 
                             f'is not valid for HF: {mode}')
    return False

# -----------------------------------------------------------------------------
# Helper functions below this point. These are not part of this module's API.
# -----------------------------------------------------------------------------
def mode_best_guess(mode: str, frequency: float) -> str:
    """Clean up a mode string as best we can
    
    This function expects the mode already to be in upper case with no
    whitespace at either end of the string.
    """
    first_mode_chars = mode[:4]
    if first_mode_chars == 'VARA':
        if frequency < HF_FREQUENCY_UPPER_BOUNDARY:
            return 'VARA'
        else:
            return 'VARA FM'
    elif first_mode_chars == 'APRS':
        return 'APRS'
    elif first_mode_chars == 'PACK':
        return 'PACKET'
    elif first_mode_chars == 'TELN':
        return 'TELNET'
    elif first_mode_chars == 'PACT':
        return 'PACTOR'
    elif first_mode_chars == 'MESH':
        return 'MESH'
    elif first_mode_chars == 'WEBM':
        return 'WEBMAIL'
    elif first_mode_chars == 'SMTP':
        return 'SMTP'
    # We have not (yet) seen these modes:
    elif first_mode_chars == 'ARDO':
        return 'ARDOP'
    else:
        raise ValueError(f'Unknown transport mode: {mode}')
    return None

# -----------------------------------------------------------------------------


__all__ = [mode_validator, is_mode_hf]