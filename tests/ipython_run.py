#!/usr/bin/python
get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

import os 
import sys
from pathlib import Path

top_level_dir = str(Path(__file__).parents[1])
get_ipython().run_line_magic('cd', top_level_dir)
sys.path.insert(0, top_level_dir)

import reinsurance_tester
import pandas as pd

def ri_run(example_dir):
    try:
        ri_filepath = os.path.join(top_level_dir,example_dir)
        (
            account_df, 
            location_df, 
            ri_info_df, 
            ri_scope_df, 
            do_reinsurance
        ) = reinsurance_tester.load_oed_dfs(
                ri_filepath,
                show_all=False)

        net_losses = reinsurance_tester.run_test(
            'run_reinsurance', 
            account_df, 
            location_df, 
            ri_info_df, 
            ri_scope_df, 
            loss_factor=1.0, 
            do_reinsurance=do_reinsurance
        )
        return net_losses
    except Exception as err:
        print("Run failed")
        print(err)


fm24 = ri_run('examples/ftest/fm24/')
LOC_1 = fm24['Inuring priority:1 - Risk level:LOC']
LOC_1.groupby(['location_number']).sum().loss_net


