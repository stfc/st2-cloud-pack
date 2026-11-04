from enum import Enum


class Platform(Enum):
    """
    Class of platforms, using IDs from netbox
    https://netbox.esc.rl.ac.uk/dcim/platforms/
    """

    ROCKY_8 = 14
    ROCKY_9 = 15
    ROCKY_10 = 36
