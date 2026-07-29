# HAL Tejas Sonic Boom Simulator - VAJRA

A real-time interactive supersonic flight physics simulator built for the HAL Tejas Mk1A fighter jet.

## What it does
- Simulates the four forces of flight (Lift, Weight, Thrust, Drag) with a real-time force balance diagram
- Visualises shockwave (Mach) cone formation when the aircraft breaks the sound barrier
- Models sonic boom N-wave pressure distribution around the aircraft
- Calculates speed of sound at any altitude using ISA atmospheric data (troposphere + stratosphere)
- Detects subsonic, transonic and supersonic flight regimes
- Shows the HAL Tejas Mk1A performance envelope with current flight state
- Displays dynamic pressure, air density, and aerodynamic force metrics

## Physics behind it
- **International Standard Atmosphere (ISA):** Troposphere lapse rate of 6.5 K/km up to 11 km, constant temperature in the lower stratosphere (11-20 km)
- **Mach cone half-angle:** θ = arcsin(1/M)
- **Sonic boom N-wave:** Characteristic overpressure-underpressure profile with sharp front/rear shocks
- **Drag model:** Subsonic skin friction + transonic wave drag rise + supersonic wave drag
- **Dynamic pressure:** q = ½ρv² used for all aerodynamic force calculations
- **Lift-drag balance:** CL derived from level flight condition (L = W)

## Tech Stack
- Python
- Streamlit
- Plotly
- NumPy

## How to run
```
pip install streamlit plotly numpy
python -m streamlit run vajra.py
```

## About
Built by Atharv Shukla, Class 12, Amity International School Sector 46 Gurgaon.
Part of a self-directed aerospace engineering project portfolio.
Inspired by HAL's Tejas Mk1A supersonic fighter jet program.
