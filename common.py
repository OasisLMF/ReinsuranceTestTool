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

#
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
    "Description", ("xref_id policy_number account_number location_number coverage_type_id peril_id tiv"))
GulRecord = namedtuple(
    "GulRecord", "event_id item_id sidx loss")
