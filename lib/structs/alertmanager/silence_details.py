from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from structs.alertmanager.alert_matcher_details import AlertMatcherDetails


# pylint: disable=too-many-instance-attributes
@dataclass
class SilenceDetails:
    """
    Class for scheduling an Alertmanager Silence.
    :param matchers: a list of AlertMatcherDetails objects
    :type matchers: list
    :param author: name to assign to silence
    :type author: string
    :param comment: comment of why silence was added
    :type comment: string
    :param end_time_dt: (Optional) end time for silence - datetime object (UTC).
        Must provide this or automatically calculated from duration_days, duration_hours
        and duration_minutes if duration_days/hours/minutes provided,
        calculated end_time will overwrite this one
    :type end_time_dt: datetime, optional
    :param start_time_dt: (Optional) start time for silence - datetime object (UTC).
        If not given, will default to datetime.now()
    :type start_time_dt: datetime, optional
    :param duration_days: (Optional) duration of silence in days from start time
    :type duration_days: integer, optional
    :param duration_hours: (Optional) duration of silence in hours from start time
    :type duration_hours: integer, optional
    :param duration_minutes: (Optional) duration of silence in minutes from start time
    :type duration_minutes: integer, optional

    :raises TypeError: when start_time_dt or end_time_dt are not datetime
    :raises ValueError: when neither end_time_dt nor any duration parameters given
    :raises ValueError: when given end_time_dt is not after start_time_dt
    """

    matchers: List[AlertMatcherDetails]
    author: str = None
    comment: str = None
    start_time_dt: Optional[datetime] = field(default_factory=datetime.now)
    end_time_dt: Optional[datetime] = None
    duration_days: Optional[int] = None
    duration_hours: Optional[int] = None
    duration_minutes: Optional[int] = None

    def __post_init__(self):
        """
        Validate datetime fields and calculate end_time_dt if duration is provided.
        Duration fields take precedence over explicitly set end_time_dt.
        """
        # Validate datetime fields
        for field_name in ["start_time_dt", "end_time_dt"]:
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, datetime):
                raise TypeError(f"{field_name} must be of type datetime.")

        # Calculate end_time_dt if any duration is provided
        if any(
            d is not None
            for d in [self.duration_days, self.duration_hours, self.duration_minutes]
        ):
            delta = timedelta(
                days=self.duration_days or 0,
                hours=self.duration_hours or 0,
                minutes=self.duration_minutes or 0,
            )
            self.end_time_dt = self.start_time_dt + delta

        # Ensure end_time_dt is set
        if self.end_time_dt is None:
            raise ValueError("Either end_time_dt or duration must be provided")

        # Ensure duration is not negative
        if self.duration < timedelta(0):
            raise ValueError("end_time_dt must be after start_time_dt")

    @property
    def start_time_str(self) -> str:
        """Convert start_time_dt to ISO format string (2025-01-22T11:50:00Z)."""
        return self.start_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def end_time_str(self) -> str:
        """Convert end_time_dt to ISO format string (2025-01-22T11:50:00Z)."""
        return self.end_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def duration(self) -> timedelta:
        """Calculate the total duration of the silence."""
        return self.end_time_dt - self.start_time_dt

    @property
    def matchers_raw(self) -> List[dict]:
        """get matchers as list of dictionaries rather than list of dataclasses"""
        return [matcher.to_dict() for matcher in self.matchers]
