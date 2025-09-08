# Liste des PIDs Torque —


## Sommaire
- [Standard OBD‑II PIDs](#standard-obdii-pids)
- [FF10xx – GPS & télémétrie de base](#ff10xx--gps--télémétrie-de-base)
- [FF12xx – Performance, O2, trajets & divers](#ff12xx--performance-o2-trajets--divers)
- [FF12A* – Suralimentation/pression (B)](#ff12a--suralimentationpression-b)
- [FF12B* – DPF & Hybrid/EV](#ff12b--dpf--hybridev)
- [FF52xx – Moyennes long terme](#ff52xx--moyennes-long-terme)

---

<details>
<summary><strong>Standard OBD‑II PIDs</strong></summary>

| PID | Nom court | Nom complet | Unité |
| :-- | :-- | :-- | :--: |
| `04` | engine_load | Engine Load | % |
| `05` | coolant_temp | Engine Coolant Temperature | °C |
| `06` | fuel_trim_b1_short | Fuel Trim Bank 1 Short Term | % |
| `07` | fuel_trim_b1_long | Fuel Trim Bank 1 Long Term | % |
| `08` | fuel_trim_b2_short | Fuel Trim Bank 2 Short Term | % |
| `09` | fuel_trim_b2_long | Fuel Trim Bank 2 Long Term | % |
| `0a` | fuel_pressure | Fuel pressure | kPa |
| `0b` | intake_manifold_pressure | Intake Manifold Pressure | kPa |
| `0c` | engine_rpm | Engine RPM | rpm |
| `0d` | speed_obd | Speed (OBD) | km/h |
| `0e` | timing_advance | Timing Advance | ° |
| `0f` | intake_air_temp | Intake Air Temperature | °C |
| `10` | mass_air_flow_rate | Mass Air Flow Rate | g/s |
| `11` | throttle_position_manifold | Throttle Position (Manifold) | % |
| `14` | fuel_trim_o2l_1 | Fuel trim {O2L:1} | % |
| `15` | fuel_trim_o2l_2 | Fuel trim {O2L:2} | % |
| `16` | fuel_trim_o2l_3 | Fuel trim {O2L:3} | % |
| `17` | fuel_trim_o2l_4 | Fuel trim {O2L:4} | % |
| `18` | fuel_trim_o2l_5 | Fuel trim {O2L:5} | % |
| `19` | fuel_trim_o2l_6 | Fuel trim {O2L:6} | % |
| `1a` | fuel_trim_o2l_7 | Fuel trim {O2L:7} | % |
| `1b` | fuel_trim_o2l_8 | Fuel trim {O2L:8} | % |
| `1f` | run_time_since_start | Run time since engine start | s |
| `21` | dist_mil_on | Distance travelled with MIL/CEL lit | km |
| `22` | fuel_rail_pressure_rel | Fuel Rail Pressure (relative to manifold vacuum) | kPa |
| `23` | fuel_rail_pressure | Fuel Rail Pressure | kPa |
| `24` | o2_o2l1_wide_voltage | O2 {O2L:1} Wide Range Voltage | V |
| `25` | o2_o2l2_wide_voltage | O2 {O2L:2} Wide Range Voltage | V |
| `26` | o2_o2l3_wide_voltage | O2 {O2L:3} Wide Range Voltage | V |
| `27` | o2_o2l4_wide_voltage | O2 {O2L:4} Wide Range Voltage | V |
| `28` | o2_o2l5_wide_voltage | O2 {O2L:5} Wide Range Voltage | V |
| `29` | o2_o2l6_wide_voltage | O2 {O2L:6} Wide Range Voltage | V |
| `2a` | o2_o2l7_wide_voltage | O2 {O2L:7} Wide Range Voltage | V |
| `2b` | o2_o2l8_wide_voltage | O2 {O2L:8} Wide Range Voltage | V |
| `2c` | egr_commanded | EGR Commanded | % |
| `2d` | egr_error | EGR Error | % |
| `2f` | fuel_level_ecu | Fuel Level (From Engine ECU) | % |
| `31` | dist_since_codes_cleared | Distance travelled since codes cleared | km |
| `32` | evap_system_vapour_pressure | Evap System Vapour Pressure | Pa |
| `33` | barometric_pressure_vehicle | Barometric pressure (from vehicle) | kPa |
| `34` | o2_o2l1_wide_current | O2 {O2L:1} Wide Range Current | mA |
| `35` | o2_o2l2_wide_current | O2 {O2L:2} Wide Range Current | mA |
| `36` | o2_o2l3_wide_current | O2 {O2L:3} Wide Range Current | mA |
| `37` | o2_o2l4_wide_current | O2 {O2L:4} Wide Range Current | mA |
| `38` | o2_o2l5_wide_current | O2 {O2L:5} Wide Range Current | mA |
| `39` | o2_o2l6_wide_current | O2 {O2L:6} Wide Range Current | mA |
| `3a` | o2_o2l7_wide_current | O2 {O2L:7} Wide Range Current | mA |
| `3b` | o2_o2l8_wide_current | O2 {O2L:8} Wide Range Current | mA |
| `3c` | cat_temp_b1s1 | Catalyst Temperature (Bank 1,Sensor 1) | °C |
| `3d` | cat_temp_b2s1 | Catalyst Temperature (Bank 2,Sensor 1) | °C |
| `3e` | cat_temp_b1s2 | Catalyst Temperature (Bank 1,Sensor 2) | °C |
| `3f` | cat_temp_b2s2 | Catalyst Temperature (Bank 2,Sensor 2) | °C |
| `42` | voltage_control_module | Voltage (Control Module) | V |
| `43` | engine_load_absolute | Engine Load(Absolute) | % |
| `44` | commanded_equivalence_ratio | Commanded Equivalence Ratio (lambda) | — |
| `45` | relative_throttle_position | Relative Throttle Position | % |
| `46` | ambient_air_temp | Ambient air temp | °C |
| `47` | absolute_throttle_position_b | Absolute Throttle Position B | % |
| `49` | accelerator_pedal_pos_d | Accelerator PedalPosition D | % |
| `4a` | accelerator_pedal_pos_e | Accelerator PedalPosition E | % |
| `4b` | accelerator_pedal_pos_f | Accelerator PedalPosition F | % |
| `52` | ethanol_fuel_pct | Ethanol Fuel % | % |
| `5a` | relative_accelerator_pedal_position | Relative Accelerator Pedal Position | % |
| `5b` | hybrid_ev_batt_charge | Hybrid Battery Charge (%) | % |
| `5c` | engine_oil_temperature | Engine Oil Temperature | °C |
| `5e` | fuel_rate_ecu | Fuel Rate (direct from ECU) | L/m |
| `61` | driver_demand_engine_torque_pct | Drivers demand engine % torque | % |
| `62` | actual_engine_torque_pct | Actual engine % torque | % |
| `63` | engine_reference_torque | Engine reference torque | Nm |
| `66` | maf_sensor_a | Mass air flow sensor A | g/s |
| `70` | boost_pressure_commanded_a | Boost Pressure Commanded A | kPa |
| `73` | exhaust_pressure_b1 | Exhaust Pressure Bank 1 | kPa |
| `77` | charge_air_cooler_temp | Charge air cooler temperature (CACT) | °C |
| `78` | egt_b1_s1 | Exhaust gas temp Bank 1 Sensor 1 | °C |
| `79` | egt_b2_s1 | Exhaust gas temp Bank 2 Sensor 1 | °C |
| `7a` | dpf_b1_delta_pressure | DPF Bank 1 Delta Pressure | kPa |
| `7b` | dpf_b2_delta_pressure | DPF Bank 2 Delta Pressure | kPa |
| `7c` | dpf_b1_inlet_temp | DPF Bank 1 Inlet Temperature | °C |
| `83` | nox_pre_scr | NOx Pre SCR | ppm |
| `87` | intake_manifold_abs_pressure_a | Intake Manifold Abs Pressure A | kPa |
| `9a` | hybrid_ev_batt_voltage | Hybrid/EV System Battery Voltage | V |
| `a6` | odometer_ecu | Odometer(from ECU) | km |
| `b2` | hybrid_ev_batt_soh | Hybrid/EV Battery State of Health | % |
| `b4` | transmission_temp_method_2 | Transmission Temperature(Method 2) | °C |

</details>

<details>
<summary><strong>FF10xx – GPS & télémétrie de base</strong></summary>

| PID | Nom court | Nom complet | Unité |
| :-- | :-- | :-- | :--: |
| `ff1001` | gps_spd | Vehicle Speed (GPS) | km/h |
| `ff1005` | TORQUE_GPS_LON | GPS Longitude | ° |
| `ff1006` | TORQUE_GPS_LAT | GPS Latitude | ° |
| `ff1010` | TORQUE_GPS_ALTITUDE | GPS Altitude | m |

</details>

<details>

<summary><strong>FF12xx – Performance, O2, trajets & divers</strong></summary>

| PID | Nom court | Nom complet | Unité |
| :-- | :-- | :-- | :--: |
| `ff1201` | mpg_instant | Miles Per Gallon(Instant) | mpg |
| `ff1202` | turbo_boost_vacuum_gauge | Turbo Boost & Vacuum Gauge | psi |
| `ff1203` | kpl_instant | Kilometers Per Litre(Instant) | kpl |
| `ff1204` | trip_distance | Trip Distance | km |
| `ff1205` | mpg_trip_avg | Trip average MPG | mpg |
| `ff1206` | kpl_trip_avg | Trip average KPL | kpl |
| `ff1207` | l_per_100_instant | Litres Per 100 Kilometer(Instant) | l/100km |
| `ff1208` | l_per_100_trip_avg | Trip average Litres/100 KM | l/100km |
| `ff120c` | trip_distance_stored | Trip distance (stored in vehicle profile) | km |
| `ff1214` | o2_b1s1_voltage | O2 {O2L:1} Voltage | V |
| `ff1215` | o2_b1s2_voltage | O2 {O2L:2} Voltage | V |
| `ff1216` | o2_b1s3_voltage | O2 {O2L:3} Voltage | V |
| `ff1217` | o2_b1s4_voltage | O2 {O2L:4} Voltage | V |
| `ff1218` | o2_b2s1_voltage | O2 {O2L:5} Voltage | V |
| `ff1219` | o2_b2s2_voltage | O2 {O2L:6} Voltage | V |
| `ff121a` | o2_b2s3_voltage | O2 {O2L:7} Voltage | V |
| `ff121b` | o2_b2s4_voltage | O2 {O2L:8} Voltage | V |
| `ff1220` | accel_x | Acceleration Sensor(X axis) | g |
| `ff1221` | accel_y | Acceleration Sensor(Y axis) | g |
| `ff1222` | accel_z | Acceleration Sensor(Z axis) | g |
| `ff1223` | accel_total | Acceleration Sensor(Total) | g |
| `ff1225` | torque | Torque | ft-lb |
| `ff1226` | horsepower_wheels | Horsepower (At the wheels) | hp |
| `ff122d` | time_0_60mph | 0-60mph Time | s |
| `ff122e` | time_0_100kph | 0-100kph Time | s |
| `ff122f` | time_quarter_mile | 1/4 mile time | s |
| `ff1230` | time_eighth_mile | 1/8 mile time | s |
| `ff1237` | spd_diff_gps_obd | GPS vs OBD Speed difference | km/h |
| `ff1238` | voltage_obd_adapter | Voltage (OBD Adapter) | V |
| `ff1239` | TORQUE_GPS_ACCURACY | GPS Accuracy | m |
| `ff123a` | gps_satellites | GPS Satellites | — |
| `ff123b` | gps_bearing | GPS Bearing | ° |
| `ff1240` | o2_o2l1_wide_eq_ratio | O2 {O2L:1} Wide Range Equivalence Ratio | λ |
| `ff1241` | o2_o2l2_wide_eq_ratio | O2 {O2L:2} Wide Range Equivalence Ratio | λ |
| `ff1242` | o2_o2l3_wide_eq_ratio | O2 {O2L:3} Wide Range Equivalence Ratio | λ |
| `ff1243` | o2_o2l4_wide_eq_ratio | O2 {O2L:4} Wide Range Equivalence Ratio | λ |
| `ff1244` | o2_o2l5_wide_eq_ratio | O2 {O2L:5} Wide Range Equivalence Ratio | λ |
| `ff1245` | o2_o2l6_wide_eq_ratio | O2 {O2L:6} Wide Range Equivalence Ratio | λ |
| `ff1246` | o2_o2l7_wide_eq_ratio | O2 {O2L:7} Wide Range Equivalence Ratio | λ |
| `ff1247` | o2_o2l8_wide_eq_ratio | O2 {O2L:8} Wide Range Equivalence Ratio | λ |
| `ff1249` | air_fuel_ratio_measured | Air Fuel Ratio(Measured) | :1 |
| `ff124d` | air_fuel_ratio_commanded | Air Fuel Ratio(Commanded) | :1 |
| `ff124f` | time_0_200kph | 0-200kph Time | s |
| `ff1257` | co2_gkm_instant | CO₂ in g/km (Instantaneous) | g/km |
| `ff1258` | co2_gkm_avg | CO₂ in g/km (Average) | g/km |
| `ff125a` | fuel_flow_rate_min | Fuel flow rate/minute | cc/min |
| `ff125c` | fuel_cost_trip | Fuel cost (trip) | cost |
| `ff125d` | fuel_flow_rate_hr | Fuel flow rate/hour | l/hr |
| `ff125e` | time_60_120mph | 60-120mph Time | s |
| `ff125f` | time_60_80mph | 60-80mph Time | s |
| `ff1260` | time_40_60mph | 40-60mph Time | s |
| `ff1261` | time_80_100mph | 80-100mph Time | s |
| `ff1263` | avg_trip_speed_moving | Average trip speed(whilst moving only) | km/h |
| `ff1264` | time_100_0kph | 100-0kph Time | s |
| `ff1265` | time_60_0mph | 60-0mph Time | s |
| `ff1266` | trip_time_since_start | Trip Time(Since journey start) | s |
| `ff1267` | trip_time_stationary | Trip time(whilst stationary) | s |
| `ff1268` | trip_time_moving | Trip time(whilst moving) | s |
| `ff1269` | volumetric_efficiency_calc | Volumetric Efficiency (Calculated) | % |
| `ff126a` | distance_to_empty_est | Distance to empty (Estimated) | km |
| `ff126b` | fuel_remaining_calc | Fuel Remaining (Calculated from vehicle profile) | % |
| `ff126d` | cost_per_km_instant | Cost per mile/km (Instant) | €/km |
| `ff126e` | cost_per_km_trip | Cost per mile/km (Trip) | €/km |
| `ff1270` | barometer_android | Barometer (on Android device) | mb |
| `ff1271` | fuel_used_trip | Fuel used (trip) | l |
| `ff1272` | avg_trip_speed_overall | Average trip speed(whilst stopped or moving) | km/h |
| `ff1273` | engine_kw_wheels | Engine kW (At the wheels) | kW |
| `ff1275` | time_80_120kph | 80-120kph Time | s |
| `ff1276` | time_60_130mph | 60-130mph Time | s |
| `ff1277` | time_0_30mph | 0-30mph Time | s |
| `ff1278` | time_0_100mph | 0-100mph Time | s |
| `ff1280` | time_100_200kph | 100-200kph Time | s |
| `ff1282` | egt_b1_s2 | Exhaust gas temp Bank 1 Sensor 2 | °C |
| `ff1283` | egt_b1_s3 | Exhaust gas temp Bank 1 Sensor 3 | °C |
| `ff1284` | egt_b1_s4 | Exhaust gas temp Bank 1 Sensor 4 | °C |
| `ff1286` | egt_b2_s2 | Exhaust gas temp Bank 2 Sensor 2 | °C |
| `ff1287` | egt_b2_s3 | Exhaust gas temp Bank 2 Sensor 3 | °C |
| `ff1288` | egt_b2_s4 | Exhaust gas temp Bank 2 Sensor 4 | °C |
| `ff128a` | nox_post_scr | NOx Post SCR | ppm |
| `ff1296` | pct_city_driving | Percentage of City driving | % |
| `ff1297` | pct_highway_driving | Percentage of Highway driving | % |
| `ff1298` | pct_idle_driving | Percentage of Idle driving | % |
| `ff129a` | android_battery_level | Android device Battery Level | % |
| `ff129b` | dpf_b1_outlet_temp | DPF Bank 1 Outlet Temperature | °C |
| `ff129c` | dpf_b2_inlet_temp | DPF Bank 2 Inlet Temperature | °C |
| `ff129d` | dpf_b2_outlet_temp | DPF Bank 2 Outlet Temperature | °C |
| `ff129e` | maf_sensor_b | Mass air flow sensor B | g/s |

</details>


<details>
<summary><strong>FF12A* – Suralimentation/pression (B)</strong></summary>

| PID | Nom court | Nom complet | Unité |
| :-- | :-- | :-- | :--: |
| `ff12a1` | intake_manifold_abs_pressure_b | Intake Manifold Abs Pressure B | kPa |
| `ff12a4` | boost_pressure_commanded_b | Boost Pressure Commanded B | kPa |
| `ff12a5` | boost_pressure_sensor_a | Boost Pressure Sensor A | kPa |
| `ff12a6` | boost_pressure_sensor_b | Boost Pressure Sensor B | kPa |
| `ff12ab` | exhaust_pressure_b2 | Exhaust Pressure Bank 2 | kPa |

</details>

<details>
<summary><strong>FF12B* – DPF & Hybrid/EV</strong></summary>

| PID | Nom court | Nom complet | Unité |
| :-- | :-- | :-- | :--: |
| `ff12b0` | dpf_b1_inlet_pressure | DPF Bank 1 Inlet Pressure | kPa |
| `ff12b1` | dpf_b1_outlet_pressure | DPF Bank 1 Outlet Pressure | kPa |
| `ff12b2` | dpf_b2_inlet_pressure | DPF Bank 2 Inlet Pressure | kPa |
| `ff12b3` | dpf_b2_outlet_pressure | DPF Bank 2 Outlet Pressure | kPa |
| `ff12b4` | hybrid_ev_batt_current | Hybrid/EV System Battery Current | A |
| `ff12b5` | hybrid_ev_batt_power | Hybrid/EV System Battery Power | W |
| `ff12b6` | positive_kinetic_energy_pke | Positive Kinetic Energy (PKE) | km/hr^2 |

</details>

<details>
<summary><strong>FF52xx – Moyennes long terme</strong></summary>

| PID | Nom court | Nom complet | Unité |
| :-- | :-- | :-- | :--: |
| `ff5201` | mpg_long_term_avg | Miles Per Gallon(Long Term Average) | mpg |
| `ff5202` | kpl_long_term_avg | Kilometers Per Litre(Long Term Average) | kpl |
| `ff5203` | l_per_100_long_term_avg | Litres Per 100 Kilometer(Long Term Average) | l/100km |

</details>

