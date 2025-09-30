import re

class Callsign:
    callsign_split_pattern = re.compile('^(.*)([-/])(.*)$')

    def __init__(self, raw_callsign: str):

        self.callsign = ""
        self.suffix = ""
        self.separator = ""

        canonical_callsign = raw_callsign.strip().upper()

        # Trim any callsigns that may have a suffix like /M or -10. Split at the
        # suffix if necessary
        cs_match = self.callsign_split_pattern.match(canonical_callsign)

        if cs_match:
            self.callsign = cs_match.group(1)
            self.separator = cs_match.group(2)
            self.suffix = cs_match.group(3)
        else:
            self.callsign = canonical_callsign

    def __repr__(self):
        return f"Callsign: {self.callsign}, " \
                f"Separator = {self.separator}, " \
                f"Suffix: {self.suffix}"

class _CallsignProcessor:
    def __init__(self):
        self.patterns = self.create_callsign_matchers()
        self.callsign_cache = {}

    def create_callsign_matchers(self):
        """Creates a set of pattern matchers for US callsigns

        Returns a list of regular expression pattern matchers
        """
        # Callsigns are broken out into a most- to least-common ranking. A few
        # of these patterns could be combined to cover more of the range of
        # calls with fewer regexps. Since the pools of calls are heavily biased
        # at the top of this ranking, most of the work will be done by the
        # first pattern met. This allows us to keeping the patterns simple and
        # allows for added functionality like counting of the various classes
        # of callsign, for example.
        callsign_matchers = []

        # Most common call is the 2x3 or group D. First character is either K,
        # W. This is the pattern that will be tried first with the match.
        callsign_matchers.append(re.compile(r"^[KW][A-Z][0-9][A-Z]{3}$"))

        # 1x3 pattern - group C. K, N, W as the prefix. Three letter suffix.
        callsign_matchers.append(re.compile(r"^[KNW][0-9][A-Z]{3}$"))

        # 2x2 pattern - group B. K, N, W plus a letter as the prefix. Two
        # letter suffix.
        callsign_matchers.append(re.compile(r"^[KNW][A-Z][0-9][A-Z]{2}$"))

        # 2x2 pattern - group A. AA - AL. Two letter suffix.
        callsign_matchers.append(re.compile(r"^A[A-L][0-9][A-Z]{2}$"))

        # 1x2 pattern - group A. Prefix: one of K, N, W. Two letter suffix.
        callsign_matchers.append(re.compile(r"^[KNW][0-9][A-Z]{2}$"))

        # 2x1 pattern - group A. Prefix - two letters: K, N, W followed by a
        # letter. Single letter suffix.
        callsign_matchers.append(re.compile(r"^[KNW][A-Z][0-9][A-Z]$"))

        # 2x1 pattern - group A. Prefix - two letters: AA-AL followed by a
        # letter. Single letter suffix.
        callsign_matchers.append(re.compile(r"^A[A-L][0-9][A-Z]$"))

        # Lastly, for the US at least - special event stations. 1x1. Prefix K,
        # N, W. Suffix: A-W or Y-Z. X is not permitted.
        callsign_matchers.append(re.compile(r"^[KNW][0-9][A-WYZ]$"))

        # Canadian catchall
        callsign_matchers.append(re.compile(r'^V[AEOY][0-9][A-Z]{2,3}$'))

        # Mexican catchall
        callsign_matchers.append(re.compile(r'^X[EF][1-4][A-Z]{2,3}$'))
        return callsign_matchers
# -----------------------------------------------------------------------------

    def validate(self, callsign: str) -> Callsign:
        """Checks to see if a string is a probable amateur radio callsign."""

        canonical_callsign = Callsign(callsign)

        call_seen_before_num = self.callsign_cache.get(canonical_callsign.callsign)
        if call_seen_before_num is not None:
            # Seen the callsign before
            self.callsign_cache[canonical_callsign.callsign] = call_seen_before_num + 1
            return canonical_callsign
        
        # Not seen this callsign before. Better validate it.
        for pattern in self.patterns:
            if pattern.match(canonical_callsign.callsign):
                self.callsign_cache.setdefault(canonical_callsign.callsign, 1)
                return canonical_callsign
        return None
# -----------------------------------------------------------------------------
    def dump_callsign_cache(self):
        s = sorted(self.callsign_cache.items(), key = lambda x: x[1])
        total_checkins = 0
        operators = 0
        for c, cnt in s:
            print(f'{c}, {cnt}')
            total_checkins += cnt
            operators += 1
        print(f'{operators} operators with {total_checkins} cumulative checkins')
        

# -----------------------------------------------------------------------------
# Set up the single instance of _CallsignProcessor and expose little bits of
# the interface
# -----------------------------------------------------------------------------

cs_processor = _CallsignProcessor()

def validate_callsign(callsign):
    return cs_processor.validate(callsign)

def print_callsign_cache():
    cs_processor.dump_callsign_cache()

__all__ = ['Callsign', 'validate_callsign', 'print_callsign_cache']