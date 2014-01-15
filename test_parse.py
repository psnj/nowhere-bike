"""Test parsing workout language."""

import unittest
import pprint

import parse

pp = pprint.pprint

class TestWorkout(unittest.TestCase):

    def test_parse_workout(self):
        r = parse.parse_workout("""
- 10m easy warmup
- 5x:
  - 1m gear up
  - 1m gear even further up
  - 2x:
    - 15s insane
    - 15s slow
- 10m cool down
        """)
        self.assertEquals(
            r,
            [{'d1': 'easy warmup', 'd2': '', 'dur': 600},
             (('REPEAT', 5),
              [{'d1': 'gear up', 'd2': '', 'dur': 60},
               {'d1': 'gear even further up', 'd2': '', 'dur': 60},
              (('REPEAT', 2),
               [{'d1': 'insane', 'd2': '', 'dur': 15},
                {'d1': 'slow', 'd2': '', 'dur': 15}])]),
            {'d1': 'cool down', 'd2': '', 'dur': 600}])
        flt = parse.flatten(r)
        self.assertEquals(
            flt,
            [{'d1': 'easy warmup', 'd2': '', 'dur': 600, 'index': 0, 'level': 0},
             {'d1': 'gear up', 'd2': '', 'dur': 60, 'index': 600, 'level': 1},
            {'d1': 'gear even further up', 'd2': '', 'dur': 60, 'index': 660, 'level': 1},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 720, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 735, 'level': 2},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 750, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 765, 'level': 2},
            {'d1': 'gear up', 'd2': '', 'dur': 60, 'index': 780, 'level': 1},
            {'d1': 'gear even further up', 'd2': '', 'dur': 60, 'index': 840, 'level': 1},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 900, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 915, 'level': 2},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 930, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 945, 'level': 2},
            {'d1': 'gear up', 'd2': '', 'dur': 60, 'index': 960, 'level': 1},
            {'d1': 'gear even further up',
             'd2': '',
             'dur': 60,
             'index': 1020,
            'level': 1},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 1080, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 1095, 'level': 2},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 1110, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 1125, 'level': 2},
            {'d1': 'gear up', 'd2': '', 'dur': 60, 'index': 1140, 'level': 1},
            {'d1': 'gear even further up',
             'd2': '',
             'dur': 60,
             'index': 1200,
            'level': 1},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 1260, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 1275, 'level': 2},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 1290, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 1305, 'level': 2},
            {'d1': 'gear up', 'd2': '', 'dur': 60, 'index': 1320, 'level': 1},
            {'d1': 'gear even further up',
             'd2': '',
             'dur': 60,
             'index': 1380,
            'level': 1},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 1440, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 1455, 'level': 2},
            {'d1': 'insane', 'd2': '', 'dur': 15, 'index': 1470, 'level': 2},
            {'d1': 'slow', 'd2': '', 'dur': 15, 'index': 1485, 'level': 2},
            {'d1': 'cool down', 'd2': '', 'dur': 600, 'index': 1500, 'level': 0}])
            
if __name__ == '__main__':
    unittest.main()
