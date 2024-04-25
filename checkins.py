from string import capwords

from callsign_processing import validate_callsign
from transport_modes import mode_validator
from gateway import gateway_validator
from location import neighbourhood_check
from storage import save_checkin

MAX_WEEK_NUMBER = 100 # TODO - load this from a config file
MAX_FREQUENCY = 5800.0 # TODO - load this from a config file


# -----------------------------------------------------------------------------
# All the checkins
# -----------------------------------------------------------------------------
_all_checkins = []

class _Checkin:
    def __init__(self, week_number: int,
                 callsign: str,
                 transport_mode: str,
                 gateway: str,
                 gw_frequency: float,
                 neighbourhood: str,
                 county: str,
                 state: str ) -> None:

        self.week_number = self.check_week_number(week_number)
        self.callsign = self.check_callsign(callsign)
        self.transport_mode = self.check_mode(transport_mode, gw_frequency)

        (canonical_gateway, canonical_frequency) = \
            gateway_validator(gateway, gw_frequency, self.transport_mode)
        self.gateway = canonical_gateway
        self.frequency = self.check_frequency(canonical_frequency)
        self.neighbourhood = self.check_location(neighbourhood)
        self.county = county
        if len(state) == 2:
            self.state = state.upper()
        else:
            self.state = state.capitalize()

    #--------------------------------------------------------------------------
    def check_frequency(self, frequency: str) -> float:
        canonical_frequency = float(frequency)
        if canonical_frequency >= 0.0 and canonical_frequency > MAX_FREQUENCY:
            raise ValueError(f'Invalid frequency: {frequency}')
        return canonical_frequency

    #--------------------------------------------------------------------------
    def check_week_number(self, week_number: str) -> int:
        canonical_week_num = int(week_number)
        if canonical_week_num < 0 or canonical_week_num > MAX_WEEK_NUMBER:
            raise ValueError(f'Invalid week number: {self.week_number}')
        return canonical_week_num

    #--------------------------------------------------------------------------
    def check_mode(self, transport_mode: str, freq: str) -> str:
        checked_mode = mode_validator(transport_mode, freq)
        if checked_mode is not None:
            self.transport_mode = checked_mode
        else:
            raise ValueError(f'Mode is invalid: {self.transport_mode}')
        return checked_mode

    #--------------------------------------------------------------------------
    def check_callsign(self, callsign: str) -> str:
        canonical_callsign = validate_callsign(callsign)
        if canonical_callsign is None:
            raise ValueError(f'Invalid callsign: {callsign}')
        return canonical_callsign

    #--------------------------------------------------------------------------
    def check_location(self, neighbourhood: str) -> str:
        (best_guess, likelihood) = neighbourhood_check(neighbourhood)
        if likelihood > 0.7:
            # print(f'Hit  ({likelihood}): {neighbourhood} -> {best_guess}')
            return best_guess
        elif neighbourhood.upper() == 'N/A':
            # This is where there is no neighbourhood in Lake Oswego associated
            # with the checkin. I.e. the checkin came from outside Lake Oswego.
            return 'N/A'
        else:
            #print(f'Miss ({likelihood}): {neighbourhood} (skip nearest: {best_guess}) -> {capwords(neighbourhood)}')
            return capwords(neighbourhood)
        
    #--------------------------------------------------------------------------
    def __repr__(self) -> str:
        return f'{self.week_number},{self.callsign},{self.transport_mode},'\
            f'{self.gateway},{self.frequency:.4f},{self.neighbourhood},'\
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
                   'neighbourhood' : self.neighbourhood,
                   'county' : self.county,
                   'state' : self.state}
#------------------------------------------------------------------------------
# Module interface below
#------------------------------------------------------------------------------
def add_checkin(week_number: int,
                callsign: str,
                transport_mode: str,
                gateway: str,
                frequency: float,
                neighbourhood: str,
                county: str,
                state: str):

    check_in = _Checkin(week_number,
                    callsign,
                    transport_mode,
                    gateway,
                    frequency,
                    neighbourhood,
                    county,
                    state)

    _all_checkins.append(check_in)
    checkin_dict = check_in.as_dict()
    save_checkin(checkin_dict)

#------------------------------------------------------------------------------
def get_last_checkin_repr() -> str:
    if len(_all_checkins) == 0:
        return "No checkins"
    else:
        return str(_all_checkins[-1])
#------------------------------------------------------------------------------
__all__ = ['add_checkin', 'get_last_checkin_repr']