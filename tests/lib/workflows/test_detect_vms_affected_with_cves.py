import pytest
from workflows.detect_vms_affected_with_cves import detect_vms_with_cves


def test_detect_vms_affected_with_cves_placeholder():
    """Test VMs detection raises NotImplementedError."""

    with pytest.raises(NotImplementedError):
        detect_vms_with_cves()
