from typing import Dict

from enums.hypervisor_states import HypervisorState


class Hypervisor:
    name: str
    uptime: int
    status: bool
    state: bool
    num_servers: int

    @staticmethod
    def from_dict(dictionary: Dict):
        hypervisor = Hypervisor()
        hypervisor.uptime = dictionary["hypervisor_uptime_days"]
        hypervisor.status = dictionary["hypervisor_status"]
        hypervisor.state = dictionary["hypervisor_state"]
        hypervisor.num_servers = dictionary["hypervisor_server_count"]
        return hypervisor

    def get_hypervisor_state(self, uptime_limit: int) -> HypervisorState:
        """
        Returns a hypervisor state given a set of hypervisor variables
        :param hypervisor: Dictionary containing hypervisor: uptime, state, status and server count
        :param uptime_limit: Number of days of uptime before hypervisor requires maintenance
        :return: Hypervisor state
        """
        if self.state == "down":
            return HypervisorState.DOWN

        if self.uptime == 0:
            return HypervisorState.REBOOTED

        if self.status == "disabled":
            return (
                HypervisorState.DRAINED
                if self.num_servers == 0
                else HypervisorState.DRAINING
            )

        if self.uptime > uptime_limit:
            return HypervisorState.PENDING_MAINTENANCE

        if self.status == "enabled":
            return (
                HypervisorState.EMPTY
                if self.num_servers == 0
                else HypervisorState.RUNNING
            )

        return HypervisorState.UNKNOWN
