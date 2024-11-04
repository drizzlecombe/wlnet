#!/usr/bin/env python

# -----------------------------------------------------------------------------
# A module for attempting to determine what transport mode has been supplied
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Canonical transport mode names 
_expected_modes = {'ARDOP', 'MESH', 'PACKET', 'PACTOR', 'SMTP',
                'TELNET', 'VARA', 'VARA FM'}

def mode_validator(raw_mode: str, frequency: float) -> str:
    if not isinstance(raw_mode, str):
        return None
    intermediate_mode = (raw_mode.strip()).upper()
    canonical_mode = mode_best_guess(intermediate_mode, frequency)
    return canonical_mode

def mode_best_guess(mode: str, frequency: float) -> str:
    """Clean up a mode string as best we can
    
    This function expects the mode already to be in upper case with no
    whitespace at either end of the string.
    """
    first_mode_chars = mode[:4]
    if first_mode_chars == 'VARA':
        if frequency < 50.0:
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
    elif first_mode_chars == 'SMTP':
        return 'SMTP'
    # We have not (yet) seen these modes:
    elif first_mode_chars == 'ARDO':
        return 'ARDOP'
    else:
        raise ValueError(f'Unknown transport mode: {mode}')
    return None
    
__all__ = [mode_validator]