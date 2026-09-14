import datetime as dt
from unittest.mock import MagicMock, patch, call
from openstack.exceptions import ResourceFailure
import pytest

from apis.alertmanager_api.structs.alert_matcher_details import AlertMatcherDetails
from apis.alertmanager_api.structs.silence_details import SilenceDetails
from workflows.hv_post_reboot import post_reboot


@pytest.fixture(name="mock_get_silence_out")
def mock_get_silence_out_fixture():
    date_start = dt.datetime(2025, 1, 1, 10, 0, 0)
    date_end = dt.datetime(2025, 1, 2, 10, 0, 0)
    silence1 = SilenceDetails(
        matchers=[
            AlertMatcherDetails(name="matcher1", value="foo"),
        ],
        author="stackstorm",
        comment="Stackstorm: HV Patching",
        start_time_dt=date_start,
        end_time_dt=date_end,
    )
    silence2 = SilenceDetails(
        matchers=[
            AlertMatcherDetails(name="matcher2", value="foo"),
        ],
        author="stackstorm",
        comment="Stackstorm: HV Patching",
        start_time_dt=date_start,
        end_time_dt=date_end,
    )
    return {"foo": {"details": silence1}, "bar": {"details": silence2}}


@pytest.mark.freeze_time("2026-09-11 15:00:01")
@patch("workflows.hv_post_reboot.update_silence")
@patch("workflows.hv_post_reboot.get_hv_silences")
@patch("workflows.hv_post_reboot.enable_service")
@patch("workflows.hv_post_reboot.create_test_server")
def test_successful_post_reboot(
    mock_create_test_server,
    mock_enable_service,
    mock_get_hv_silences,
    mock_update_silence,
    mock_get_silence_out,
):
    """
    Test successfull running of the post reboot workflow.
    """
    mock_hv_name = "hvxyz"
    mock_conn = MagicMock()
    alertmanager_account = MagicMock()
    mock_silences = mock_get_silence_out
    mock_get_hv_silences.return_value = mock_silences

    post_reboot(
        alertmanager_account,
        hypervisor_hostname=mock_hv_name,
        conn=mock_conn,
    )
    mock_create_test_server.assert_called_once_with(
        conn=mock_conn,
        hypervisor_names=mock_hv_name,
        test_all_flavors=False,
        delete_on_failure=True,
    )
    mock_enable_service.assert_called_once_with(
        conn=mock_conn, hypervisor_name=mock_hv_name, service_binary="nova-compute"
    )
    mock_get_hv_silences.assert_called_once_with(alertmanager_account, mock_hv_name)
    mock_update_silence.assert_has_calls(
        [
            call(
                alertmanager_account,
                "foo",
                SilenceDetails(
                    matchers=[
                        AlertMatcherDetails(name="matcher1", value="foo"),
                    ],
                    author="stackstorm",
                    comment="Stackstorm: HV Patched",
                    start_time_dt=dt.datetime.now(dt.timezone.utc),
                    duration_hours=3,
                ),
            ),
            call(
                alertmanager_account,
                "bar",
                SilenceDetails(
                    matchers=[
                        AlertMatcherDetails(name="matcher2", value="foo"),
                    ],
                    author="stackstorm",
                    comment="Stackstorm: HV Patched",
                    start_time_dt=dt.datetime.now(dt.timezone.utc),
                    duration_hours=3,
                ),
            ),
        ],
        any_order=True,
    )


@pytest.mark.freeze_time("2026-09-11 15:00:01")
@patch("workflows.hv_post_reboot.update_silence")
@patch("workflows.hv_post_reboot.get_hv_silences")
@patch("workflows.hv_post_reboot.disable_service")
@patch("workflows.hv_post_reboot.enable_service")
@patch("workflows.hv_post_reboot.create_test_server")
def test_failed_post_reboot(
    mock_create_test_server,
    mock_enable_service,
    mock_disable_service,
    mock_get_hv_silences,
    mock_update_silence,
    mock_get_silence_out,
):
    """
    Test unsuccessful running of the post reboot workflow, where create_test_server fails
    """
    mock_hv_name = "hvxyz"
    mock_conn = MagicMock()
    alertmanager_account = MagicMock()
    mock_silences = mock_get_silence_out
    mock_get_hv_silences.return_value = mock_silences
    mock_create_test_server.side_effect = ResourceFailure

    with pytest.raises(ResourceFailure):
        post_reboot(
            alertmanager_account,
            hypervisor_hostname=mock_hv_name,
            conn=mock_conn,
        )
    mock_enable_service.assert_called_once_with(
        conn=mock_conn, hypervisor_name=mock_hv_name, service_binary="nova-compute"
    )
    mock_create_test_server.assert_called_once_with(
        conn=mock_conn,
        hypervisor_names=mock_hv_name,
        test_all_flavors=False,
        delete_on_failure=True,
    )
    mock_disable_service.assert_called_once_with(
        conn=mock_conn,
        hypervisor_name=mock_hv_name,
        service_binary="nova-compute",
        disabled_reason="2026-09-11 - Failed to schedule after patching - ST2",
    )
    mock_get_hv_silences.assert_not_called()
    mock_update_silence.assert_not_called()
