#!/usr/bin/env python

# -----------------------------------------------------------------------------
# A module for attempting to determine what transport mode has been supplied
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Canonical transport mode names 
_expected_modes = {'ARDOP', 'MESH', 'PACKET', 'PACTOR', 'SMTP',
                'TELNET', 'VARA', 'VARA FM'}

def mode_validator(mode: str) -> bool:
    return mode.upper() in _expected_modes

def mode_best_guess(mode: str, frequency: str) -> str:
    # Deal with the VARA modes first since there is scope for a lot of
    # variation. This module only recognises VARA and VARA FM. Anything else
    # has to fall into one of those two categories.
    #
    # The frequency used provides a hint what version of VARA we choose.
    # Typically VARA is used only on HF whereas VARA FM is only used on VHF and
    # UHF.
    
    uc_mode = mode.upper()

    if uc_mode == 'VARA FM' or \
        uc_mode == 'VARAFM' or \
            uc_mode == 'VARA-FM' or \
                uc_mode == 'VARA_FM':
        return 'VARA FM'
    elif uc_mode[:4] == 'VARA':
        return 'VARA'
    elif uc_mode[:4] == 'PACT':
        return 'PACTOR'
    else:
        raise ValueError(f'Invalid mode: {mode}')

    
__all__ = [mode_validator, mode_best_guess]