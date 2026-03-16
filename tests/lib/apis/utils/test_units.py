"""Unit tests for class QuotaSize"""

import pytest
from apis.utils.units import QuotaSize


class TestDefaultUnit:
    """Tests the default behavior of QuotaSize when no unit is specified."""

    def test_default_unit_is_mib(self):
        """Verify that the default input unit is interpreted as MiB."""
        s = QuotaSize(1)
        assert s.MiB == pytest.approx(1.0)

    def test_1_mib_to_mb(self):
        """Verify conversion from 1 MiB to MB."""
        assert QuotaSize(1).MB == pytest.approx(1.048576)

    def test_1_mib_to_gb(self):
        """Verify conversion from 1 MiB to GB."""
        assert QuotaSize(1).GB == pytest.approx(1.048576e-3)

    def test_1_mib_to_gib(self):
        """Verify conversion from 1 MiB to GiB."""
        assert QuotaSize(1).GiB == pytest.approx(1 / 1024)

    def test_1_mib_to_tb(self):
        """Verify conversion from 1 MiB to TB."""
        assert QuotaSize(1).TB == pytest.approx(1.048576e-6)

    def test_1_mib_to_tib(self):
        """Verify conversion from 1 MiB to TiB."""
        assert QuotaSize(1).TiB == pytest.approx(1 / (1024**2))


class TestMBInput:
    """Tests conversions when the input unit is set to MB (Megabytes)."""

    def test_1_mb_to_mb(self):
        """Verify that 1 MB remains 1.0 when accessed as MB."""
        assert QuotaSize(1, "MB").MB == pytest.approx(1.0)

    def test_1_mb_to_mib(self):
        """Verify conversion from 1 MB to MiB."""
        assert QuotaSize(1, "MB").MiB == pytest.approx(1_000_000 / 1_048_576)

    def test_1000_mb_to_gb(self):
        """Verify conversion from 1000 MB to 1 GB."""
        assert QuotaSize(1000, "MB").GB == pytest.approx(1.0)


class TestGBInput:
    """Tests conversions when the input unit is set to GB (Gigabytes)."""

    def test_1_gb_to_gb(self):
        """Verify that 1 GB remains 1.0 when accessed as GB."""
        assert QuotaSize(1, "GB").GB == pytest.approx(1.0)

    def test_1_gb_to_gib(self):
        """Verify conversion from 1 GB to GiB."""
        assert QuotaSize(1, "GB").GiB == pytest.approx(1e9 / 1_073_741_824)

    def test_1_gb_to_mb(self):
        """Verify conversion from 1 GB to MB."""
        assert QuotaSize(1, "GB").MB == pytest.approx(1000.0)

    def test_1_gb_to_mib(self):
        """Verify conversion from 1 GB to MiB."""
        assert QuotaSize(1, "GB").MiB == pytest.approx(1e9 / 1_048_576)


class TestGiBInput:
    """Tests conversions when the input unit is set to GiB (Gibibytes)."""

    def test_1_gib_to_gib(self):
        """Verify that 1 GiB remains 1.0 when accessed as GiB."""
        assert QuotaSize(1, "GiB").GiB == pytest.approx(1.0)

    def test_1_gib_to_mib(self):
        """Verify conversion from 1 GiB to MiB."""
        assert QuotaSize(1, "GiB").MiB == pytest.approx(1024.0)

    def test_1_gib_to_gb(self):
        """Verify conversion from 1 GiB to GB."""
        assert QuotaSize(1, "GiB").GB == pytest.approx(1.073741824)

    def test_1_gib_to_tib(self):
        """Verify conversion from 1 GiB to TiB."""
        assert QuotaSize(1, "GiB").TiB == pytest.approx(1 / 1024)


class TestTBInput:
    """Tests conversions when the input unit is set to TB (Terabytes)."""

    def test_1_tb_to_tb(self):
        """Verify that 1 TB remains 1.0 when accessed as TB."""
        assert QuotaSize(1, "TB").TB == pytest.approx(1.0)

    def test_1_tb_to_tib(self):
        """Verify conversion from 1 TB to TiB."""
        assert QuotaSize(1, "TB").TiB == pytest.approx(1e12 / 1_099_511_627_776)

    def test_1_tb_to_gb(self):
        """Verify conversion from 1 TB to GB."""
        assert QuotaSize(1, "TB").GB == pytest.approx(1000.0)


class TestTiBInput:
    """Tests conversions when the input unit is set to TiB (Tebibytes)."""

    def test_1_tib_to_tib(self):
        """Verify that 1 TiB remains 1.0 when accessed as TiB."""
        assert QuotaSize(1, "TiB").TiB == pytest.approx(1.0)

    def test_1_tib_to_gib(self):
        """Verify conversion from 1 TiB to GiB."""
        assert QuotaSize(1, "TiB").GiB == pytest.approx(1024.0)

    def test_1_tib_to_tb(self):
        """Verify conversion from 1 TiB to TB."""
        assert QuotaSize(1, "TiB").TB == pytest.approx(1_099_511_627_776 / 1e12)


class TestEdgeCases:
    """Tests edge cases, error handling, and data integrity (roundtrips)."""

    def test_zero_value(self):
        """Verify that a zero value results in zero for all output units."""
        s = QuotaSize(0, "GB")
        assert s.TB == pytest.approx(0.0)
        assert s.MiB == pytest.approx(0.0)

    def test_large_value(self):
        """Verify handling of larger numerical values."""
        assert QuotaSize(1024, "TiB").TiB == pytest.approx(1024.0)

    def test_fractional_value(self):
        """Verify handling of fractional/float input values."""
        assert QuotaSize(0.5, "GiB").MiB == pytest.approx(512.0)

    def test_invalid_unit_raises(self):
        """Verify that an unsupported unit string raises a ValueError."""
        with pytest.raises(ValueError, match="Unknown unit"):
            QuotaSize(1, "KB")

    def test_invalid_unit_message(self):
        """Verify that specific invalid units trigger a ValueError."""
        with pytest.raises(ValueError):
            QuotaSize(10, "bytes")

    def test_roundtrip_mib_gib_mib(self):
        """Verify data integrity when converting MiB -> GiB -> MiB."""
        original = 512.0
        s = QuotaSize(original, "MiB")
        back = QuotaSize(s.GiB, "GiB")
        assert back.MiB == pytest.approx(original)

    def test_roundtrip_gb_tb_gb(self):
        """Verify data integrity when converting GB -> TB -> GB."""
        original = 250.0
        s = QuotaSize(original, "GB")
        back = QuotaSize(s.TB, "TB")
        assert back.GB == pytest.approx(original)
