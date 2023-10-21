from callsign_processing import validate_callsign
from callsign_processing import print_callsign_cache
from callsign_processing import clean_callsign
from WinlinkMode import mode_validator, mode_best_guess

MAX_WEEK_NUMBER = 75 # TODO - load this from a config file

_all_checkins = []
_last_checkin = None

class _Checkin:
    def __init__(self, week_number: int, callsign: str, transport_mode: str,
                 gateway: str, gw_frequency: float, location: str,
                 state: str ) -> None:

        self.validated = False
        self.week_number = week_number
        self.callsign = callsign.upper()
        self.mode = transport_mode.upper()
        self.gateway = gateway.upper()
        self.frequency = gw_frequency
        self.location = location.capitalize()
        if len(state) == 2:
            self.state = state.upper()
        else:
            self.state = state.capitalize()
        self.validate()
    #-------------------------------------------------------------------------
    def validate(self):
        # Do some simple cleaning of the data before storing it
        clean_week_num = -1
        if self.week_number < 0 or self.week_number > MAX_WEEK_NUMBER:
            raise ValueError(f'Invalid week number: {self.week_number}')
        if not validate_callsign(self.callsign):
            # See if the callsign has some sort of suffix like /M or -10.
            # If so, remove that and try again
            self.callsign = clean_callsign(self.callsign)
            if not validate_callsign(self.callsign):
                raise ValueError(f'Invalid callsign: {self.allsign}')
        if not mode_validator(self.mode):
            # Before we raise an error, let's see if there is a possible
            # match
            try:
                self.mode = mode_best_guess(self.mode, self.frequency)
            except:
                raise ValueError(f'Mode is incorrect: {self.mode}')
        self.validated = True
    #--------------------------------------------------------------------------
    def isvalidated(self):
        return self.validated
    #-------------------------------------------------------------------------
    def __repr__(self) -> str:
        return f'{self.week_number}, {self.callsign}, {self.mode}, '\
            f'{self.gateway}, {self.frequency:.4f}, {self.location}, '\
            f'{self.state}'
    #-------------------------------------------------------------------------
    def __str__(self) -> str:
        return self.__repr__()
    
#------------------------------------------------------------------------------
def add_checkin(week_number: int,
                callsign: str,
                transport_mode: str,
                rms_id: str,
                rms_frequency: float,
                location: str,
                state: str):
    
    global _last_checkin
    check_in = _Checkin(week_number, 
                    callsign,
                    transport_mode, 
                    rms_id,
                    rms_frequency,
                    location,
                    state)
    _last_checkin = check_in
    _all_checkins.append(check_in)
#------------------------------------------------------------------------------
def get_last_checkin_repr() -> str:
    if len(_all_checkins) == 0:
        return "No checkins"
    else:
        return str(_last_checkin)
#------------------------------------------------------------------------------
__all__ = ['add_checkin', 'get_last_checkin_repr']