import subprocess
import logging
import requests
from st2reactor.sensor.base import Sensor
from st2reactor.container.sensor_wrapper import SensorService
from amphorae import get_amphorae


# pylint: disable=abstract-method
class LoadbalancerSensor(Sensor):
    def __init__(self, sensor_service: SensorService, config):
        # pylint: disable=super-with-arguments
        super(LoadbalancerSensor, self).__init__(
            sensor_service=sensor_service, config=config
        )
        self.sensor_service: SensorService = sensor_service
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)

    def run(
        self,
        cloud_account: str = "dev-admin",
    ):
        """
        Action to check loadbalancer and amphorae status
        output suitable to be passed to create_tickets
        """

        amphorae = get_amphorae(cloud_account)

        amph_json = self._check_amphora_status(amphorae)
        # pylint: disable=line-too-long
        output = {
            "title": "{p[title_text]}",
            "body": "The loadbalance ping test result was: {p[lb_status]}\nThe status of the amphora was: {p[amp_status]}\nThe amphora id is: {p[amp_id]}\nThe loadbalancer id is: {p[lb_id]}",
            "server_list": [],
        }
        if amphorae.status_code != 200:
            # Notes problem with accessing api if anything other than 403 or 200 returned
            logging.critical("We encountered a problem accessing the API")
            logging.critical("The status code was: %s ", str(amphorae.status_code))
            logging.critical("The JSON response was: \n %s", str(amph_json))

        # Gets list of amphorae and iterates through it to check the loadbalancer and amphora status.
        for i in amph_json["amphorae"]:
            status = self._check_status(i)
            ping_result = self._ping_lb(i["lb_network_ip"])
            # This section builds out the ticket for each one with an error
            if status[0].lower() == "error" and ping_result.lower() == "error":
                output["server_list"].append(
                    {
                        "dataTitle": {
                            "title_text": "Issue with loadbalancer "
                            + str(i["loadbalancer_id"] or "null")
                            + " and amphora "
                            + str(i["id"] or "null"),
                            "lb_id": str(i["loadbalancer_id"] or "null"),
                            "amp_id": str(i["id"] or "null"),
                        },
                        "dataBody": {
                            "lb_status": str(ping_result or "null"),
                            "amp_status": str(status[1] or "null"),
                            "lb_id": str(i["loadbalancer_id"] or "null"),
                            "amp_id": str(i["id"] or "null"),
                        },
                    }
                )
            if status[0].lower() == "error" and ping_result.lower() != "error":
                output["server_list"].append(
                    {
                        "dataTitle": {
                            "title_text": "Issue with loadbalancer "
                            + str(i["loadbalancer_id"] or "null"),
                            "lb_id": str(i["loadbalancer_id"] or "null"),
                        },
                        "dataBody": {
                            "lb_status": str(ping_result or "null"),
                            "amp_status": str(status[1] or "null"),
                            "lb_id": str(i["loadbalancer_id"] or "null"),
                            "amp_id": str(i["id"] or "null"),
                        },
                    }
                )
            if status[0].lower() != "error" and ping_result.lower() == "error":
                output["server_list"].append(
                    {
                        "dataTitle": {
                            "title_text": "Issue with amphora "
                            + str(i["id"] or "null"),
                            "amp_id": str(i["id"] or "null"),
                        },
                        "dataBody": {
                            "lb_status": str(ping_result or "null"),
                            "amp_status": str(status[1] or "null"),
                            "lb_id": str(i["loadbalancer_id"] or "null"),
                            "amp_id": str(i["id"] or "null"),
                        },
                    }
                )
            else:
                logging.info("%s is fine.", i["id"])
        if len(output["server_list"]) > 0:
            self.sensor_service.dispatch(
                trigger="stackstorm_openstack.openstack.loadbalancer", payload=output
            )

    @staticmethod
    def _check_amphora_status(amphorae):
        try:
            amph_json = amphorae.json()
            return amph_json
        except requests.exceptions.JSONDecodeError:
            logging.critical(
                msg="There was no JSON response \nThe status code was: "
                + str(amphorae.status_code)
                + "\nThe body was: \n"
                + str(amphorae.content)
            )
            # pylint: disable=line-too-long
            return (
                "There was no JSON response \nThe status code was: "
                + str(amphorae.status_code)
                + "\nThe body was: \n"
                + str(amphorae.content)
            )

    # pylint: disable=missing-function-docstring
    @staticmethod
    def _check_status(amphora):
        # Extracts the status of the amphora and returns relevant info
        status = amphora["status"]
        if status.upper() in ("ALLOCATED", "BOOTING", "READY"):
            return ["ok", status]

        return ["error", status]

    # pylint: disable=invalid-name
    @staticmethod
    def _ping_lb(ip):
        # Runs the ping command to check that loadbalancer is up
        response = subprocess.run(["ping", "-q", "-c", "1", ip], check=False)
        # Checks output of ping command
        if response.returncode == 0:
            logging.info(msg="Successfully pinged " + ip)
            return "success"

        logging.info(msg=ip + " is down")
        return "error"

    def add_trigger(self, trigger):
        pass

    def cleanup(self):
        pass

    def remove_trigger(self, trigger):
        pass

    def setup(self):
        pass

    def update_trigger(self, trigger):
        pass
