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
class Gateway:
    
    def __init__(self, identifier: str, frequency: float):
        """
        identifier is the callsign-ssid. For example: N1ACW-10. frequency is the
        operating frequency for this gateway.

        The reason why we need this class is that some gateways have the same
        identifier but operate on separate frequencies. This also means that
        they probably are physically different (separate radio and antenna
        system.) We used to treat RMSs the same if they had the same identifier,
        but now we differentiate those with the same identifier but different
        frequencies.
        
        For example: W7YAM-10 on 144.970 MHz and W7YAM-10 on 441.050 MHz are now
        considered different RMSs (as of 11th August 2024 (net week 197)).
        """
        self.identifier = identifier
        self.frequency = frequency

    def is_satellite(self):
        """We special case telnet checkins that use space satellite
        communications because we encourage AUXCs to think outside amateur radio
        use. At the moment the only service that offers readily available
        internet access via satellite is Starlink."""
        return self.identifier == 'STARLINK' and self.frequency == 0.0

    def __eq__(self, other):
        return self.identifier == other.identifier and \
               self.frequency == other.frequency

    def __hash__(self):
        # Returning the hash of a tuple seems to be the standard way of doing
        # this.
        return hash((self.identifier, self.frequency))

    def __repr__(self):
        return f'{self.identifier}, {self.frequency}'

# -----------------------------------------------------------------------------
# All known gateways and the number of times they have been used. 
# Prepopulate with values for telnet sessions
# -----------------------------------------------------------------------------
_gw_satellite = Gateway('STARLINK', 0.0)
_gw_telnet = Gateway('N/A', 0.0) # Note - this handles APRS also.

_all_gateways: dict[Gateway, int] = {
    _gw_telnet: 0, 
    _gw_satellite: 0}

# -----------------------------------------------------------------------------
# Match various guises of the not applicable gateway value.

NA_pattern = re.compile('N */ *A')

# -----------------------------------------------------------------------------
# Store a gateway that an AUXC has used and, as a side effect, increment its use
# counter.
# -----------------------------------------------------------------------------
def register_gateway(raw_gateway_id: str, frequency: float) -> Gateway:
    """
    Gateways can be specified as:
        1) N/A - when telnet or SMTP mail has been used to checkin.
        2) a callsign hyphen SSID - this is the most common way. 
            For example W7YAM-10
        3) a callsign only - often seen with HF RMS gateways and the mesh.
            For example: AI7NC (a mesh gateway in Eugene)
        4) Starlink - when the Starlink service is being used for mobile
           operations.
    Returns gateway object
    """
    if not isinstance(raw_gateway_id, str):
        raise ValueError(f'Gateway identifier is not a string: {raw_gateway_id}')
    
    canonical_gateway_id = raw_gateway_id.strip().upper()

    if NA_pattern.match(canonical_gateway_id):
        if frequency in {0.0, 144.390}: #@TODO - handle APRS differently
            _all_gateways[_gw_telnet] = _all_gateways.get(_gw_telnet, 0) + 1
            return _gw_telnet
        else: # frequency != 0.0
            raise ValueError('Gateway is N/A (telnet over non-satellite internet) '
                             f'but frequency not 0.0 ({frequency})')
    
    elif canonical_gateway_id == 'STARLINK':
        if frequency == 0.0:
            _all_gateways[_gw_satellite] = _all_gateways.get(_gw_satellite, 0) + 1
            return _gw_satellite
        else: # frequency != 0.0:
            raise ValueError('Gateway is telnet over satellite '
                         f'but frequency not 0.0 ({frequency})')

    else:
        validated_gw_callsign = validate_callsign(canonical_gateway_id)
        if validated_gw_callsign is not None:
            # Now, let's see if there is an SSID and if so, see if it is in
            # the expected range.
            # @TODO - could there be RMS callsign suffixes that are nonnumerical?
            if len(validated_gw_callsign.suffix) >= 1:
                ssid_val = int(validated_gw_callsign.suffix)
                if not (ssid_val >= 0 and ssid_val <= 15):
                    raise ValueError("Gateway has an invalid SSID because it's not an integer: "
                                    f'{raw_gateway_id}: {ssid_val}')
            return Gateway(canonical_gateway_id, frequency)
        else:
            raise ValueError('Gateway has an invalid callsign: '
                            f'{raw_gateway_id}, {validated_gw_callsign}')
