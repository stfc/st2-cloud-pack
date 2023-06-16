from structs.query.query_preset_details import QueryPresetDetails
from structs.query.query_output_details import QueryOutputDetails

from tests.lib.openstack_query.mocks.mocked_props import MockProperties
from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets

from enums.query.query_output_types import QueryOutputTypes

MOCKED_PRESET_DETAILS = QueryPresetDetails(
    preset=MockQueryPresets.ITEM_1,
    prop=MockProperties.PROP_1,
    args={"arg1": "val1", "arg2": "val2"},
)

MOCKED_OUTPUT_DETAILS = QueryOutputDetails(
    properties_to_select=[MockProperties.PROP_1, MockProperties.PROP_2],
    output_type=QueryOutputTypes.TO_STR,
)
