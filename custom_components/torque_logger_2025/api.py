# -*- coding: utf-8 -*-
"""Torque Logger API Client/DataView."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import logging

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.util import slugify
from homeassistant.config_entries import ConfigEntryState

# --- pint est optionnel : on ne casse pas l'intégration s'il n'est pas installé
try:
    import pint  # type: ignore
    ureg = pint.UnitRegistry()
except Exception:  # pragma: no cover
    pint = None
    ureg = None

from .const import TORQUE_CODES

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

# --- Conversion d’unités ---
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
    """Convertit via pint si dispo, sinon renvoie la valeur et l'unité d'entrée (pas de conversion)."""
    if ureg is None:
        # Pas de pint -> on ne convertit pas
        return {"value": round(float(value), 2), "unit": u_in}
    q_in = ureg.Quantity(value, u_in)
    q_out = q_in.to(u_out)
    return {"value": round(q_out.magnitude, 2), "unit": str(q_out.units)}


def _pretty_convert_units(value: float, u_in: str, u_out: str):
    """Convertit et renvoie une unité 'jolie' ; si pint absent -> pas de conversion."""
    p_in = _unpretty_units(u_in)
    p_out = _unpretty_units(u_out)
    res = _convert_units(value, p_in, p_out)
    return {"value": res["value"], "unit": _pretty_units(res["unit"])}


def _normalize_unit(unit: Optional[str]) -> str:
    """Corrige les encodages foireux (°, etc.) et trim."""
    if not unit:
        return ""
    return unit.replace("°", "°").replace("", "").strip()


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

            # Override temporaire via URL ?lang=fr
            lang_param = (request.query.get("lang") or request.query.get("language") or "").lower()
            if lang_param in ("en", "fr"):
                self.lang = lang_param

            session = self.parse_fields(request.query)
            if session:
                await self._async_publish_data(session)

            return web.Response(text="OK!")
        except Exception as err:  # pragma: no cover
            # Log l’erreur mais renvoie OK pour ne pas casser l’envoi côté Torque
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
        name: str = self.data[session]["fullName"].get(key, defaults.get("fullName", key))
        short_name: str = self.data[session]["shortName"].get(key, defaults.get("shortName", key))
        unit: str = self.data[session]["defaultUnit"].get(key, defaults.get("unit", ""))
        value = self.data[session]["value"].get(key)

        # Localisation du libellé (insensible à la casse)
        if self.lang != "en":
            name = _localize(self.lang, name)

        short_name = slugify(str(short_name))

        # Normaliser / trimmer l’unité
        unit = _normalize_unit(unit)

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
            # Évite d'écraser un autre PID ayant le même short_name
            if short in retdata:
                short = f"{short}-{key}"

            retdata[short] = row_data["value"]
            meta[short] = {"name": row_data["name"], "unit": row_data["unit"]}

        retdata["meta"] = meta
        return retdata

    async def _async_publish_data(self, session: str):
        """Valide l’état d’installation, reconstruit un Name si absent, puis pousse vers le coordinator."""
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
        profile = session_data["profile"]

        # Si le nom de véhicule manque, on le reconstruit (id/email/session) plutôt que de jeter la trame
        if not profile.get("Name"):
            current_id = profile.get("id")

            # Tente de récupérer un Name d’une autre session avec le même id
            if current_id:
                other_sessions = [
                    self.data[key]
                    for key in self.data.keys()
                    if self.data[key]["profile"].get("id") == current_id
                    and self.data[key]["profile"].get("Name")
                ]
                if other_sessions:
                    profile["Name"] = other_sessions[0]["profile"]["Name"]

            # Fallback si toujours rien
            if not profile.get("Name"):
                fallback = current_id or profile.get("email") or session or "vehicle"
                profile["Name"] = str(fallback)
                _LOGGER.debug("No profile Name; using fallback=%r", profile["Name"])

        # Mémorise par voiture et notifie les entités
        self.coordinator.update_from_session(session_data)
        await self.coordinator.add_entities(session_data)
