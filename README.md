# 🚗 Torque Logger 2025 — Intégration Home Assistant

**Domaine :** `torque_logger_2025` · **Version :** `2025.09.0b1` · **IoT class :** `local_push`

<p align="center">
  <img src="docs/hero.png" alt="Torque Logger 2025" width="720">
</p>
<p align="center">
  <a href="https://img.shields.io/badge/version-2025.09.0b1-blue.svg"><img alt="Version" src="https://img.shields.io/badge/version-2025.09.0b1-blue.svg"></a>
  <a href="#"><img alt="Home Assistant" src="https://img.shields.io/badge/Home%20Assistant-Custom%20Component-41BDF5.svg"></a>
  <a href="#"><img alt="IoT Class" src="https://img.shields.io/badge/IoT%20class-local__push-8A2BE2.svg"></a>
  <a href="#"><img alt="Language" src="https://img.shields.io/badge/FR%20%2F%20EN-localisation-00A86B.svg"></a>
</p>

Torque Logger 2025 reçoit en **push** les données de l’app **Torque (Android)** et crée automatiquement des **capteurs (PID)** + un **`device_tracker`** (position GPS du véhicule) dans **Home Assistant**.  
C’est simple, rapide, et prêt pour vos tableaux de bord de passionné. 🔧📈

---

## 🧭 Sommaire

- [✨ Fonctionnalités](#fonctionnalites)
- [📦 Installation](#installation)
- [⚙️ Configuration côté Home Assistant](#configuration-ha)
- [📱 Réglages dans Torque (Android)](#reglages-torque)
- [🧪 Tests rapides (sans Torque)](#tests-rapides)
- [🛰️ Capteurs & suivi GPS](#capteurs-gps)
- [🗑️ Supprimer un véhicule (sans enlever l’intégration)](#supprimer-vehicule)
- [🧰 Dépannage](#depannage)
- [🧠 Notes techniques](#notes-techniques)
- [🗒️ Changelog](#changelog)
- [🔐 Sécurité & bonnes pratiques](#securite)
- [🤝 Remerciements](#remerciements)

---

<a id="fonctionnalites"></a>
## ✨ Fonctionnalités

- Création **auto** des capteurs à partir des **PIDs** connus (voir `const.py`).
- **Device tracker** basé sur `gpslat` / `gpslon` (position en temps réel).
- **Localisation FR/EN** des libellés de capteurs.
- **Conversion d’unités** (km→mi, °C→°F, km/h→mph, m→ft) via **pint**.
- Anti-bruit : **filtrage optionnel par email** (seuls vos envois passent).
- **Désambiguïsation automatique** quand deux PIDs portent le même *short name*.
- **Suppression ciblée d’un véhicule** directement depuis l’UI d’Home Assistant.

---

<a id="installation"></a>
## 📦 Installation

1. Copiez le dossier `custom_components/torque_logger_2025` dans votre instance **Home Assistant**.
2. **Redémarrez** Home Assistant.

> ⚠️ **Une seule instance** de l’intégration est autorisée.

---

<a id="configuration-ha"></a>
## ⚙️ Configuration côté Home Assistant

1. **Paramètres → Intégrations → Ajouter une intégration → “Torque Logger 2025”**  
2. Renseignez :
   - **Email (facultatif)** : si défini, seuls les envois Torque portant **exactement** cet email seront traités.
   - **Unités impériales** : conversions automatiques.
   - **Langue** : `fr` ou `en` pour les libellés.

> ℹ️ Ces options sont modifiables plus tard via **Options de l’intégration**.

---

<a id="reglages-torque"></a>
## 📱 Réglages dans Torque (Android)

Dans **Torque Pro** :

1. Activez l’upload vers serveur web  
   *(Data Logging & Upload → Upload to Web Server)*.
2. **URL du serveur :**
http(s)://VOTRE_HA:PORT/api/torque_logger_2025
3. *(Conseillé)* Renseignez **votre email** dans Torque (champ envoyé en `eml=...`) — il doit **correspondre** si vous avez activé le filtre côté intégration.
4. Laissez Torque envoyer ses paramètres par défaut (`session`, `id`, `eml`, `profileName`, `time`, `kXX`, etc.).

> 💡 L’endpoint n’exige pas d’authentification par défaut (upload direct depuis le téléphone).  
> Si votre HA est **exposé sur Internet**, **protégez-le** (reverse proxy, VPN, allow-list IP) ou utilisez le **filtre email**.

---

<a id="tests-rapides"></a>
## 🧪 Tests rapides (sans Torque)

**Vitesse OBD (PID `0x0D`) :**
```bash
curl "http://HA:8123/api/torque_logger_2025?session=A1&id=devA&eml=votre@mail.tld&profileName=Ma%20Voiture&v=1.0&time=1694090000&userFullName0d=Vehicle%20speed&userShortName0d=speed&defaultUnit0d=km/h&k0d=250"

