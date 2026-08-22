# VAJRA — Indian Aerospace Physics Simulator

An interactive real-time physics simulator showcasing India's indigenous aerospace capabilities. Built with real engineering parameters, VAJRA lets you explore the physics behind India's most advanced defence and space systems.

**Live app:** [vajra-hal-tejas.streamlit.app](https://vajra-hal-tejas.streamlit.app)

## Platforms Simulated

### Defence
- **HAL Tejas Mk1A** — Supersonic flight physics: Mach cone formation, sonic boom N-wave, four forces of flight, performance envelope, flight regime detection
- **BrahMos Missile** — Ramjet vs scramjet propulsion, sea-skimming terminal phase, cruise trajectory

### ISRO
- **PSLV-XL** — Multi-stage orbital mechanics, Tsiolkovsky rocket equation, gravity-turn trajectory
- **GSLV Mk III (LVM3)** — Cryogenic upper stage, heavy-lift payload analysis, stage separation dynamics

### Private Space
- **Agnikul Cosmos — Agnibaan** — 3D-printed Agnilet semi-cryogenic engine, single-piece combustion chamber
- **Skyroot — Vikram-1** — 3D-printed Raman engine, carbon composite structure, solid + liquid staging

## Physics Models

| Model | Application |
|-------|-------------|
| International Standard Atmosphere (ISA) | Temperature, pressure, density vs altitude (troposphere + stratosphere) |
| Mach cone geometry | Shockwave half-angle: θ = arcsin(1/M) |
| Sonic boom N-wave | Overpressure–underpressure shock profile |
| Tsiolkovsky rocket equation | Multi-stage delta-v and propellant mass |
| Drag model | Subsonic skin friction + transonic wave drag rise + supersonic wave drag |
| Dynamic pressure | q = ½ρv² for aerodynamic force calculations |
| Gravity-turn trajectory | Orbital insertion approximation |
| Prandtl-Glauert correction | Compressibility effects near Mach 1 |

## Tech Stack

- **Python** + **Streamlit** — web framework and deployment
- **Plotly** — interactive 3D and 2D data visualisation
- **NumPy** — physics computations

## Run Locally

```bash
pip install streamlit plotly numpy
streamlit run vajra.py
```

## Roadmap

- Chandrayaan orbital mechanics simulator
- Gaganyaan re-entry heat shield analysis
- AMCA stealth aircraft profile
- Akash missile intercept trajectory
- Live ISRO satellite tracking
- Mobile app (Play Store / App Store)

## About

Built by **Atharv Shukla**, Class 12, Amity International School Sector 46 Gurgaon.
Self-directed aerospace engineering project portfolio.
