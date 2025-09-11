# -*- coding: utf-8 -*-
"""Torque Logger 2025 API Client/DataView."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import logging

from aiohttp import web
import pint
from homeassistant.components.http import HomeAssistantView
from homeassistant.util import slugify
from homeassistant.config_entries import ConfigEntryState

from .const import TORQUE_CODES

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

# --- Conversion d’unités ---
ureg = pint.UnitRegistry()

# Mappage d’unités pour l’affichage "joli" et les conversions impériales
imperial_units = {"km": "mi", "°C": "°F", "km/h": "mph", "m": "ft"}
prettyPint = {
    "degC": "°C",
    "degF": "°F",
    "mile / hour": "mph",
    "kilometer / hour": "km/h",
    "mile": "mi",
    "kilometer": "km",
    "meter": "m",
    "foot": "ft",
}

# --- Libellés localisés (extensible) ---
LABELS = {
    "fr": {
        "engine load": "Charge moteur",
        "coolant temperature": "Température liquide refroidissement",
        "engine rpm": "Régime moteur",
        "vehicle speed": "Vitesse du véhicule",
        "intake air temperature": "Température air d’admission",
        "throttle position": "Position d’accélérateur",
        "distance since engine start": "Distance depuis démarrage moteur",
        "distance with mil on": "Distance avec MIL allumée",
        "fuel level": "Niveau de carburant",
        "distance with mil off": "Distance avec MIL éteinte",
        "vehicle speed (gps)": "Vitesse du véhicule (GPS)",
        "gps bearing": "Cap GPS",
        "gps satellites": "Satellites GPS",
        "gps altitude": "Altitude GPS",
        "gps latitude": "Latitude GPS",
        "gps accuracy": "Précision GPS",
        "gps vs obd speed difference": "Écart vit. GPS/OBD",
        "fuel used (trip)": "Carburant utilisé (trajet)",
        "gps longitude": "Longitude GPS",
        "absolute throttle position b": "Position papillon absolue B",
        "acceleration sensor (total)": "Accéléromètre (total)",
        "acceleration sensor (x axis)": "Accéléromètre (axe X)",
        "acceleration sensor (y axis)": "Accéléromètre (axe Y)",
        "acceleration sensor (z axis)": "Accéléromètre (axe Z)",
        "accelerator pedalposition d": "Pos. pédale accél. D",
        "accelerator pedalposition e": "Pos. pédale accél. E",
        "accelerator pedalposition f": "Pos. pédale accél. F",
        "air fuel ratio (commanded)": "Rapport air/carburant (ciblé)",
        "air fuel ratio (measured)": "Rapport air/carburant (mesuré)",
        "air status": "État air secondaire",
        "ambient air temp": "Température de l’air ambiant",
        "average trip speed (whilst moving only)": "Vit. moy. traj. (mouv.)",
        "average trip speed (whilst stopped or moving)": "Vit. moy. traj. (arrêt+mouv.)",
        "barometer (on android device)": "Baromètre (appareil)",
        "barometric pressure (from vehicle)": "Pression barométrique (véhicule)",
        "catalyst temperature (bank 1 sensor 1)": "Temp. catalyseur (B1 S1)",
        "catalyst temperature (bank 1 sensor 2)": "Temp. catalyseur (B1 S2)",
        "catalyst temperature (bank 2 sensor 1)": "Temp. catalyseur (B2 S1)",
        "catalyst temperature (bank 2 sensor 2)": "Temp. catalyseur (B2 S2)",
        "commanded equivalence ratio (lambda)": "Lambda commandée",
        "cost per mile/km (instant)": "Coût par km/mile (inst.)",
        "cost per mile/km (trip)": "Coût par km/mile (trajet)",
        "co2 in g/km (average)": "CO₂ g/km (moy.)",
        "co2 in g/km (instantaneous)": "CO₂ g/km (inst.)",
        "distance to empty (estimated)": "Autonomie (estimée)",
        "egr commanded": "EGR commandée",
        "egr error": "Erreur EGR",
        "engine kw (at the wheels)": "Puissance kW (roues)",
        "engine load (absolute)": "Charge moteur (absolue)",
        "engine oil temperature": "Température d’huile moteur",
        "ethanol fuel %": "% éthanol",
        "evap system vapour pressure": "Pression vapeur EVAP",
        "exhaust gas temperature 1": "Temp. gaz échapp. 1",
        "exhaust gas temperature 2": "Temp. gaz échapp. 2",
        "fuel cost (trip)": "Coût carburant (trajet)",
        "fuel flow rate/hour": "Débit carburant/heure",
        "fuel flow rate/minute": "Débit carburant/min",
        "fuel pressure": "Pression carburant",
        "fuel rail pressure": "Pression rampe",
        "fuel rail pressure (relative to manifold vacuum)": "Pression rampe (rel. au vide)",
        "fuel remaining (calculated from vehicle profile)": "Carburant restant (profil)",
        "fuel status": "Statut carburant",
        "fuel trim bank 1 long term": "Ajust. carburant B1 LT",
        "fuel trim bank 1 sensor 1": "Ajust. carburant B1 S1",
        "fuel trim bank 1 sensor 2": "Ajust. carburant B1 S2",
        "fuel trim bank 1 sensor 3": "Ajust. carburant B1 S3",
        "fuel trim bank 1 sensor 4": "Ajust. carburant B1 S4",
        "fuel trim bank 1 short term": "Ajust. carburant B1 CT",
        "fuel trim bank 2 long term": "Ajust. carburant B2 LT",
        "fuel trim bank 2 sensor 1": "Ajust. carburant B2 S1",
        "fuel trim bank 2 sensor 2": "Ajust. carburant B2 S2",
        "fuel trim bank 2 sensor 3": "Ajust. carburant B2 S3",
        "fuel trim bank 2 sensor 4": "Ajust. carburant B2 S4",
        "fuel trim bank 2 short term": "Ajust. carburant B2 CT",
        "horsepower (at the wheels)": "Puissance (roues)",
        "intake manifold pressure": "Pression collecteur d’admission",
        "kilometers per litre (instant)": "km/L (inst.)",
        "kilometers per litre (long term average)": "km/L (moy. LT)",
        "litres per 100 kilometer (instant)": "L/100 km (inst.)",
        "litres per 100 kilometer (long term average)": "L/100 km (moy. LT)",
        "mass air flow rate": "Débit massique d’air",
        "miles per gallon (instant)": "mpg (inst.)",
        "miles per gallon (long term average)": "mpg (moy. LT)",
        "o2 sensor1 equivalence ratio": "Lambda O2 S1",
        "o2 sensor1 equivalence ratio (alternate)": "Lambda O2 S1 (alt.)",
        "o2 sensor1 wide-range voltage": "Tension O2 large bande S1",
        "o2 sensor2 equivalence ratio": "Lambda O2 S2",
        "o2 sensor2 wide-range voltage": "Tension O2 large bande S2",
        "o2 sensor3 equivalence ratio": "Lambda O2 S3",
        "o2 sensor3 wide-range voltage": "Tension O2 large bande S3",
        "o2 sensor4 equivalence ratio": "Lambda O2 S4",
        "o2 sensor4 wide-range voltage": "Tension O2 large bande S4",
        "o2 sensor5 equivalence ratio": "Lambda O2 S5",
        "o2 sensor5 wide-range voltage": "Tension O2 large bande S5",
        "o2 sensor6 equivalence ratio": "Lambda O2 S6",
        "o2 sensor6 wide-range voltage": "Tension O2 large bande S6",
        "o2 sensor7 equivalence ratio": "Lambda O2 S7",
        "o2 sensor7 wide-range voltage": "Tension O2 large bande S7",
        "o2 sensor8 equivalence ratio": "Lambda O2 S8",
        "o2 sensor8 wide-range voltage": "Tension O2 large bande S8",
        "o2 volts bank 1 sensor 1": "Tension O2 B1 S1",
        "o2 volts bank 1 sensor 2": "Tension O2 B1 S2",
        "o2 volts bank 1 sensor 3": "Tension O2 B1 S3",
        "o2 volts bank 1 sensor 4": "Tension O2 B1 S4",
        "o2 volts bank 2 sensor 1": "Tension O2 B2 S1",
        "o2 volts bank 2 sensor 2": "Tension O2 B2 S2",
        "o2 volts bank 2 sensor 3": "Tension O2 B2 S3",
        "o2 volts bank 2 sensor 4": "Tension O2 B2 S4",
        "relative accelerator pedal position": "Pos. pédale accél. (rel.)",
        "relative throttle position": "Position papillon (rel.)",
        "tilt (x)": "Inclinaison (x)",
        "tilt (y)": "Inclinaison (y)",
        "tilt (z)": "Inclinaison (z)",
        "timing advance": "Avance à l’allumage",
        "torque": "Couple",
        "transmission temperature (method 1)": "Temp. boîte (M1)",
        "transmission temperature (method 2)": "Temp. boîte (M2)",
        "trip average kpl": "km/L (moy. trajet)",
        "trip average litres/100 km": "L/100 km (moy. trajet)",
        "trip average mpg": "mpg (moy. trajet)",
        "trip distance": "Distance du trajet",
        "trip distance (stored in vehicle profile)": "Distance trajet (profil)",
        "trip time (since journey start)": "Temps de trajet (depuis départ)",
        "trip time (whilst moving)": "Temps de trajet (en mouvement)",
        "trip time (whilst stationary)": "Temps de trajet (à l’arrêt)",
        "turbo boost & vacuum gauge": "Boost & dépression turbo",
        "voltage (control module)": "Tension (module de contrôle)",
        "voltage (obd adapter)": "Tension (adaptateur OBD)",
        "volumetric efficiency (calculated)": "Rendement volumétrique (calc.)",

        # Variantes vues dans Torque
        "average trip speed whilst moving only": "Vit. moy. traj. (mouv.)",
        "average trip speed whilst stopped or moving": "Vit. moy. traj. (arrêt+mouv.)",
        "cost per milekm (instant)": "Coût par km/mile (inst.)",
        "cost per milekm (trip)": "Coût par km/mile (trajet)",
        "co2 in gkm (average)": "CO₂ g/km (moy.)",
        "co2 in gkm (instantaneous)": "CO₂ g/km (inst.)",
        "engine kw at the wheels": "Puissance kW (roues)",
        "horsepower at the wheels": "Puissance (roues)",
        "percentage of city driving": "Part conduite urbaine",
        "percentage of highway driving": "Part conduite autoroute",
        "percentage of idle driving": "Part au ralenti",
        "positive kinetic energy (pke)": "Énergie cinétique positive (PKE)",

        # Chronos
        "0-60mph time": "0–60 mph (temps)",
        "time 0 60mph": "0–60 mph (temps)",
        "0 60mph time": "0–60 mph (temps)",
        "0-100kph time": "0–100 km/h (temps)",
        "time 0 100kph": "0–100 km/h (temps)",
        "0 100kph time": "0–100 km/h (temps)",
        "40-60mph time": "40–60 mph (temps)",
        "time 40 60mph": "40–60 mph (temps)",
        "60-0mph time": "60–0 mph (temps)",
        "time 60 0mph": "60–0 mph (temps)",
        "60-80mph time": "60–80 mph (temps)",
        "time 60 80mph": "60–80 mph (temps)",
        "60-120mph time": "60–120 mph (temps)",
        "time 60 120mph": "60–120 mph (temps)",
        "60-130mph time": "60–130 mph (temps)",
        "time 60 130mph": "60–130 mph (temps)",
        "80-120kph time": "80–120 km/h (temps)",
        "time 80 120kph": "80–120 km/h (temps)",
        "100-0kph time": "100–0 km/h (temps)",
        "time 100 0kph": "100–0 km/h (temps)",
        "100-200kph time": "100–200 km/h (temps)",
        "time 100 200kph": "100–200 km/h (temps)",
        "1/8 mile time": "1/8 mile (temps)",
        "time eighth mile": "1/8 mile (temps)",
        "1/4 mile time": "1/4 mile (temps)",
        "time quarter mile": "1/4 mile (temps)",
    }
}

# Overrides manuels par *clé* (shortName slugifié) si nécessaire
FR_BY_KEY: dict[str, str] = {
    "vit_moy_traj_mouv": "Vitesse moy. trajet (mouv.)",
    "vit_moy_traj_arret_mouv": "Vitesse moy. trajet (arrêt + mouvement)",

    # Séparation claire des 2 capteurs de cap GPS
    "gps_bearing": "Cap GPS",
    "gps_bearing_legacy_ff1007": "Cap GPS (legacy)",

    "co2_g_km_moy": "CO₂ g/km (moy.)",
    "co2_g_km_inst": "CO₂ g/km (inst.)",
    "cout_par_km_mile_inst": "Coût par km/mile (inst.)",
    "cout_par_km_mile_trajet": "Coût par km/mile (trajet)",
    "puissance_kw_roues": "Puissance kW (roues)",
    "puissance_roues": "Puissance (roues)",
    "couple": "Couple",
    "energie_cinetique_positive_pke": "Énergie cinétique positive (PKE)",
    "trip_average_l_100km": "L/100 km (moy. trajet)",
    "distance_du_trajet": "Distance du trajet",
    "vitesse_du_vehicule": "Vitesse du véhicule",
    "vitesse_du_vehicule_gps": "Vitesse (GPS)",

    # Chronos si tes shortName FR sont identiques au slug par défaut :
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

# --- Auto-build FR_BY_KEY from LABELS + TORQUE_CODES -------------------------
def _auto_fr_by_key_from_labels() -> dict[str, str]:
    fr_map: dict[str, str] = {}
    labels_fr = LABELS.get("fr", {})
    labels_fr_cf = {k.casefold(): v for k, v in labels_fr.items()}
    for _, defs in TORQUE_CODES.items():
        short_raw = defs.get("shortName", "")
        full_raw = defs.get("fullName", "")
        short_key = slugify(str(short_raw))   # ex: "engine_rpm"
        full_key = str(full_raw).casefold()   # ex: "engine rpm"
        if short_key and full_key in labels_fr_cf:
            fr_map[short_key] = labels_fr_cf[full_key]
    return fr_map

FR_BY_KEY_AUTO = _auto_fr_by_key_from_labels()

def _pretty_units(unit: str) -> str:
    return prettyPint.get(unit, unit)

def _unpretty_units(unit: str) -> str:
    for pint_unit, pretty_unit in prettyPint.items():
        if pretty_unit == unit:
            return pint_unit
    return unit

def _convert_units(value: float, u_in: str, u_out: str):
    q_in = ureg.Quantity(value, u_in)
    q_out = q_in.to(u_out)
    return {"value": round(q_out.magnitude, 2), "unit": str(q_out.units)}

def _pretty_convert_units(value: float, u_in: str, u_out: str):
    p_in = _unpretty_units(u_in)
    p_out = _unpretty_units(u_out)
    res = _convert_units(value, p_in, p_out)
    return {"value": res["value"], "unit": _pretty_units(res["unit"])}

def _localize(lang: str, name: str) -> str:
    """Retourne le libellé localisé, insensible à la casse."""
    loc = LABELS.get(lang)
    if not loc or not name:
        return name
    return loc.get(name, loc.get(name.casefold(), name))

class TorqueReceiveDataView(HomeAssistantView):
    """Handle data from Torque requests."""

    url = "/api/torque_logger_2025"
    name = "api:torque_logger_2025"
    requires_auth = False  # recommandé pour envoi direct par Torque

    coordinator: Optional["TorqueLoggerCoordinator"]

    def __init__(self, data: dict, email: str, imperial: bool, language: str = "en"):
        """Initialize a Torque view."""
        self.data = data
        self.email = (email or "").strip()
        self.imperial = bool(imperial)
        self.lang = (language or "en").lower()
        if self.lang not in ("en", "fr"):
            self.lang = "en"
        self.coordinator = None  # injecté par __init__.py

    async def get(self, request):
        """Handle Torque data GET request."""
        try:
            _LOGGER.debug("Torque payload: %s", dict(request.query))

            # Permettre override temporaire via URL ?lang=fr
            lang_param = (request.query.get("lang") or request.query.get("language") or "").lower()
            if lang_param in ("en", "fr"):
                self.lang = lang_param

            session = self.parse_fields(request.query)
            if session:
                await self._async_publish_data(session)

            return web.Response(text="OK!")
        except Exception as err:
            # On log l’erreur mais on renvoie OK pour ne pas casser l’envoi côté Torque
            _LOGGER.exception("Error handling Torque payload: %s", err)
            return web.Response(text="OK!")

    def parse_fields(self, qdata):  # noqa
        """Parse les champs de la requête Torque et remplit le buffer de session."""
        session: str = qdata.get("session")
        if not session:
            raise web.HTTPBadRequest(text="Missing session")

        if session not in self.data:
            self.data[session] = {
                "profile": {},
                "unit": {},
                "defaultUnit": {},
                "fullName": {},
                "shortName": {},
                "value": {},
                "unknown": [],
                "time": 0,
            }

        for key, value in qdata.items():
            if key.startswith("userUnit"):
                continue
            if key.startswith("userShortName"):
                item = key[13:]
                self.data[session]["shortName"][item] = value
                continue
            if key.startswith("userFullName"):
                item = key[12:]
                self.data[session]["fullName"][item] = value
                continue
            if key.startswith("defaultUnit"):
                item = key[11:]
                self.data[session]["defaultUnit"][item] = value
                continue
            if key.startswith("k"):
                item = key[1:]
                if len(item) == 1:
                    item = "0" + item
                self.data[session]["value"][item] = value
                continue
            if key.startswith("profile"):
                # ex: profileName -> Name
                item = key[7:]
                self.data[session]["profile"][item] = value
                continue
            if key == "eml":
                self.data[session]["profile"]["email"] = value
                continue
            if key == "time":
                try:
                    self.data[session]["time"] = int(value)
                except (ValueError, TypeError):
                    self.data[session]["time"] = 0
                continue
            if key == "v":
                self.data[session]["profile"]["version"] = value
                continue
            if key == "session":
                continue
            if key == "id":
                self.data[session]["profile"]["id"] = value
                continue

            self.data[session]["unknown"].append({"key": key, "value": value})

        # Filtrage par email : si aucun email n'est défini côté intégration -> accepter tout
        payload_email = self.data[session]["profile"].get("email", "").strip().lower()
        cfg_email = self.email.lower()
        if not cfg_email or payload_email == cfg_email:
            return session

        _LOGGER.debug(
            "Ignoring payload: email %r doesn't match configured %r",
            payload_email,
            cfg_email,
        )
        return None

    def _get_field(self, session: str, key: str):
        # Vérifier que le PID est connu
        if TORQUE_CODES.get(key) is None:
            return None

        defaults = TORQUE_CODES[key]
        # Valeurs brutes
        name: str = self.data[session]["fullName"].get(key, defaults.get("fullName", key))
        short_name_raw: str = self.data[session]["shortName"].get(key, defaults.get("shortName", key))
        unit: str = self.data[session]["defaultUnit"].get(key, defaults.get("unit", ""))
        value = self.data[session]["value"].get(key)

        # Clé normalisée pour l’ID & la localisation par clé
        short_key = slugify(str(short_name_raw))  # ex: "engine_rpm"

        # Harmonisation des capteurs 'Cap GPS'
        # - ff123b => capteur principal (short_key = "gps_bearing")
        # - ff1007 => capteur legacy (short_key = "gps_bearing_legacy_ff1007")
        if key in ("ff1007", "ff123b"):
            if key == "ff1007":
                short_key = "gps_bearing_legacy_ff1007"
                # nom par défaut si rien n'existe
                name = name or "GPS Bearing (legacy)"
            else:
                short_key = "gps_bearing"
                name = name or "GPS Bearing"

            # Certaines versions de Torque n’envoient pas l’unité → on force le °
            if not unit:
                unit = "°"

        # Localisation: priorité clé statique -> clé auto -> libellé
        if self.lang == "fr":
            name = FR_BY_KEY.get(short_key) or FR_BY_KEY_AUTO.get(short_key) or _localize("fr", name)

        # Conversion en impérial si demandé
        if self.imperial and unit in imperial_units and value not in (None, ""):
            try:
                conv = _pretty_convert_units(float(value), unit, imperial_units[unit])
                value = conv["value"]
                unit = conv["unit"]
            except (ValueError, TypeError):
                _LOGGER.debug("Unit conversion skipped for %s=%r %s", key, value, unit)

        return {
            "name": name,
            "short_name": short_key,
            "unit": unit,
            "value": value,
        }

    def _get_profile(self, session: str):
        return self.data[session]["profile"]

    def _get_data(self, session: str):
        retdata = {"profile": self._get_profile(session), "time": self.data[session]["time"]}
        meta = {}

        for key in self.data[session]["value"].keys():
            row_data = self._get_field(session, key)
            if row_data is None:
                continue

            short = row_data["short_name"]
            # Évite d'écraser un autre PID ayant le même short_name
            if short in retdata:
                short = f"{short}-{key}"

            retdata[short] = row_data["value"]
            meta[short] = {"name": row_data["name"], "unit": row_data["unit"]}

        retdata["meta"] = meta
        return retdata

    async def _async_publish_data(self, session: str):
        # --- GARDE ANTI-STALE : ignorer si l'entrée n'est pas chargée ---
        if not getattr(self, "coordinator", None):
            _LOGGER.warning("No coordinator bound to view; dropping payload")
            return

        entry = getattr(self.coordinator, "config_entry", None) or getattr(self.coordinator, "entry", None)
        if entry is None:
            _LOGGER.warning("Missing config entry on coordinator; dropping payload")
            return

        if entry.state != ConfigEntryState.LOADED:
            _LOGGER.warning("Config entry not loaded (state=%s); dropping payload", entry.state)
            return
        # -----------------------------------------------------------------

        session_data = self._get_data(session)

        # Ne publie pas tant qu'on n'a pas le nom du véhicule
        if "Name" not in session_data["profile"]:
            current_id = session_data["profile"].get("id")
            other_sessions = [
                self.data[key]
                for key in self.data.keys()
                if self.data[key]["profile"].get("id") == current_id
                and "Name" in self.data[key]["profile"]
            ]
            if not other_sessions:
                _LOGGER.warning("Missing profile name from torque data.")
                return
            session_data["profile"]["Name"] = other_sessions[0]["profile"]["Name"]

        # Mémorise par voiture et notifie les entités
        self.coordinator.update_from_session(session_data)
        await self.coordinator.add_entities(session_data)
