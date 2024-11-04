#!/usr/bin/env python

# -----------------------------------------------------------------------------
# A module for validating a checkin's gateway
#
# A gateway either looks like a callsign, possibly with a numeric suffix OR it
# can be N/A when Telnet is used as the mode.
#
# -----------------------------------------------------------------------------

from callsign_processing import validate_callsign

# -----------------------------------------------------------------------------
# Canonical transport gateway names 

def gateway_validator(gateway_callsign: str, frequency: float,
                        mode: str) -> str:
    
    if not isinstance(gateway_callsign, str):
        return None
    intermediate_gateway = (gateway_callsign.strip()).upper()
    canonical_mode = (mode.strip()).upper()
    (canonical_gateway, clean_mode) = gateway_best_guess(intermediate_gateway,
                                           frequency,
                                           canonical_mode)
    return (canonical_gateway, clean_mode)

def gateway_best_guess(gateway_id: str, frequency: float, mode: str) -> str:
    """Clean up a gateway string as best we can
    
    Gateways can be specified as:
        1) a callsign hyphen SSID - this is the most common way. 
            For example W7YAM-10
        2) a callsign only - often seen with HF RMS gateways and the mesh.
            For example: AI7NC (a mesh gateway in Eugene)
        3) N/A - when telnet or SMTP mail has been used to checkin.

    This function also attempts to clean up the frequency. For Telnet, this is
    easy: 0.0 is used. For everything else, the frequency is just passed back
    at this time.

    Returns (gateway_id, frequency)
    """
    # Deal with the simple one first - Telnet mode. 
    if mode == 'TELNET' or mode == 'APRS' or mode == 'SMTP' or mode == 'MESH':
        return ('N/A', 0.0)
    
    # Okay, the mode must use a callsign, possibly with an SSID.
    gateway_id_parts = gateway_id.split(sep='-') # Might have to use a RE here.

    # We should have a callsign in gateway_parts[0] and, if there is an SSID,
    # that should be in gateway_parts[1].

    validated_gw_callsign = validate_callsign(gateway_id_parts[0])
    if validated_gw_callsign is None:
        raise ValueError('Gateway has an invalid callsign: '
                         f'{gateway_id}, {validated_gw_callsign}')
    
    # To get here, the gateway's callsign must match a regular callsign
    # pattern. Now, let's see if there is an SSID and if so, see if it is in
    # the expected range.

    if len(gateway_id_parts) > 1:
        ssid_val = int(gateway_id_parts[1])
        if not (ssid_val >= 0 and ssid_val <= 15):
            raise ValueError('Gateway has an invalid SSID: '
                             f'{gateway_id}: {ssid_val}')

    return (gateway_id, frequency)
    
__all__ = [gateway_validator]