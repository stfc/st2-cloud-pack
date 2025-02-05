from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


# pylint: disable=too-many-instance-attributes
@dataclass
class SilenceDetails:
    """
    Class for scheduling an Alertmanager Silence.

    The values for start and end times are datetime objects in UTC.
    Duration can be specified in days, hours, or minutes which will
    automatically calculate the end_time_dt from start_time_dt.
    """

    # TODO: make a matchers dataclass to make adding silences easier
    matchers: List
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

        # Ensure end_time_dt is after start_time_dt
        if self.end_time_dt <= self.start_time_dt:
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
