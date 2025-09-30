#!/usr/bin/env python

# -----------------------------------------------------------------------------
# A module for validating a checkin's gateway
#
# A gateway either looks like a callsign, possibly with a numeric suffix OR it
# can be N/A when Telnet is used as the mode.
#
# -----------------------------------------------------------------------------

import re
from callsign_processing import Callsign, validate_callsign


# -----------------------------------------------------------------------------
# Match various guises of the not applicable gateway value.

NA_pattern = re.compile('N */ *A')

# -----------------------------------------------------------------------------
# Canonical transport gateway names

def gateway_validator(raw_gateway_id: str) -> str:
    """Clean up a gateway string as best we can
    
    Gateways can be specified as:
        1) N/A - when telnet or SMTP mail has been used to checkin.
        2) a callsign hyphen SSID - this is the most common way. 
            For example W7YAM-10
        3) a callsign only - often seen with HF RMS gateways and the mesh.
            For example: AI7NC (a mesh gateway in Eugene)
        4) Starlink - when the Starlink service is being used for mobile
           operations.
    Returns gateway_id
    """
    if not isinstance(raw_gateway_id, str):
        raise ValueError(f'Unknown value for a gateway identifier: {raw_gateway_id}')
    
    canonical_gateway_id = raw_gateway_id.strip().upper()

    if NA_pattern.match(canonical_gateway_id):
        return 'N/A'
    elif canonical_gateway_id == 'STARLINK':
        return 'STARLINK'
    
    validated_gw_callsign = validate_callsign(canonical_gateway_id)
    if validated_gw_callsign is None:
        raise ValueError('Gateway has an invalid callsign: '
                         f'{raw_gateway_id}, {validated_gw_callsign}')
    
    # To get here, the gateway's callsign must match a regular callsign
    # pattern. Now, let's see if there is an SSID and if so, see if it is in
    # the expected range.

    if len(validated_gw_callsign.suffix) > 1:
        ssid_val = int(validated_gw_callsign.suffix)
        if not (ssid_val >= 0 and ssid_val <= 15):
            raise ValueError('Gateway has an invalid SSID: '
                             f'{raw_gateway_id}: {ssid_val}')

    return (canonical_gateway_id)
    
__all__ = [gateway_validator]