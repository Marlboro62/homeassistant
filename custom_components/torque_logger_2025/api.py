# -*- coding: utf-8 -*-
"""Torque Logger 2025 API Client/DataView."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import logging

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.util import slugify
from homeassistant.config_entries import ConfigEntryState

# --- pint optionnel : ne bloque pas l'intégration s'il est absent
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
imperial_units = {
    "km": "mile",
    "m": "foot",
    "km/h": "mile / hour",
    "m/s": "mile / hour",
    "°C": "degF",
    "kPa": "psi",
    "bar": "psi",
    "l": "gallon",
    "l/hr": "gallon / hour",
    "l/min": "gallon / minute",
    "cc/min": "cubic_inch / minute",
    "g/s": "pound / second",
    "Nm": "pound_force * foot",
    "kW": "horsepower",
    "g/km": "gram / mile",
    "kpl": "mile / gallon",
    "l/100km": "mile / gallon",
}
prettyPint = {
    "degC": "°C",
    "degree_Celsius": "°C",
    "degF": "°F",
    "degree_Fahrenheit": "°F",
    "kilometer / hour": "km/h",
    "kilometre / hour": "km/h",
    "mile / hour": "mph",
    "meter / second": "m/s",
    "metre / second": "m/s",
    "kilometer": "km",
    "kilometre": "km",
    "meter": "m",
    "metre": "m",
    "mile": "mi",
    "foot": "ft",
    "newton * meter": "Nm",
    "pound_force * foot": "ft·lb",
    "kilopascal": "kPa",
    "pascal": "Pa",
    "bar": "bar",
    "psi": "psi",
    "liter": "L",
    "litre": "L",
    "liter / hour": "L/h",
    "liter / minute": "L/min",
    "gallon": "gal",
    "gallon / hour": "gph",
    "gallon / minute": "gpm",
    "cubic_centimeter / minute": "cc/min",
    "cubic_inch / minute": "in³/min",
    "gram / second": "g/s",
    "watt": "W",
    "kilowatt": "kW",
    "horsepower": "hp",
    "mile / gallon": "mpg",
}

# Canonicalisation -> formes attendues par Pint
_PINT_CANON = {
    "km": "kilometer",
    "m": "meter",
    "km/h": "kilometer / hour",
    "m/s": "meter / second",
    "°C": "degC",
    "°F": "degF",
    "kPa": "kilopascal",
    "Pa": "pascal",
    "bar": "bar",
    "psi": "psi",
    "l": "liter",
    "L": "liter",
    "l/hr": "liter / hour",
    "L/h": "liter / hour",
    "l/min": "liter / minute",
    "L/min": "liter / minute",
    "cc/min": "cubic_centimeter / minute",
    "g/s": "gram / second",
    "Nm": "newton * meter",
    "ft·lb": "pound_force * foot",
    "kW": "kilowatt",
    "W": "watt",
    "g/km": "gram / kilometer",
    "kpl": "kilometer / liter",
    "l/100km": "liter / 100 kilometer",
}
def _to_pint(unit: str) -> str:
    if not unit:
        return ""
    unit = unit.strip()
    # si 'unit' est déjà une forme "jolie", on la mappe vers la clé Pint correspondante
    for pint_unit, pretty_unit in prettyPint.items():
        if pretty_unit == unit:
            return pint_unit
    return _PINT_CANON.get(unit, unit)

# --- Libellés localisés (extensible) ---
LABELS = {
    "fr": {
        "engine load": "Charge moteur",
        "engine coolant temperature": "T LdR",
        "fuel trim bank 1 short term": "Fuel Trim Bank 1 Short Term",
        "fuel trim bank 1 long term": "Fuel Trim Bank 1 Long Term",
        "fuel trim bank 2 short term": "Fuel Trim Bank 2 Short Term",
        "fuel trim bank 2 long term": "Fuel Trim Bank 2 Long Term",
        "fuel pressure": "P carburant",
        "intake manifold pressure": "P adm.",
        "engine rpm": "Régime",
        "speed (obd)": "Vit. OBD",
        "timing advance": "Avance allumage",
        "intake air temperature": "T air adm.",
        "mass air flow rate": "Débit air (MAF)",
        "throttle position (manifold)": "Papillon (adm.)",
        "fuel trim {o2l:1}": "Fuel trim {O2L:1}",
        "fuel trim {o2l:2}": "Fuel trim {O2L:2}",
        "fuel trim {o2l:3}": "Fuel trim {O2L:3}",
        "fuel trim {o2l:4}": "Fuel trim {O2L:4}",
        "fuel trim {o2l:5}": "Fuel trim {O2L:5}",
        "fuel trim {o2l:6}": "Fuel trim {O2L:6}",
        "fuel trim {o2l:7}": "Fuel trim {O2L:7}",
        "fuel trim {o2l:8}": "Fuel trim {O2L:8}",
        "run time since engine start": "Temps depuis dém.",
        "distance travelled with mil/cel lit": "Dist. MIL allumée",
        "fuel rail pressure (relative to manifold vacuum)": "P rampe (rel. vide)",
        "fuel rail pressure": "P rampe",
        "o2 {o2l:1} wide range voltage": "O2 L1 U O2 LB",
        "o2 {o2l:2} wide range voltage": "O2 L2 U O2 LB",
        "o2 {o2l:3} wide range voltage": "O2 L3 U O2 LB",
        "o2 {o2l:4} wide range voltage": "O2 L4 U O2 LB",
        "o2 {o2l:5} wide range voltage": "O2 L5 U O2 LB",
        "o2 {o2l:6} wide range voltage": "O2 L6 U O2 LB",
        "o2 {o2l:7} wide range voltage": "O2 L7 U O2 LB",
        "o2 {o2l:8} wide range voltage": "O2 L8 U O2 LB",
        "egr commanded": "EGR cmd.",
        "egr error": "Erreur EGR",
        "fuel level (from engine ecu)": "Fuel Level (From Engine ECU)",
        "distance travelled since codes cleared": "Dist. depuis effacement",
        "evap system vapour pressure": "Evap System Vapour Pressure",
        "barometric pressure (from vehicle)": "Baro (véh.)",
        "o2 {o2l:1} wide range current": "O2 L1 I O2 LB",
        "o2 {o2l:2} wide range current": "O2 L2 I O2 LB",
        "o2 {o2l:3} wide range current": "O2 L3 I O2 LB",
        "o2 {o2l:4} wide range current": "O2 L4 I O2 LB",
        "o2 {o2l:5} wide range current": "O2 L5 I O2 LB",
        "o2 {o2l:6} wide range current": "O2 L6 I O2 LB",
        "o2 {o2l:7} wide range current": "O2 L7 I O2 LB",
        "o2 {o2l:8} wide range current": "O2 L8 I O2 LB",
        "catalyst temperature (bank 1,sensor 1)": "T cata B1 S1",
        "catalyst temperature (bank 2,sensor 1)": "T cata B2 S1",
        "catalyst temperature (bank 1,sensor 2)": "T cata B1 S2",
        "catalyst temperature (bank 2,sensor 2)": "T cata B2 S2",
        "voltage (control module)": "U module",
        "engine load(absolute)": "Charge (abs.)",
        "commanded equivalence ratio (lambda)": "Commanded Lambda (lambda)",
        "relative throttle position": "Papillon (rel.)",
        "ambient air temp": "T air amb.",
        "absolute throttle position b": "Papillon abs. B",
        "accelerator pedalposition d": "Pédale D",
        "accelerator pedalposition e": "Pédale E",
        "accelerator pedalposition f": "Pédale F",
        "ethanol fuel %": "% éthanol",
        "relative accelerator pedal position": "Pédale (rel.)",
        "hybrid battery charge (%)": "SOC batt. HV",
        "engine oil temperature": "T huile mot.",
        "fuel rate (direct from ecu)": "Débit carb. (ECU)",
        "drivers demand engine % torque": "% couple demandé",
        "actual engine % torque": "% couple effectif",
        "engine reference torque": "Couple réf. moteur",
        "mass air flow sensor a": "Débit air A",
        "boost pressure commanded a": "Boost cmd. A",
        "exhaust pressure bank 1": "P éch. B1",
        "charge air cooler temperature (cact)": "T CACT",
        "exhaust gas temp bank 1 sensor 1": "T éch. B1 S1",
        "exhaust gas temp bank 2 sensor 1": "T éch. B2 S1",
        "dpf bank 1 delta pressure": "ΔP FAP B1",
        "dpf bank 2 delta pressure": "ΔP FAP B2",
        "dpf bank 1 inlet temperature": "T FAP B1 entrée",
        "nox pre scr": "NOx pré SCR",
        "intake manifold abs pressure a": "P abs. adm. A",
        "hybrid/ev system battery voltage": "U batt. HV",
        "odometer(from ecu)": "Odomètre ECU",
        "hybrid/ev battery state of health": "SOH batt. HV",
        "transmission temperature(method 2)": "Transmission Temperature(Method 2)",
        "vehicle speed (gps)": "Vit. GPS",
        "gps longitude": "Lon. GPS",
        "gps latitude": "Lat. GPS",
        "gps altitude": "Alt. GPS",
        "miles per gallon(instant)": "Inst. mpg",
        "turbo boost & vacuum gauge": "Boost & dépr.",
        "kilometers per litre(instant)": "Inst. km/L",
        "trip distance": "Dist. trajet",
        "trip average mpg": "Moy. traj. mpg",
        "trip average kpl": "Moy. traj. km/L",
        "litres per 100 kilometer(instant)": "Inst. L/100",
        "trip average litres/100 km": "Moy. traj. L/100",
        "trip distance (stored in vehicle profile)": "Trip distance (stored in vehicle profile)",
        "o2 {o2l:1} voltage": "O2 L1 Voltage",
        "o2 {o2l:2} voltage": "O2 L2 Voltage",
        "o2 {o2l:3} voltage": "O2 L3 Voltage",
        "o2 {o2l:4} voltage": "O2 L4 Voltage",
        "o2 {o2l:5} voltage": "O2 L5 Voltage",
        "o2 {o2l:6} voltage": "O2 L6 Voltage",
        "o2 {o2l:7} voltage": "O2 L7 Voltage",
        "o2 {o2l:8} voltage": "O2 L8 Voltage",
        "acceleration sensor(x axis)": "Acceleration Sensor(X axis)",
        "acceleration sensor(y axis)": "Acceleration Sensor(Y axis)",
        "acceleration sensor(z axis)": "Acceleration Sensor(Z axis)",
        "acceleration sensor(total)": "Acceleration Sensor(Total)",
        "torque": "Couple",
        "horsepower (at the wheels)": "HP (roues)",
        "0-60mph time": "0→60 mph",
        "0-100kph time": "0→100 km/h",
        "1/4 mile time": "1/4 mile (t)",
        "1/8 mile time": "1/8 mile (t)",
        "gps vs obd speed difference": "Écart vit. GPS/OBD",
        "voltage (obd adapter)": "U OBD",
        "gps accuracy": "Préc. GPS",
        "gps satellites": "Sat. GPS",
        "gps bearing": "Cap GPS",
        "o2 {o2l:1} wide range equivalence ratio": "O2 L1 Lambda LB",
        "o2 {o2l:2} wide range equivalence ratio": "O2 L2 Lambda LB",
        "o2 {o2l:3} wide range equivalence ratio": "O2 L3 Lambda LB",
        "o2 {o2l:4} wide range equivalence ratio": "O2 L4 Lambda LB",
        "o2 {o2l:5} wide range equivalence ratio": "O2 L5 Lambda LB",
        "o2 {o2l:6} wide range equivalence ratio": "O2 L6 Lambda LB",
        "o2 {o2l:7} wide range equivalence ratio": "O2 L7 Lambda LB",
        "o2 {o2l:8} wide range equivalence ratio": "O2 L8 Lambda LB",
        "air fuel ratio(measured)": "Air Fuel Ratio(Measured)",
        "air fuel ratio(commanded)": "Air Fuel Ratio(Commanded)",
        "0-200kph time": "0→200 km/h",
        "co\u2082 in g/km (instantaneous)": "CO₂ inst.",
        "co\u2082 in g/km (average)": "CO₂ moy.",
        "fuel flow rate/minute": "Fuel flow rate/minute",
        "fuel cost (trip)": "Fuel cost (trip)",
        "fuel flow rate/hour": "Fuel flow rate/hour",
        "60-120mph time": "60-120mph Time",
        "60-80mph time": "60-80mph Time",
        "40-60mph time": "40-60mph Time",
        "80-100mph time": "80-100mph Time",
        "average trip speed(whilst moving only)": "Vit. moy. (mouv.)",
        "100-0kph time": "100→0 km/h",
        "60-0mph time": "60-0mph Time",
        "trip time(since journey start)": "Temps (depuis départ)",
        "trip time(whilst stationary)": "Temps (arrêt)",
        "trip time(whilst moving)": "Temps (mouv.)",
        "volumetric efficiency (calculated)": "Rdt. volumétrique",
        "distance to empty (estimated)": "Autonomie (estim.)",
        "fuel remaining (calculated from vehicle profile)": "Carburant restant (profil)",
        "cost per mile/km (instant)": "Cost per mile/km (Instant)",
        "cost per mile/km (trip)": "Cost per mile/km (Trip)",
        "barometer (on android device)": "Baro (appareil)",
        "fuel used (trip)": "Carburant (trajet)",
        "average trip speed(whilst stopped or moving)": "Vit. moy. (tot.)",
        "engine kw (at the wheels)": "kW (roues)",
        "80-120kph time": "80-120kph Time",
        "60-130mph time": "60-130mph Time",
        "0-30mph time": "0→30 mph",
        "0-100mph time": "0→100 mph",
        "100-200kph time": "100-200kph Time",
        "exhaust gas temp bank 1 sensor 2": "T éch. B1 S2",
        "exhaust gas temp bank 1 sensor 3": "T éch. B1 S3",
        "exhaust gas temp bank 1 sensor 4": "T éch. B1 S4",
        "exhaust gas temp bank 2 sensor 2": "T éch. B2 S2",
        "exhaust gas temp bank 2 sensor 3": "T éch. B2 S3",
        "exhaust gas temp bank 2 sensor 4": "T éch. B2 S4",
        "nox post scr": "NOx post SCR",
        "percentage of city driving": "Percentage of City driving",
        "percentage of highway driving": "Percentage of Highway driving",
        "percentage of idle driving": "Percentage of Idle driving",
        "android device battery level": "Batt. Android",
        "dpf bank 1 outlet temperature": "T FAP B1 sortie",
        "dpf bank 2 inlet temperature": "T FAP B2 entrée",
        "dpf bank 2 outlet temperature": "T FAP B2 sortie",
        "mass air flow sensor b": "Débit air B",
        "intake manifold abs pressure b": "P abs. adm. B",
        "boost pressure commanded b": "Boost cmd. B",
        "boost pressure sensor a": "Boost capteur A",
        "boost pressure sensor b": "Boost capteur B",
        "exhaust pressure bank 2": "P éch. B2",
        "dpf bank 1 inlet pressure": "P FAP B1 entrée",
        "dpf bank 1 outlet pressure": "P FAP B1 sortie",
        "dpf bank 2 inlet pressure": "P FAP B2 entrée",
        "dpf bank 2 outlet pressure": "P FAP B2 sortie",
        "hybrid/ev system battery current": "I batt. HV",
        "hybrid/ev system battery power": "P batt. HV",
        "positive kinetic energy (pke)": "PKE",
        "miles per gallon(long term average)": "mpg (moy. LT)",
        "kilometers per litre(long term average)": "km/L (moy. LT)",
        "litres per 100 kilometer(long term average)": "L/100 (moy. LT)",
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
    """Convertit via pint si dispo, sinon renvoie la valeur et l'unité d'entrée."""
    if ureg is None:
        return {"value": round(float(value), 2), "unit": u_in}
    try:
        q_in = ureg.Quantity(value, _to_pint(u_in))
        q_out = q_in.to(_to_pint(u_out))
        return {"value": round(q_out.magnitude, 2), "unit": str(q_out.units)}
    except Exception:  # pragma: no cover
        return {"value": round(float(value), 2), "unit": u_in}


def _pretty_convert_units(value: float, u_in: str, u_out: str):
    """Convertit et renvoie une unité 'jolie' ; si pint absent -> pas de conversion."""
    res = _convert_units(value, u_in, u_out)
    return {"value": res["value"], "unit": _pretty_units(res["unit"])}


def _normalize_unit(unit: Optional[str]) -> str:
    """Corrige les encodages foireux (Â°, etc.) et trim."""
    if not unit:
        return ""
    # retire les 'Â' parasites et normalise le symbole degré
    return unit.replace("Â°", "°").replace("Â", "").strip()


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
        short_in = self.data[session]["shortName"].get(key, defaults.get("shortName", ""))
        unit: str = self.data[session]["defaultUnit"].get(key, defaults.get("unit", ""))
        value = self.data[session]["value"].get(key)

        # Localisation du libellé (insensible à la casse)
        if self.lang != "en":
            name = _localize(self.lang, name)

        # Slug court et sûr
        short_slug = slugify(str(short_in)) if short_in else ""
        if not short_slug or short_slug in ("none", "-"):
            # fallback sur le nom localisé ou, à défaut, PID
            short_slug = slugify(str(name)) or f"pid_{key}"

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
            "short_name": short_slug,
            "unit": unit,
            "value": value,
        }

    def _get_profile(self, session: str):
        return self.data[session]["profile"]

    def _get_data(self, session: str):
        retdata = {"profile": self._get_profile(session), "time": self.data[session]["time"]}
        meta = {}

        for key in list(self.data[session]["value"].keys()):
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
        # --- GARDE ANTI-STALE ---
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
        # -------------------------

        session_data = self._get_data(session)
        profile = session_data["profile"]

        # Si le nom de véhicule manque, on reconstruit (id/email/session)
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
