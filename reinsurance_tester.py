"""
Test tool for reinsurance functaionality and OED data input.
Takes input data in OED format, and invokes the Oasis Platform financial module.
"""
from tabulate import tabulate
import pandas as pd
import shutil
import os
import argparse
from reinsurance_layer import ReinsuranceLayer, validate_reinsurance_structures
from direct_layer import DirectLayer
import common
from collections import OrderedDict


def load_oed_dfs(oed_dir, show_all=False):
    """
    Load OED data files.
    """

    do_reinsuarnce = True
    if oed_dir is not None:
        if not os.path.exists(oed_dir):
            print("Path does not exist: {}".format(oed_dir))
            exit(1)
        # Account file
        oed_account_file = os.path.join(oed_dir, "account.csv")
        if not os.path.exists(oed_account_file):
            print("Path does not exist: {}".format(oed_account_file))
            exit(1)
        account_df = pd.read_csv(oed_account_file)

        # Location file
        oed_location_file = os.path.join(oed_dir, "location.csv")
        if not os.path.exists(oed_location_file):
            print("Path does not exist: {}".format(oed_location_file))
            exit(1)
        location_df = pd.read_csv(oed_location_file)

        # RI files
        oed_ri_info_file = os.path.join(oed_dir, "ri_info.csv")
        oed_ri_scope_file = os.path.join(oed_dir, "ri_scope.csv")
        oed_ri_info_file_exists = os.path.exists(oed_ri_info_file)
        oed_ri_scope_file_exists = os.path.exists(oed_ri_scope_file)

        if not oed_ri_info_file_exists and not oed_ri_scope_file_exists:
            ri_info_df = None
            ri_scope_df = None
            do_reinsuarnce = False
        elif oed_ri_info_file_exists and oed_ri_scope_file_exists:
            ri_info_df = pd.read_csv(oed_ri_info_file)
            ri_scope_df = pd.read_csv(oed_ri_scope_file)
        else:
            print("Both reinsurance files must exist: {} {}".format(
                oed_ri_info_file, oed_ri_scope_file))
        if not show_all:
            account_df = account_df[common.OED_ACCOUNT_FIELDS].copy()
            location_df = location_df[common.OED_LOCATION_FIELDS].copy()
            if do_reinsuarnce:
                ri_info_df = ri_info_df[common.OED_REINS_INFO_FIELDS].copy()
                ri_scope_df = ri_scope_df[common.OED_REINS_SCOPE_FIELDS].copy()
    return (account_df, location_df, ri_info_df, ri_scope_df, do_reinsuarnce)


def run_inuring_level_risk_level(
        inuring_priority,
        account_df,
        location_df,
        items,
        coverages,
        fm_xrefs,
        xref_descriptions,
        ri_info_df,
        ri_scope_df,
        previous_risk_level,
        risk_level):

    reins_numbers_1 = ri_info_df[
        ri_info_df['InuringPriority'] == inuring_priority].ReinsNumber
    if reins_numbers_1.empty:
        return None
    reins_numbers_2 = ri_scope_df[
        ri_scope_df.isin({"ReinsNumber": reins_numbers_1}).ReinsNumber &
        (ri_scope_df.RiskLevel == risk_level)].ReinsNumber
    if reins_numbers_2.empty:
        return None

    ri_info_inuring_priority_df = ri_info_df[ri_info_df.isin(
        {"ReinsNumber": reins_numbers_2}).ReinsNumber]
    output_name = "ri_{}_{}".format(inuring_priority, risk_level)
    reinsurance_layer = ReinsuranceLayer(
        name=output_name,
        ri_info=ri_info_inuring_priority_df,
        ri_scope=ri_scope_df,
        accounts=account_df,
        locations=location_df,
        items=items,
        coverages=coverages,
        fm_xrefs=fm_xrefs,
        xref_descriptions=xref_descriptions,
        risk_level=risk_level
    )

    reinsurance_layer.generate_oasis_structures()
    reinsurance_layer.write_oasis_files()

    input_name = ""
    if inuring_priority == 1 and previous_risk_level is None:
        input_name = "ils"
    else:
        input_name = "ri_{}_{}".format(inuring_priority, previous_risk_level)

    reinsurance_layer_losses_df = common.run_fm(
        input_name, output_name, reinsurance_layer.xref_descriptions)

    return reinsurance_layer_losses_df


def run_test(
        run_name,
        account_df, location_df, ri_info_df, ri_scope_df,
        loss_factor,
        do_reinsurance):
    """
    Run the direct and reinsurance layers through the Oasis FM.abs
    Returns an array of net loss data frames, the first for the direct layers 
    and then one per inuring layer.
    """

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
        if do_reinsurance:
            (is_valid, reisurance_layers) = validate_reinsurance_structures(
                ri_info_df, ri_scope_df)
            if not is_valid:
                print("Reinsuarnce structure not valid")
                for reinsurance_layer in reisurance_layers:
                    if not reinsurance_layer.is_valid:
                        print("Inuring layer {} invalid:".format(
                            reinsurance_layer.inuring_priority))
                        for validation_message in reinsurance_layer.validation_messages:
                            print("\t{}".format(validation_message))

            for inuring_priority in range(1, ri_info_df['InuringPriority'].max() + 1):
                previous_risk_level = None
                for risk_level in common.REINS_RISK_LEVELS:
                    if ri_scope_df[ri_scope_df.RiskLevel == risk_level].shape[0] == 0:
                        continue
                    reinsurance_layer_losses_df = run_inuring_level_risk_level(
                        inuring_priority,
                        account_df,
                        location_df,
                        direct_layer.items,
                        direct_layer.coverages,
                        direct_layer.fm_xrefs,
                        direct_layer.xref_descriptions,
                        ri_info_df,
                        ri_scope_df,
                        previous_risk_level,
                        risk_level)
                    previous_risk_level = risk_level
                    if reinsurance_layer_losses_df is not None:
                        net_losses['Inuring priority:{} - Risk level:{}'.format(
                            inuring_priority, risk_level)] = reinsurance_layer_losses_df

    finally:
        os.chdir(cwd)

    return net_losses


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

    args = parser.parse_args()

    run_name = args.name
    oed_dir = args.oed_dir
    loss_factor = args.loss_factor

    (account_df, location_df, ri_info_df, ri_scope_df,
     do_reinsurance) = load_oed_dfs(oed_dir)

    net_losses = run_test(
        run_name,
        account_df, location_df, ri_info_df, ri_scope_df,
        loss_factor,
        do_reinsurance)

    for (description, net_loss) in net_losses.items():
        print(description)
        print(tabulate(net_loss, headers='keys', tablefmt='psql', floatfmt=".2f"))
        print("")
        print("")
