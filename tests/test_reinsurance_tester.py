"""
    docs: 
        https://github.com/wolever/parameterized
    Run using:
        python -m unittest -v tests/test_reinsurance_tester.py
        py.test -v tests/test_reinsurance_tester.py
"""
import unittest
from parameterized import parameterized
from pandas.util.testing import assert_frame_equal

import pandas as pd
import os 
import sys
from pathlib import Path

top_level_dir = str(Path(__file__).parents[1])
sys.path.insert(0, top_level_dir)
import reinsurance_tester


expected_output_dir = os.path.join(top_level_dir, 'tests', 'expected', 'calc')


input_dir = os.path.join(top_level_dir, 'examples')
#test_examples = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
test_examples = ['multiple_FAC',
                 'multiple_QS_1',
                 'loc_limit_QS',
                 'acc_limit_QS',
                 'simple_CAT_XL',
                 #'ftest',
                 'acc_SS',
                 'pol_SS',
                 'pol_limit_QS',
                 'simple_loc_FAC',
                 'multiple_QS_2',
                 #'volume_simple_QS',
                 'multiple_SS',
                 'multiple_CAT_XL',
                 'simple_acc_FAC',
                 'loc_SS',
                 'simple_pol_FAC',
                 'simple_QS']

fm_input_dir = os.path.join(top_level_dir, 'examples', 'ftest')
#fm_examples = [d for d in os.listdir(fm_input_dir) if os.path.isdir(os.path.join(fm_input_dir, d))]
fm_examples = ['fm24',
               'fm27']


test_cases = []
for case in test_examples:
    test_cases.append((
        case, 
        os.path.join(input_dir, case),
        os.path.join(expected_output_dir, case)
    ))
for case in fm_examples:
    test_cases.append((
        case, 
        os.path.join(fm_input_dir, case),
        os.path.join(expected_output_dir, case)
    ))





class test_reinsurance_values(unittest.TestCase):
    @parameterized.expand(test_cases)
    def test_fmcalc(self, name, case_dir, expected_dir):
        loss_factor = 1.0
        (
            account_df, 
            location_df, 
            ri_info_df, 
            ri_scope_df, 
            do_reinsurance
        ) = reinsurance_tester.load_oed_dfs(case_dir)

        net_losses = reinsurance_tester.run_test(
            "ri_testing",
            account_df, location_df, ri_info_df, ri_scope_df,
            loss_factor,
            do_reinsurance,
        )

        for key in net_losses.keys():
            expected_file = os.path.join(
                expected_dir, 
                "{}.csv".format(key.replace(' ', '_'))
            )    

            expected_df = pd.read_csv(expected_file)
            assert_frame_equal(net_losses[key],
                               expected_df)



