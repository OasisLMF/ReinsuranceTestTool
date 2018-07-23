#!/usr/bin/python
import os 
import sys
from pathlib import Path

top_level_dir = str(Path(__file__).parents[1])
sys.path.insert(0, top_level_dir)

import reinsurance_tester
import pandas as pd


input_dir = os.path.join(top_level_dir, 'examples')
output_dir = os.path.join(top_level_dir, 'tests', 'expected')
examples_paths = [os.path.join(input_dir, d) for d in os.listdir(input_dir)]
examples_list = [d for d in examples_paths if os.path.isdir(d)] 

print(os.listdir(input_dir))
for case in examples_list:
    try:
        (
            account_df, 
            location_df, 
            ri_info_df, 
            ri_scope_df, 
            do_reinsurance
        ) = reinsurance_tester.load_oed_dfs(case, show_all=False)

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
                os.path.join(output_dir,
                             'calc',
                             case.rsplit('/')[-1],
                             key
                )
            ).replace(' ', '_')
            print(file_out)    
            try:
                os.makedirs(str(Path(file_out).parents[0]))
            except: 
                print('Skip dir creation')
            net_losses[key].to_csv(file_out, index=False)
    except:
        print('Case failed')
