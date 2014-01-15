"""Parsing the Workout Language.

Parses the workout language, which is based on yaml.
"""

import re
import yaml


RE_DURATION = re.compile(r'\b(?:(\d+m)?(\d+s)?)\s*\b')
RE_REPEAT = re.compile('^(\d+) ?x$')
DUR = {'m': 60, 's': 1}


class ParseError(Exception):
    pass


def parse_duration(dur_s):
    """Parse a duration string

    Returning seconds integer value, plus the remainer of the unparsed
    string. Return (None, dur_s) if not parsable. Format is:

>>> parse_duration("5m")
(300, '')
>>> parse_duration('30s')
(30, '')
>>> parse_duration('127s')
(127, '')
>>> parse_duration('5m')
(300, '')
>>> parse_duration('5m13s')
(313, '')
>>> parse_duration('5m13s ok')
(313, 'ok')
"""
    parsed = RE_DURATION.match(dur_s)
    if parsed:
        return (sum(int(g[:-1]) * DUR[g[-1]] for g in parsed.groups() if g),
                dur_s[len(parsed.group(0)):])
    else:
        return (None, dur_s)


def parse_step(step_s):
    """Parse a single step.

>>> parse_step('10m easy')
{'dur': 600, 'd1': 'easy'}
"""
    dur, rest_s = parse_duration(step_s)
    if not dur:
        raise ParseError(step_s, 'No duration supplied')
    if '/' in rest_s:
        d1, d2 = rest_s.split('/', 1)
    else:
        d1, d2 = rest_s, ''
    return {'dur': dur, 'd1': d1, 'd2': d2}


def parse_workout(workout_s):
    """Parse workout YAML string."""
    struct = yaml.safe_load(workout_s)
    return parse_wo_elt(struct)


def parse_wo_elt(elt):
    """Parse a workout element."""
    if isinstance(elt, list):
        return [ parse_wo_elt(child) for child in elt ]
    elif isinstance(elt, basestring):
        return parse_step(elt)
    elif isinstance(elt, dict):
        # We only ever expect dicts of one key, for loops.
        if len(elt) != 1:
            raise ParseError(elt, 'Invalid dict')
        return ( parse_directive(elt.keys()[0]),
                 parse_wo_elt(elt.values()[0]) )


def parse_directive(dir_s):
    """Parse a directive string (ie. the "2x" in loop)."""
    match = RE_REPEAT.match(dir_s)
    if match:
        return ('REPEAT', int(match.group(1)))
    raise ParseError(dir_s, 'Unknown directive')


def flatten(workout):
    """
    Flatten a parsed workout into a list of workout steps.

    Essentially just unroll loops. Add to each step dict a time index (key:
    'index') (ie. the number of seconds from the beginning of the
    workout that the step begins) so that we can easily index into a
    step anywhere in the workout.
    """
    time_ix = {'offset': 0}  # box int for closure below

    def index_step(step, level):
        """Return a copy of (atomic) step with 'index' time key, and
        level as the loop level."""
        result = dict(step, index=time_ix['offset'], level=level)
        time_ix['offset'] += step['dur']
        return result

    def _flatten(wo, level=0):
        result = []
        for step in wo:
            # ordinary steps are dicts already
            if isinstance(step, dict):
                result.append(index_step(step, level))
            # otherwise they're tuples: (directive, [steps])
            elif step[0][0] == 'REPEAT':
                for ix in xrange(step[0][1]):
                    result.extend(_flatten(step[1], 1 + level))
            else:
                raise ParseError(step, "Can't flatten step")
        return result

    return _flatten(workout)
