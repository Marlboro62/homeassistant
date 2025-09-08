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
        "engine coolant temperature": "Température liquide refroidissement",
        "fuel trim bank 1 short term": "Fuel Trim B1 Short Term",
        "fuel trim bank 1 long term": "Fuel Trim B1 Long Term",
        "fuel trim bank 2 short term": "Fuel Trim B2 Short Term",
        "fuel trim bank 2 long term": "Fuel Trim B2 Long Term",
        "fuel pressure": "Pression carburant",
        "intake manifold pressure": "Pression collecteur d’admission",
        "engine rpm": "Régime moteur",
        "speed (obd)": "Vitesse (OBD)",
        "timing advance": "Avance à l’allumage",
        "intake air temperature": "Température air d’admission",
        "mass air flow rate": "Débit massique d’air",
        "throttle position (manifold)": "Position d’accélérateur",
        "fuel trim {o2l:1}": "Fuel trim {O2L:1}",
        "fuel trim {o2l:2}": "Fuel trim {O2L:2}",
        "fuel trim {o2l:3}": "Fuel trim {O2L:3}",
        "fuel trim {o2l:4}": "Fuel trim {O2L:4}",
        "fuel trim {o2l:5}": "Fuel trim {O2L:5}",
        "fuel trim {o2l:6}": "Fuel trim {O2L:6}",
        "fuel trim {o2l:7}": "Fuel trim {O2L:7}",
        "fuel trim {o2l:8}": "Fuel trim {O2L:8}",
        "run time since engine start": "Temps depuis démarrage moteur",
        "distance travelled with mil/cel lit": "Distance avec MIL allumée",
        "fuel rail pressure (relative to manifold vacuum)": "Pression rampe (rel. au vide)",
        "fuel rail pressure": "Pression rampe",
        "o2 {o2l:1} wide range voltage": "Tension large bande O2 {O2L:1}",
        "o2 {o2l:2} wide range voltage": "Tension large bande O2 {O2L:2}",
        "o2 {o2l:3} wide range voltage": "Tension large bande O2 {O2L:3}",
        "o2 {o2l:4} wide range voltage": "Tension large bande O2 {O2L:4}",
        "o2 {o2l:5} wide range voltage": "Tension large bande O2 {O2L:5}",
        "o2 {o2l:6} wide range voltage": "Tension large bande O2 {O2L:6}",
        "o2 {o2l:7} wide range voltage": "Tension large bande O2 {O2L:7}",
        "o2 {o2l:8} wide range voltage": "Tension large bande O2 {O2L:8}",
        "egr commanded": "EGR commandée",
        "egr error": "Erreur EGR",
        "fuel level (from engine ecu)": "Fuel Level (From Moteur ECU)",
        "distance travelled since codes cleared": "Distance depuis effacement défauts",
        "evap system vapour pressure": "Evap System Vapour pression",
        "barometric pressure (from vehicle)": "Pression barométrique (véhicule)",
        "o2 {o2l:1} wide range current": "Courant large bande O2 {O2L:1}",
        "o2 {o2l:2} wide range current": "Courant large bande O2 {O2L:2}",
        "o2 {o2l:3} wide range current": "Courant large bande O2 {O2L:3}",
        "o2 {o2l:4} wide range current": "Courant large bande O2 {O2L:4}",
        "o2 {o2l:5} wide range current": "Courant large bande O2 {O2L:5}",
        "o2 {o2l:6} wide range current": "Courant large bande O2 {O2L:6}",
        "o2 {o2l:7} wide range current": "Courant large bande O2 {O2L:7}",
        "o2 {o2l:8} wide range current": "Courant large bande O2 {O2L:8}",
        "catalyst temperature (bank 1,sensor 1)": "Temp. catalyseur (B1 S1)",
        "catalyst temperature (bank 2,sensor 1)": "Temp. catalyseur (B2 S1)",
        "catalyst temperature (bank 1,sensor 2)": "Temp. catalyseur (B1 S2)",
        "catalyst temperature (bank 2,sensor 2)": "Temp. catalyseur (B2 S2)",
        "voltage (control module)": "Tension (module de contrôle)",
        "engine load(absolute)": "Charge moteur (absolue)",
        "commanded equivalence ratio (lambda)": "(ciblé) Equivalence Ratio (lambda)",
        "relative throttle position": "Position papillon (rel.)",
        "ambient air temp": "Température de l’air ambiant",
        "absolute throttle position b": "Position papillon absolue B",
        "accelerator pedalposition d": "Pos. pédale accél. D",
        "accelerator pedalposition e": "Pos. pédale accél. E",
        "accelerator pedalposition f": "Pos. pédale accél. F",
        "ethanol fuel %": "% éthanol",
        "relative accelerator pedal position": "Pos. pédale accél. (rel.)",
        "hybrid battery charge (%)": "Charge batterie hybride",
        "engine oil temperature": "Température d’huile moteur",
        "fuel rate (direct from ecu)": "Débit carburant (ECU)",
        "drivers demand engine % torque": "% couple demandé conducteur",
        "actual engine % torque": "% couple effectif moteur",
        "engine reference torque": "Couple de référence moteur",
        "mass air flow sensor a": "Débitmètre A",
        "boost pressure commanded a": "Pression boost commandée A",
        "exhaust pressure bank 1": "Pression échappement B1",
        "charge air cooler temperature (cact)": "Temp. refroidisseur d’air de suralimentation (CACT)",
        "exhaust gas temp bank 1 sensor 1": "Temp. gaz échapp. B1 S1",
        "exhaust gas temp bank 2 sensor 1": "Temp. gaz échapp. B2 S1",
        "dpf bank 1 delta pressure": "Pression delta FAP B1",
        "dpf bank 2 delta pressure": "Pression delta FAP B2",
        "dpf bank 1 inlet temperature": "Temp. FAP B1 entrée",
        "nox pre scr": "NOx avant SCR",
        "intake manifold abs pressure a": "Pression abs. collecteur A",
        "hybrid/ev system battery voltage": "Tension batterie hybride/EV",
        "odometer(from ecu)": "Odomètre (ECU)",
        "hybrid/ev battery state of health": "État de santé batterie hybride/EV",
        "transmission temperature(method 2)": "Transmission température(Method 2)",
        "vehicle speed (gps)": "Vitesse du véhicule (GPS)",
        "gps longitude": "Longitude GPS",
        "gps latitude": "Latitude GPS",
        "gps altitude": "Altitude GPS",
        "miles per gallon(instant)": "mpg (inst.)",
        "turbo boost & vacuum gauge": "Boost & dépression turbo",
        "kilometers per litre(instant)": "km/L (inst.)",
        "trip distance": "Distance du trajet",
        "trip average mpg": "mpg (moy. trajet)",
        "trip average kpl": "km/L (moy. trajet)",
        "litres per 100 kilometer(instant)": "L/100 km (inst.)",
        "trip average litres/100 km": "L/100 km (moy. trajet)",
        "trip distance (stored in vehicle profile)": "Trip distance (stored in vehicle profile)",
        "o2 {o2l:1} voltage": "Tension O2 {O2L:1}",
        "o2 {o2l:2} voltage": "Tension O2 {O2L:2}",
        "o2 {o2l:3} voltage": "Tension O2 {O2L:3}",
        "o2 {o2l:4} voltage": "Tension O2 {O2L:4}",
        "o2 {o2l:5} voltage": "Tension O2 {O2L:5}",
        "o2 {o2l:6} voltage": "Tension O2 {O2L:6}",
        "o2 {o2l:7} voltage": "Tension O2 {O2L:7}",
        "o2 {o2l:8} voltage": "Tension O2 {O2L:8}",
        "acceleration sensor(x axis)": "Acceleration Sensor(X axis)",
        "acceleration sensor(y axis)": "Acceleration Sensor(Y axis)",
        "acceleration sensor(z axis)": "Acceleration Sensor(Z axis)",
        "acceleration sensor(total)": "Acceleration Sensor(Total)",
        "torque": "Couple",
        "horsepower (at the wheels)": "Puissance (roues)",
        "0-60mph time": "0-60 mph (temps)",
        "0-100kph time": "0-100kph Time",
        "1/4 mile time": "1/4 mile (temps)",
        "1/8 mile time": "1/8 mile (temps)",
        "gps vs obd speed difference": "Écart vit. GPS/OBD",
        "voltage (obd adapter)": "Tension (adaptateur OBD)",
        "gps accuracy": "Précision GPS",
        "gps satellites": "Satellites GPS",
        "gps bearing": "Cap GPS",
        "o2 {o2l:1} wide range equivalence ratio": "Lambda large bande O2 {O2L:1}",
        "o2 {o2l:2} wide range equivalence ratio": "Lambda large bande O2 {O2L:2}",
        "o2 {o2l:3} wide range equivalence ratio": "Lambda large bande O2 {O2L:3}",
        "o2 {o2l:4} wide range equivalence ratio": "Lambda large bande O2 {O2L:4}",
        "o2 {o2l:5} wide range equivalence ratio": "Lambda large bande O2 {O2L:5}",
        "o2 {o2l:6} wide range equivalence ratio": "Lambda large bande O2 {O2L:6}",
        "o2 {o2l:7} wide range equivalence ratio": "Lambda large bande O2 {O2L:7}",
        "o2 {o2l:8} wide range equivalence ratio": "Lambda large bande O2 {O2L:8}",
        "air fuel ratio(measured)": "Rapport air/carburant (mesuré)",
        "air fuel ratio(commanded)": "Rapport air/carburant (ciblé)",
        "0-200kph time": "0-200 km/h (temps)",
        "co\u2082 in g/km (instantaneous)": "CO₂ g/km (inst.)",
        "co\u2082 in g/km (average)": "CO₂ g/km (moy.)",
        "fuel flow rate/minute": "Débit carburant/minute",
        "fuel cost (trip)": "Fuel cost (trip)",
        "fuel flow rate/hour": "Débit carburant/heure",
        "60-120mph time": "60-120 mph (temps)",
        "60-80mph time": "60-80 mph (temps)",
        "40-60mph time": "40-60 mph (temps)",
        "80-100mph time": "80-100 mph (temps)",
        "average trip speed(whilst moving only)": "Vit. moy. traj. (mouv.)",
        "100-0kph time": "100-0 km/h (temps)",
        "60-0mph time": "60-0mph Time",
        "trip time(since journey start)": "Temps de trajet (depuis départ)",
        "trip time(whilst stationary)": "Temps de trajet (à l’arrêt)",
        "trip time(whilst moving)": "Temps de trajet (en mouvement)",
        "volumetric efficiency (calculated)": "Rendement volumétrique (calc.)",
        "distance to empty (estimated)": "Autonomie (estimée)",
        "fuel remaining (calculated from vehicle profile)": "Carburant restant (profil)",
        "cost per mile/km (instant)": "Cost per mile/km (Instant)",
        "cost per mile/km (trip)": "Cost per mile/km (Trip)",
        "barometer (on android device)": "Baromètre (appareil)",
        "fuel used (trip)": "Carburant utilisé (trajet)",
        "average trip speed(whilst stopped or moving)": "Vit. moy. traj. (arrêt+mouv.)",
        "engine kw (at the wheels)": "Puissance kW (roues)",
        "80-120kph time": "80-120 km/h (temps)",
        "60-130mph time": "60-130 mph (temps)",
        "0-30mph time": "0-30mph Time",
        "0-100mph time": "0-100 mph (temps)",
        "100-200kph time": "100-200kph Time",
        "exhaust gas temp bank 1 sensor 2": "Temp. gaz échapp. B1 S2",
        "exhaust gas temp bank 1 sensor 3": "Temp. gaz échapp. B1 S3",
        "exhaust gas temp bank 1 sensor 4": "Temp. gaz échapp. B1 S4",
        "exhaust gas temp bank 2 sensor 2": "Temp. gaz échapp. B2 S2",
        "exhaust gas temp bank 2 sensor 3": "Temp. gaz échapp. B2 S3",
        "exhaust gas temp bank 2 sensor 4": "Temp. gaz échapp. B2 S4",
        "nox post scr": "NOx après SCR",
        "percentage of city driving": "Pourcentage conduite urbaine",
        "percentage of highway driving": "Pourcentage conduite autoroute",
        "percentage of idle driving": "Pourcentage ralenti",
        "android device battery level": "Batterie appareil Android",
        "dpf bank 1 outlet temperature": "Temp. FAP B1 sortie",
        "dpf bank 2 inlet temperature": "Temp. FAP B2 entrée",
        "dpf bank 2 outlet temperature": "Temp. FAP B2 sortie",
        "mass air flow sensor b": "Débitmètre B",
        "intake manifold abs pressure b": "Pression abs. collecteur B",
        "boost pressure commanded b": "Pression boost commandée B",
        "boost pressure sensor a": "Capteur pression boost A",
        "boost pressure sensor b": "Capteur pression boost B",
        "exhaust pressure bank 2": "Pression échappement B2",
        "dpf bank 1 inlet pressure": "Pression FAP B1 entrée",
        "dpf bank 1 outlet pressure": "Pression FAP B1 sortie",
        "dpf bank 2 inlet pressure": "Pression FAP B2 entrée",
        "dpf bank 2 outlet pressure": "Pression FAP B2 sortie",
        "hybrid/ev system battery current": "Courant batterie hybride/EV",
        "hybrid/ev system battery power": "Puissance batterie hybride/EV",
        "positive kinetic energy (pke)": "Énergie cinétique positive (PKE)",
        "miles per gallon(long term average)": "mpg (moy. LT)",
        "kilometers per litre(long term average)": "km/L (moy. LT)",
        "litres per 100 kilometer(long term average)": "L/100 km (moy. LT)",
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
