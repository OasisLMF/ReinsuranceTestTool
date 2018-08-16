import pandas as pd
import subprocess
from collections import namedtuple


#
# Ktools constants
#
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

CALCRULE_ID_DEDUCTIBLE_AND_LIMIT = 1
CALCRULE_ID_DEDUCTIBLE_ATTACHMENT_LIMIT_AND_SHARE = 2
CALCRULE_ID_FRANCHISE_DEDUCTIBLE_AND_LIMIT = 3
CALCRULE_ID_DEDUCTIBLE_AND_LIMIT_PERCENT_TIV = 4
CALCRULE_ID_DEDUCTIBLE_AND_LIMIT_PERCENT_LOSS = 5
CALCRULE_ID_DEDUCTIBLE_PERCENT_TIV = 6
CALCRULE_ID_LIMIT_AND_MAX_DEDUCTIBLE = 7
CALCRULE_ID_LIMIT_AND_MIN_DEDUCTIBLE = 8
CALCRULE_ID_LIMIT_WITH_DEDUCTIBLE_PERCENT_LIMIT = 9
CALCRULE_ID_MAX_DEDUCTIBLE = 10
CALCRULE_ID_MIN_DEDUCTIBLE = 11
CALCRULE_ID_DEDUCTIBLE_ONLY = 12
CALCRULE_ID_MAIN_AND_MAX_DEDUCTIBLE = 13
CALCRULE_ID_LIMIT_ONLY = 14
CALCRULE_ID_LIMIT_PERCENT_LOSS = 15
CALCRULE_ID_DEDUCTIBLE_PERCENT_LOSS = 16
CALCRULE_ID_DEDUCTIBLE_PERCENT_LOSS_ATTACHMENT_LIMIT_AND_SHARE = 17
CALCRULE_ID_DEDUCTIBLE_PERCENT_TIV_ATTACHMENT_LIMIT_AND_SHARE = 18
CALCRULE_ID_DEDUCTIBLE_PERCENT_LOSS_WITH_MIN_AND_MAX = 19
CALCRULE_ID_REVERSE_FRANCHISE_DEDUCTIBLE = 20
CALCRULE_ID_SHARE_AND_LIMIT = 21
CALCRULE_ID_QUOTA_SHARE = 22
CALCRULE_ID_OCCURRENCE_LIMIT_AND_SHARE = 23
CALCRULE_ID_OCCURRENCE_CATASTROPHE_EXCESS_OF_LOSS = 24
CALCRULE_ID_FACULTATIVE_WITH_POLICY_SHARE = 25

NO_ALLOCATION_ALLOC_ID = 0
ALLOCATE_TO_ITEMS_BY_GUL_ALLOC_ID = 1
ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID = 2

BUILDING_COVERAGE_TYPE_ID = 1
OTHER_BUILDING_COVERAGE_TYPE_ID = 2
CONTENTS_COVERAGE_TYPE_ID = 3
TIME_COVERAGE_TYPE_ID = 4
COVERAGE_TYPES = [
    BUILDING_COVERAGE_TYPE_ID,
    OTHER_BUILDING_COVERAGE_TYPE_ID,
    CONTENTS_COVERAGE_TYPE_ID,
    TIME_COVERAGE_TYPE_ID]

PERIL_WIND = 1
PERILS = [PERIL_WIND]

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




NOT_SET_ID = -1
LARGE_VALUE = 9999999999999

# OED constants
##

POLICYITEM_LEVEL = 0
LOCATION_LEVEL = 1
POLICY_LEVEL = 2
ACCOUNT_LEVEL = 3
OCCURRENCE_LEVEL = 4

PASSTHROUGH_NODE_TYPE = 1
NOLOSS_NODE_TYPE = 1

REINS_TYPE_FAC = "FAC"
REINS_TYPE_QUOTA_SHARE = "QS"
REINS_TYPE_SURPLUS_SHARE = "SS"
REINS_TYPE_PER_RISK = "PR"
REINS_TYPE_CAT_XL = "CAT XL"
REINS_TYPE_AGG_XL = "XL"

REINS_RISK_LEVEL_PORTFOLIO = "SEL"
REINS_RISK_LEVEL_LOCATION = "LOC"
#REINS_RISK_LEVEL_LOCATION_GROUP = "Location Group"
REINS_RISK_LEVEL_POLICY = "POL"
REINS_RISK_LEVEL_ACCOUNT = "ACC"
REINS_RISK_LEVELS = [
    REINS_RISK_LEVEL_LOCATION,
    REINS_RISK_LEVEL_POLICY,
    REINS_RISK_LEVEL_ACCOUNT,
    REINS_RISK_LEVEL_PORTFOLIO,
]


# Subset of the fields that are currently used
OED_ACCOUNT_FIELDS = [
    'PortfolioNumber',
    'AccountNumber',
    'PolicyNumber',
    'PerilCode',
    'Ded6',
    'Limit6'
]

OED_LOCATION_FIELDS = [
    'AccountNumber',
    'LocationNumber',
    'Ded6',
    'Limit6',
    'BuildingTIV',
    'OtherTIV',
    'ContentsTIV',
    'BITIV'
]

OED_REINS_INFO_FIELDS = [
    'ReinsNumber',
    'ReinsLayerNumber',
    'CededPercent',
    'RiskLimit',
    'RiskAttachmentPoint',
    'OccLimit',
    'OccurenceAttachmentPoint',
    'InuringPriority',
    'ReinsType',
    'PlacementPercent',
    'TreatyPercent'
]

OED_REINS_SCOPE_FIELDS = [
    'ReinsNumber',
    'PortfolioNumber',
    'AccountNumber',
    'PolicyNumber',
    'LocationNumber',
    'RiskLevel',
    'CededPercent'
]

Item = namedtuple(
    "Item", "item_id coverage_id areaperil_id vulnerability_id group_id")
Coverage = namedtuple(
    "Coverage", "coverage_id tiv")
FmProgramme = namedtuple(
    "FmProgramme", "from_agg_id level_id to_agg_id")
FmProfile = namedtuple(
    "FmProfile", "profile_id calcrule_id deductible1 deductible2 deductible3 attachment limit share1 share2 share3")
FmPolicyTc = namedtuple(
    "FmPolicyTc", "layer_id level_id agg_id profile_id")
GulSummaryXref = namedtuple(
    "GulSummaryXref", "coverage_id summary_id summaryset_id")
FmSummaryXref = namedtuple(
    "FmSummaryXref", "output_id summary_id summaryset_id")
FmXref = namedtuple(
    "FmXref", "output_id agg_id layer_id")
XrefDescription = namedtuple(
    "Description", ("xref_id policy_number account_number location_number coverage_type_id peril_id tiv"))
GulRecord = namedtuple(
    "GulRecord", "event_id item_id sidx loss")

def get_no_loss_profile(profile_id):
    return FmProfile(
        profile_id=profile_id,
        calcrule_id=CALCRULE_ID_LIMIT_ONLY,
        deductible1=0,  # Not used
        deductible2=0,  # Not used
        deductible3=0,  # Not used
        attachment=0,   # Not used
        limit=0,
        share1=0,       # Not used
        share2=0,       # Not used
        share3=0        # Not used
        )

def get_pass_through_profile(profile_id):
    return FmProfile(
        profile_id=profile_id,
        calcrule_id=CALCRULE_ID_DEDUCTIBLE_ONLY,
        deductible1=0,
        deductible2=0,  # Not used
        deductible3=0,  # Not used
        attachment=0,   # Not used
        limit=0,        # Not used
        share1=0,       # Not used
        share2=0,       # Not used
        share3=0        # Not used
        )

def get_profile(
    profile_id,
    deductible=0,
    attachment=0,
    limit=0,
    share=1.0
    ):
    
    if limit == 0:
        limit = LARGE_VALUE

    return FmProfile(
        profile_id=profile_id,
        calcrule_id=CALCRULE_ID_DEDUCTIBLE_ATTACHMENT_LIMIT_AND_SHARE,
        deductible1=deductible,
        deductible2=0,  # Not used
        deductible3=0,  # Not used
        attachment=attachment,
        limit=limit,
        share1=share,
        share2=0,       # Not used
        share3=0        # Not used
        )

def get_reinsurance_profile(
    profile_id,
    attachment=0,
    limit=0,
    ceded=1.0,
    placement=1.0
    ):
    
    if limit == 0:
        limit = LARGE_VALUE

    return FmProfile(
        profile_id=profile_id,
        calcrule_id=CALCRULE_ID_OCCURRENCE_CATASTROPHE_EXCESS_OF_LOSS,
        deductible1=0,  # Not used
        deductible2=0,  # Not used
        deductible3=0,  # Not used
        attachment=attachment,
        limit=limit,
        share1=ceded,
        share2=placement, # PlacementPercent
        share3=1.0        # Not used
        )

def get_occlim_profile(
    profile_id,
    attachment=0,
    limit=0,
    ceded=1.0,
    placement=1.0
    ):
    
    if limit == 0:
        limit = LARGE_VALUE

    return FmProfile(
        profile_id=profile_id,
        calcrule_id=CALCRULE_ID_OCCURRENCE_LIMIT_AND_SHARE,
        deductible1=0,  # Not used
        deductible2=0,  # Not used
        deductible3=0,  # Not used
        attachment=attachment,
        limit=limit,
        share1=0,         # Not used
        share2=placement, # Not used
        share3=1.0        # Not used
        )

def run_fm(
    input_name,
    output_name,
    xref_descriptions,
    allocation=ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID):
    command = \
        "../ktools/fmcalc -p {0} -n -a {2} < {1}.bin | tee {0}.bin | ../ktools/fmtocsv > {0}.csv".format(
            output_name, input_name, allocation)
    proc = subprocess.Popen(command, shell=True)
    print(command)
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
