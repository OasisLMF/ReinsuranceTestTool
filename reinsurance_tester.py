"""
Test tool for reinsurance functaionality. 
Takes input data in OED format, and invokes the Oasis Platform financial module.
"""

import argparse
import itertools
import os
import shutil
import subprocess
from collections import namedtuple
from tabulate import tabulate
import pandas as pd

DEDUCTIBLE_AND_LIMIT_CALCRULE_ID = 1
FRANCHISE_DEDUCTIBLE_AND_LIMIT_CALCRULE_ID = 3
DEDUCTIBLE_ONLY_CALCRULE_ID = 12
DEDUCTIBLE_AS_A_CAP_ON_THE_RETENTION_OF_INPUT_LOSSES_CALCRULE_ID = 10
DEDUCTIBLE_AS_A_FLOOR_ON_THE_RETENTION_OF_INPUT_LOSSES_CALCRULE_ID = 11
DEDUCTIBLE_LIMIT_AND_SHARE_CALCRULE_ID = 2
DEDUCTIBLE_AND_LIMIT_AS_A_PROPORTION_OF_LOSS_CALCRUKE_ID = 5
DEDUCTIBLE_WITH_LIMIT_AS_A_PROPORTION_OF_LOSS_CALCRUKE_ID = 9
LIMIT_ONLY_CALCRULE_ID = 14
LIMIT_AS_A_PROPORTION_OF_LOSS_CALCRULE_ID = 15
DEDUCTIBLE_AS_A_PROPORTION_OF_LOSS_CALCRULE_ID = 16

NO_ALLOCATION_ALLOC_ID = 0
ALLOCATE_TO_ITEMS_BY_GUL_ALLOC_ID = 1
ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID = 2

BUILDING_COVERAGE_TYPE_ID = 1
OTHER_BUILDING_COVERAGE_TYPE_ID = 2
CONTENTS_COVERAGE_TYPE_ID = 3
TIME_COVERAGE_TYPE_ID = 4

PERIL_WIND = 1

REINS_TYPE_FAC = "FAC"
REINS_TYPE_CAT_XL = "CAT XL"

REINS_ATTACHMENT_BASIS_LOCATION = "LO"

GUL_INPUTS_FILES = [
    'coverages',
    'gulsummaryxref',
    'items']

IL_INPUTS_FILES = [
    'fm_policytc',
    'fm_profile',
    'fm_programme',
    'fm_xref',
    'fmsummaryxref']

OPTIONAL_INPUTS_FILES = [
    'events']

CONVERSION_TOOLS = {
    'coverages': '../ktools/coveragetobin',
    'events': '../ktools/evetobin',
    'fm_policytc': '../ktools/fmpolicytctobin',
    'fm_profile': '../ktools/fmprofiletobin',
    'fm_programme': '../ktools/fmprogrammetobin',
    'fm_xref': '../ktools/fmxreftobin',
    'fmsummaryxref': '../ktools/fmsummaryxreftobin',
    'gulsummaryxref': '../ktools/gulsummaryxreftobin',
    'items': "../ktools/itemtobin"}

COVERAGE_TYPES = [
    BUILDING_COVERAGE_TYPE_ID,
    OTHER_BUILDING_COVERAGE_TYPE_ID,
    CONTENTS_COVERAGE_TYPE_ID,
    TIME_COVERAGE_TYPE_ID]

PERILS = [PERIL_WIND]

Item = namedtuple(
    "Item", "item_id coverage_id areaperil_id vulnerability_id group_id")
Coverage = namedtuple(
    "Coverage", "coverage_id tiv")
FmProgramme = namedtuple(
    "FmProgramme", "from_agg_id level_id to_agg_id")
FmProfile = namedtuple(
    "FmProfile", "policytc_id calcrule_id allocrule_id ccy_id deductible limit " +
    "share_prop_of_lim deductible_prop_of_loss limit_prop_of_loss deductible_prop_of_tiv " +
    "limit_prop_of_tiv deductible_prop_of_limit")
FmPolicyTc = namedtuple(
    "FmPolicyTc", "layer_id level_id agg_id policytc_id")
GulSummaryXref = namedtuple(
    "GulSummaryXref", "coverage_id summary_id summaryset_id")
FmSummaryXref = namedtuple(
    "FmSummaryXref", "output_id summary_id summaryset_id")
FmXref = namedtuple(
    "FmXref", "output_id agg_id layer_id")
XrefDescription = namedtuple(
    "Description", ("xref_id policy_id account_number location_number coverage_type_id peril_id tiv"))
GulRecord = namedtuple(
    "GulRecord", "event_id item_id sidx loss")

# Generate the policy and reinsurance data stuctures
class DirectLayer(object):
    """
    Set of direct policiies.
    """
    def __init__(self, accounts, locations):
        self.accounts = accounts
        self.locations = locations

        self.item_ids = list()
        self.item_tivs = list()
        self.coverages = pd.DataFrame()
        self.items = pd.DataFrame()
        self.fmprogrammes = pd.DataFrame()
        self.fmprofiles = pd.DataFrame()
        self.fm_policytcs = pd.DataFrame()
        self.fm_xrefs = pd.DataFrame()
        self.xref_descriptions = pd.DataFrame()

    def _get_location_tiv(self, location, coverage_type_id):
        switcher = {
            BUILDING_COVERAGE_TYPE_ID: location.BuildingTIV,
            OTHER_BUILDING_COVERAGE_TYPE_ID: location.OtherTIV,
            CONTENTS_COVERAGE_TYPE_ID: location.ContentsTIV,
            TIME_COVERAGE_TYPE_ID: location.BITIV
        }
        return switcher.get(coverage_type_id, 0)

    def generate_oasis_structures(self):
        coverage_id = 0
        item_id = 0
        group_id = 0
        policy_agg_id = 0
        policytc_id = 0

        coverages_list = list()
        items_list = list()
        fmprogrammes_list = list()
        fmprofiles_list = list()
        fm_policytcs_list = list()
        fm_xrefs_list = list()
        xref_descriptions_list = list()

        site_agg_id = 0
        for policy_index, policy in self.accounts.iterrows():
            policy_agg_id = policy_agg_id + 1
            policytc_id = policytc_id + 1
            fmprofiles_list.append(FmProfile(
                policytc_id=policytc_id,
                calcrule_id=DEDUCTIBLE_AND_LIMIT_CALCRULE_ID,
                ccy_id=-1,
                allocrule_id=ALLOCATE_TO_ITEMS_BY_GUL_ALLOC_ID,
                deductible=policy.Ded6,
                limit=policy.Limit6,
                share_prop_of_lim=0.0,          # Not used
                deductible_prop_of_loss=0.0,    # Not used
                limit_prop_of_loss=0.0,         # Not used
                deductible_prop_of_tiv=0.0,     # Not used
                limit_prop_of_tiv=0.0,          # Not used
                deductible_prop_of_limit=0.0    # Not used
            ))
            fm_policytcs_list.append(FmPolicyTc(
                layer_id=1,
                level_id=2,
                agg_id=policy_agg_id,
                policytc_id=policytc_id
            ))
            for location_index, location in self.locations.loc[self.locations["AccountNumber"] == policy.AccountNumber].iterrows():
                group_id = group_id + 1
                site_agg_id = site_agg_id + 1
                policytc_id = policytc_id + 1
                fmprofiles_list.append(FmProfile(
                    policytc_id=policytc_id,
                    calcrule_id=DEDUCTIBLE_AND_LIMIT_CALCRULE_ID,
                    ccy_id=-1,
                    allocrule_id=ALLOCATE_TO_ITEMS_BY_GUL_ALLOC_ID,
                    deductible=location.Ded6,
                    limit=location.Limit6,
                    share_prop_of_lim=0.0,          # Not used
                    deductible_prop_of_loss=0.0,    # Not used
                    limit_prop_of_loss=0.0,         # Not used
                    deductible_prop_of_tiv=0.0,     # Not used
                    limit_prop_of_tiv=0.0,          # Not used
                    deductible_prop_of_limit=0.0    # Not used
                ))
                fm_policytcs_list.append(FmPolicyTc(
                    layer_id=1,
                    level_id=1,
                    agg_id=site_agg_id,
                    policytc_id=policytc_id
                ))
                fmprogrammes_list.append(
                    FmProgramme(
                        from_agg_id=site_agg_id,
                        level_id=2,
                        to_agg_id=policy_agg_id
                    )
                )

                for coverage_type_id in COVERAGE_TYPES:
                    tiv = self._get_location_tiv(location, coverage_type_id)
                    if tiv > 0:
                        coverage_id = coverage_id + 1
                        coverages_list.append(
                            Coverage(
                                coverage_id=coverage_id,
                                tiv=tiv
                            ))
                        for peril in PERILS:
                            item_id = item_id + 1
                            self.item_ids.append(item_id)
                            self.item_tivs.append(tiv)
                            items_list.append(
                                Item(
                                    item_id=item_id,
                                    coverage_id=coverage_id,
                                    areaperil_id=-1,
                                    vulnerability_id=-1,
                                    group_id=group_id
                                ))
                            fmprogrammes_list.append(
                                FmProgramme(
                                    from_agg_id=item_id,
                                    level_id=1,
                                    to_agg_id=site_agg_id
                                )
                            )
                            fm_xrefs_list.append(
                                FmXref(
                                    output_id=item_id,
                                    agg_id=item_id,
                                    layer_id=1
                                ))
                            xref_descriptions_list.append(XrefDescription(
                                xref_id=item_id,
                                account_number=location.AccountNumber,
                                location_number=location.LocationNumber,
                                coverage_type_id=coverage_type_id,
                                peril_id=peril,
                                policy_id=policy.PolicyNumber,
                                tiv=tiv
                            )
                            )

        self.coverages = pd.DataFrame(coverages_list)
        self.items = pd.DataFrame(items_list)
        self.fmprogrammes = pd.DataFrame(fmprogrammes_list)
        self.fmprofiles = pd.DataFrame(fmprofiles_list)
        self.fm_policytcs = pd.DataFrame(fm_policytcs_list)
        self.fm_xrefs = pd.DataFrame(fm_xrefs_list)
        self.xref_descriptions = pd.DataFrame(xref_descriptions_list)

    def write_oasis_files(self):

        self.coverages.to_csv("coverages.csv", index=False)
        self.items.to_csv("items.csv", index=False)
        self.fmprogrammes.to_csv("fm_programme.csv", index=False)
        self.fmprofiles.to_csv("fm_profile.csv", index=False)
        self.fm_policytcs.to_csv("fm_policytc.csv", index=False)
        self.fm_xrefs.to_csv("fm_xref.csv", index=False)

        directory = "direct"
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)
        input_files = GUL_INPUTS_FILES + IL_INPUTS_FILES

        for input_file in input_files:
            conversion_tool = CONVERSION_TOOLS[input_file]
            input_file_path = input_file + ".csv"
            if not os.path.exists(input_file_path):
                continue

            output_file_path = os.path.join(directory, input_file + ".bin")
            command = "{} < {} > {}".format(
                conversion_tool, input_file_path, output_file_path)
            proc = subprocess.Popen(command, shell=True)
            proc.wait()
            if proc.returncode != 0:
                raise Exception(
                    "Failed to convert {}: {}".format(input_file_path, command))

    def apply_fm(self, loss_percentage_of_tiv=1.0, net=False):
        guls_list = list()
        for item_id, tiv in zip(self.item_ids, self.item_tivs):
            event_loss = loss_percentage_of_tiv * tiv
            guls_list.append(
                GulRecord(event_id=1, item_id=item_id, sidx=-1, loss=event_loss))
            guls_list.append(
                GulRecord(event_id=1, item_id=item_id, sidx=1, loss=event_loss))
        guls_df = pd.DataFrame(guls_list)
        guls_df.to_csv("guls.csv", index=False)
        net_flag = ""
        if net:
            net_flag = "-n"
        command = "../ktools/gultobin -S 1 < guls.csv | ../ktools/fmcalc -p direct {} | tee ils.bin | ../ktools/fmtocsv > ils.csv".format(
            net_flag)
        proc = subprocess.Popen(command, shell=True)
        proc.wait()
        if proc.returncode != 0:
            raise Exception("Failed to run fm")
        losses_df = pd.read_csv("ils.csv")
        losses_df.drop(losses_df[losses_df.sidx != 1].index, inplace=True)
        del losses_df['sidx']
        guls_df.drop(guls_df[guls_df.sidx != 1].index, inplace=True)
        del guls_df['event_id']
        del guls_df['sidx']
        guls_df = pd.merge(
            self.xref_descriptions,
            guls_df, left_on=['xref_id'], right_on=['item_id'])
        losses_df = pd.merge(
            guls_df,
            losses_df, left_on='xref_id', right_on='output_id',
            suffixes=["_gul", "_il"])
        del losses_df['event_id']
        del losses_df['output_id']
        del losses_df['xref_id']
        del losses_df['item_id']

        return losses_df

class ReinsuranceLayer(object):

    def __init__(
        self, name, ri_info, ri_scope, accounts, locations, items, coverages, xref_descriptions):
        
        self.name = name
        self.ri_info = ri_info
        self.ri_scope = ri_scope
        self.accounts = accounts
        self.locations = locations

        self.coverages = items
        self.items = coverages
        self.xref_descriptions = xref_descriptions

        self.item_ids = list()
        self.item_tivs = list()
        self.fmprogrammes = pd.DataFrame()
        self.fmprofiles = pd.DataFrame()
        self.fm_policytcs = pd.DataFrame()
        self.fm_xrefs = pd.DataFrame()

    def generate_oasis_structures(self):

        level_1_agg_id = 0
        level_2_agg_id = 0
        level_3_agg_id = 0
        layer_tc_id = 0
        layer_layer_id = 0

        fmprogrammes_list = list()
        fmprofiles_list = list()
        fm_policytcs_list = list()
        fm_xrefs_list = list()

        layer_tc_id = layer_tc_id + 1
        passthroughtc_id = layer_tc_id
        fmprofiles_list.append(FmProfile(
            policytc_id=passthroughtc_id,
            calcrule_id=DEDUCTIBLE_ONLY_CALCRULE_ID,
            ccy_id=-1,
            allocrule_id=ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID,
            deductible=0.0,
            limit=0.0,                      # Not used
            share_prop_of_lim=0.0,          # Not used
            deductible_prop_of_loss=0.0,    # Not used
            limit_prop_of_loss=0.0,         # Not used
            deductible_prop_of_tiv=0.0,     # Not used
            limit_prop_of_tiv=0.0,          # Not used
            deductible_prop_of_limit=0.0    # Not used
        ))

        layer_tc_id = layer_tc_id + 1
        nolosstc_id = layer_tc_id
        fmprofiles_list.append(FmProfile(
            policytc_id=nolosstc_id,
            calcrule_id=LIMIT_ONLY_CALCRULE_ID,
            ccy_id=-1,
            allocrule_id=ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID,
            deductible=0.0,                 # Not used
            limit=0.0,
            share_prop_of_lim=0.0,          # Not used
            deductible_prop_of_loss=0.0,    # Not used
            limit_prop_of_loss=0.0,         # Not used
            deductible_prop_of_tiv=0.0,     # Not used
            limit_prop_of_tiv=0.0,          # Not used
            deductible_prop_of_limit=0.0    # Not used
        ))

        level_1_agg_id = level_1_agg_id + 1
        noloss_level_1_agg_id = level_1_agg_id
        fm_policytcs_list.append(FmPolicyTc(
            layer_id=1,
            level_id=1,
            agg_id=noloss_level_1_agg_id,
            policytc_id=nolosstc_id
        ))

        first = True

        reinsurance_layers = pd.merge(
            left=self.ri_info,right=self.ri_scope, left_on='ReinsNumber', right_on='ReinsNumber',
            suffixes=('_treaty', '_risk'))
        for index, layer in reinsurance_layers.iterrows():

            if first:
                level_1_agg_id = level_1_agg_id + 1
            layer_tc_id = layer_tc_id + 1 
            layer_layer_id = layer_layer_id + 1

            if layer.ReinsType == REINS_TYPE_CAT_XL:
                fmprofiles_list.append(FmProfile(
                    policytc_id=layer_tc_id,
                    calcrule_id=DEDUCTIBLE_LIMIT_AND_SHARE_CALCRULE_ID,
                    ccy_id=-1,
                    allocrule_id=ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID,
                    deductible=layer.OccurenceAttachmentPoint,
                    limit=layer.OccurenceLimit,
                    share_prop_of_lim=layer.CededAmount_treaty * layer.CededAmount_risk * layer.TreatyPercent * layer.PlacementPercent,
                    deductible_prop_of_loss=0.0,    # Not used
                    limit_prop_of_loss=0.0,         # Not used
                    deductible_prop_of_tiv=0.0,     # Not used
                    limit_prop_of_tiv=0.0,          # Not used
                    deductible_prop_of_limit=0.0    # Not used
                ))
            elif layer.ReinsType == REINS_TYPE_FAC:
                fmprofiles_list.append(FmProfile(
                    policytc_id=layer_tc_id,
                    calcrule_id=DEDUCTIBLE_LIMIT_AND_SHARE_CALCRULE_ID,
                    ccy_id=-1,
                    allocrule_id=ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID,
                    deductible=layer.RiskAttachmentPoint,
                    limit=layer.RiskLimit,
                    share_prop_of_lim=layer.CededAmount_treaty * layer.CededAmount_risk * layer.TreatyPercent * layer.PlacementPercent,
                    deductible_prop_of_loss=0.0,    # Not used
                    limit_prop_of_loss=0.0,         # Not used
                    deductible_prop_of_tiv=0.0,     # Not used
                    limit_prop_of_tiv=0.0,          # Not used
                    deductible_prop_of_limit=0.0    # Not usedfmcalc -p ri1 < ils.bin | tee ri1.bin | fmtocsv
                ))

            fm_policytcs_list.append(FmPolicyTc(
                layer_id=layer_layer_id,
                level_id=1,
                agg_id=level_1_agg_id,
                policytc_id=layer_tc_id
            ))

            if first:
                if layer.ReinsType == REINS_TYPE_CAT_XL:
                    for __, xref_description in self.xref_descriptions.iterrows():
                        fmprogrammes_list.append(
                            FmProgramme(
                                from_agg_id=xref_description.xref_id,
                                level_id=1,
                                to_agg_id=level_1_agg_id
                            )
                        )
                elif layer.ReinsType == REINS_TYPE_FAC:
                    # With filter?
                    location_scope = pd.merge(
                        left=self.ri_scope, right=self.locations,
                        left_on=['AccountNumber', 'LocationNumber'],
                        right_on=['AccountNumber', 'LocationNumber'],
                        )

                    for __, xref_description in self.xref_descriptions.iterrows():
                        if (
                            xref_description.location_number == layer.LocationNumber and
                            xref_description.account_number == layer.AccountNumber):

                            fmprogrammes_list.append(
                                FmProgramme(
                                    from_agg_id=xref_description.xref_id,
                                    level_id=1,
                                    to_agg_id=level_1_agg_id
                                )
                            )
                        else:
                            fmprogrammes_list.append(
                                FmProgramme(
                                    from_agg_id=xref_description.xref_id,
                                    level_id=1,
                                    to_agg_id=noloss_level_1_agg_id
                                )
                            )
            if first:
                first = False


        output_id = 0
        for __, xref_description in self.xref_descriptions.iterrows():
            output_id = output_id + 1
            fm_xrefs_list.append(
                FmXref(
                    output_id=output_id, #xref_description.xref_id,
                    agg_id=xref_description.xref_id,
                    layer_id=layer_layer_id + 1 # max layer ID
                ))

        self.fmprogrammes = pd.DataFrame(fmprogrammes_list)
        self.fmprofiles = pd.DataFrame(fmprofiles_list)
        self.fm_policytcs = pd.DataFrame(fm_policytcs_list)
        self.fm_xrefs = pd.DataFrame(fm_xrefs_list)

    def write_oasis_files(self):

        self.fmprogrammes.to_csv("fm_programme.csv", index=False)
        self.fmprofiles.to_csv("fm_profile.csv", index=False)
        self.fm_policytcs.to_csv("fm_policytc.csv", index=False)
        self.fm_xrefs.to_csv("fm_xref.csv", index=False)

        directory = self.name
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        input_files = GUL_INPUTS_FILES + IL_INPUTS_FILES
        
        for input_file in input_files:
            conversion_tool = CONVERSION_TOOLS[input_file]
            input_file_path = input_file + ".csv"
            if not os.path.exists(input_file_path):
                continue

            output_file_path = os.path.join(directory, input_file + ".bin")
            command = "{} < {} > {}".format(
                conversion_tool, input_file_path, output_file_path)
            proc = subprocess.Popen(command, shell=True)
            proc.wait()
            if proc.returncode != 0:
                raise Exception(
                    "Failed to convert {}: {}".format(input_file_path, command))

    def apply_fm(self, input):
        command = \
            "../ktools/fmcalc -p {0} -n < {1}.bin | tee {0}.bin | ../ktools/fmtocsv > {0}.csv".format(
                self.name, input)

        proc = subprocess.Popen(command, shell=True)
        proc.wait()
        if proc.returncode != 0:
            raise Exception("Failed to run fm")
        losses_df = pd.read_csv("{}.csv".format(self.name))
        inputs_df = pd.read_csv("{}.csv".format(input))
        losses_df.drop(losses_df[losses_df.sidx != 1].index, inplace=True)
        inputs_df.drop(inputs_df[inputs_df.sidx != 1].index, inplace=True)
        losses_df = pd.merge(
            inputs_df,
            losses_df, left_on='output_id', right_on='output_id',
            suffixes=('_pre', '_net'))
        losses_df = pd.merge(
            self.xref_descriptions,
            losses_df, left_on='xref_id', right_on='output_id')
        del losses_df['event_id_pre']
        del losses_df['sidx_pre']
        del losses_df['event_id_net']
        del losses_df['sidx_net']
        del losses_df['output_id']
        del losses_df['xref_id']
        return losses_df


def load_oed_dfs(oed_dir):

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

        # RI info file
        oed_ri_info_file = os.path.join(oed_dir, "ri_info.csv")
        if not os.path.exists(oed_ri_info_file):
            print("Path does not exist: {}".format(oed_ri_info_file))
            exit(1)
        ri_info_df = pd.read_csv(oed_ri_info_file)

        # RI scope file
        oed_ri_scope_file = os.path.join(oed_dir, "ri_scope.csv")
        if not os.path.exists(oed_ri_scope_file):
            print("Path does not exist: {}".format(oed_ri_scope_file))
            exit(1)
        ri_scope_df = pd.read_csv(oed_ri_scope_file)
    
    return (account_df, location_df, ri_info_df, ri_scope_df)

def run_test(run_name, account_df, location_df, ri_info_df, ri_scope_df, loss_factor):

    if os.path.exists(run_name):
        shutil.rmtree(run_name)
    os.mkdir(run_name)

    net_losses = []

    cwd = os.getcwd()
    try:
        os.chdir(run_name)

        direct_layer = DirectLayer(account_df, location_df)
        direct_layer.generate_oasis_structures()
        direct_layer.write_oasis_files()
        losses_df = direct_layer.apply_fm(loss_percentage_of_tiv=loss_factor, net=False)
        net_losses.append(losses_df)
#        print("Direct layer loss")
#        print(tabulate(losses_df, headers='keys', tablefmt='psql', floatfmt=".2f"))
#        print("")
#        print("")

        for inuring_priority in range(1, ri_info_df['InuringPriority'].max()+1):
            reinsurance_layer = ReinsuranceLayer(
                name="ri{}".format(inuring_priority),
                ri_info = ri_info_df.loc[ri_info_df['InuringPriority'] == inuring_priority],
                ri_scope = ri_scope_df,
                accounts = account_df,
                locations = location_df,
                items=direct_layer.items,
                coverages=direct_layer.coverages,
                xref_descriptions=direct_layer.xref_descriptions
            )

            reinsurance_layer.generate_oasis_structures()
            reinsurance_layer.write_oasis_files()
            if inuring_priority == 1:
                reinsurance_layer_losses_df = reinsurance_layer.apply_fm("ils")
            else:
                reinsurance_layer_losses_df = reinsurance_layer.apply_fm("ri{}".format(inuring_priority-1))        

            net_losses.append(reinsurance_layer_losses_df)

            # print("Reinsurance - first inuring layer")
            # print(tabulate(treaty_losses_df, headers='keys', tablefmt='psql', floatfmt=".2f"))
            # print("")
            # print("")

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

    (account_df, location_df, ri_info_df, ri_scope_df) = load_oed_dfs(oed_dir)

    net_losses = run_test(run_name, account_df, location_df, ri_info_df, ri_scope_df, loss_factor)

    for net_loss in net_losses:
        #print("Reinsurance - first inuring layer")
        print(tabulate(net_loss, headers='keys', tablefmt='psql', floatfmt=".2f"))
        print("")
        print("")