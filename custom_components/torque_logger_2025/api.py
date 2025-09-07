"""Torque Logger API Client/DataView."""
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

# --- Conversion dâ€™unitÃ©s ---
ureg = pint.UnitRegistry()

# Mappage dâ€™unitÃ©s pour lâ€™affichage "joli" et les conversions impÃ©riales
imperial_units = {"km": "mi", "Â°C": "Â°F", "km/h": "mph", "m": "ft"}
prettyPint = {
    "degC": "Â°C",
    "degF": "Â°F",
    "mile / hour": "mph",
    "kilometer / hour": "km/h",
    "mile": "mi",
    "kilometer": "km",
    "meter": "m",
    "foot": "ft",
}

# --- LibellÃ©s localisÃ©s (extensible) ---
LABELS = {
    "fr": {
        "engine load": "Charge moteur",
        "coolant temperature": "TempÃ©rature liquide refroidissement",
        "engine rpm": "RÃ©gime moteur",
        "vehicle speed": "Vitesse du vÃ©hicule",
        "intake air temperature": "TempÃ©rature air dâ€™admission",
        "throttle position": "Position dâ€™accÃ©lÃ©rateur",
        "distance since engine start": "Distance depuis dÃ©marrage moteur",
        "distance with mil on": "Distance avec MIL allumÃ©e",
        "fuel level": "Niveau de carburant",
        "distance with mil off": "Distance avec MIL Ã©teinte",
        "vehicle speed (gps)": "Vitesse du vÃ©hicule (GPS)",
        "gps bearing": "Cap GPS",
        "gps satellites": "Satellites GPS",
        "gps altitude": "Altitude GPS",
        "gps latitude": "Latitude GPS",
        "gps accuracy": "PrÃ©cision GPS",
        "gps vs obd speed difference": "Ã‰cart vit. GPS/OBD",
        "fuel used (trip)": "Carburant utilisÃ© (trajet)",
        "gps longitude": "Longitude GPS",
        "absolute throttle position b": "Position papillon absolue B",
        "acceleration sensor (total)": "AccÃ©lÃ©romÃ¨tre (total)",
        "acceleration sensor (x axis)": "AccÃ©lÃ©romÃ¨tre (axe X)",
        "acceleration sensor (y axis)": "AccÃ©lÃ©romÃ¨tre (axe Y)",
        "acceleration sensor (z axis)": "AccÃ©lÃ©romÃ¨tre (axe Z)",
        "accelerator pedalposition d": "Pos. pÃ©dale accÃ©l. D",
        "accelerator pedalposition e": "Pos. pÃ©dale accÃ©l. E",
        "accelerator pedalposition f": "Pos. pÃ©dale accÃ©l. F",
        "air fuel ratio (commanded)": "Rapport air/carburant (ciblÃ©)",
        "air fuel ratio (measured)": "Rapport air/carburant (mesurÃ©)",
        "air status": "Ã‰tat air secondaire",
        "ambient air temp": "TempÃ©rature de lâ€™air ambiant",
        "average trip speed (whilst moving only)": "Vit. moy. traj. (mouv.)",
        "average trip speed (whilst stopped or moving)": "Vit. moy. traj. (arrÃªt+mouv.)",
        "barometer (on android device)": "BaromÃ¨tre (appareil)",
        "barometric pressure (from vehicle)": "Pression baromÃ©trique (vÃ©hicule)",
        "catalyst temperature (bank 1 sensor 1)": "Temp. catalyseur (B1 S1)",
        "catalyst temperature (bank 1 sensor 2)": "Temp. catalyseur (B1 S2)",
        "catalyst temperature (bank 2 sensor 1)": "Temp. catalyseur (B2 S1)",
        "catalyst temperature (bank 2 sensor 2)": "Temp. catalyseur (B2 S2)",
        "commanded equivalence ratio (lambda)": "Lambda commandÃ©e",
        "cost per mile/km (instant)": "CoÃ»t par km/mile (inst.)",
        "cost per mile/km (trip)": "CoÃ»t par km/mile (trajet)",
        "co2 in g/km (average)": "COâ‚‚ g/km (moy.)",
        "co2 in g/km (instantaneous)": "COâ‚‚ g/km (inst.)",
        "distance to empty (estimated)": "Autonomie (estimÃ©e)",
        "egr commanded": "EGR commandÃ©e",
        "egr error": "Erreur EGR",
        "engine kw (at the wheels)": "Puissance kW (roues)",
        "engine load (absolute)": "Charge moteur (absolue)",
        "engine oil temperature": "TempÃ©rature dâ€™huile moteur",
        "ethanol fuel %": "% Ã©thanol",
        "evap system vapour pressure": "Pression vapeur EVAP",
        "exhaust gas temperature 1": "Temp. gaz Ã©chapp. 1",
        "exhaust gas temperature 2": "Temp. gaz Ã©chapp. 2",
        "fuel cost (trip)": "CoÃ»t carburant (trajet)",
        "fuel flow rate/hour": "DÃ©bit carburant/heure",
        "fuel flow rate/minute": "DÃ©bit carburant/min",
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
        "intake manifold pressure": "Pression collecteur dâ€™admission",
        "kilometers per litre (instant)": "km/L (inst.)",
        "kilometers per litre (long term average)": "km/L (moy. LT)",
        "litres per 100 kilometer (instant)": "L/100 km (inst.)",
        "litres per 100 kilometer (long term average)": "L/100 km (moy. LT)",
        "mass air flow rate": "DÃ©bit massique dâ€™air",
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
        "relative accelerator pedal position": "Pos. pÃ©dale accÃ©l. (rel.)",
        "relative throttle position": "Position papillon (rel.)",
        "tilt (x)": "Inclinaison (x)",
        "tilt (y)": "Inclinaison (y)",
        "tilt (z)": "Inclinaison (z)",
        "timing advance": "Avance Ã  lâ€™allumage",
        "torque": "Couple",
        "transmission temperature (method 1)": "Temp. boÃ®te (M1)",
        "transmission temperature (method 2)": "Temp. boÃ®te (M2)",
        "trip average kpl": "km/L (moy. trajet)",
        "trip average litres/100 km": "L/100 km (moy. trajet)",
        "trip average mpg": "mpg (moy. trajet)",
        "trip distance": "Distance du trajet",
        "trip distance (stored in vehicle profile)": "Distance trajet (profil)",
        "trip time (since journey start)": "Temps de trajet (depuis dÃ©part)",
        "trip time (whilst moving)": "Temps de trajet (en mouvement)",
        "trip time (whilst stationary)": "Temps de trajet (Ã  lâ€™arrÃªt)",
        "turbo boost & vacuum gauge": "Boost & dÃ©pression turbo",
        "voltage (control module)": "Tension (module de contrÃ´le)",
        "voltage (obd adapter)": "Tension (adaptateur OBD)",
        "volumetric efficiency (calculated)": "Rendement volumÃ©trique (calc.)",
    }
}


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
    """Retourne le libellÃ© localisÃ©, insensible Ã  la casse."""
    loc = LABELS.get(lang)
    if not loc or not name:
        return name
    return loc.get(name, loc.get(name.casefold(), name))


class TorqueReceiveDataView(HomeAssistantView):
    """Handle data from Torque requests."""

    url = "/api/torque_logger_2025"
    name = "api:torque_logger_2025"
    requires_auth = False  # recommandÃ© pour envoi direct par Torque

    coordinator: Optional["TorqueLoggerCoordinator"]

    def __init__(self, data: dict, email: str, imperial: bool, language: str = "en"):
        """Initialize a Torque view."""
        self.data = data
        self.email = (email or "").strip()
        self.imperial = bool(imperial)
        self.lang = (language or "en").lower()
        if self.lang not in ("en", "fr"):
            self.lang = "en"
        self.coordinator = None  # injectÃ© par __init__.py

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
            # On log lâ€™erreur mais on renvoie OK pour ne pas casser lâ€™envoi cÃ´tÃ© Torque
            _LOGGER.exception("Error handling Torque payload: %s", err)
            return web.Response(text="OK!")

    def parse_fields(self, qdata):  # noqa
        """Parse les champs de la requÃªte Torque et remplit le buffer de session."""
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

        # Filtrage par email : si aucun email n'est dÃ©fini cÃ´tÃ© intÃ©gration -> accepter tout
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
        # VÃ©rifier que le PID est connu
        if TORQUE_CODES.get(key) is None:
            return None

        defaults = TORQUE_CODES[key]
        name: str = self.data[session]["fullName"].get(key, defaults.get("fullName", key))
        short_name: str = self.data[session]["shortName"].get(key, defaults.get("shortName", key))
        unit: str = self.data[session]["defaultUnit"].get(key, defaults.get("unit", ""))
        value = self.data[session]["value"].get(key)

        # Localisation du libellÃ© (insensible Ã  la casse)
        if self.lang != "en":
            name = _localize(self.lang, name)

        short_name = slugify(str(short_name))

        # Conversion en impÃ©rial si demandÃ©
        if self.imperial and unit in imperial_units and value not in (None, ""):
            try:
                conv = _pretty_convert_units(float(value), unit, imperial_units[unit])
                value = conv["value"]
                unit = conv["unit"]
            except (ValueError, TypeError):
                _LOGGER.debug("Unit conversion skipped for %s=%r %s", key, value, unit)

        return {
            "name": name,
            "short_name": short_name,
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
            # Ã‰vite d'Ã©craser un autre PID ayant le mÃªme short_name
            if short in retdata:
                short = f"{short}-{key}"

            retdata[short] = row_data["value"]
            meta[short] = {"name": row_data["name"], "unit": row_data["unit"]}

        retdata["meta"] = meta
        return retdata

    async def _async_publish_data(self, session: str):
        # --- GARDE ANTI-STALE : ignorer si l'entrÃ©e n'est pas chargÃ©e ---
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

        # Ne publie pas tant qu'on n'a pas le nom du vÃ©hicule
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

        # MÃ©morise par voiture et notifie les entitÃ©s
        self.coordinator.update_from_session(session_data)
        await self.coordinator.add_entities(session_data)

