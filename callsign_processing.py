import re

class _CallsignProcessor:
    def __init__(self):
        self.patterns = self.create_callsign_matchers()
        self.callsign_split_pattern = re.compile('^(.*)([-/])(.*)$')
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

        # Lastly - special event stations. 1x1. Prefix K, N, W. Suffix: A-W or
        # Y-Z. X is not permitted.
        callsign_matchers.append(re.compile(r"^[KNW][0-9][A-WYZ]$"))

        return callsign_matchers
# -----------------------------------------------------------------------------

    def remove_suffix(self, callsign: str) -> str:
        """Trim any callsigns that may have a suffix like /M or -10"""
        clean_callsign = callsign.strip()
        clean_callsign = clean_callsign.upper()
        cs_match = self.callsign_split_pattern.match(clean_callsign)
        if cs_match:
            return cs_match.group(1)
        return callsign

# -----------------------------------------------------------------------------
    def validate(self, callsign: str) -> str:
        """Checks to see if a string is a probable amateur radio callsign."""

        wip_callsign = callsign.strip().upper()
        canonical_callsign = self.remove_suffix(wip_callsign)

        call_seen_before_num = self.callsign_cache.get(canonical_callsign)
        if call_seen_before_num is not None:
            # Seen the callsign before
            self.callsign_cache[canonical_callsign] = call_seen_before_num + 1
            return canonical_callsign
        
        # Not seen this callsign before. Better validate it.
        for pattern in self.patterns:
            if pattern.match(canonical_callsign):
                self.callsign_cache.setdefault(canonical_callsign, 1)
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

__all__ = ['validate_callsign', 'print_callsign_cache']