"""Home Assistant representation of an GeoRide Tracker device."""
from georideapilib.objects import GeoRideTracker, GeoRideTrackerBeacon
from .const import DOMAIN as GEORIDE_DOMAIN


class Device:
    """Home Assistant representation of a GeoRide Tracker device."""

    def __init__(self, tracker):
        """Initialize GeoRideTracker device."""
        self._tracker: GeoRideTracker = tracker
        

    @property
    def tracker(self):
        """return the tracker"""
        return self._tracker

    @property
    def name(self) -> str:
        """Get the name."""
        return self._tracker.tracker_name

    @property
    def default_manufacturer(self) -> str:
        """Get the default_manufacturer."""
        return "GeoRide"

    @property
    def manufacturer(self) -> str:
        """Get the manufacturer."""
        return "GeoRide"
        
    @property
    def default_model(self) -> str:
        """Get the default model."""
        return "GeoRide 1"

    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Garage"
        
    @property
    def model_name(self) -> str:
        """Get the model name."""
        name = None
        if self._tracker.version == 1:
            name = "GeoRide 1"
        elif self._tracker.version == 2:
            name = "GeoRide 2"
        elif self._tracker.version == 3:
            if self._tracker.model == 'georide-3':
                name = "GeoRide 3"
            else:
                name = "GeoRide Mini"
        else:
            name = "Prototype / Unknown"
        return name
    
    @property
    def sw_version(self) -> str:
        """Get the software version."""
        return str(self._tracker.software_version)

    @property
    def hw_version(self) -> str:
        """Get the hardware version."""
        return str(self._tracker.version)

    @property
    def unique_id(self) -> str:
        """Get the unique id."""
        return {(GEORIDE_DOMAIN, self._tracker.tracker_id)}

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": self.unique_id,
            "manufacturer": self.manufacturer,
            "model": self.model_name,
            "suggested_area": self.suggested_area,
            "sw_version" : self.sw_version,
            "hw_version": self.hw_version
        }

    def __str__(self) -> str:
        """Get string representation."""
        return f"GeoRide Device: {self.name}::{self.model_name}::{self.unique_id}"

class DeviceBeacon:
    """Home Assistant representation of a GeoRide Tracker device."""

    def __init__(self, beacon):
        """Initialize GeoRideTracker device."""
        self._beacon: GeoRideTrackerBeacon = beacon

    @property
    def beacon(self):
        """return the tracker beacon"""
        return self._beacon

    @property
    def name(self) -> str:
        """Get the name."""
        return self._beacon.name

    @property
    def default_manufacturer(self) -> str:
        """Get the default_manufacturer."""
        return "GeoRide"

    @property
    def manufacturer(self) -> str:
        """Get the manufacturer."""
        return "GeoRide"
        
    @property
    def default_model(self) -> str:
        """Get the default model."""
        return "GeoRide Beacon"

    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Garage"

    @property
    def model_name(self) -> str:
        """Get the model name."""
        name = "GeoRide Beacon"
        return name

    @property
    def unique_id(self) -> str:
        """Get the unique id."""
        return {(GEORIDE_DOMAIN, self._beacon.beacon_id)}

    @property
    def via_device(self) -> str:
        """Get the unique id."""
        return (GEORIDE_DOMAIN, self._beacon.linked_tracker_id )

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": self.unique_id,
            "manufacturer": self.manufacturer,
            "model": self.model_name,
            "suggested_area": self.suggested_area,
            "via_device": self.via_device
        }

    def __str__(self) -> str:
        """Get string representation."""
        return f"GeoRide Device: {self.name}::{self.model_name}::{self.unique_id}"