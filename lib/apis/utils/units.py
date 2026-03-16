# pylint: disable=invalid-name
class QuotaSize:
    UNITS = {
        "MB": 10**6,
        "MiB": 2**20,
        "GB": 10**9,
        "GiB": 2**30,
        "TB": 10**12,
        "TiB": 2**40,
    }

    def __init__(self, value, unit="MiB"):
        """
        Initialise a QuotaSize instance with a numeric value and unit.

        The provided value is internally converted and stored in bytes,
        allowing conversion to other supported units.

        :param value: The numeric size to represent.
        :type value: int or float
        :param unit: The unit of the provided value. Must be one of the supported units.
                     Defaults to MiB.
        :type unit: str
        :raises ValueError: If the specified unit is not supported.
        """
        if unit not in self.UNITS:
            raise ValueError(f"Unknown unit '{unit}'. Valid units: {list(self.UNITS)}")
        self._bytes = value * self.UNITS[unit]

    def _convert(self, unit):
        return self._bytes / self.UNITS[unit]

    @property
    def MB(self):
        return self._convert("MB")

    @property
    def MiB(self):
        return self._convert("MiB")

    @property
    def GB(self):
        return self._convert("GB")

    @property
    def GiB(self):
        return self._convert("GiB")

    @property
    def TB(self):
        return self._convert("TB")

    @property
    def TiB(self):
        return self._convert("TiB")
