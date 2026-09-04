# VAJRA — Indian Aerospace Physics Simulator

An interactive real-time physics simulator showcasing India's indigenous aerospace capabilities. Built with real engineering parameters across 11 platforms, 3 exploration tools, a mission challenge lab, and live satellite tracking.

**Live app:** [vajra-hal-tejas.streamlit.app](https://vajra-hal-tejas.streamlit.app)

## Platforms

### Defence
- **HAL Tejas Mk1A** — Supersonic flight physics: Mach cone formation, sonic boom N-wave, four forces of flight, performance envelope, drag vs Mach, ISA atmosphere profile, ground footprint
- **BrahMos Missile** — Ramjet/scramjet propulsion, cruise trajectory with sea-skimming terminal phase, 3 variants (Block III, ER, Hypersonic)
- **AMCA Stealth Fighter** — Radar cross section comparison across 6 aircraft, radar detection range calculator, angular RCS polar pattern (Tejas vs AMCA)
- **Akash Missile** — Surface-to-air intercept trajectory with proportional navigation, kill envelope visualization

### ISRO
- **Chandrayaan 3** — Earth orbit raising sequence (7 maneuvers with real mission data), lunar orbit insertion, vis-viva orbital velocity charts, powered descent profile for Vikram lander
- **Gaganyaan Re-entry** — Atmospheric re-entry simulation, G-force profile, heat shield stagnation temperature, parachute deployment phases, adjustable entry angle
- **PSLV-XL** — 4-stage launch trajectory, velocity/G-force profiles, stage separation events
- **GSLV Mk III (LVM3)** — 3-stage heavy-lift trajectory with cryogenic upper stage
- **Live Satellite Tracker** — Real-time Indian satellite positions from CelesTrak TLE data, SGP4 orbit propagation, ground position map, orbit classification, speed vs altitude analysis

### Private Space
- **Agnikul Cosmos (Agnibaan)** — 3D-printed Agnilet engine, 2-stage launch simulation
- **Skyroot (Vikram-1)** — 3D-printed Raman engine, 3-stage solid+liquid launch simulation

### Explore
- **Compare Platforms** — Side-by-side specs and charts for any 2 of 8 platforms
- **Satellite Orbit Visualizer** — Ground track, orbital velocity, period, Indian satellite reference orbits
- **Mission Challenge Lab** — 5 interactive physics challenges: orbit insertion, re-entry survival, stealth penetration, rocket design, missile intercept. Real-time calculations with visual feedback

## Physics Models

| Model | Application |
|-------|-------------|
| International Standard Atmosphere (ISA) | Temperature, pressure, density vs altitude |
| Mach cone geometry | Shockwave half-angle: arcsin(1/M) |
| Sonic boom N-wave | Overpressure shock profile |
| Tsiolkovsky rocket equation | Multi-stage delta-v and propellant mass |
| Transonic drag model | Subsonic + wave drag rise + supersonic |
| Vis-viva equation | Orbital velocity at any point in an orbit |
| Keplerian orbit geometry | Elliptical transfer orbits |
| Radar equation | Detection range vs RCS |
| Proportional navigation | Missile intercept guidance law |
| Sutton-Graves heating | Re-entry stagnation point temperature |
| Satellite ground track | Orbital projection onto Earth surface |
| SGP4 orbit propagation | Real-time satellite position from TLE data |

## Tech Stack

- **Python** + **Streamlit** — web framework and deployment
- **Plotly** — interactive 3D and 2D data visualisation
- **NumPy** — physics computations

## Run Locally

```bash
pip install streamlit plotly numpy sgp4
streamlit run vajra.py
```

## Roadmap

- Tejas Mk1A spotting log + community map
- Mobile app (Play Store / App Store)

## About

Built by **Atharv Shukla**, Class 12, Amity International School Sector 46 Gurgaon.
Self-directed aerospace engineering project portfolio.
