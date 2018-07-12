import pandas as pd
import os
import subprocess
import anytree
import shutil
import common
from collections import namedtuple


def validate_reinsurance_structures(ri_info_df, ri_scope_df):
    pass

class ReinsuranceLayer(object):
    """
    Generates ktools inputs and runs financial module for a
    set of reinsurance layers.
    """

    def __init__(self, name, ri_info, ri_scope, accounts, locations, 
                items, coverages, fm_xrefs, xref_descriptions, risk_level):

        self.name = name
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

        self.risk_level = risk_level

        self.ri_info = ri_info
        self.ri_scope = ri_scope

        self.add_profiles_args = namedtuple(
            "AddProfilesArgs", 
            "program_node, ri_info_row, scope_rows, layer_id, " \
            "node_layer_profile_map, fmprofiles_list, nolossprofile_id, passthroughprofile_id")

    def _add_program_node(self, level_id):
        return anytree.Node(
            "Occurrence",
            parent=None,
            level_id=level_id,
            agg_id=1,
            account_number=common.NOT_SET_ID,
            policy_number=common.NOT_SET_ID,
            location_number=common.NOT_SET_ID)

    def _add_item_node(self, xref_id, parent):
        return anytree.Node(
            "Item_id:{}".format(xref_id),
            parent=parent,
            level_id=1,
            agg_id=xref_id,
            account_number=common.NOT_SET_ID,
            policy_number=common.NOT_SET_ID,
            location_number=common.NOT_SET_ID)

    def _add_location_node(
        self, level_id, agg_id, xref_description, parent):
        return anytree.Node(
            "Account_number:{} Policy_number:{} Location_number:{}".format(
                xref_description.account_number, 
                xref_description.policy_number, 
                xref_description.location_number),
            parent=parent,
            level_id=level_id,
            agg_id=agg_id,
            account_number=xref_description.account_number,
            policy_number=xref_description.policy_number,
            location_number=xref_description.location_number)

    def _add_policy_node(
        self, level_id, agg_id, xref_description, parent):
        return anytree.Node(
            "Account_number:{} Policy_number:{}".format(
                xref_description.account_number, xref_description.policy_number),
            parent=parent,
            level_id=level_id,
            agg_id=agg_id,
            account_number=xref_description.account_number,
            policy_number=xref_description.policy_number,
            location_number=common.NOT_SET_ID)

    def _add_account_node(
        self, agg_id, level_id, xref_description, parent):
        return anytree.Node(
            "Account_number:{}".format(xref_description.account_number),
            parent=parent,
            level_id=level_id,
            agg_id=agg_id,
            account_number=xref_description.account_number,
            policy_number=common.NOT_SET_ID,
            location_number=common.NOT_SET_ID)

    def _does_location_node_match_scope_row(self, node, ri_scope_row):
        node_summary = (node.account_number, node.policy_number, node.location_number)
        scope_row_summary = (ri_scope_row.AccountNumber, ri_scope_row.PolicyNumber, ri_scope_row.LocationNumber)
        return (node_summary == scope_row_summary)

    def _does_policy_node_match_scope_row(self, node, ri_scope_row):
        node_summary = (node.account_number, node.policy_number, node.location_number)
        scope_row_summary = (ri_scope_row.AccountNumber, ri_scope_row.PolicyNumber, common.NOT_SET_ID)
        return (node_summary == scope_row_summary)

    def _does_account_node_match_scope_row(self, node, ri_scope_row):
        node_summary = (node.account_number, node.policy_number, node.location_number)
        scope_row_summary = (ri_scope_row.AccountNumber, common.NOT_SET_ID, common.NOT_SET_ID)
        return (node_summary == scope_row_summary)

    def _get_tree(self):
        current_location_number = 0
        current_policy_number = 0
        current_account_number = 0
        current_location_node = None
        current_policy_node = None
        current_account_node = None

        program_node_level_id = 3
        if self.risk_level == common.REINS_RISK_LEVEL_PORTFOLIO:
            program_node_level_id = 2
        program_node = self._add_program_node(program_node_level_id)
        xref_descriptions = self.xref_descriptions.sort_values(
            by=["location_number", "policy_number", "account_number"])

        agg_id = 0
        if self.risk_level == common.REINS_RISK_LEVEL_PORTFOLIO:
            for _, row in xref_descriptions.iterrows():
                self._add_item_node(row.xref_id, program_node)
        elif self.risk_level == common.REINS_RISK_LEVEL_ACCOUNT:
            for _, row in xref_descriptions.iterrows():
                if current_account_number != row.account_number:
                    agg_id = agg_id + 1
                    level_id = 2
                    current_account_number = row.account_number
                    current_account_node = self._add_account_node(
                        agg_id, level_id, row, program_node)
                self._add_item_node(row.xref_id, current_account_node)
        elif self.risk_level == common.REINS_RISK_LEVEL_POLICY:
            for _, row in xref_descriptions.iterrows():
                if current_policy_number != row.policy_number:
                    agg_id = agg_id + 1
                    level_id = 2
                    current_policy_number = row.policy_number
                    current_policy_node = self._add_location_node(level_id, agg_id, row, program_node)
                self._add_item_node(row.xref_id, current_policy_node)
        elif self.risk_level == common.REINS_RISK_LEVEL_LOCATION:
            for _, row in xref_descriptions.iterrows():
                if current_location_number != row.location_number:
                    agg_id = agg_id + 1
                    level_id = 2
                    current_location_number = row.location_number
                    current_location_node = self._add_location_node(level_id, agg_id, row, program_node)
                self._add_item_node(row.xref_id, current_location_node)
        return program_node

    def _add_fac_profiles(self, add_profiles_args):
        profile_id = max(x.profile_id for x in add_profiles_args.fmprofiles_list)

        for node in anytree.iterators.LevelOrderIter(add_profiles_args.program_node):
            add_profiles_args.node_layer_profile_map[(node, add_profiles_args.layer_id)] = add_profiles_args.nolossprofile_id

        profile_id = profile_id + 1
        add_profiles_args.fmprofiles_list.append(common.get_profile(
            profile_id,
            attachment=add_profiles_args.ri_info_row.RiskAttachmentPoint,
            limit=add_profiles_args.ri_info_row.RiskLimit
            ))

        for _, ri_scope_row in add_profiles_args.scope_rows.iterrows():
            if ri_scope_row.RiskLevel == common.REINS_RISK_LEVEL_LOCATION:
                nodes = anytree.search.findall(
                    add_profiles_args.program_node, 
                    filter_= lambda node: self._does_location_node_match_scope_row(node, ri_scope_row))                            
                for node in nodes:
                    add_profiles_args.node_layer_profile_map[(
                        node, add_profiles_args.layer_id)] = profile_id
                    for child in anytree.iterators.LevelOrderIter(node):
                        add_profiles_args.node_layer_profile_map[(
                            child, add_profiles_args.layer_id)] = add_profiles_args.nolossprofile_id
                    parent = node.parent
                    while parent != add_profiles_args.program_node:
                        add_profiles_args.node_layer_profile_map[(
                            parent, add_profiles_args.layer_id)] = add_profiles_args.nolossprofile_id
            elif ri_scope_row.RiskLevel == common.REINS_RISK_LEVEL_POLICY:
                nodes = anytree.search.findall(
                    add_profiles_args.program_node, 
                    filter_=lambda node: self._does_policy_node_match_scope_row(node, ri_scope_row))
                for node in nodes:
                    add_profiles_args.node_layer_profile_map[(
                        node, add_profiles_args.layer_id)] = profile_id
            elif ri_scope_row.RiskLevel == common.REINS_RISK_LEVEL_ACCOUNT:
                nodes = anytree.search.findall(
                    add_profiles_args.program_node, 
                    filter_=lambda node: self._does_account_node_match_scope_row(node, ri_scope_row))
                for node in nodes:
                    add_profiles_args.node_layer_profile_map[(
                        node, add_profiles_args.layer_id)] = profile_id
            else:
                raise Exception(
                    "Unsupported risk level: {}".format(ri_scope_row.RiskLevel))

    def _add_quota_share_profiles(self, add_profiles_args):
        profile_id = max(x.profile_id for x in add_profiles_args.fmprofiles_list)

        # Add any risk limits
        if self.risk_level == common.REINS_RISK_LEVEL_PORTFOLIO:
            pass
        else:
            profile_id = profile_id + 1
            add_profiles_args.fmprofiles_list.append(
                common.get_profile(
                    profile_id,
                    limit=add_profiles_args.ri_info_row.RiskLimit
            ))
            nodes = anytree.search.findall(
                add_profiles_args.program_node, filter_=lambda node: node.level_id == 2)
            for node in nodes:
                add_profiles_args.node_layer_profile_map[(node.name, add_profiles_args.layer_id)] = profile_id

        # Add occurrence limit and share
        profile_id = profile_id + 1
        add_profiles_args.fmprofiles_list.append(
            common.get_profile(
                profile_id,
                limit=add_profiles_args.ri_info_row.OccLimit,
                share=add_profiles_args.ri_info_row.CededPercent
                ))
        add_profiles_args.node_layer_profile_map[
            (add_profiles_args.program_node.name, add_profiles_args.layer_id)] = profile_id


    def _add_cat_xl_profiles(self, add_profiles_args):

        profile_id = max(x.profile_id for x in add_profiles_args.fmprofiles_list)
        profile_id = profile_id + 1
        add_profiles_args.fmprofiles_list.append(
            common.get_profile(
                profile_id,
                attachment=add_profiles_args.ri_info_row.OccurenceAttachmentPoint,
                limit=add_profiles_args.ri_info_row.OccLimit,
                share=add_profiles_args.ri_info_row.CededPercent
                ))
        add_profiles_args.node_layer_profile_map[
            (add_profiles_args.program_node.name, add_profiles_args.layer_id)] = profile_id


    def generate_oasis_structures(self):

        fmprogrammes_list = list()
        fmprofiles_list = list()
        fm_policytcs_list = list()

        profile_id = 0

        profile_id = profile_id + 1
        nolossprofile_id = profile_id
        fmprofiles_list.append(
            common.get_no_loss_profile(nolossprofile_id))
            
        profile_id = profile_id + 1
        passthroughprofile_id = profile_id
        fmprofiles_list.append(
            common.get_pass_through_profile(passthroughprofile_id))
            
        node_layer_profile_map = {}

        #
        # Build the tree representation of the program
        #
        program_node = self._get_tree()

        #
        # Overlay the reinsurance structure
        #
        layer_id = 0
        for _, ri_info_row in self.ri_info.iterrows():
            layer_id = layer_id + 1

            scope_rows = self.ri_scope[
                (self.ri_scope.ReinsNumber == ri_info_row.ReinsNumber) &
                (self.ri_scope.RiskLevel == self.risk_level)]
            if scope_rows.shape[0] == 0: 
                continue

            add_profiles_args = self.add_profiles_args(
                program_node, ri_info_row, scope_rows, layer_id, node_layer_profile_map, 
                fmprofiles_list, nolossprofile_id, passthroughprofile_id)

            if ri_info_row.ReinsType == common.REINS_TYPE_FAC:
                self._add_fac_profiles(add_profiles_args)
            elif ri_info_row.ReinsType == common.REINS_TYPE_QUOTA_SHARE:
                self._add_quota_share_profiles(add_profiles_args)
            elif ri_info_row.ReinsType == common.REINS_TYPE_CAT_XL:
                self._add_cat_xl_profiles(add_profiles_args)
            else:
                raise Exception("ReinsType not supported yet: {}".format(
                    ri_info_row.ReinsType))

        #
        # Generate the FmProgrammes and FmPolicyTcs
        #
        for node in anytree.iterators.LevelOrderIter(program_node):
            if node.parent is not None:
                fmprogrammes_list.append(
                    common.FmProgramme(
                        from_agg_id=node.agg_id,
                        level_id=node.level_id,
                        to_agg_id=node.parent.agg_id
                    )
                )
        max_layer_id = layer_id
        for layer_id in range(1, max_layer_id + 1):
            for node in anytree.iterators.LevelOrderIter(program_node):
                if node.level_id > 1:
                    fm_policytcs_list.append(common.FmPolicyTc(
                        layer_id=layer_id,
                        level_id=node.level_id-1,
                        agg_id=node.agg_id,
                        profile_id=node_layer_profile_map[(node.name, layer_id)]
                    ))

        self.fmprogrammes = pd.DataFrame(fmprogrammes_list)
        self.fmprofiles = pd.DataFrame(fmprofiles_list)
        self.fm_policytcs = pd.DataFrame(fm_policytcs_list)

    def write_oasis_files(self):

        self.fmprogrammes.to_csv("fm_programme.csv", index=False)
        self.fmprofiles.to_csv("fm_profile.csv", index=False)
        self.fm_policytcs.to_csv("fm_policytc.csv", index=False)
        self.fm_xrefs.to_csv("fm_xref.csv", index=False)

        directory = self.name
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        input_files = common.GUL_INPUTS_FILES + common.IL_INPUTS_FILES

        for input_file in input_files:
            conversion_tool = common.CONVERSION_TOOLS[input_file]
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

    def apply_fm(self, input_name):
        command = \
            "../ktools/fmcalc -p {0} -n -a {2} < {1}.bin | tee {0}.bin | ../ktools/fmtocsv > {0}.csv".format(
                self.name, input_name, common.ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID)
        proc = subprocess.Popen(command, shell=True)
        proc.wait()
        if proc.returncode != 0:
            raise Exception("Failed to run fm")
        losses_df = pd.read_csv("{}.csv".format(self.name))
        inputs_df = pd.read_csv("{}.csv".format(input_name))

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