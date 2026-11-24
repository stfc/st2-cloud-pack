import pytest
from workflows.shutoff_vms_not_fixed import shutoff_vms_not_fixed


def test_detect_vms_affected_with_cves_placeholder():
    """Test Shutoff VMs not fixed raises NotImplementedError."""

    with pytest.raises(NotImplementedError):
        shutoff_vms_not_fixed()
