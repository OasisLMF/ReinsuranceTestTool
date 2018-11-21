#!/usr/bin/env python
"""
Test tool for reinsurance functaionality and OED data input.
Takes input data in OED format, and invokes the Oasis Platform financial module.
"""
from tabulate import tabulate
import pandas as pd
import shutil
import os
import json
import argparse
import time
import logging
import subprocess
import shutil
from oasislmf.exposures import reinsurance_layer
from oasislmf.exposures import oed
from oasislmf.model_execution import bin

from direct_layer import DirectLayer
from collections import OrderedDict



def run_fm(
    input_name,
    output_name,
    xref_descriptions,
    allocation=oed.ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID):
    command = "fmcalc -p {0} -n -a {2} < {1}.bin | tee {0}.bin | fmtocsv > {0}.csv".format(
            output_name, input_name, allocation)
    print(command)
    proc = subprocess.Popen(command, shell=True)
    proc.wait()
    if proc.returncode != 0:
        raise Exception("Failed to run fm")
    losses_df = pd.read_csv("{}.csv".format(output_name))
    inputs_df = pd.read_csv("{}.csv".format(input_name))

    losses_df.drop(losses_df[losses_df.sidx != 1].index, inplace=True)
    inputs_df.drop(inputs_df[inputs_df.sidx != 1].index, inplace=True)
    losses_df = pd.merge(
        inputs_df,
        losses_df, left_on='output_id', right_on='output_id',
        suffixes=('_pre', '_net'))

    losses_df = pd.merge(
        xref_descriptions,
        losses_df, left_on='xref_id', right_on='output_id')

    del losses_df['event_id_pre']
    del losses_df['sidx_pre']
    del losses_df['event_id_net']
    del losses_df['sidx_net']
    del losses_df['output_id']
    del losses_df['xref_id']
    return losses_df


def run_test(
        run_name,
        account_df, location_df, ri_info_df, ri_scope_df,
        loss_factor,
        do_reinsurance,
        logger=None):
    """
    Run the direct and reinsurance layers through the Oasis FM.abs
    Returns an array of net loss data frames, the first for the direct layers
    and then one per inuring layer.
    """
    t_start = time.time()


    if os.path.exists(run_name):
        shutil.rmtree(run_name)
    os.mkdir(run_name)

    cwd = os.getcwd()

    if os.path.exists(run_name):
        shutil.rmtree(run_name)
    os.mkdir(run_name)

    net_losses = OrderedDict()

    cwd = os.getcwd()
    try:
        os.chdir(run_name)

        direct_layer = DirectLayer(account_df, location_df)
        direct_layer.generate_oasis_structures()
        direct_layer.write_oasis_files()
        losses_df = direct_layer.apply_fm(
            loss_percentage_of_tiv=loss_factor, net=False)
        net_losses['Direct'] = losses_df


        oed_validator = oed.OedValidator()
        if  do_reinsurance:
            (is_valid, error_msgs) = oed_validator.validate(ri_info_df, ri_scope_df)
            if not is_valid:
                print("Validation Failed:")
                for m in error_msgs:
                    print(json.dumps(m, indent=4, sort_keys=True))
                return False

        ri_layers = reinsurance_layer.generate_files_for_reinsurance(
			items=direct_layer.items,
			coverages=direct_layer.coverages,
			fm_xrefs=direct_layer.fm_xrefs,
			xref_descriptions=direct_layer.xref_descriptions,
			ri_info_df=ri_info_df,
			ri_scope_df=ri_scope_df,
			direct_oasis_files_dir='',
		)
        
        previous_inuring_priority = None
        previous_risk_level = None
        for idx in ri_layers:
            '''
            {'inuring_priority': 1, 'risk_level': 'LOC', 'directory': 'run/RI_1'}
            {'inuring_priority': 1, 'risk_level': 'ACC', 'directory': 'run/RI_2'}
            {'inuring_priority': 2, 'risk_level': 'LOC', 'directory': 'run/RI_3'}
            {'inuring_priority': 3, 'risk_level': 'LOC', 'directory': 'run/RI_4'}

            '''
            if idx < 2:                                                                                                                
                input_name = "ils"
            else:
                input_name = ri_layers[idx-1]['directory']
            bin.create_binary_files(ri_layers[idx]['directory'],
                                    ri_layers[idx]['directory'], 
                                    do_il=True)

            reinsurance_layer_losses_df = run_fm(input_name, 
                                                 ri_layers[idx]['directory'], 
                                                 direct_layer.xref_descriptions)
            output_name = "Inuring_priority:{} - Risk_level:{}".format(ri_layers[idx]['inuring_priority'], 
                                            ri_layers[idx]['risk_level'])
            net_losses[output_name] = reinsurance_layer_losses_df
        return net_losses

    finally:
        os.chdir(cwd)
        t_end = time.time()
        print("Exec time: {}".format(t_end - t_start))

        if logger:
            print("\n\nItems_to_Locations: mapping")
            print(tabulate(direct_layer.report_item_ids(),
                         headers='keys', tablefmt='psql', floatfmt=".2f")) 
            logger.debug("Items_to_Locations: mapping")
            logger.debug(tabulate(direct_layer.report_item_ids(),
                         headers='keys', tablefmt='psql', floatfmt=".2f")) 
    return net_losses



def setup_logger(log_name):
    log_file = "run_{}.log".format(time.strftime("%Y%m%d-%H%M%S"))
    if log_name:
        log_file = "{}.log".format(log_name)

    log_dir = 'logs'
    

    log_level = logging.DEBUG
    #log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_format = '%(message)s\n'

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    #logging.basicConfig(stream=sys.stdout, level=log_level, format=log_format)
    logging.basicConfig(level=log_level,
                        format=log_format,
                        filename=os.path.join(log_dir, log_file),
                        filemode='w')
    return logging.getLogger()



if __name__ == "__main__":
    # execute only if run as a script
    parser = argparse.ArgumentParser(
        description='Run Oasis FM examples with reinsurance.')
    parser.add_argument(
        '-n', '--name', metavar='N', type=str, required=True,
        help='The analysis name. All intermediate files will be "+ \
        policies=a         "saved in a labelled directory.')
    parser.add_argument(
        '-o', '--oed_dir', metavar='N', type=str, default=None, required=False,
        help='The directory containing the set of OED exposure data files.')
    parser.add_argument(
        '-l', '--loss_factor', metavar='N', type=float, default=1.0,
        help='The loss factor to apply to TIVs.')
    parser.add_argument(
       '-d', '--debug', action='store', default=None,
       help='Store Debugging Logs under ./logs')

    args = parser.parse_args()

    run_name = args.name
    oed_dir = args.oed_dir
    loss_factor = args.loss_factor
    logger = (setup_logger(args.debug) if args.debug else None)

    (ri_info_df, ri_scope_df, do_reinsurance) = oed.load_oed_dfs(oed_dir)

    net_losses = run_test(
        run_name,
        ri_info_df, ri_scope_df,
        loss_factor,
        do_reinsurance,
        logger)

    for (description, net_loss) in net_losses.items():
        #Print / Write Output to csv
        filename = '{}_output.csv'.format(description.replace(' ', '_'))
        net_loss.to_csv(os.path.join(run_name, filename), index=False)
        print(description)
        print(tabulate(net_loss, headers='keys', tablefmt='psql', floatfmt=".2f"))

        # print / write, output sum by location_number
        if 'loss_net' in net_loss.columns:
            loc_sum_df = net_loss.groupby(['location_number']).sum()
            filename = '{}_output_locsum.csv'.format(description.replace(' ', '_'))
            loc_sum_df.to_csv(os.path.join(run_name, filename), index=False)
            print(tabulate(loc_sum_df[['tiv','loss_pre', 'loss_net']], 
                  headers='keys', tablefmt='psql', floatfmt=".2f"))

        if args.debug:
            logger.debug(description)
            logger.debug(tabulate(net_loss, headers='keys', tablefmt='psql', floatfmt=".2f"))
        print("")
        print("")
