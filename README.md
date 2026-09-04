<div align="center">

# VAJRA

### India's Aerospace Physics Simulator

[![Live App](https://img.shields.io/badge/LAUNCH_APP-vajra--hal--tejas.streamlit.app-ff9933?style=for-the-badge&logo=streamlit&logoColor=white)](https://vajra-hal-tejas.streamlit.app)

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive_Charts-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**11 platforms. 12 physics models. 5 mission challenges. Live satellite tracking.**

Real engineering parameters. Real equations. Real time.

[Launch App](https://vajra-hal-tejas.streamlit.app) | [Features](#features) | [Physics](#physics-models) | [Run Locally](#run-locally)

</div>

---

## What is VAJRA?

An interactive simulator that lets you explore the real physics behind India's most advanced aerospace systems. Not animations. Not approximations. Actual engineering models running in your browser.

Fly the **Tejas** through its Mach envelope and watch the shockwave cone form. Launch a **PSLV** through 4 stage separations. Guide an **Akash missile** to intercept. Bring **Gaganyaan** home through the re-entry corridor without killing the crew. Track **Indian satellites** moving across the globe in real time.

> Built by a Class 12 student. Runs entirely in the browser. Zero installation needed.

---

## Features

### Defence

| Platform | What You Can Do |
|----------|----------------|
| **HAL Tejas Mk1A** | Mach cone formation, sonic boom N-wave, four forces of flight, performance envelope, drag vs Mach, ISA atmosphere model, ground footprint |
| **BrahMos Missile** | Ramjet propulsion, cruise trajectory with sea-skimming terminal phase, 3 variants (Block III, ER, Hypersonic) |
| **AMCA Stealth Fighter** | RCS comparison across 6 aircraft, radar detection range calculator, angular RCS polar pattern |
| **Akash Missile** | Surface-to-air intercept with proportional navigation, kill envelope visualization |

### ISRO

| Platform | What You Can Do |
|----------|----------------|
| **Chandrayaan 3** | Earth orbit raising (7 real maneuvers), lunar orbit insertion, vis-viva velocity charts, Vikram lander powered descent |
| **Gaganyaan Re-entry** | Atmospheric re-entry, G-force profile, heat shield stagnation temperature, parachute deployment, adjustable entry angle |
| **PSLV-XL** | 4-stage launch trajectory, velocity/G-force profiles, stage separation events |
| **GSLV Mk III (LVM3)** | 3-stage heavy-lift trajectory with cryogenic upper stage |
| **Live Satellite Tracker** | Real-time Indian satellite positions (SGP4 + CelesTrak TLE), auto-refreshing world map, orbit classification, speed vs altitude plot |

### Private Space

| Platform | What You Can Do |
|----------|----------------|
| **Agnikul Cosmos (Agnibaan)** | 3D-printed Agnilet engine, 2-stage launch simulation |
| **Skyroot (Vikram-1)** | 3D-printed Raman engine, 3-stage solid+liquid launch simulation |

### Explore

| Tool | What You Can Do |
|------|----------------|
| **Compare Platforms** | Side-by-side specs and charts for any 2 of 8 platforms |
| **Satellite Orbit Visualizer** | Ground track, orbital velocity, period, Indian satellite reference orbits |
| **Mission Challenge Lab** | 5 interactive challenges: orbit insertion, re-entry survival, stealth penetration, rocket design, missile intercept |

---

## Mission Challenge Lab

Not a quiz. Not multiple choice. You set the parameters, the physics decides if your mission succeeds or fails.

| Challenge | Your Task | Physics Used |
|-----------|-----------|-------------|
| **Orbit Insertion** | Pick the right delta-v to reach a target altitude | Vis-viva equation, Hohmann transfer |
| **Re-entry Survival** | Choose the entry angle that keeps the crew alive | Sutton-Graves heating, G-force corridor |
| **Stealth Penetration** | Slip past an S-400 radar undetected | Radar equation, radar horizon |
| **Rocket Design** | Build a 2-stage rocket that reaches orbit | Tsiolkovsky equation, staging |
| **Missile Intercept** | Defend airspace against an incoming aircraft | Proportional navigation, kill geometry |

---

## Physics Models

Every simulation uses published equations from aerospace engineering. Nothing is faked.

| Model | What It Does |
|-------|-------------|
| International Standard Atmosphere (ISA) | Temperature, pressure, density vs altitude |
| Mach cone geometry | Shockwave half-angle: arcsin(1/M) |
| Sonic boom N-wave | Overpressure shock profile |
| Tsiolkovsky rocket equation | Multi-stage delta-v and propellant mass |
| Transonic drag model | Subsonic + wave drag rise + supersonic |
| Vis-viva equation | Orbital velocity at any point in an orbit |
| Keplerian orbit geometry | Elliptical transfer orbits |
| Radar equation | Detection range vs RCS (4th root scaling) |
| Proportional navigation | Missile intercept guidance law |
| Sutton-Graves heating | Re-entry stagnation point temperature |
| Satellite ground track | Orbital projection onto Earth surface |
| SGP4 orbit propagation | Real-time satellite position from TLE data |

---

## Tech Stack

| Component | Role |
|-----------|------|
| **Python** | Core language |
| **Streamlit** | Web framework + deployment |
| **Plotly** | Interactive 2D/3D data visualization |
| **NumPy** | Physics computations |
| **SGP4** | Satellite orbit propagation |

---

## Run Locally

```bash
git clone https://github.com/atharvshukladartagnan-create/vajra-tejas.git
cd vajra-tejas
pip install -r requirements.txt
streamlit run vajra.py
```

---

## Roadmap

- [ ] Tejas Mk1A spotting log + community map
- [ ] Mobile app (Play Store / App Store)
- [ ] More defence platforms

---

## About

Built by **Atharv Shukla**, Class 12, Amity International School Sector 46 Gurgaon.

Self-directed aerospace engineering project. No templates. No tutorials. Built from physics textbooks and ISRO mission reports.

---

<div align="center">

**If this helped you understand aerospace physics, consider giving it a star.**

[![Star this repo](https://img.shields.io/github/stars/atharvshukladartagnan-create/vajra-tejas?style=social)](https://github.com/atharvshukladartagnan-create/vajra-tejas)

</div>
