from enums.icinga.icinga_objects import IcingaObject

from structs.icinga.icinga_account import IcingaAccount

from icinga_api import downtime


def post_reboot(icinga_account: IcingaAccount, object_type: str, name: str):
    """ """
    # Remove downtime
    downtime.remove_downtime(
        icinga_account=icinga_account,
        object_type=IcingaObject[object_type.upper()],
        object_name=name,
    )
    # Remove alertmanager silence
    # test vm creation
    # enable in openstack
