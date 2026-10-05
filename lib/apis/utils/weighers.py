import datetime as dt

DESIRED_OS_VERSION = 9


class Weighers:
    @staticmethod
    def last_fw_patch_date(patch_date: str) -> int:
        """
        Prioritise hosts with longer FW patch date duration

        :param patch_date: Date of the last FW patch date
        :type patch_date: str

        :return: FW patch date metric
        :rtype: int
        """
        date = dt.datetime.strptime(patch_date, "%Y-%m-%d")
        return (dt.datetime.now() - date).days

    @staticmethod
    def os_version(os_version: int) -> bool:
        """
        Deprioritse hosts currently runing the desired version
        of the operating system

        :param os_version: OS version of the host
        :type os_version: int

        :return: OS version metric
        :rtype: bool
        """
        return os_version != DESIRED_OS_VERSION

    @staticmethod
    def hypervisor_server_count(hypervisor_server_count: int) -> int:
        """
        Favour hypervisors with fewer VMs on

        :param hypervisor_server_count: Number of servers on the hypervisor
        :type hypervisor_server_count: int

        :return: Server count metric
        :rtype: int
        """
        return -hypervisor_server_count


def get_weights():
    return {
        "os_version": 10,
        "last_fw_patch_date": 2,
        "hypervisor_server_count": 0.5,
    }


def calc_weight(host: dict, weights: dict) -> float:
    """
    Calculates the weight of a host based on property metrics
    To sort them into priority order

    weight = (m1 * w1) + (m2 * w2) + ...

    :param host: Dictionary containing properties of the host to weigh
    :type host: dict
    :param weights: Multipliers for the properties to (de)priorities their importance
    :type weights: dict

    :return: Host priority weight
    :rtype: float
    """
    weighers = Weighers()
    host_weight = 0

    for field in host:
        try:
            value_fn = getattr(weighers, field)
        except AttributeError as exc:
            if weights.get(field):
                raise AttributeError() from exc
            continue
        value = value_fn(host[field])

        host_weight += value * weights.get(field)

    return host_weight
