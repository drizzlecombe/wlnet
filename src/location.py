
# -----------------------------------------------------------------------------
# Helper functions and data
# -----------------------------------------------------------------------------
# A dictionary of all known neighbourhoods in Lake Oswego. The key is the
# neighbourhood name in a canonicalised form. This is the actual name, all
# lower case and white space removed. This forms just one word to match against
# and improves the matching process.
# 
from difflib import SequenceMatcher
import string

# This table maps punctuation and whitespace characters to nothing - i.e.
# removes them from the source string when using the translate() function.
_translation_table = str.maketrans('','',string.punctuation +
                                   string.whitespace)

_LAKE_OSWEGO_NEIGHBOURHOODS = {
    'birdshill': 'Birdshill',
    'blueheron': 'Blue Heron',
    'bryant': 'Bryant',
    'childs': 'Childs',
    'evergreen': 'Evergreen',
    'firstaddition': 'First Addition',
    'foothills': 'Foothills',
    'foresthighlands': 'Forest Highlands',
    'glenmorrie': 'Glenmorrie',
    'hallinan': 'Hallinan',
    'hollyorchard': 'Holly Orchard',
    'lakeforest': 'Lake Forest',
    'lakegrove': 'Lake Grove',
    'lakewood': 'Lakewood',
    'marylhurst': 'Marylhurst',
    'mcvey': 'McVey',
    'mountainpark': 'Mountain Park',
    'northshore': 'North Shore',
    'oakcreek': 'Oak Creek',
    'oldtown': 'Old Town',
    'palisades': 'Palisades', 
    'rosewood': 'Rosewood',
    'skylands': 'Skylands',
    'uplands': 'Uplands',
    'waluga': 'Waluga',
    'westlake': 'Westlake',
    'westridge': 'Westridge'}

def canonicalise(s: str) -> str:
    """Converts a string into canonicalised form
    
    Remove unwanted characters like punctuation and whitespace and convert to
    lower case. For example: 'First Addition' -> 'firstaddition'

    :param s: a string
    :returns: a string that has been stripped of whitespace and punctuation
              and converted to lower case.
    """

    return s.translate(_translation_table).lower()

_neighbourhood_SM = SequenceMatcher()

def neighbourhood_check(s: str) -> tuple[str, float]:
    """Tests if the input string is likely to be a Lake Oswego neighbourood
    
    :param s: a neighbourhood candidate string
    :returns: a tuple containing the best match neighbourhood name and a
        measure of how likely this is as a match:
          (0 (very unlikely) -> 1 (very likely))
    """
    if s is None:
        raise ValueError('A location was not set')
    
    can_s: str = canonicalise(s)
    max_likelihood: float = 0.0
    candidate_nh: str = ''
    for k in _LAKE_OSWEGO_NEIGHBOURHOODS.keys():
        _neighbourhood_SM.set_seq1(can_s)
        _neighbourhood_SM.set_seq2(k)
        lh: float = _neighbourhood_SM.ratio()
        if lh > max_likelihood:
            max_likelihood = lh
            candidate_nh = _LAKE_OSWEGO_NEIGHBOURHOODS[k]
    return (candidate_nh, max_likelihood)