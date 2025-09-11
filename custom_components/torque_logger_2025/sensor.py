# -*- coding: utf-8 -*-
"""Sensor platform for Torque Logger 2025."""

from __future__ import annotations

import logging
import re
import math
from typing import TYPE_CHECKING, List, Optional

from homeassistant.components.sensor import RestoreSensor
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import entity_registry as er, device_registry as dr

from .const import (
    CITY_ICON,
    DISTANCE_ICON,
    DOMAIN,
    DEFAULT_ICON,
    FUEL_ICON,
    HIGHWAY_ICON,
    SENSOR,
    SPEED_ICON,
    TIME_ICON,
    CONF_LANGUAGE,
    DEFAULT_LANGUAGE,
)
from .entity import TorqueEntity

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor platform."""
    coordinator: "TorqueLoggerCoordinator" = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator.async_add_sensor = async_add_entities

    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)

    devices = [
        device
        for device in dev_reg.devices.values()
        if any(ident[0] == DOMAIN for ident in device.identifiers)
    ]
    _LOGGER.debug("%d devices found for restore", len(devices))

    to_add: List["TorqueSensor"] = []

    for device in devices:
        try:
            car_id = next(ident[1] for ident in device.identifiers if ident[0] == DOMAIN)
        except StopIteration:
            _LOGGER.debug("Skipping device without %s identifier: %s", DOMAIN, device.id)
            continue

        device_info = DeviceInfo(
            identifiers=device.identifiers,
            manufacturer=device.manufacturer,
            model=device.model,
            name=device.name,
            sw_version=device.sw_version,
        )

        prefix = f"{DOMAIN}_{entry.entry_id}_{car_id}_"
        restore_entities = [
            TorqueSensor(
                coordinator,
                entry,
                er_ent.unique_id[len(prefix):],
                device_info,
            )
            for er_ent in ent_reg.entities.values()
            if er_ent.device_id == device.id
            and er_ent.domain == SENSOR
            and er_ent.unique_id
            and er_ent.unique_id.startswith(prefix)
        ]

        if restore_entities:
            _LOGGER.debug(
                "Restoring sensors for %s: %s",
                device.model,
                ", ".join(e.sensor_key for e in restore_entities),
            )
            to_add.extend(restore_entities)

    if to_add:
        async_add_entities(to_add)


# --- Helpers -----------------------------------------------------------------

def _to_finite_float(val):
    """Retourne un float fini ou None (filtre NaN/±inf et erreurs de cast)."""
    try:
        f = float(val)
    except (ValueError, TypeError):
        return None
    return f if math.isfinite(f) else None


def _title_from_key(key: str) -> str:
    """Nom lisible par défaut à partir d'une clé slug (fallback si pas de meta/restore)."""
    s = key.replace("_", " ").strip()
    s = re.sub(r"\bkmh\b", "km/h", s, flags=re.I)
    s = re.sub(r"\bkph\b", "km/h", s, flags=re.I)
    return s[:1].upper() + s[1:]


def _strip_repeated_prefix(text: str, prefix: Optional[str]) -> str:
    if not text or not prefix:
        return text
    pat = re.compile(rf"^(?:{re.escape(prefix)}\s+)+", flags=re.IGNORECASE)
    return pat.sub("", text).strip()


# --- Localisation FR par *clé* shortName (slug) ------------------------------
FR_BY_KEY: dict[str, str] = {
    # GPS
    "gps_bearing": "Cap GPS",
    "gps_bearing_legacy_ff1007": "Cap GPS (legacy)",
    "gps_bearing-ff123b": "Cap GPS",
    "gps_acc": "Précision GPS",
    "gps_height": "Altitude GPS",
    "gps_spd": "Vitesse (GPS)",

    # Temp/air/moteur
    "coolant_temp": "Température liquide refroidissement",
    "intake_temp": "Température d’admission",
    "engine_rpm": "Régime moteur",
    "engine_load": "Charge moteur",
    "throttle_pos": "Position papillon",
    "mass_air_flow_rate": "Débit massique d’air",
    "intake_manifold_pressure": "Pression collecteur d’admission",

    # Capteurs O2 / trims
    "o2_volts_bank_1_sensor_1": "Tension O₂ banc 1 sonde 1",
    "o2_volts_bank_1_sensor_2": "Tension O₂ banc 1 sonde 2",
    "fuel_trim_bank_1_short_term": "Ajust carburant banc 1 (CT)",
    "fuel_trim_bank_1_long_term": "Ajust carburant banc 1 (LT)",
    "fuel_trim_bank_1_sensor_1": "Ajust carburant banc 1 (sonde 1)",

    # Conso / économies
    "kilometers_per_litre_instant": "km/L (instantané)",
    "kilometers_per_litre_long_term_average": "km/L (moy. LT)",
    "litres_per_100_kilometer_instant": "L/100 km (instantané)",
    "litres_per_100_kilometer_long_term_average": "L/100 km (moy. LT)",
    "miles_per_gallon_instant": "MPG (instantané)",
    "miles_per_gallon_long_term_average": "MPG (moy. LT)",
    "fuel_cost_trip": "Coût carburant (trajet)",
    "fuel_used_trip": "Carburant utilisé (trajet)",
    "fuel_flow_ratehour": "Débit carburant (L/h)",
    "fuel_flow_rateminute": "Débit carburant (L/min)",
    "fuel_remaining_calculated_from_vehicle_profile": "Carburant restant (profil véhicule)",

    # CO2 / coûts (clés slug)
    "co2_in_gkm_average": "CO₂ g/km (moy.)",
    "co2_in_gkm_instantaneous": "CO₂ g/km (inst.)",
    "cost_per_milekm_instant": "Coût par km/mile (inst.)",
    "cost_per_milekm_trip": "Coût par km/mile (trajet)",

    # Vitesses moyennes (clés slug Torque)
    "average_trip_speed_whilst_moving_only": "Vitesse moy. trajet (mouv.)",
    "average_trip_speed_whilst_stopped_or_moving": "Vitesse moy. trajet (arrêt + mouvement)",

    # Divers conduite
    "speed": "Vitesse",
    "distance_to_empty_estimated": "Autonomie estimée",
    "dis_mil_on": "Distance avec MIL allumée",
    "dis_mil_off": "Distance avec MIL éteinte",
    "distance_du_trajet": "Distance du trajet",
    "trip_distance_stored_in_vehicle_profile": "Distance trajet (profil véhicule)",
    "spd_diff": "Écart vitesse GPS/OBD",
    "trip_time_since_journey_start": "Temps trajet (depuis départ)",
    "trip_time_whilst_moving": "Temps trajet (en mouvement)",
    "trip_time_whilst_stationary": "Temps trajet (à l’arrêt)",
    "timing_advance": "Avance à l’allumage",

    # Appareil
    "android_battery_level": "Batterie appareil Android",

    # Puissance / couple
    "engine_kw_at_the_wheels": "Puissance kW (roues)",
    "horsepower_at_the_wheels": "Puissance (roues)",
    "puissance_kw_roues": "Puissance kW (roues)",
    "puissance_roues": "Puissance (roues)",
    "couple": "Couple",

    # PKE
    "positive_kinetic_energy_pke": "Énergie cinétique positive (PKE)",
    "energie_cinetique_positive_pke": "Énergie cinétique positive (PKE)",

    # Trip averages
    "trip_average_kpl": "km/L (moy. trajet)",
    "trip_average_litres100_km": "L/100 km (moy. trajet)",
    "trip_average_litres100km": "L/100 km (moy. trajet)",
    "trip_average_mpg": "mpg (moy. trajet)",
    "trip_distance": "Distance du trajet",

    # Boost
    "turbo_boost_vacuum_gauge": "Boost & dépression turbo",
    "turbo_boost_&_vacuum_gauge": "Boost & dépression turbo",

    # Divers
    "voltage_obd_adapter": "Tension (adaptateur OBD)",
    "voltage_control_module": "Tension (module de contrôle)",

    # Accéléromètre
    "acceleration_sensor_total": "Accéléromètre total",
    "acceleration_sensor_x_axis": "Accéléromètre axe X",
    "acceleration_sensor_y_axis": "Accéléromètre axe Y",
    "acceleration_sensor_z_axis": "Accéléromètre axe Z",

    # Chronos
    "0_60mph_time": "0–60 mph (temps)",
    "0_100kph_time": "0–100 km/h (temps)",
    "40_60mph_time": "40–60 mph (temps)",
    "60_0mph_time": "60–0 mph (temps)",
    "60_80mph_time": "60–80 mph (temps)",
    "60_120mph_time": "60–120 mph (temps)",
    "60_130mph_time": "60–130 mph (temps)",
    "80_120kph_time": "80–120 km/h (temps)",
    "100_0kph_time": "100–0 km/h (temps)",
    "100_200kph_time": "100–200 km/h (temps)",
    "time_eighth_mile": "1/8 mile (temps)",
    "time_quarter_mile": "1/4 mile (temps)",
}


# --- Entity ------------------------------------------------------------------

class TorqueSensor(TorqueEntity, RestoreSensor):
    """Torque Sensor class."""

    def __init__(
        self,
        coordinator: "TorqueLoggerCoordinator",
        config_entry: ConfigEntry,
        sensor_key: str,
        device: DeviceInfo,
    ):
        super().__init__(coordinator, config_entry, sensor_key, device)

        self._attr_name: Optional[str] = None
        self._attr_native_unit_of_measurement: Optional[str] = None
        self._attr_icon = DEFAULT_ICON
        self._restored_state = None
        self._customized_name = False

        # 1) Méta existantes ?
        meta = self.coordinator.get_meta(self._car_id)
        if meta and self.sensor_key in meta:
            self._attr_native_unit_of_measurement = meta[self.sensor_key].get("unit")
            meta_name = meta[self.sensor_key].get("name")
            if meta_name:
                self._attr_name = meta_name

        # 2) Fallback lisible
        if self._attr_name is None:
            self._attr_name = _title_from_key(self.sensor_key)

        # 3) Localisation immédiate si FR (avant 1er payload)
        self._maybe_localize_name()
        self._set_icon()

    # --- Langue / localisation -----------------------------------------------

    def _get_lang(self) -> str:
        entry = self.coordinator.entry
        lang = entry.options.get(CONF_LANGUAGE, entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE))
        return (lang or DEFAULT_LANGUAGE).lower()

    def _maybe_localize_name(self) -> None:
        if self._get_lang() != "fr":
            return
        fr = FR_BY_KEY.get(self.sensor_key)
        if fr and not self._customized_name and self._attr_name != fr:
            self._attr_name = fr

    # --- Rafraîchissement quand le coordinator bouge -------------------------

    def _maybe_refresh_metadata(self) -> None:
        meta = self.coordinator.get_meta(self._car_id)
        if not meta or self.sensor_key not in meta:
            return
        m = meta[self.sensor_key]
        changed = False

        new_unit = m.get("unit")
        if new_unit and new_unit != self._attr_native_unit_of_measurement:
            self._attr_native_unit_of_measurement = new_unit
            changed = True

        new_name = m.get("name")
        if new_name and not self._customized_name and new_name != self._attr_name:
            self._attr_name = new_name
            changed = True

        before = self._attr_name
        self._maybe_localize_name()
        if self._attr_name != before:
            changed = True

        if changed:
            self._set_icon()
            self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        self._maybe_refresh_metadata()
        super()._handle_coordinator_update()

    # --- Valeur native --------------------------------------------------------

    @property
    def native_value(self):
        value = self.coordinator.get_value(self._car_id, self.sensor_key)

        f = _to_finite_float(value)
        if f is not None:
            return round(f, 2)

        if self._restored_state is not None:
            f = _to_finite_float(self._restored_state)
            if f is not None:
                return round(f, 2)

        return None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        # Détection d'un nom custom
        try:
            ent_reg = er.async_get(self.hass)
            entity_id = ent_reg.async_get_entity_id(SENSOR, DOMAIN, self.unique_id)
            if entity_id:
                reg_ent = ent_reg.async_get(entity_id)
                if reg_ent and reg_ent.name:
                    cleaned = _strip_repeated_prefix(reg_ent.name, self._car_name)
                    if cleaned != reg_ent.name:
                        try:
                            ent_reg.async_update_entity(entity_id, name=cleaned or None)
                        except Exception:
                            pass
                    self._customized_name = cleaned is not None

                    # Auto-fix: ancien legacy nommé "Cap GPS" -> enlève custom
                    if (
                        self.sensor_key == "gps_bearing_legacy_ff1007"
                        and cleaned
                        and cleaned.strip().lower() in ("cap gps", "gps bearing")
                    ):
                        try:
                            ent_reg.async_update_entity(entity_id, name=None)
                            self._customized_name = False
                        except Exception:
                            pass
        except Exception as err:
            _LOGGER.debug("Entity Registry lookup/cleanup failed for %s: %s", self.unique_id, err)

        state = await self.async_get_last_state()
        native_state = await self.async_get_last_sensor_data()

        if native_state is not None:
            _LOGGER.debug("Restore state of %s to %s", self.entity_id, native_state)
            self._restored_state = native_state.native_value

        if self._attr_name is None and state is not None and state.name:
            restored_name = _strip_repeated_prefix(state.name, self._car_name)
            if restored_name:
                self._attr_name = restored_name

        if self._attr_native_unit_of_measurement is None and native_state is not None:
            self._attr_native_unit_of_measurement = native_state.native_unit_of_measurement

        self._maybe_localize_name()
        if self._attr_name is None:
            self._attr_name = _title_from_key(self.sensor_key)

        self._set_icon()

    def _set_icon(self) -> None:
        self._attr_icon = DEFAULT_ICON

        u = (self._attr_native_unit_of_measurement or "").strip().lower().replace(" ", "")
        u = u.replace("kmh", "km/h").replace("kph", "km/h")

        name = (self._attr_name or "")

        speed_units = {"km/h", "mph", "m/s", "kn"}
        distance_units = {"km", "mi", "m", "ft"}
        fuel_units = {"l/100km", "mpg", "km/l", "l", "gal", "wh/km", "kwh/100km", "gph"}
        time_units = {"s", "sec", "secs", "secondes", "min", "mins", "h", "hr", "hrs", "ms"}

        if u in distance_units:
            self._attr_icon = DISTANCE_ICON
            return
        if u in speed_units:
            self._attr_icon = SPEED_ICON
            return
        if u in fuel_units:
            self._attr_icon = FUEL_ICON
            return
        if u in time_units:
            self._attr_icon = TIME_ICON
            return

        n = name.lower()
        if re.search(r"\b(distance|kilometers?|miles?|kilom(è|e)tres?)\b", n, re.IGNORECASE):
            self._attr_icon = DISTANCE_ICON
            return
        if re.search(r"\b(speed|vitesse)\b", n, re.IGNORECASE):
            self._attr_icon = SPEED_ICON
            return
        if re.search(
            r"\b(litre?s?|gallons?|fuel|carburant|essence|diesel)\b", n, re.IGNORECASE
        ) or re.search(r"\b(l/100 ?km|mpg|km/l|wh/km|kwh/100km|gph)\b", n, re.IGNORECASE):
            self._attr_icon = FUEL_ICON
            return
        if re.search(r"\b(time|min|sec|dur(é|e)e|ralenti|idle)\b", n, re.IGNORECASE):
            self._attr_icon = TIME_ICON
            return
        if re.search(r"\b(autoroute|highway)\b", n, re.IGNORECASE):
            self._attr_icon = HIGHWAY_ICON
            return
        if re.search(r"\b(ville|city)\b", n, re.IGNORECASE):
            self._attr_icon = CITY_ICON
            return
