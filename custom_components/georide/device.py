"""Home Assistant representation of an GeoRide Tracker device."""
import georideapilib.objects as GeoRideTracker
from .const import DOMAIN as GEORIDE_DOMAIN


class Device:
    """Home Assistant representation of a GeoRide Tracker device."""

    def __init__(self, tracker):
        """Initialize GeoRideTracker device."""
        self._tracker: GeoRideTracker = tracker

    @property
    def name(self) -> str:
        """Get the name."""
        return self._tracker.name

    @property
    def manufacturer(self) -> str:
        """Get the manufacturer."""
        return "GeoRide"

    @property
    def model_name(self) -> str:
        """Get the model name."""
        name = "GeoRide 1"
        if self._tracker.is_old_tracker:
            name = "Prototype / GeoRide 1"
        elif self._tracker.is_second_gen:
            name = "GeoRide 2 / GeoRide 3"
        return name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker.tracker_id)},
            "manufacturer": "GeoRide",
            "model": self.model_name,
            "suggested_area": "Garage"
        }


    @property
    def unique_id(self) -> str:
        """Get the unique id."""
        return {(GEORIDE_DOMAIN, self._tracker.tracker_id)}

    def __str__(self) -> str:
        """Get string representation."""
        return f"GeoRide Device: {self.name}::{self.model_name}::self.unique_id"
