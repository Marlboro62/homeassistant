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
from homeassistant.util import slugify as ha_slugify  # pour normaliser les clés FR

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

    # Restore previously loaded sensors
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
        # car_id depuis l'identifier (DOMAIN, car_id)
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

        # Reconstitue sensor_key depuis le unique_id stable
        prefix = f"{DOMAIN}_{entry.entry_id}_{car_id}_"
        restore_entities = [
            TorqueSensor(
                coordinator,
                entry,
                er_ent.unique_id[len(prefix) :],
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
    # petites normalisations usuelles
    s = re.sub(r"\bkmh\b", "km/h", s, flags=re.I)
    s = re.sub(r"\bkph\b", "km/h", s, flags=re.I)
    return s[:1].upper() + s[1:]


def _strip_repeated_prefix(text: str, prefix: Optional[str]) -> str:
    """Supprime toute répétition initiale du nom de véhicule dans le libellé."""
    if not text or not prefix:
        return text
    pat = re.compile(rf"^(?:{re.escape(prefix)}\s+)+", flags=re.IGNORECASE)
    return pat.sub("", text).strip()


# --- Dictionnaire de localisation FR (par *clé* Torque shortName) ------------

# IMPORTANT : les clés doivent correspondre à la version *slugifiée* du shortName
# (c’est exactement ce que renvoie l’API pour sensor_key). Pour être robustes,
# on enregistre **la clé brute ET la clé slugifiée** (voir construction de FR_BY_KEY).
_FR_BY_KEY_RAW = {
    "acceleration_sensor_total": "Accéléromètre total",
    "acceleration_sensor_x_axis": "Accéléromètre axe X",
    "acceleration_sensor_y_axis": "Accéléromètre axe Y",
    "acceleration_sensor_z_axis": "Accéléromètre axe Z",
    "android_battery_level": "Batterie appareil Android",

    "average_trip_speed_whilst_moving_only": "Vitesse moy. trajet (mouv.)",
    "average_trip_speed_whilst_stopped_or_moving": "Vitesse moy. trajet (arrêt + mouvement)",

    "co2_in_gkm_average": "CO₂ g/km (moy.)",
    "co2_in_gkm_instantaneous": "CO₂ g/km (inst.)",

    "cost_per_milekm_instant": "Coût par km/mile (inst.)",
    "cost_per_milekm_trip": "Coût par km/mile (trajet)",

    "coolant_temp": "Température liquide refroidissement",

    "dis_mil_on": "Distance avec MIL allumée",
    "dis_mil_off": "Distance avec MIL éteinte",

    "distance_to_empty_estimated": "Autonomie estimée",

    "engine_kw_at_the_wheels": "Puissance kW (roues)",
    "engine_load": "Charge moteur",
    "engine_rpm": "Régime moteur",
    "horsepower_at_the_wheels": "Puissance (roues)",

    "fuel_cost_trip": "Coût carburant (trajet)",
    "fuel_flow_ratehour": "Débit carburant (L/h)",
    "fuel_flow_rateminute": "Débit carburant (L/min)",
    "fuel_remaining_calculated_from_vehicle_profile": "Carburant restant (profil véhicule)",
    "fuel_trim_bank_1_long_term": "Ajust carburant banc 1 (LT)",
    "fuel_trim_bank_1_sensor_1": "Ajust carburant banc 1 (sonde 1)",
    "fuel_trim_bank_1_short_term": "Ajust carburant banc 1 (CT)",
    "fuel_used_trip": "Carburant utilisé (trajet)",

    "gps_acc": "Précision GPS",
    "gps_bearing": "Cap GPS",
    "gps_bearing-ff123b": "Cap GPS",            # doublons possibles selon PID
    "gps_bearing-ff1007": "Cap GPS",
    "gps_bearing_legacy_ff1007": "Cap GPS",
    "gps_brng": "Cap GPS",
    "gps_height": "Altitude GPS",
    "gps_spd": "Vitesse (GPS)",

    "intake_manifold_pressure": "Pression collecteur d’admission",
    "intake_temp": "Température d’admission",

    "kilometers_per_litre_instant": "km/L (instantané)",
    "kilometers_per_litre_long_term_average": "km/L (moy. LT)",

    "litres_per_100_kilometer_instant": "L/100 km (instantané)",
    "litres_per_100_kilometer_long_term_average": "L/100 km (moy. LT)",

    "mass_air_flow_rate": "Débit massique d’air",

    "miles_per_gallon_instant": "MPG (instantané)",
    "miles_per_gallon_long_term_average": "MPG (moy. LT)",

    "o2_volts_bank_1_sensor_1": "Tension O₂ banc 1 sonde 1",
    "o2_volts_bank_1_sensor_2": "Tension O₂ banc 1 sonde 2",

    "pct_city_driving": "Part conduite urbaine",
    "pct_highway_driving": "Part conduite autoroute",
    "pct_idle_driving": "Part au ralenti",

    "positive_kinetic_energy_pke": "Énergie cinétique positive (PKE)",

    "spd_diff": "Écart vitesse GPS/OBD",
    "speed": "Vitesse",
    "throttle_pos": "Position papillon",
    "timing_advance": "Avance à l’allumage",

    "trip_average_kpl": "km/L (moy. trajet)",
    "trip_average_litres100_km": "L/100 km (moy. trajet)",
    "trip_average_mpg": "MPG (moy. trajet)",
    "trip_distance": "Distance du trajet",
    "trip_distance_stored_in_vehicle_profile": "Distance trajet (profil véhicule)",
    "trip_time_since_journey_start": "Temps trajet (depuis départ)",
    "trip_time_whilst_moving": "Temps trajet (en mouvement)",
    "trip_time_whilst_stationary": "Temps trajet (à l’arrêt)",

    # shortName original contient "&" -> slugifié devient "turbo_boost_vacuum_gauge"
    "turbo_boost_&_vacuum_gauge": "Boost & dépression turbo",

    "voltage_obd_adapter": "Tension (adaptateur OBD)",
    "volumetric_efficiency_calculated": "Rendement volumétrique (calculé)",

    # Chronos de perf
    "time_0_60mph": "0–60 mph (temps)",
    "time_0_100kph": "0–100 km/h (temps)",
    "time_40_60mph": "40–60 mph (temps)",
    "time_60_0mph": "60–0 mph (temps)",
    "time_60_80mph": "60–80 mph (temps)",
    "time_60_120mph": "60–120 mph (temps)",
    "time_60_130mph": "60–130 mph (temps)",
    "time_80_120kph": "80–120 km/h (temps)",
    "time_100_0kph": "100–0 km/h (temps)",
    "time_100_200kph": "100–200 km/h (temps)",
    "time_eighth_mile": "1/8 mile (temps)",
    "time_quarter_mile": "1/4 mile (temps)",
}

# Construction robuste : on ajoute à la fois la clé brute ET la clé slugifiée.
FR_BY_KEY: dict[str, str] = {}
for _k, _v in _FR_BY_KEY_RAW.items():
    FR_BY_KEY[_k] = _v
    FR_BY_KEY[ha_slugify(_k)] = _v


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

        # Toujours initialiser pour éviter AttributeError
        self._attr_name = None
        self._attr_native_unit_of_measurement = None
        self._attr_icon = DEFAULT_ICON
        self._restored_state = None

        # Trace la provenance du nom: 'init' | 'meta' | 'restored' | 'registry' | 'fallback' | 'localized'
        self._name_source: str = "init"

        # 1) Essaye d'abord les métadonnées de la voiture (si déjà dispos au boot)
        meta = self.coordinator.get_meta(self._car_id)
        if meta and self.sensor_key in meta:
            self._attr_native_unit_of_measurement = meta[self.sensor_key].get("unit")
            meta_name = meta[self.sensor_key].get("name")
            if meta_name:
                self._attr_name = meta_name
                self._name_source = "meta"

        # ⚠️ Pas de fallback ici : on laisse async_added_to_hass() faire la restauration.
        self._maybe_localize_name()
        self._set_icon()

    # --- Utils langue ---------------------------------------------------------

    def _get_lang(self) -> str:
        entry = self.coordinator.entry
        lang = entry.options.get(CONF_LANGUAGE, entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE))
        return (lang or DEFAULT_LANGUAGE).lower()

    def _maybe_localize_name(self) -> None:
        """Si langue=fr et qu'on connait une traduction par clé, l'appliquer
        sauf si l'utilisateur a explicitement personnalisé (source=registry)."""
        if self._get_lang() != "fr":
            return
        # essaie la clé telle quelle puis sa version slugifiée (pour gérer les tirets éventuels)
        fr = FR_BY_KEY.get(self.sensor_key) or FR_BY_KEY.get(ha_slugify(self.sensor_key))
        if not fr:
            return
        if self._name_source == "registry":
            return
        # Si nom absent ou provenant de meta/fallback/restored, on force FR
        if self._attr_name != fr:
            self._attr_name = fr
            self._name_source = "localized"

    # --- Rafraîchissement dynamique des métadonnées quand le coordinator bouge

    def _maybe_refresh_metadata(self) -> None:
        """Si meta fournit name/unit pour ce capteur, mets à jour et pousse l'état."""
        meta = self.coordinator.get_meta(self._car_id)
        if not meta or self.sensor_key not in meta:
            return
        m = meta[self.sensor_key]
        changed = False

        # Toujours mettre à jour l'unité si elle change
        new_unit = m.get("unit")
        if new_unit and new_unit != self._attr_native_unit_of_measurement:
            self._attr_native_unit_of_measurement = new_unit
            changed = True

        # Mettre à jour le nom meta uniquement si le nom n'a PAS été personnalisé
        new_name = m.get("name")
        if new_name and new_name != self._attr_name and self._name_source not in ("restored", "registry", "localized"):
            self._attr_name = new_name
            self._name_source = "meta"
            changed = True

        # Appliquer localisation FR si besoin
        before = self._attr_name
        self._maybe_localize_name()
        if self._attr_name != before:
            changed = True

        if changed:
            self._set_icon()
            self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Appelé à chaque update du CoordinatorEntity."""
        self._maybe_refresh_metadata()
        super()._handle_coordinator_update()

    # --- Valeur native (avec filtre inf/NaN)

    @property
    def native_value(self):
        """Return the native value of the sensor (per car)."""
        value = self.coordinator.get_value(self._car_id, self.sensor_key)

        f = _to_finite_float(value)
        if f is not None:
            return round(f, 2)

        # fallback sur l'état restauré (si c'est numérique et fini)
        if self._restored_state is not None:
            f = _to_finite_float(self._restored_state)
            if f is not None:
                return round(f, 2)

        # Sinon, pas de valeur exploitable → état indisponible
        return None

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        native_state = await self.async_get_last_sensor_data()

        if native_state is not None:
            _LOGGER.debug("Restore state of %s to %s", self.entity_id, native_state)
            self._restored_state = native_state.native_value

        # 1) Restaure nom/unité si meta pas encore reçue
        if self._attr_name is None and state is not None and state.name:
            restored_name = _strip_repeated_prefix(state.name, self._car_name)
            if restored_name:
                self._attr_name = restored_name
                self._name_source = "restored"

        if self._attr_native_unit_of_measurement is None and native_state is not None:
            self._attr_native_unit_of_measurement = native_state.native_unit_of_measurement

        # 2) Tente de récupérer / nettoyer le nom depuis l'Entity Registry
        try:
            ent_reg = er.async_get(self.hass)
            entity_id = ent_reg.async_get_entity_id(SENSOR, DOMAIN, self.unique_id)
            if entity_id:
                reg_ent = ent_reg.async_get(entity_id)
                if reg_ent and reg_ent.name:
                    cleaned = _strip_repeated_prefix(reg_ent.name, self._car_name)
                    if cleaned != reg_ent.name:
                        # Si tout le nom n'était que des préfixes, on supprime la customisation
                        new_name = cleaned or None
                        try:
                            ent_reg.async_update_entity(entity_id, name=new_name)
                            _LOGGER.debug(
                                "Cleaned registry name for %s: '%s' -> '%s'",
                                entity_id, reg_ent.name, cleaned
                            )
                        except Exception as err:
                            _LOGGER.debug("Registry name cleanup failed for %s: %s", entity_id, err)
                    if self._attr_name is None and cleaned:
                        self._attr_name = cleaned
                        self._name_source = "registry"
        except Exception as err:
            _LOGGER.debug("Entity Registry lookup/cleanup failed for %s: %s", self.unique_id, err)

        # 3) Localisation FR (si configurée) à partir de la clé
        self._maybe_localize_name()

        # 4) Fallback lisible depuis la clé
        if self._attr_name is None:
            self._attr_name = _title_from_key(self.sensor_key)
            self._name_source = "fallback"

        self._set_icon()

    def _set_icon(self) -> None:
        """Déduit une icône basique à partir du nom (FR/EN)."""
        name = (self._attr_name or "").lower()
        self._attr_icon = DEFAULT_ICON

        # distance
        if re.search(r"\b(kilometers?|kilomètres?|km|miles?)\b", name):
            self._attr_icon = DISTANCE_ICON
        if "distance" in name:  # FR/EN identique
            self._attr_icon = DISTANCE_ICON

        # carburant
        if re.search(r"\b(litre?s?|gallons?)\b", name):
            self._attr_icon = FUEL_ICON
        if "fuel" in name or "carburant" in name:
            self._attr_icon = FUEL_ICON

        # temps
        if "time" in name or "temps" in name or "idle" in name or "ralenti" in name:
            self._attr_icon = TIME_ICON

        # conduite / contexte
        if "highway" in name or "autoroute" in name:
            self._attr_icon = HIGHWAY_ICON
        if "city" in name or "ville" in name:
            self._attr_icon = CITY_ICON

        # vitesse
        if "speed" in name or "vitesse" in name:
            self._attr_icon = SPEED_ICON
