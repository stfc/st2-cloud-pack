import json
from datetime import datetime


class SilenceDetails:  # pylint: disable=too-few-public-methods
    def __init__(
        self,
        instance_name=None,
        start_time_dt=None,
        end_time_dt=None,
        author=None,
        comment=None,
        silence_id=None,
        status=None,
    ):
        """
        class to handle together all attributes describing a Silence event.
        The values for the start and end times are datetime objects.
        To convert a string like this (we assume it is UTC):

            2025-01-22T12:50:00

        into a datetime object, code like this can be used:

            naive_datetime = datetime.strptime(datetime_string, datetime_format)
            utc_datetime = naive_datetime.replace(tzinfo=timezone.utc)

        :param instance_name: name of the server
        :type instance_name: str
        :param start_time_dt: start time of the silence event
        :type start_time_dt: datetime
        :param end_time_dt: end time of the silence event
        :type end_time_dt: datetime
        :param author: entity creating the silence event
        :type author: str
        :param comment: explanation for the silence event
        :type comment: str
        :param silence_id: the ID for a valid silence event
        :type comment: str
        :param status: the status of a valid silence event (pending, expired, active)
        :type status: str
        """
        # we want to ensure start_time_dt and end_time_dt
        # are really instances of type datetime
        # and not just strings
        if start_time_dt is not None and not isinstance(start_time_dt, datetime):
            raise TypeError("start_time_dt must be of type datetime.")
        if end_time_dt is not None and not isinstance(end_time_dt, datetime):
            raise TypeError("end_time_dt must be of type datetime.")
        self.instance_name = instance_name
        self.start_time_dt = start_time_dt
        self.end_time_dt = end_time_dt
        self.author = author
        self.comment = comment
        self.silence_id = silence_id
        self.status = status

    @property
    def is_active(self):
        """
        check if the current date and time is between the start time
        and the end time of the silence event

        :return: True now is between the start time and the end time
        :rtype: bool
        """
        return self.status == "active"

    @property
    def is_pending(self):
        """
        :return: True if silence status is pending, False otherwise.
        :rtype: bool
        """
        return self.status == "pending"

    @property
    def has_expired(self):
        """
        :return: True if silence status is expired, False otherwise.
        :rtype: bool
        """
        return self.status == "expired"

    @property
    def is_valid(self):
        """
        :return: True if the silence has not finished yet
        :rtype: bool
        """
        return self.status in ["active", "pending"]

    @property
    def start_time_str(self):
        """
        converts the content of self.start_time_dt to a string with format
        "2025-01-22T11:50:00Z"

        :return: the converted start date
        :rtype: str
        """
        return self.start_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def end_time_str(self):
        """
        converts the content of self.end_time_dt to a string with format
        "2025-01-22T11:50:00Z"

        :return: the converted start date
        :rtype: str
        """
        return self.end_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class SilenceDetailsHandler(list):
    """
    class to host and handle multiple SilenceDetails objects
    """

    def add_from_json(self, json_doc_l):
        """
        create one or more new SilenceDetails objects with info
        from a JSON doc.
        This JSON doc can be, for example, the output of querying the
        alertmanager for all existing silence events.

        The JSON looks like this

            [
                {
                    "id": "949fec12-0e14-492d-b2de-c08cf10e65a5",
                    "status": {
                        "state": "expired"
                    },
                    "updatedAt": "2025-01-16T07:31:31.257Z",
                    "comment": "Testing.",
                    "createdBy": "admin",
                    "endsAt": "2025-01-16T10:51:00.000Z",
                    "matchers": [
                        {
                            "isEqual": true,
                            "isRegex": false,
                            "name": "instance",
                            "value": "hv123.matrix.net"
                        }
                    ],
                    "startsAt": "2025-01-16T10:50:00.000Z"
                },
                {
                    "id": "29da0e56-3aee-4b92-b9fb-abf551224f34",
                    "status": {
                        "state": "expired"
                    },
                    "updatedAt": "2025-01-16T07:32:25.792Z",
                    "comment": "Testing.",
                    "createdBy": "admin",
                    "endsAt": "2025-01-16T10:51:00.000Z",
                    "matchers": [
                        {
                            "isEqual": true,
                            "isRegex": false,
                            "name": "instance",
                            "value": "hv123.matrix.net"
                        }
                    ],
                    "startsAt": "2025-01-16T10:50:00.000Z"
                }
            ]

        :param json_doc_l: JSON document with specifications for SilenceDetails instances
        :type json_doc_l: str
        """
        # Convert JSON string to a list of dictionaries if needed
        if isinstance(json_doc_l, str):
            json_doc_l = json.loads(json_doc_l)

        for json_doc in json_doc_l:
            # Set the 'id' attribute
            silence_id = json_doc["id"]

            # Convert the startsAt field to a datetime object and set as start_time_dt
            # Replace trailing 'Z' if present, to handle UTC datetime
            start_time_dt = datetime.fromisoformat(
                json_doc["startsAt"].replace("Z", "+00:00")
            )

            # Convert the endsAt field to a datetime object and set as end_time_dt
            end_time_dt = datetime.fromisoformat(
                json_doc["endsAt"].replace("Z", "+00:00")
            )

            # Set the author from the createdBy field
            author = json_doc["createdBy"]

            # Set the comment
            comment = json_doc["comment"]

            # Extract the instance name from the matchers list (look for a 'name' == 'instance')
            for matcher in json_doc.get("matchers", []):
                if matcher["name"] == "instance":
                    instance_name = matcher["value"]
                    break

            status = json_doc["status"]["state"]

            new_silence_detail = SilenceDetails(
                instance_name,
                start_time_dt,
                end_time_dt,
                author,
                comment,
                silence_id,
                status,
            )
            self.append(new_silence_detail)

    @property
    def active_silences(self):
        """
        returns a new SilenceDetailsHandler object containing only the
        active SilenceDetails instances, where active means the current
        date and time is between start_time and end_time

        :return: the new list with only valid SilenceDetails instances
        :rtype: SilenceDetailsHandler
        """
        silencedetailshandler = SilenceDetailsHandler()
        for silence in iter(self):
            if silence.is_active:
                silencedetailshandler.append(silence)
        return silencedetailshandler

    @property
    def valid_silences(self):
        """
        returns a new SilenceDetailsHandler object containing only the
        valid SilenceDetails instances, where valid means:
            - the silence has not started yet
            - the silence has started but has not finished yet

        :return: the new list with only valid SilenceDetails instances
        :rtype: SilenceDetailsHandler
        """
        silencedetailshandler = SilenceDetailsHandler()
        for silence in iter(self):
            if silence.is_valid:
                silencedetailshandler.append(silence)
        return silencedetailshandler

    def get_by_name(self, instance_name):
        """
        filter this list and keep only the
        silence events for a given instance_name

        :param instance_name: HyperVisor name
        :type instance _name: str
        :return: a new list of silence events
        :rtype: SilenceDetailsHandler
        """
        silencedetailshandler = SilenceDetailsHandler()
        for silence in iter(self):
            if silence.instance_name == instance_name:
                silencedetailshandler.append(silence)
        return silencedetailshandler
