#!/usr/bin/env python
import os
import sys
import pathlib

top_level_dir = str(pathlib.Path(__file__).parents[1])
sys.path.insert(0, top_level_dir)

import pandas as pd

import reinsurance_tester
from oasislmf.exposures import oed


output_dir = os.path.join(top_level_dir, 'tests', 'expected')


class term_colour:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Simple set of tests
input_dir = os.path.join(top_level_dir, 'examples')
examples_paths    = [os.path.join(input_dir, d) for d in os.listdir(input_dir)]
examples_list = [d for d in examples_paths if os.path.isdir(d)]

# ftest ri cases
fm_input_dir = os.path.join(top_level_dir, 'examples', 'ftest')
fm_examples_paths = [os.path.join(fm_input_dir, d) for d in os.listdir(fm_input_dir)]
fm_examples_list = [d for d in fm_examples_paths if os.path.isdir(d)]

#case_run_list = examples_list + fm_examples_list
case_run_list = examples_list
"""
case_run_list =  [
    './examples/multiple_FAC',
    './examples/multiple_QS_1',
    './examples/multiple_QS_2',
    './examples/loc_limit_QS',
    './examples/acc_limit_QS',
    './examples/simple_CAT_XL',
    './examples/ftest',
    './examples/acc_SS',
    './examples/pol_SS',
    './examples/pol_limit_QS',
    './examples/simple_loc_FAC',
    './examples/volume_simple_QS',
    './examples/multiple_SS',
    './examples/multiple_CAT_XL',
    './examples/simple_acc_FAC',
    './examples/loc_SS',
    './examples/simple_pol_FAC',
    './examples/simple_QS',
    './examples/ftest/fm3',
    './examples/ftest/fm10',
    './examples/ftest/fm12',
    './examples/ftest/fm27',
    './examples/ftest/fm11',
    './examples/ftest/fm37',
    './examples/ftest/fm24',
    './examples/ftest/fm23'
]
"""


#print(os.listdir(input_dir))
for case in case_run_list:
    output_location = os.path.join(output_dir, 'calc', case.rsplit('/')[-1])
    try:
        os.makedirs(output_location)
        try:
            print('[RUNNING]  "{}"'.format(case))
            (
                account_df,
                location_df,
                ri_info_df,
                ri_scope_df,
                do_reinsurance
            ) = oed.load_oed_dfs(case, show_all=False)

            net_losses = reinsurance_tester.run_test(
                'run_reinsurance',
                account_df,
                location_df,
                ri_info_df,
                ri_scope_df,
                loss_factor=1.0,
                do_reinsurance=do_reinsurance
            )

            for key in net_losses.keys():
                file_out = "{}.csv".format(
                    os.path.join(output_location, key)).replace(' ', '_')
                #print(file_out)
                net_losses[key].to_csv(file_out, index=False)
                
            print(term_colour.OKGREEN + '[SUCCESS]  "{}"'.format(case) + term_colour.ENDC)
        except Exception as e:
            print(term_colour.FAIL + '[FAILED]   "{} - {}"'.format(case,e) + term_colour.ENDC)

    except FileExistsError as e:
        print(term_colour.WARNING + '[SKIPPED]  "{}" dir exisits'.format(case, output_location) + term_colour.ENDC)
