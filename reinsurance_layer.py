import pandas as pd
import os
import subprocess
import anytree
from common import *

class ReinsuranceLayer(object):
    """
    Set of reinsuarnce layers at the same priority.
    Generates ktools inputs and runs financial module.
    """

    def __init__(
            self, name, ri_info, ri_scope, accounts, locations, items, coverages, fm_xrefs, xref_descriptions):

        self.name = name
        self.ri_info = ri_info
        self.ri_scope = ri_scope
        self.accounts = accounts
        self.locations = locations

        self.coverages = items
        self.items = coverages
        self.fm_xrefs = fm_xrefs
        self.xref_descriptions = xref_descriptions

        self.item_ids = list()
        self.item_tivs = list()
        self.fmprogrammes = pd.DataFrame()
        self.fmprofiles = pd.DataFrame()
        self.fm_policytcs = pd.DataFrame()

    def generate_oasis_structures(self):

        program_node = anytree.Node(
            "Occurrence",
            level=OCCURRENCE_LEVEL,
            account_number=NOT_SET_ID,
            policy_number=NOT_SET_ID,
            location_number=NOT_SET_ID)

        current_location_number = 0
        current_policy_number = 0
        current_account_number = 0
        current_location_node = 0
        current_policy_node = 0
        current_account_node = 0

        #
        # General risk structure
        #

        coverages_list = list()
        items_list = list()
        fmprogrammes_list = list()
        fmprofiles_list = list()
        fm_policytcs_list = list()
        fm_xrefs_list = list()
        xref_descriptions_list = list()

        policytc_id = 0

        policytc_id = policytc_id + 1
        nolosstc_id = policytc_id
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

        policytc_id = policytc_id + 1
        passthroughtc_id = policytc_id
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

        node_layer_profile_map = {}
        nodes = ()
        location_df = pd.merge(
            self.accounts, self.locations, on="AccountNumber")

        inuring_level_risk_level = REINS_RISK_LEVEL_PORTFOLIO
        program_node_level_id = 3
        if inuring_level_risk_level == REINS_RISK_LEVEL_PORTFOLIO:
            program_node_level_id = 2
        program_node = anytree.Node(
            "Occurrence",
            parent=None,
            level_id=program_node_level_id,
            agg_id=1,
            account_number=NOT_SET_ID,
            policy_number=NOT_SET_ID,
            location_number=NOT_SET_ID)

        xref_descriptions = self.xref_descriptions.sort_values(
            by=["location_number", "policy_number", "account_number"])

        agg_id = 0
        if inuring_level_risk_level == REINS_RISK_LEVEL_PORTFOLIO:
            for index, row in xref_descriptions.iterrows():
                anytree.Node(
                    "",
                    parent=program_node,
                    level_id=1,
                    agg_id=row.xref_id,
                    account_number=NOT_SET_ID,
                    policy_number=NOT_SET_ID,
                    location_number=NOT_SET_ID)
        elif inuring_level_risk_level == REINS_RISK_LEVEL_ACCOUNT:
            for index, row in xref_descriptions.iterrows():
                if current_account_number != row.AccountNumber:
                    agg_id = agg_id + 1
                    current_account_number = row.AccountNumber
                    anytree.Node(
                        "",
                        parent=program_node,
                        level_id=2,
                        agg_id=agg_id,
                        account_number=row.AccountNumber,
                        policy_number=NOT_SET_ID,
                        location_number=NOT_SET_ID)
                anytree.Node(
                    "",
                    parent=current_account_node,
                    level_id=1,
                    agg_id=row.xref_id,
                    account_number=NOT_SET_ID,
                    policy_number=NOT_SET_ID,
                    location_number=NOT_SET_ID)
        elif inuring_level_risk_level == REINS_RISK_LEVEL_POLICY:
            for index, row in xref_descriptions.iterrows():
                if current_policy_number != row.PolicyNumber:
                    agg_id = agg_id + 1
                    current_policy_number = row.PolicyNumber
                    anytree.Node(
                        "",
                        parent=program_node,
                        level_id=2,
                        agg_id=agg_id,
                        account_number=row.AccountNumber,
                        policy_number=row.PolicyNumber,
                        location_number=NOT_SET_ID)
                anytree.Node(
                    "",
                    parent=current_account_node,
                    level_id=1,
                    agg_id=row.xref_id,
                    account_number=NOT_SET_ID,
                    policy_number=NOT_SET_ID,
                    location_number=NOT_SET_ID)
        elif inuring_level_risk_level == REINS_RISK_LEVEL_LOCATION:
            for index, row in xref_descriptions.iterrows():
                if current_location_number != row.LocationNumber:
                    agg_id = agg_id + 1
                    current_location_number = row.LocationNumber
                    anytree.Node(
                        "",
                        parent=program_node,
                        level_id=2,
                        agg_id=agg_id,
                        account_number=row.AccountNumber,
                        policy_number=row.PolicyNumber,
                        location_number=row.LocationNumber)
                anytree.Node(
                    "",
                    parent=current_account_node,
                    level_id=1,
                    agg_id=row.xref_id,
                    account_number=NOT_SET_ID,
                    policy_number=NOT_SET_ID,
                    location_number=NOT_SET_ID)

        #
        # Overlay the resinsurance structure
        #
        layer_id = 0
        covered_accounts_all = False
        covered_accounts = ()
        for ri_info_index, ri_info_row in self.ri_info.iterrows():
            layer_id = layer_id + 1
            if ri_info_row.ReinsType == REINS_TYPE_FAC:

                for node in anytree.iterators.LevelOrderIter(program_node):
                    node_layer_profile_map[(node, layer_id)] = nolosstc_id

                policytc_id = policytc_id + 1
                fmprofiles_list.append(FmProfile(
                    policytc_id=policytc_id,
                    calcrule_id=DEDUCTIBLE_LIMIT_AND_SHARE_CALCRULE_ID,
                    ccy_id=-1,
                    allocrule_id=ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID,
                    deductible=ri_info_row.RiskAttachmentPoint,
                    limit=ri_info_row.RiskLimit,
                    share_prop_of_lim=1.0,
                    deductible_prop_of_loss=0.0,    # Not used
                    limit_prop_of_loss=0.0,         # Not used
                    deductible_prop_of_tiv=0.0,     # Not used
                    limit_prop_of_tiv=0.0,          # Not used
                    deductible_prop_of_limit=0.0    # Not used
                ))

                for ri_scope_index, ri_scope_row in ri_scope_df[ri_scope_df.ReinsNumber == ri_info_row.ReinsNumber].iterrows():
                    if ri_scope_row.RiskLevel == REINS_RISK_LEVEL_LOCATION:
                        nodes = anytree.search.findall(
                            program_node, filter_=lambda node:
                            (node.account_number, node.policy_number, node.location_number) == (ri_scope_row.AccountNumber, ri_scope_row.PolicyNumber, ri_scope_row.LocationNumbe))
                        for node in nodes:
                            node_layer_profile_map[(
                                node, layer_id)] = policytc_id
                            for child in anytree.iterators.LevelOrderIter(node):
                                node_layer_profile_map[(
                                    child, layer_id)] = nolosstc_id
                            parent = node.parent
                            while parent != program_node:
                                node_layer_profile_map[(
                                    parent, layer_id)] = nolosstc_id
                    elif ri_scope_row.RiskLevel == REINS_RISK_LEVEL_POLICY:
                        nodes = anytree.search.findall(
                            program_node, filter_=lambda node:
                                (node.account_number, node.policy_number, node.location_number) == (ri_scope_row.AccountNumber, ri_scope_row.PolicyNumber, NOT_SET_ID))
                        for node in nodes:
                            node_layer_profile_map[(
                                node, layer_id)] = policytc_id
                    elif ri_scope_row.RiskLevel == REINS_RISK_LEVEL_ACCOUNT:
                        nodes = anytree.search.findall(
                            program_node, filter_=lambda node:
                                (node.account_number, node.policy_number, node.location_number) == (ri_scope_row.AccountNumber, NOT_SET_ID, NOT_SET_ID))
                        for node in nodes:
                            node_layer_profile_map[(
                                node, layer_id)] = policytc_id
                    else:
                        raise Exception(
                            "Unsupported risk level: {}".format(ri_scope_row.RiskLevel))

            elif ri_info_row.ReinsType == REINS_TYPE_QUOTA_SHARE:

                # Add pass through layer for all nodes
                for node in anytree.iterators.LevelOrderIter(program_node):
                    node_layer_profile_map[(node, layer_id)] = nolosstc_id
                covered_accounts_all = True

                # Add any risk limits
                # TODO risk specific limits
                scope_rows = self.ri_scope[self.ri_scope.ReinsNumber ==
                                         ri_info_row.ReinsNumber]
                if len(scope_rows) == 0:
                    raise Exception("No scope set")
                elif len(scope_rows) > 1:
                    raise Exception("Variable scope not supported")
                else:  # exactly 1 row
                    risk_level = scope_rows.iloc[0].RiskLevel
                    if risk_level == REINS_RISK_LEVEL_PORTFOLIO:
                        pass
                    else:
                        # Add the risk level terms
                        policytc_id = policytc_id + 1
                        fmprofiles_list.append(FmProfile(
                            policytc_id=policytc_id,
                            calcrule_id=DEDUCTIBLE_LIMIT_AND_SHARE_CALCRULE_ID,
                            ccy_id=-1,
                            allocrule_id=ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID,
                            deductible=ri_info_row.RiskAttachmentPoint,
                            limit=ri_info_row.RiskLimit,
                            share_prop_of_lim=ri_info_row.CededPercent,
                            deductible_prop_of_loss=0.0,    # Not used
                            limit_prop_of_loss=0.0,         # Not used
                            deductible_prop_of_tiv=0.0,     # Not used
                            limit_prop_of_tiv=0.0,          # Not used
                            deductible_prop_of_limit=0.0    # Not used
                        ))
                        if risk_level == REINS_RISK_LEVEL_ACCOUNT:
                            nodes = anytree.search.findall(
                                program_node, filter_=lambda node:
                                    node.level == ACCOUNT_LEVEL)
                            for node in nodes:
                                node_layer_profile_map[(
                                    node, layer_id)] = policytc_id
                        elif risk_level == REINS_RISK_LEVEL_POLICY:
                            nodes = anytree.search.findall(
                                program_node, filter_=lambda node:
                                    node.level == POLICY_LEVEL)
                            for node in nodes:
                                node_layer_profile_map[(
                                    node, layer_id)] = policytc_id
                        elif risk_level == REINS_RISK_LEVEL_LOCATION:
                            nodes = anytree.search.findall(
                                program_node, filter_=lambda node:
                                    node.level == LOCATION_LEVEL)
                            for node in nodes:
                                node_layer_profile_map[(
                                    node, layer_id)] = policytc_id
                        else:
                            raise Exception(
                                "Unsupported risk level: {}".format(risk_level))

                # Add occurrence limit and share
                policytc_id = policytc_id + 1
                occurrence_limit = ri_info_row.OccLimit
                if occurrence_limit == 0:
                    occurrence_limit = 999999999999999

                fmprofiles_list.append(FmProfile(
                    policytc_id=policytc_id,
                    calcrule_id=DEDUCTIBLE_LIMIT_AND_SHARE_CALCRULE_ID,
                    ccy_id=-1,
                    allocrule_id=ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID,
                    deductible=0.0,
                    limit=occurrence_limit,
                    share_prop_of_lim=ri_info_row.CededPercent,  # Not used
                    deductible_prop_of_loss=0.0,                # Not used
                    limit_prop_of_loss=0.0,                     # Not used
                    deductible_prop_of_tiv=0.0,                 # Not used
                    limit_prop_of_tiv=0.0,                      # Not used
                    deductible_prop_of_limit=0.0                # Not used
                ))
                node_layer_profile_map[(program_node, layer_id)] = policytc_id
            else:
                raise Exception("ReinsType not supported yet: {}".format(
                    ri_info_row.ReinsType))

        max_layer_id = layer_id
        max_agg_id = 0

        for node in anytree.iterators.LevelOrderIter(program_node):
            if node.parent is not None:
                fmprogrammes_list.append(
                    FmProgramme(
                        from_agg_id=node.agg_id,
                        level_id=node.level_id,
                        to_agg_id=node.parent.agg_id
                    )
                )

        # print node_layer_profile_map

        for layer_id in range(1, max_layer_id + 1):
            for node in anytree.iterators.LevelOrderIter(program_node):
                if node.level_id > 1:
                    fm_policytcs_list.append(FmPolicyTc(
                        layer_id=layer_id,
                        level_id=1,
                        agg_id=node.agg_id,
                        policytc_id=node_layer_profile_map[(node, layer_id)]
                    ))

        # Write out ktools input files
        #self.coverages = pd.DataFrame(coverages_list)
        #self.items = pd.DataFrame(items_list)
        self.fmprogrammes = pd.DataFrame(fmprogrammes_list)
        self.fmprofiles = pd.DataFrame(fmprofiles_list)
        self.fm_policytcs = pd.DataFrame(fm_policytcs_list)
        #self.fm_xrefs = pd.DataFrame(fm_xrefs_list)
        #self.xref_descriptions = pd.DataFrame(xref_descriptions_list)

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
        print(command)
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

        print(losses_df.head())
        print(self.xref_descriptions.head())

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