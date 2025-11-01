"""EcoFlow battery sensors."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_SN, DOMAIN
from .coordinator import EcoFlowCoordinator

# Battery sensor definitions based on EcoFlow API fields
BATTERY_SENSORS = [
    {
        "key": "bms_bmsStatus.soc",
        "name": "Battery level",
        "device_class": SensorDeviceClass.BATTERY,
        "unit": PERCENTAGE,
        "icon": "mdi:battery",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "bms_bmsStatus.vol",
        "name": "Battery voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": UnitOfElectricPotential.MILLIVOLT,
        "icon": "mdi:flash",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "bms_bmsStatus.temp",
        "name": "Battery temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "bms_bmsStatus.inputWatts",
        "name": "Battery input power",
        "device_class": SensorDeviceClass.POWER,
        "unit": UnitOfPower.WATT,
        "icon": "mdi:battery-charging",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "bms_bmsStatus.outputWatts",
        "name": "Battery output power",
        "device_class": SensorDeviceClass.POWER,
        "unit": UnitOfPower.WATT,
        "icon": "mdi:battery-arrow-down",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "pd.soc",
        "name": "Power delivery SOC",
        "device_class": SensorDeviceClass.BATTERY,
        "unit": PERCENTAGE,
        "icon": "mdi:battery-outline",
        "state_class": SensorStateClass.MEASUREMENT,
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EcoFlow sensors."""
    coordinator: EcoFlowCoordinator = config_entry.runtime_data
    device_sn = config_entry.data[CONF_DEVICE_SN]

    entities = [
        EcoFlowSensor(coordinator, device_sn, sensor_config)
        for sensor_config in BATTERY_SENSORS
    ]
    async_add_entities(entities)


class EcoFlowSensor(CoordinatorEntity[EcoFlowCoordinator], SensorEntity):
    """EcoFlow sensor entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoFlowCoordinator,
        device_sn: str,
        sensor_config: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_config = sensor_config
        self._attr_unique_id = f"{device_sn}_{sensor_config['key']}"
        self._attr_name = sensor_config["name"]
        self._attr_device_class = sensor_config["device_class"]
        self._attr_native_unit_of_measurement = sensor_config["unit"]
        self._attr_icon = sensor_config["icon"]
        self._attr_state_class = sensor_config["state_class"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_sn)},
            name=f"EcoFlow {device_sn}",
            manufacturer="EcoFlow",
            model="Battery System",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.coordinator.data is not None
            and self._sensor_config["key"] in self.coordinator.data
        )

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor_config["key"])