🚗 Torque Logger 2025 — Intégration Home Assistant

Domaine : torque_logger_2025 · Version : 2025.09.0b1 · IoT class : local_push

<p align="center"> <img src="docs/hero.png" alt="Torque Logger 2025" width="720"> </p> <p align="center"> <a href="https://img.shields.io/badge/version-2025.09.0b1-blue.svg"><img alt="Version" src="https://img.shields.io/badge/version-2025.09.0b1-blue.svg"></a> <a href="#"><img alt="Home Assistant" src="https://img.shields.io/badge/Home%20Assistant-Custom%20Component-41BDF5.svg"></a> <a href="#"><img alt="IoT Class" src="https://img.shields.io/badge/IoT%20class-local__push-8A2BE2.svg"></a> <a href="#"><img alt="Language" src="https://img.shields.io/badge/FR%20%2F%20EN-localisation-00A86B.svg"></a> </p>

Torque Logger 2025 reçoit en push les données de l’app Torque (Android) et crée automatiquement des capteurs (PID) + un device_tracker (position GPS du véhicule) dans Home Assistant.
C’est simple, rapide, et prêt pour vos tableaux de bord de passionné. 🔧📈

🧭 Sommaire

✨ Fonctionnalités

📦 Installation

⚙️ Configuration côté Home Assistant

📱 Réglages dans Torque (Android)

🧪 Tests rapides (sans Torque)

🛰️ Capteurs & suivi GPS

🗑️ Supprimer un véhicule (sans enlever l’intégration)

🧰 Dépannage

🧠 Notes techniques

🗒️ Changelog

🔐 Sécurité & bonnes pratiques

🤝 Remerciements


✨ Fonctionnalités

Création auto des capteurs à partir des PIDs connus (voir const.py).

Device tracker basé sur gpslat / gpslon (position en temps réel).

Localisation FR/EN des libellés de capteurs.

Conversion d’unités (km→mi, °C→°F, km/h→mph, m→ft) via pint.

Anti-bruit : filtrage optionnel par email (seuls vos envois passent).

Désambiguïsation automatique quand deux PIDs portent le même short name.

Suppression ciblée d’un véhicule directement depuis l’UI d’Home Assistant.

