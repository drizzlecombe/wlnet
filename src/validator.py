from string import capwords

from callsign_processing import validate_callsign
from transport_modes import mode_validator
from gateway import gateway_validator
from location import location_check

MAX_WEEK_NUMBER = 200 # TODO - load this from a config file
MAX_FREQUENCY = 5800.0 # TODO - load this from a config file

# -----------------------------------------------------------------------------
# All the checkins - valid and invalid.
# -----------------------------------------------------------------------------
_valid_checkins = []
_invalid_checkins = []

# -----------------------------------------------------------------------------
# Holds checkin information and contains the individual field validators
# -----------------------------------------------------------------------------
class Checkin:
    # The highest week number seen is considered to be the previous week's net
    # identifier.

    max_week_number = 0

    def __init__(self, week_number: str,
                 callsign: str,
                 transport_mode: str,
                 gateway: str,
                 frequency: str,
                 location: str,
                 county: str,
                 state: str ) -> None:

        # Check frequency first because this is the only value that is
        # not a string. If input values are in the wrong category, this
        # will most likely detect the issue.
        self.frequency = self.check_frequency(frequency)
        self.week_number = self.check_week_number(week_number)

        if self.week_number > Checkin.max_week_number:
            Checkin.max_week_number = self.week_number

        self.callsign = self.check_callsign(callsign)
        self.transport_mode = self.check_mode(transport_mode, self.frequency)
        self.gateway = gateway_validator(gateway)

        self.location = self.check_location(location)
        self.county = county
        if not isinstance(state, str):
            raise ValueError(f'State is not a string: {state}')
        if len(state) == 2:
            self.state = state.upper()
        else:
            self.state = state.capitalize()

    #--------------------------------------------------------------------------
    def check_frequency(self, frequency: str) -> float:
        canonical_frequency = None
        try:
            canonical_frequency = float(frequency)
        except Exception as e:
            raise ValueError(f'Frequency: {e}')
        if canonical_frequency >= 0.0 and canonical_frequency > MAX_FREQUENCY:
            raise ValueError(f'Frequency: {frequency}')
        return canonical_frequency

    #--------------------------------------------------------------------------
    def check_week_number(self, week_number: str) -> int:
        canonical_week_num = int(week_number)
        if canonical_week_num < 0 or canonical_week_num > MAX_WEEK_NUMBER:
            raise ValueError(f'Week number: {self.week_number}')
        return canonical_week_num

    #--------------------------------------------------------------------------
    def check_mode(self, transport_mode: str, frequency: float) -> str:
        checked_mode = mode_validator(transport_mode, frequency)
        if checked_mode is not None:
            self.transport_mode = checked_mode
        else:
            raise ValueError(f'Mode: {self.transport_mode}')
        return checked_mode

    #--------------------------------------------------------------------------
    def check_callsign(self, callsign: str) -> str:
        canonical_callsign = validate_callsign(callsign)
        if canonical_callsign is None:
            raise ValueError(f'Callsign: {callsign}')
        return canonical_callsign

    #--------------------------------------------------------------------------
    def check_location(self, location: str) -> str:
        (best_guess, likelihood) = location_check(location)
        if likelihood > 0.7:
            # print(f'Hit  ({likelihood}): {location} -> {best_guess}')
            return best_guess
        elif location.upper() == 'N/A':
            # This is where there is no location in Lake Oswego associated
            # with the checkin. I.e. the checkin came from outside Lake Oswego.
            return 'N/A'
        else:
            #print(f'Miss ({likelihood}): {location} (skip nearest: {best_guess}) -> {capwords(location)}')
            return capwords(location)
        
    #--------------------------------------------------------------------------
    def __repr__(self) -> str:
        return f'{self.week_number},{self.callsign},{self.transport_mode},'\
            f'{self.gateway},{self.frequency:.4f},{self.location},'\
            f'{self.state}'
    #--------------------------------------------------------------------------
    def __str__(self) -> str:
        return self.__repr__()

    def as_dict(self) -> dict:
        return {'week_number' : self.week_number,
                   'callsign' : self.callsign,
                   'transport_mode' : self.transport_mode,
                   'gateway' : self.gateway,
                   'frequency' : self.frequency,
                   'location' : self.location,
                   'county' : self.county,
                   'state' : self.state}
#------------------------------------------------------------------------------
# Module interface below
#------------------------------------------------------------------------------
def validate_checkins(raw_checkins: list[dict]) -> tuple[list[Checkin] , list[Checkin]]:

    for raw_checkin in raw_checkins:
        try:
            check_in = Checkin(raw_checkin['week_number'],
                            raw_checkin['callsign'],
                            raw_checkin['transport_mode'],
                            raw_checkin['gateway'],
                            raw_checkin['frequency'],
                            raw_checkin['location'],
                            raw_checkin['county'],
                            raw_checkin['state'])
        except ValueError as e:
            print(f'Invalid checkin. {e}:\n{raw_checkin}')
            _invalid_checkins.append(raw_checkin)

        _valid_checkins.append(check_in)

    return (_valid_checkins, _invalid_checkins)
