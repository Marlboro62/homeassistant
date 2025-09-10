# -*- coding: utf-8 -*-
"""Constants for Torque Logger 2025"""
from __future__ import annotations

# Base component constants
from typing import Final
import json
import os

NAME: Final = "Torque Logger 2025"
DOMAIN: Final = "torque_logger_2025"

# Lecture sécurisée de la version depuis manifest.json
_manifest = os.path.join(os.path.dirname(__file__), "manifest.json")
try:
    with open(_manifest, encoding="utf-8") as file:
        VERSION: Final = json.load(file).get("version", "0.0.0")
except Exception:
    VERSION: Final = "0.0.0"

ATTRIBUTION: Final = "Torque Pro 2025"
ISSUE_URL: Final = "https://github.com/Marlboro62/homeassistant/issues"

# CONF
CONF_EMAIL: Final = "email"
CONF_IMPERIAL: Final = "imperial"
# Langue (défaut FR)
CONF_LANGUAGE: Final = "language"
DEFAULT_LANGUAGE: Final = "fr"
SUPPORTED_LANGS: Final = {"en": "English", "fr": "Français"}

# Platforms
DEVICE_TRACKER: Final = "device_tracker"
SENSOR: Final = "sensor"
PLATFORMS: Final = [SENSOR, DEVICE_TRACKER]

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# DEFAULTs (icônes)
DEFAULT_ICON: Final = "mdi:engine"
GPS_ICON: Final = "mdi:car"
DISTANCE_ICON: Final = "mdi:map-marker-distance"
HIGHWAY_ICON: Final = "mdi:highway"
FUEL_ICON: Final = "mdi:gas-station"
TIME_ICON: Final = "mdi:clock"
CITY_ICON: Final = "mdi:city"
SPEED_ICON: Final = "mdi:speedometer"

# ATTR
ATTR_ALTITUDE: Final = "altitude"
ATTR_SPEED: Final = "speed"
ATTR_GPS_TIME: Final = "gps_time"

ENTITY_GPS: Final = "gps"

TORQUE_GPS_LAT: Final = "gpslat"
TORQUE_GPS_LON: Final = "gpslon"
TORQUE_GPS_ALTITUDE: Final = "gps_height"
TORQUE_GPS_ACCURACY: Final = "gps_acc"

# Webhook codes
TORQUE_CODES: Final = {
  "04": {
    "shortName": "engine_load",
    "fullName": "Engine Load",
    "unit": "%"
  },
  "05": {
    "shortName": "coolant_temp",
    "fullName": "Coolant Temperature",
    "unit": "°C"
  },
  "0c": {
    "shortName": "engine_rpm",
    "fullName": "Engine RPM",
    "unit": "rpm"
  },
  "0d": {
    "shortName": "speed",
    "fullName": "Vehicle Speed",
    "unit": "km/h"
  },
  "0f": {
    "shortName": "intake_temp",
    "fullName": "Intake Air Temperature",
    "unit": "°C"
  },
  "11": {
    "shortName": "throttle_pos",
    "fullName": "Throttle Position",
    "unit": "%"
  },
  "1f": {
    "shortName": "run_since_start",
    "fullName": "Distance Since Engine Start",
    "unit": "km"
  },
  "21": {
    "shortName": "dis_mil_on",
    "fullName": "Distance with MIL on",
    "unit": "km"
  },
  "2f": {
    "shortName": "fuel",
    "fullName": "Fuel Level",
    "unit": "%"
  },
  "31": {
    "shortName": "dis_mil_off",
    "fullName": "Distance with MIL off",
    "unit": "km"
  },
  "ff1001": {
    "shortName": "gps_spd",
    "fullName": "Vehicle Speed (GPS)",
    "unit": "km/h"
  },
  "ff1007": {
    "shortName": "gps_brng",
    "fullName": "GPS Bearing",
    "unit": "°"
  },
  "ff123a": {
    "shortName": "gps_sat",
    "fullName": "GPS Satellites",
    "unit": "count"
  },
  "ff1010": {
    "shortName": TORQUE_GPS_ALTITUDE,
    "fullName": "GPS Altitude",
    "unit": "m"
  },
  "ff1006": {
    "shortName": TORQUE_GPS_LAT,
    "fullName": "GPS Latitude",
    "unit": "°"
  },
  "ff1239": {
    "shortName": TORQUE_GPS_ACCURACY,
    "fullName": "GPS Accuracy",
    "unit": "m"
  },
  "ff1237": {
    "shortName": "spd_diff",
    "fullName": "GPS vs OBD Speed difference",
    "unit": "km/h"
  },
  "ff1271": {
    "shortName": "fuel_used_trip",
    "fullName": "Fuel used (trip)",
    "unit": "L"
  },
  "ff1005": {
    "shortName": TORQUE_GPS_LON,
    "fullName": "GPS Longitude",
    "unit": "°"
  },
  "47": {
    "shortName": "absolute_throttle_position_b",
    "fullName": "Absolute Throttle Position B",
    "unit": "%"
  },
  "ff1223": {
    "shortName": "acceleration_sensor_total",
    "fullName": "Acceleration Sensor (Total)",
    "unit": "m/s²"
  },
  "ff1220": {
    "shortName": "acceleration_sensor_x_axis",
    "fullName": "Acceleration Sensor (X axis)",
    "unit": "m/s²"
  },
  "ff1221": {
    "shortName": "acceleration_sensor_y_axis",
    "fullName": "Acceleration Sensor (Y axis)",
    "unit": "m/s²"
  },
  "ff1222": {
    "shortName": "acceleration_sensor_z_axis",
    "fullName": "Acceleration Sensor (Z axis)",
    "unit": "m/s²"
  },
  "49": {
    "shortName": "accelerator_pedalposition_d",
    "fullName": "Accelerator Pedal Position D",
    "unit": "%"
  },
  "4a": {
    "shortName": "accelerator_pedalposition_e",
    "fullName": "Accelerator Pedal Position E",
    "unit": "%"
  },
  "4b": {
    "shortName": "accelerator_pedalposition_f",
    "fullName": "Accelerator Pedal Position F",
    "unit": "%"
  },
  "ff124d": {
    "shortName": "air_fuel_ratio_commanded",
    "fullName": "Air Fuel Ratio (Commanded)",
    "unit": "λ"
  },
  "ff1249": {
    "shortName": "air_fuel_ratio_measured",
    "fullName": "Air Fuel Ratio (Measured)",
    "unit": "λ"
  },
  "12": {
    "shortName": "air_status",
    "fullName": "Air Status",
    "unit": ""
  },
  "46": {
    "shortName": "ambient_air_temp",
    "fullName": "Ambient air temp",
    "unit": "°C"
  },
  "ff1263": {
    "shortName": "average_trip_speed_whilst_moving_only",
    "fullName": "Average trip speed (whilst moving only)",
    "unit": "km/h"
  },
  "ff1272": {
    "shortName": "average_trip_speed_whilst_stopped_or_moving",
    "fullName": "Average trip speed (whilst stopped or moving)",
    "unit": "km/h"
  },
  "ff1270": {
    "shortName": "barometer_on_android_device",
    "fullName": "Barometer (on Android device)",
    "unit": "hPa"
  },
  "33": {
    "shortName": "barometric_pressure_from_vehicle",
    "fullName": "Barometric pressure (from vehicle)",
    "unit": "kPa"
  },
  "3c": {
    "shortName": "catalyst_temperature_bank_1_sensor_1",
    "fullName": "Catalyst Temperature (Bank 1 Sensor 1)",
    "unit": "°C"
  },
  "3e": {
    "shortName": "catalyst_temperature_bank_1_sensor_2",
    "fullName": "Catalyst Temperature (Bank 1 Sensor 2)",
    "unit": "°C"
  },
  "3d": {
    "shortName": "catalyst_temperature_bank_2_sensor_1",
    "fullName": "Catalyst Temperature (Bank 2 Sensor 1)",
    "unit": "°C"
  },
  "3f": {
    "shortName": "catalyst_temperature_bank_2_sensor_2",
    "fullName": "Catalyst Temperature (Bank 2 Sensor 2)",
    "unit": "°C"
  },
  "44": {
    "shortName": "commanded_equivalence_ratio_lambda",
    "fullName": "Commanded Equivalence Ratio (lambda)",
    "unit": "λ"
  },
  "ff126d": {
    "shortName": "cost_per_milekm_instant",
    "fullName": "Cost per mile/km (Instant)",
    "unit": "€/km"
  },
  "ff126e": {
    "shortName": "cost_per_milekm_trip",
    "fullName": "Cost per mile/km (Trip)",
    "unit": "€/km"
  },
  "ff1258": {
    "shortName": "co2_in_gkm_average",
    "fullName": "CO2 in g/km (Average)",
    "unit": "g/km"
  },
  "ff1257": {
    "shortName": "co2_in_gkm_instantaneous",
    "fullName": "CO2 in g/km (Instantaneous)",
    "unit": "g/km"
  },
  "ff126a": {
    "shortName": "distance_to_empty_estimated",
    "fullName": "Distance to empty (Estimated)",
    "unit": "km"
  },
  "2c": {
    "shortName": "egr_commanded",
    "fullName": "EGR Commanded",
    "unit": "%"
  },
  "2d": {
    "shortName": "egr_error",
    "fullName": "EGR Error",
    "unit": "%"
  },
  "ff1273": {
    "shortName": "engine_kw_at_the_wheels",
    "fullName": "Engine kW (At the wheels)",
    "unit": "kW"
  },
  "43": {
    "shortName": "engine_load_absolute",
    "fullName": "Engine Load (Absolute)",
    "unit": "%"
  },
  "5c": {
    "shortName": "engine_oil_temperature",
    "fullName": "Engine Oil Temperature",
    "unit": "°C"
  },
  "52": {
    "shortName": "ethanol_fuel_%",
    "fullName": "Ethanol Fuel %",
    "unit": "%"
  },
  "32": {
    "shortName": "evap_system_vapour_pressure",
    "fullName": "Evap System Vapour Pressure",
    "unit": "Pa"
  },
  "78": {
    "shortName": "exhaust_gas_temperature_1",
    "fullName": "Exhaust Gas Temperature 1",
    "unit": "°C"
  },
  "79": {
    "shortName": "exhaust_gas_temperature_2",
    "fullName": "Exhaust Gas Temperature 2",
    "unit": "°C"
  },
  "ff125c": {
    "shortName": "fuel_cost_trip",
    "fullName": "Fuel cost (trip)",
    "unit": "€"
  },
  "ff125d": {
    "shortName": "fuel_flow_ratehour",
    "fullName": "Fuel flow rate/hour",
    "unit": "L/h"
  },
  "ff125a": {
    "shortName": "fuel_flow_rateminute",
    "fullName": "Fuel flow rate/minute",
    "unit": "L/min"
  },
  "0a": {
    "shortName": "fuel_pressure",
    "fullName": "Fuel pressure",
    "unit": "kPa"
  },
  "23": {
    "shortName": "fuel_rail_pressure",
    "fullName": "Fuel Rail Pressure",
    "unit": "kPa"
  },
  "22": {
    "shortName": "fuel_rail_pressure_relative_to_manifold_vacuum",
    "fullName": "Fuel Rail Pressure (relative to manifold vacuum)",
    "unit": "kPa"
  },
  "ff126b": {
    "shortName": "fuel_remaining_calculated_from_vehicle_profile",
    "fullName": "Fuel Remaining (Calculated from vehicle profile)",
    "unit": "%"
  },
  "03": {
    "shortName": "fuel_status",
    "fullName": "Fuel Status",
    "unit": ""
  },
  "07": {
    "shortName": "fuel_trim_bank_1_long_term",
    "fullName": "Fuel Trim Bank 1 Long Term",
    "unit": "%"
  },
  "14": {
    "shortName": "fuel_trim_bank_1_sensor_1",
    "fullName": "Fuel trim bank 1 sensor 1",
    "unit": "%"
  },
  "15": {
    "shortName": "fuel_trim_bank_1_sensor_2",
    "fullName": "Fuel trim bank 1 sensor 2",
    "unit": "%"
  },
  "16": {
    "shortName": "fuel_trim_bank_1_sensor_3",
    "fullName": "Fuel trim bank 1 sensor 3",
    "unit": "%"
  },
  "17": {
    "shortName": "fuel_trim_bank_1_sensor_4",
    "fullName": "Fuel trim bank 1 sensor 4",
    "unit": "%"
  },
  "06": {
    "shortName": "fuel_trim_bank_1_short_term",
    "fullName": "Fuel Trim Bank 1 Short Term",
    "unit": "%"
  },
  "09": {
    "shortName": "fuel_trim_bank_2_long_term",
    "fullName": "Fuel Trim Bank 2 Long Term",
    "unit": "%"
  },
  "18": {
    "shortName": "fuel_trim_bank_2_sensor_1",
    "fullName": "Fuel trim bank 2 sensor 1",
    "unit": "%"
  },
  "19": {
    "shortName": "fuel_trim_bank_2_sensor_2",
    "fullName": "Fuel trim bank 2 sensor 2",
    "unit": "%"
  },
  "1a": {
    "shortName": "fuel_trim_bank_2_sensor_3",
    "fullName": "Fuel trim bank 2 sensor 3",
    "unit": "%"
  },
  "1b": {
    "shortName": "fuel_trim_bank_2_sensor_4",
    "fullName": "Fuel trim bank 2 sensor 4",
    "unit": "%"
  },
  "08": {
    "shortName": "fuel_trim_bank_2_short_term",
    "fullName": "Fuel Trim Bank 2 Short Term",
    "unit": "%"
  },
  "ff123b": {
    "shortName": "gps_bearing",
    "fullName": "GPS Bearing",
    "unit": "°"
  },
  "ff1226": {
    "shortName": "horsepower_at_the_wheels",
    "fullName": "Horsepower (At the wheels)",
    "unit": "hp"
  },
  "0b": {
    "shortName": "intake_manifold_pressure",
    "fullName": "Intake Manifold Pressure",
    "unit": "kPa"
  },
  "ff1203": {
    "shortName": "kilometers_per_litre_instant",
    "fullName": "Kilometers Per Litre (Instant)",
    "unit": "km/L"
  },
  "ff5202": {
    "shortName": "kilometers_per_litre_long_term_average",
    "fullName": "Kilometers Per Litre (Long Term Average)",
    "unit": "km/L"
  },
  "ff1207": {
    "shortName": "litres_per_100_kilometer_instant",
    "fullName": "Litres Per 100 Kilometer (Instant)",
    "unit": "L/100km"
  },
  "ff5203": {
    "shortName": "litres_per_100_kilometer_long_term_average",
    "fullName": "Litres Per 100 Kilometer (Long Term Average)",
    "unit": "L/100km"
  },
  "10": {
    "shortName": "mass_air_flow_rate",
    "fullName": "Mass Air Flow Rate",
    "unit": "g/s"
  },
  "ff1201": {
    "shortName": "miles_per_gallon_instant",
    "fullName": "Miles Per Gallon (Instant)",
    "unit": "mpg"
  },
  "ff5201": {
    "shortName": "miles_per_gallon_long_term_average",
    "fullName": "Miles Per Gallon (Long Term Average)",
    "unit": "mpg"
  },
  "24": {
    "shortName": "o2_sensor1_equivalence_ratio",
    "fullName": "O2 Sensor1 Equivalence Ratio",
    "unit": "λ"
  },
  "34": {
    "shortName": "o2_sensor1_equivalence_ratio_alternate",
    "fullName": "O2 Sensor1 Equivalence Ratio (alternate)",
    "unit": "λ"
  },
  "ff1240": {
    "shortName": "o2_sensor1_wide_range_voltage",
    "fullName": "O2 Sensor1 wide-range Voltage",
    "unit": "V"
  },
  "25": {
    "shortName": "o2_sensor2_equivalence_ratio",
    "fullName": "O2 Sensor2 Equivalence Ratio",
    "unit": "λ"
  },
  "ff1241": {
    "shortName": "o2_sensor2_wide_range_voltage",
    "fullName": "O2 Sensor2 wide-range Voltage",
    "unit": "V"
  },
  "26": {
    "shortName": "o2_sensor3_equivalence_ratio",
    "fullName": "O2 Sensor3 Equivalence Ratio",
    "unit": "λ"
  },
  "ff1242": {
    "shortName": "o2_sensor3_wide_range_voltage",
    "fullName": "O2 Sensor3 wide-range Voltage",
    "unit": "V"
  },
  "27": {
    "shortName": "o2_sensor4_equivalence_ratio",
    "fullName": "O2 Sensor4 Equivalence Ratio",
    "unit": "λ"
  },
  "ff1243": {
    "shortName": "o2_sensor4_wide_range_voltage",
    "fullName": "O2 Sensor4 wide-range Voltage",
    "unit": "V"
  },
  "28": {
    "shortName": "o2_sensor5_equivalence_ratio",
    "fullName": "O2 Sensor5 Equivalence Ratio",
    "unit": "λ"
  },
  "ff1244": {
    "shortName": "o2_sensor5_wide_range_voltage",
    "fullName": "O2 Sensor5 wide-range Voltage",
    "unit": "V"
  },
  "29": {
    "shortName": "o2_sensor6_equivalence_ratio",
    "fullName": "O2 Sensor6 Equivalence Ratio",
    "unit": "λ"
  },
  "ff1245": {
    "shortName": "o2_sensor6_wide_range_voltage",
    "fullName": "O2 Sensor6 wide-range Voltage",
    "unit": "V"
  },
  "2a": {
    "shortName": "o2_sensor7_equivalence_ratio",
    "fullName": "O2 Sensor7 Equivalence Ratio",
    "unit": "λ"
  },
  "ff1246": {
    "shortName": "o2_sensor7_wide_range_voltage",
    "fullName": "O2 Sensor7 wide-range Voltage",
    "unit": "V"
  },
  "2b": {
    "shortName": "o2_sensor8_equivalence_ratio",
    "fullName": "O2 Sensor8 Equivalence Ratio",
    "unit": "λ"
  },
  "ff1247": {
    "shortName": "o2_sensor8_wide_range_voltage",
    "fullName": "O2 Sensor8 wide-range Voltage",
    "unit": "V"
  },
  "ff1214": {
    "shortName": "o2_volts_bank_1_sensor_1",
    "fullName": "O2 Volts Bank 1 sensor 1",
    "unit": "V"
  },
  "ff1215": {
    "shortName": "o2_volts_bank_1_sensor_2",
    "fullName": "O2 Volts Bank 1 sensor 2",
    "unit": "V"
  },
  "ff1216": {
    "shortName": "o2_volts_bank_1_sensor_3",
    "fullName": "O2 Volts Bank 1 sensor 3",
    "unit": "V"
  },
  "ff1217": {
    "shortName": "o2_volts_bank_1_sensor_4",
    "fullName": "O2 Volts Bank 1 sensor 4",
    "unit": "V"
  },
  "ff1218": {
    "shortName": "o2_volts_bank_2_sensor_1",
    "fullName": "O2 Volts Bank 2 sensor 1",
    "unit": "V"
  },
  "ff1219": {
    "shortName": "o2_volts_bank_2_sensor_2",
    "fullName": "O2 Volts Bank 2 sensor 2",
    "unit": "V"
  },
  "ff121a": {
    "shortName": "o2_volts_bank_2_sensor_3",
    "fullName": "O2 Volts Bank 2 sensor 3",
    "unit": "V"
  },
  "ff121b": {
    "shortName": "o2_volts_bank_2_sensor_4",
    "fullName": "O2 Volts Bank 2 sensor 4",
    "unit": "V"
  },
  "5a": {
    "shortName": "relative_accelerator_pedal_position",
    "fullName": "Relative Accelerator Pedal Position",
    "unit": "%"
  },
  "45": {
    "shortName": "relative_throttle_position",
    "fullName": "Relative Throttle Position",
    "unit": "%"
  },
  "ff124a": {
    "shortName": "tilt_x",
    "fullName": "Tilt (x)",
    "unit": "°"
  },
  "ff124b": {
    "shortName": "tilt_y",
    "fullName": "Tilt (y)",
    "unit": "°"
  },
  "ff124c": {
    "shortName": "tilt_z",
    "fullName": "Tilt (z)",
    "unit": "°"
  },
  "0e": {
    "shortName": "timing_advance",
    "fullName": "Timing Advance",
    "unit": "°"
  },
  "ff1225": {
    "shortName": "torque",
    "fullName": "Torque",
    "unit": "ft-lb"
  },
  "fe1805": {
    "shortName": "transmission_temperature_method_1",
    "fullName": "Transmission Temperature (Method 1)",
    "unit": "°C"
  },
  "b4": {
    "shortName": "transmission_temperature_method_2",
    "fullName": "Transmission Temperature (Method 2)",
    "unit": "°C"
  },
  "ff1206": {
    "shortName": "trip_average_kpl",
    "fullName": "Trip average KPL",
    "unit": "km/L"
  },
  "ff1208": {
    "shortName": "trip_average_litres100_km",
    "fullName": "Trip average L/100km",
    "unit": "L/100km"
  },
  "ff1205": {
    "shortName": "trip_average_mpg",
    "fullName": "Trip average MPG",
    "unit": "mpg"
  },
  "ff1204": {
    "shortName": "trip_distance",
    "fullName": "Trip Distance",
    "unit": "km"
  },
  "ff120c": {
    "shortName": "trip_distance_stored_in_vehicle_profile",
    "fullName": "Trip distance (stored in vehicle profile)",
    "unit": "km"
  },
  "ff1266": {
    "shortName": "trip_time_since_journey_start",
    "fullName": "Trip Time (Since journey start)",
    "unit": "s"
  },
  "ff1268": {
    "shortName": "trip_time_whilst_moving",
    "fullName": "Trip Time (whilst moving)",
    "unit": "s"
  },
  "ff1267": {
    "shortName": "trip_time_whilst_stationary",
    "fullName": "Trip time (whilst stationary)",
    "unit": "s"
  },
  "ff1202": {
    "shortName": "turbo_boost_&_vacuum_gauge",
    "fullName": "Turbo Boost & Vacuum Gauge",
    "unit": "kPa"
  },
  "42": {
    "shortName": "voltage_control_module",
    "fullName": "Voltage (Control Module)",
    "unit": "V"
  },
  "ff1238": {
    "shortName": "voltage_obd_adapter",
    "fullName": "Voltage (OBD Adapter)",
    "unit": "V"
  },
  "ff1269": {
    "shortName": "volumetric_efficiency_calculated",
    "fullName": "Volumetric Efficiency (Calculated)",
    "unit": "%"
  },
  "35": {
    "shortName": "o2_o2l2_wide_current",
    "fullName": "O2 {O2L:2} Wide Range Current",
    "unit": "mA"
  },
  "36": {
    "shortName": "o2_o2l3_wide_current",
    "fullName": "O2 {O2L:3} Wide Range Current",
    "unit": "mA"
  },
  "37": {
    "shortName": "o2_o2l4_wide_current",
    "fullName": "O2 {O2L:4} Wide Range Current",
    "unit": "mA"
  },
  "38": {
    "shortName": "o2_o2l5_wide_current",
    "fullName": "O2 {O2L:5} Wide Range Current",
    "unit": "mA"
  },
  "39": {
    "shortName": "o2_o2l6_wide_current",
    "fullName": "O2 {O2L:6} Wide Range Current",
    "unit": "mA"
  },
  "3a": {
    "shortName": "o2_o2l7_wide_current",
    "fullName": "O2 {O2L:7} Wide Range Current",
    "unit": "mA"
  },
  "3b": {
    "shortName": "o2_o2l8_wide_current",
    "fullName": "O2 {O2L:8} Wide Range Current",
    "unit": "mA"
  },
  "5b": {
    "shortName": "hybrid_ev_batt_charge",
    "fullName": "Hybrid Battery Charge (%)",
    "unit": "%"
  },
  "5e": {
    "shortName": "fuel_rate_ecu",
    "fullName": "Fuel Rate (direct from ECU)",
    "unit": "L/min"
  },
  "61": {
    "shortName": "driver_demand_engine_torque_pct",
    "fullName": "Drivers demand engine % torque",
    "unit": "%"
  },
  "62": {
    "shortName": "actual_engine_torque_pct",
    "fullName": "Actual engine % torque",
    "unit": "%"
  },
  "63": {
    "shortName": "engine_reference_torque",
    "fullName": "Engine reference torque",
    "unit": "Nm"
  },
  "66": {
    "shortName": "maf_sensor_a",
    "fullName": "Mass air flow sensor A",
    "unit": "g/s"
  },
  "70": {
    "shortName": "boost_pressure_commanded_a",
    "fullName": "Boost Pressure Commanded A",
    "unit": "kPa"
  },
  "73": {
    "shortName": "exhaust_pressure_b1",
    "fullName": "Exhaust Pressure Bank 1",
    "unit": "kPa"
  },
  "77": {
    "shortName": "charge_air_cooler_temp",
    "fullName": "Charge air cooler temperature (CACT)",
    "unit": "°C"
  },
  "7a": {
    "shortName": "dpf_b1_delta_pressure",
    "fullName": "DPF Bank 1 Delta Pressure",
    "unit": "kPa"
  },
  "7b": {
    "shortName": "dpf_b2_delta_pressure",
    "fullName": "DPF Bank 2 Delta Pressure",
    "unit": "kPa"
  },
  "7c": {
    "shortName": "dpf_b1_inlet_temp",
    "fullName": "DPF Bank 1 Inlet Temperature",
    "unit": "°C"
  },
  "83": {
    "shortName": "nox_pre_scr",
    "fullName": "NOx Pre SCR",
    "unit": "ppm"
  },
  "87": {
    "shortName": "intake_manifold_abs_pressure_a",
    "fullName": "Intake Manifold Abs Pressure A",
    "unit": "kPa"
  },
  "9a": {
    "shortName": "hybrid_ev_batt_voltage",
    "fullName": "Hybrid/EV System Battery Voltage",
    "unit": "V"
  },
  "a6": {
    "shortName": "odometer_ecu",
    "fullName": "Odometer (from ECU)",
    "unit": "km"
  },
  "b2": {
    "shortName": "hybrid_ev_batt_soh",
    "fullName": "Hybrid/EV Battery State of Health",
    "unit": "%"
  },
  "ff122d": {
    "shortName": "time_0_60mph",
    "fullName": "0-60mph Time",
    "unit": "s"
  },
  "ff122e": {
    "shortName": "time_0_100kph",
    "fullName": "0-100kph Time",
    "unit": "s"
  },
  "ff122f": {
    "shortName": "time_quarter_mile",
    "fullName": "1/4 mile time",
    "unit": "s"
  },
  "ff1230": {
    "shortName": "time_eighth_mile",
    "fullName": "1/8 mile time",
    "unit": "s"
  },
  "ff124f": {
    "shortName": "time_0_200kph",
    "fullName": "0-200kph Time",
    "unit": "s"
  },
  "ff125e": {
    "shortName": "time_60_120mph",
    "fullName": "60-120mph Time",
    "unit": "s"
  },
  "ff125f": {
    "shortName": "time_60_80mph",
    "fullName": "60-80mph Time",
    "unit": "s"
  },
  "ff1260": {
    "shortName": "time_40_60mph",
    "fullName": "40-60mph Time",
    "unit": "s"
  },
  "ff1261": {
    "shortName": "time_80_100mph",
    "fullName": "80-100mph Time",
    "unit": "s"
  },
  "ff1264": {
    "shortName": "time_100_0kph",
    "fullName": "100-0kph Time",
    "unit": "s"
  },
  "ff1265": {
    "shortName": "time_60_0mph",
    "fullName": "60-0mph Time",
    "unit": "s"
  },
  "ff1275": {
    "shortName": "time_80_120kph",
    "fullName": "80-120kph Time",
    "unit": "s"
  },
  "ff1276": {
    "shortName": "time_60_130mph",
    "fullName": "60-130mph Time",
    "unit": "s"
  },
  "ff1277": {
    "shortName": "time_0_30mph",
    "fullName": "0-30mph Time",
    "unit": "s"
  },
  "ff1278": {
    "shortName": "time_0_100mph",
    "fullName": "0-100mph Time",
    "unit": "s"
  },
  "ff1280": {
    "shortName": "time_100_200kph",
    "fullName": "100-200kph Time",
    "unit": "s"
  },
  "ff1282": {
    "shortName": "egt_b1_s2",
    "fullName": "Exhaust gas temp Bank 1 Sensor 2",
    "unit": "°C"
  },
  "ff1283": {
    "shortName": "egt_b1_s3",
    "fullName": "Exhaust gas temp Bank 1 Sensor 3",
    "unit": "°C"
  },
  "ff1284": {
    "shortName": "egt_b1_s4",
    "fullName": "Exhaust gas temp Bank 1 Sensor 4",
    "unit": "°C"
  },
  "ff1286": {
    "shortName": "egt_b2_s2",
    "fullName": "Exhaust gas temp Bank 2 Sensor 2",
    "unit": "°C"
  },
  "ff1287": {
    "shortName": "egt_b2_s3",
    "fullName": "Exhaust gas temp Bank 2 Sensor 3",
    "unit": "°C"
  },
  "ff1288": {
    "shortName": "egt_b2_s4",
    "fullName": "Exhaust gas temp Bank 2 Sensor 4",
    "unit": "°C"
  },
  "ff128a": {
    "shortName": "nox_post_scr",
    "fullName": "NOx Post SCR",
    "unit": "ppm"
  },
  "ff1296": {
    "shortName": "pct_city_driving",
    "fullName": "Percentage of City driving",
    "unit": "%"
  },
  "ff1297": {
    "shortName": "pct_highway_driving",
    "fullName": "Percentage of Highway driving",
    "unit": "%"
  },
  "ff1298": {
    "shortName": "pct_idle_driving",
    "fullName": "Percentage of Idle driving",
    "unit": "%"
  },
  "ff129a": {
    "shortName": "android_battery_level",
    "fullName": "Android device Battery Level",
    "unit": "%"
  },
  "ff129b": {
    "shortName": "dpf_b1_outlet_temp",
    "fullName": "DPF Bank 1 Outlet Temperature",
    "unit": "°C"
  },
  "ff129c": {
    "shortName": "dpf_b2_inlet_temp",
    "fullName": "DPF Bank 2 Inlet Temperature",
    "unit": "°C"
  },
  "ff129d": {
    "shortName": "dpf_b2_outlet_temp",
    "fullName": "DPF Bank 2 Outlet Temperature",
    "unit": "°C"
  },
  "ff129e": {
    "shortName": "maf_sensor_b",
    "fullName": "Mass air flow sensor B",
    "unit": "g/s"
  },
  "ff12a1": {
    "shortName": "intake_manifold_abs_pressure_b",
    "fullName": "Intake Manifold Abs Pressure B",
    "unit": "kPa"
  },
  "ff12a4": {
    "shortName": "boost_pressure_commanded_b",
    "fullName": "Boost Pressure Commanded B",
    "unit": "kPa"
  },
  "ff12a5": {
    "shortName": "boost_pressure_sensor_a",
    "fullName": "Boost Pressure Sensor A",
    "unit": "kPa"
  },
  "ff12a6": {
    "shortName": "boost_pressure_sensor_b",
    "fullName": "Boost Pressure Sensor B",
    "unit": "kPa"
  },
  "ff12ab": {
    "shortName": "exhaust_pressure_b2",
    "fullName": "Exhaust Pressure Bank 2",
    "unit": "kPa"
  },
  "ff12b0": {
    "shortName": "dpf_b1_inlet_pressure",
    "fullName": "DPF Bank 1 Inlet Pressure",
    "unit": "kPa"
  },
  "ff12b1": {
    "shortName": "dpf_b1_outlet_pressure",
    "fullName": "DPF Bank 1 Outlet Pressure",
    "unit": "kPa"
  },
  "ff12b2": {
    "shortName": "dpf_b2_inlet_pressure",
    "fullName": "DPF Bank 2 Inlet Pressure",
    "unit": "kPa"
  },
  "ff12b3": {
    "shortName": "dpf_b2_outlet_pressure",
    "fullName": "DPF Bank 2 Outlet Pressure",
    "unit": "kPa"
  },
  "ff12b4": {
    "shortName": "hybrid_ev_batt_current",
    "fullName": "Hybrid/EV System Battery Current",
    "unit": "A"
  },
  "ff12b5": {
    "shortName": "hybrid_ev_batt_power",
    "fullName": "Hybrid/EV System Battery Power",
    "unit": "W"
  },
  "ff12b6": {
    "shortName": "positive_kinetic_energy_pke",
    "fullName": "Positive Kinetic Energy (PKE)",
    "unit": "km/h^2"
  }
}
