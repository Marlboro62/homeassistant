[FRENCH]
<a id="installation"></a>
## 📦 Installation

### HACS (recommandé)
1. Assurez-vous d’avoir **HACS** installé dans Home Assistant.
2. Ouvrez **HACS → Intégrations → ⋮ → Dépôts personnalisés**.
3. Ajoutez ce dépôt :  
   **`https://github.com/custom-cards/bar-card`**  
   *(Type : **Tableau de bord**)*  
> ⚠️ Vérifiez qu’il n’y a **pas d’espace** dans l’URL si vous copiez/collez.
4. Dans **HACS → Intégrations**, recherchez **“Bar Card”**, installez.
5. **Redémarrez** Home Assistant si demandé.
6. Vérifiez que la ressource a été ajoutée automatiquement :

> ℹ️ Paramètres → Tableaux de bord → Ressources doit contenir :

```bash
URL : /hacsfiles/bar-card/bar-card.js
Type : module
```

> ⚠️ Si elle n’y est pas, ajoutez-la manuellement.

[ENGLISH]
<a id="installation"></a>
## 📦 Installation

### HACS (recommended)
1. Make sure HACS is installed in Home Assistant.
2. Open **HACS → Intégrations → ⋮ → Custom repositories.**.
3. Add this repository: :  
   **`https://github.com/custom-cards/bar-card`**  
   *(Category: Dashboard**)*  
> ⚠️ Make sure there are **no spaces** in the URL if you copy/paste.
4. In **HACS → Intégrations**, search for **“Bar Card”**, and install it.
5. **Restart** Home Assistant if prompted.
6. Confirm the resource was added automatically :

> ℹ️ Settings → Dashboards → Resources should include :

```bash
URL : /hacsfiles/bar-card/bar-card.js
Type : module
```

> ⚠️ If it’s not there, add it manually.




type: vertical-stack
cards:
  - type: custom:bar-card
    title: SLK Mikael — Live
    columns: 2
    height: 28
    entities:
      - entity: sensor.slk_mikael_vitesse_du_vehicule
        name: Speed (OBD)
        icon: mdi:speedometer
        max: 250
        severity:
          - from: 0
            to: 50
            color: "#4caf50"
          - from: 50
            to: 130
            color: "#ffc107"
          - from: 130
            to: 300
            color: "#f44336"
      - entity: sensor.slk_mikael_vitesse_du_vehicule_gps
        name: Speed (GPS)
        icon: mdi:speedometer-medium
        max: 250
      - entity: sensor.slk_mikael_regime_moteur
        name: RPM
        icon: mdi:engine
        max: 7000
        severity:
          - from: 0
            to: 2500
            color: "#4caf50"
          - from: 2500
            to: 4500
            color: "#ffc107"
          - from: 4500
            to: 9000
            color: "#f44336"
      - entity: sensor.slk_mikael_position_daccelerateur
        name: Throttle
        icon: mdi:car-shift-pattern
        max: 100
      - entity: sensor.slk_mikael_charge_moteur
        name: Engine load
        icon: mdi:engine-outline
        max: 100
      - entity: sensor.slk_mikael_temperature_liquide_refroidissement
        name: Coolant
        icon: mdi:thermometer
        max: 120
        severity:
          - from: -40
            to: 70
            color: "#03a9f4"
          - from: 70
            to: 100
            color: "#4caf50"
          - from: 100
            to: 120
            color: "#f44336"
      - entity: sensor.slk_mikael_temperature_air_dadmission
        name: Intake temp
        icon: mdi:thermometer
        max: 80
      - entity: sensor.slk_mikael_boost_depression_turbo
        name: Boost/Vacuum
        icon: mdi:gauge
      - entity: sensor.slk_mikael_carburant_restant_profil
        name: Fuel remaining
        icon: mdi:gas-station
      - entity: sensor.slk_mikael_autonomie_estimee
        name: DTE (est.)
        icon: mdi:map-marker-distance
        severity:
          - from: 0
            to: 50
            color: "#f44336"
          - from: 50
            to: 150
            color: "#ffc107"
          - from: 150
            to: 9999
            color: "#4caf50"