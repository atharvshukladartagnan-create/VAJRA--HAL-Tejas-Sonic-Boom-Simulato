import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timezone
import json
import urllib.request
from sgp4.api import Satrec, WGS72
from sgp4.api import jday

st.set_page_config(page_title="VAJRA - Indian Aerospace Simulator", layout="wide", page_icon="⚡")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Rajdhani:wght@300;400;500;600;700&display=swap');
.stApp { background: linear-gradient(160deg, #0c1a2e 0%, #112240 100%); }
.hud-title {
    font-family: 'Archivo', sans-serif; font-size: 2.8rem; font-weight: 900;
    color: #f0f4f8; text-align: center; letter-spacing: 2px; margin-bottom: 0;
}
.hud-title span { color: #ff9933; }
.hud-subtitle {
    font-family: 'Rajdhani', sans-serif; font-size: 1.05rem; color: #7a8ba4;
    text-align: center; letter-spacing: 6px; text-transform: uppercase; margin-top: 0;
}
.hud-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 20px; margin: 8px 0;
}
.hud-metric { font-family: 'JetBrains Mono', monospace; text-align: center; padding: 15px 10px; }
.hud-metric .value {
    font-size: 1.7rem; font-weight: 700; color: #f0f4f8; display: block;
}
.hud-metric .label {
    font-family: 'Rajdhani', sans-serif; font-size: 0.8rem; color: #7a8ba4;
    text-transform: uppercase; letter-spacing: 2px; margin-top: 4px; display: block;
}
.regime-badge {
    font-family: 'Archivo', sans-serif; font-size: 0.75rem; padding: 5px 16px;
    border-radius: 100px; text-align: center; font-weight: 700;
    letter-spacing: 1px; display: inline-block; margin: 5px auto; text-transform: uppercase;
}
.regime-subsonic { background: rgba(74,222,128,0.12); border: 1px solid rgba(74,222,128,0.3); color: #4ade80; }
.regime-transonic { background: rgba(255,153,51,0.12); border: 1px solid rgba(255,153,51,0.3); color: #ff9933; }
.regime-supersonic { background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.3); color: #ef4444; }
.specs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-family: 'Rajdhani', sans-serif; }
.spec-item {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 8px 12px; text-align: center;
}
.spec-item .spec-val { font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #f0f4f8; display: block; }
.spec-item .spec-label { font-size: 0.7rem; color: #7a8ba4; text-transform: uppercase; letter-spacing: 1px; }
.section-header {
    font-family: 'Archivo', sans-serif; font-size: 1rem; color: #f0f4f8; font-weight: 700;
    letter-spacing: 1px; border-left: 3px solid #ff9933; padding-left: 12px;
    margin-bottom: 15px; text-transform: uppercase;
}
.alert-box { font-family: 'Rajdhani', sans-serif; padding: 12px 20px; border-radius: 8px; margin: 5px 0; font-size: 1rem; letter-spacing: 1px; }
.alert-boom { background: rgba(239,68,68,0.08); border-left: 3px solid #ef4444; color: #fca5a5; }
.alert-transonic { background: rgba(255,153,51,0.08); border-left: 3px solid #ff9933; color: #ffb366; }
.alert-normal { background: rgba(74,222,128,0.08); border-left: 3px solid #4ade80; color: #86efac; }
.alert-limit { background: rgba(239,68,68,0.08); border-left: 3px solid #ef4444; color: #fca5a5; }
.alert-info { background: rgba(255,153,51,0.08); border-left: 3px solid #ff9933; color: #ffcc80; }
div[data-testid="stSidebar"] { background: linear-gradient(180deg, #091626, #0c1a2e, #091626); border-right: 1px solid rgba(255,255,255,0.06); }
</style>
""", unsafe_allow_html=True)

CHART_GRID = 'rgba(255,255,255,0.05)'
CHART_AXIS = '#7a8ba4'
CHART_TITLE = '#f0f4f8'
CHART_BG = 'rgba(8,16,30,0.8)'
ACCENT = '#ff9933'
GREEN = '#4ade80'
RED = '#ef4444'
YELLOW = '#fbbf24'
TEXT = '#f0f4f8'
MUTED = '#7a8ba4'


def plotly_layout(fig, height=450, **kwargs):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=CHART_BG,
        height=height, margin=dict(l=50, r=20, t=40, b=40),
        font=dict(family='Rajdhani, sans-serif'),
        xaxis=dict(gridcolor=CHART_GRID, color=CHART_AXIS),
        yaxis=dict(gridcolor=CHART_GRID, color=CHART_AXIS),
        **kwargs
    )


def isa_atmosphere(alt):
    if alt <= 11000:
        t = 288.15 - 0.0065 * alt
        p = 101325 * (t / 288.15) ** 5.2561
    else:
        t = 216.65
        p = 22632 * np.exp(-0.00015769 * (alt - 11000))
    rho = p / (287.05 * t)
    a = np.sqrt(1.4 * 287.05 * t)
    return t, p, rho, a


def simulate_launch(stages, total_mass):
    dt = 0.5
    t_sim, alt_sim, vel_sim, acc_sim, mach_sim = [0], [0], [0], [0], [0]
    current_mass = total_mass
    v, h = 0.0, 0.0
    stage_boundaries = []
    for si, stage in enumerate(stages):
        fuel_mass = stage["mass_full"] - stage["mass_empty"]
        mdot = fuel_mass / stage["burn_time"]
        for step in range(int(stage["burn_time"] / dt)):
            t = t_sim[-1] + dt
            t_atm, p_atm, rho_atm, a_atm = isa_atmosphere(min(h, 20000))
            g = 9.81 * (6371000 / (6371000 + h)) ** 2
            thrust = stage["thrust"] * 1000
            drag_f = 0.5 * rho_atm * v**2 * 0.3 * (3.14 * 1.5**2) if h < 80000 else 0
            acc = (thrust - drag_f) / current_mass - g
            v = max(0, v + acc * dt)
            h = h + v * dt
            current_mass -= mdot * dt
            t_sim.append(t)
            alt_sim.append(h / 1000)
            vel_sim.append(v)
            acc_sim.append(acc / 9.81)
            mach_sim.append(v / a_atm if h < 20000 else v / 295.0)
        current_mass -= stage["mass_empty"]
        current_mass = max(current_mass, 500)
        stage_boundaries.append((t_sim[-1], alt_sim[-1], stage["name"]))
    return t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries


def show_launch_charts(name, t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries):
    fig_traj = go.Figure()
    fig_traj.add_trace(go.Scatter(x=t_sim, y=alt_sim, mode='lines',
        line=dict(color=ACCENT, width=3), name='Altitude'))
    for tb, ab, sn in stage_boundaries:
        fig_traj.add_vline(x=tb, line_dash="dot", line_color="rgba(255,255,255,0.15)")
        fig_traj.add_annotation(x=tb, y=ab, text=f"{sn.split('(')[0].strip()} sep",
            font=dict(color=MUTED, size=9, family='Rajdhani'), showarrow=True,
            arrowcolor=MUTED, arrowsize=0.8)
    fig_traj.update_layout(title=dict(text=f"{name} Launch Trajectory",
        font=dict(color=CHART_TITLE, family='Archivo', size=14)),
        xaxis_title="Time (s)", yaxis_title="Altitude (km)")
    plotly_layout(fig_traj, height=400)
    st.plotly_chart(fig_traj, use_container_width=True)

    with st.expander("What am I looking at?"):
        st.markdown("The orange curve shows the rocket climbing through the atmosphere. Dotted lines mark **stage separations** — when an empty fuel tank is dropped so the rocket gets lighter and accelerates faster.")

    vc1, vc2 = st.columns(2)
    with vc1:
        fig_vel = go.Figure()
        fig_vel.add_trace(go.Scatter(x=t_sim, y=vel_sim, mode='lines',
            line=dict(color=GREEN, width=2), name='Velocity'))
        fig_vel.update_layout(title=dict(text="Velocity Profile",
            font=dict(color=CHART_TITLE, family='Archivo', size=12)),
            xaxis_title="Time (s)", yaxis_title="Velocity (m/s)")
        plotly_layout(fig_vel, height=350)
        st.plotly_chart(fig_vel, use_container_width=True)
        with st.expander("About velocity"):
            st.markdown("Speed builds with each stage. To reach orbit you need ~7,800 m/s (28,000 km/h) — 23x the speed of sound.")
    with vc2:
        fig_g = go.Figure()
        fig_g.add_trace(go.Scatter(x=t_sim, y=acc_sim, mode='lines',
            line=dict(color=YELLOW, width=2), name='G-force'))
        fig_g.add_hline(y=6, line_dash="dash", line_color="rgba(239,68,68,0.4)",
            annotation_text="Human limit ~6G", annotation_font=dict(color=RED, size=9))
        fig_g.update_layout(title=dict(text="G-Force Profile",
            font=dict(color=CHART_TITLE, family='Archivo', size=12)),
            xaxis_title="Time (s)", yaxis_title="G-force")
        plotly_layout(fig_g, height=350)
        st.plotly_chart(fig_g, use_container_width=True)
        with st.expander("About G-force"):
            st.markdown("As fuel burns the rocket gets lighter but thrust stays the same, so G-force **rises** through each stage. The red line is the human tolerance limit (~6G).")

    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">{max(alt_sim):.0f} km</span><span class="label">Max Alt</span></div>
      <div class="hud-metric"><span class="value">{max(vel_sim):.0f} m/s</span><span class="label">Max Vel</span></div>
      <div class="hud-metric"><span class="value">{max(vel_sim)/1000*3.6:.0f} km/h</span><span class="label">Max Speed</span></div>
      <div class="hud-metric"><span class="value">{max(mach_sim):.1f}</span><span class="label">Max Mach</span></div>
      <div class="hud-metric"><span class="value">{max(acc_sim):.1f}G</span><span class="label">Peak G</span></div>
      <div class="hud-metric"><span class="value">{t_sim[-1]:.0f}s</span><span class="label">Total Burn</span></div>
    </div>
    """, unsafe_allow_html=True)


def show_stage_cards(stages):
    for i, stage in enumerate(stages):
        st.sidebar.markdown(f"""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:8px; margin:4px 0;">
            <span style="font-family:Archivo,sans-serif; color:#ff9933; font-size:0.7rem; font-weight:700; letter-spacing:1px;">STAGE {i+1}</span><br>
            <span style="font-family:Rajdhani,sans-serif; color:#c0cfe0; font-size:0.85rem;">{stage['name']}</span><br>
            <span style="color:#7a8ba4; font-size:0.75rem;">Thrust: {stage['thrust']} kN | Burn: {stage['burn_time']}s | Isp: {stage['isp']}s</span>
        </div>
        """, unsafe_allow_html=True)


# --- HEADER ---
st.markdown('<h1 class="hud-title">V<span>A</span>JR<span>A</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hud-subtitle">Indian Aerospace Simulator Platform</p>', unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown('<p class="section-header">Navigate</p>', unsafe_allow_html=True)

category = st.sidebar.selectbox("Category", ["Defence", "ISRO", "Private Space", "Explore", "About"], label_visibility="collapsed")

if category == "Defence":
    page = st.sidebar.radio("Platform", ["HAL Tejas Mk1A", "BrahMos Missile", "AMCA Stealth Fighter", "Akash Missile"], label_visibility="collapsed")
elif category == "ISRO":
    page = st.sidebar.radio("Mission", ["Chandrayaan 3", "Gaganyaan Re-entry", "PSLV-XL", "GSLV Mk III (LVM3)", "Live Satellite Tracker"], label_visibility="collapsed")
elif category == "Private Space":
    page = st.sidebar.radio("Company", ["Agnikul Cosmos — Agnibaan", "Skyroot — Vikram-1"], label_visibility="collapsed")
elif category == "Explore":
    page = st.sidebar.radio("Tool", ["Compare Platforms", "Satellite Orbit Visualizer", "Quiz"], label_visibility="collapsed")
else:
    page = "About VAJRA"

st.sidebar.markdown("---")


# ================================================================
# HAL TEJAS Mk1A
# ================================================================
if page == "HAL Tejas Mk1A":
    st.sidebar.markdown('<p class="section-header">Tejas Controls</p>', unsafe_allow_html=True)
    mach = st.sidebar.slider("Mach Number", 0.1, 1.8, 0.8, 0.01,
        help="Mach = speed / speed of sound. Tejas maxes out at Mach 1.8.")
    altitude = st.sidebar.slider("Altitude (m)", 0, 16500, 5000, 100,
        help="Height above sea level. Tejas ceiling is 16,500 m.")

    TEJAS_WING_AREA = 38.4
    TEJAS_MASS = 9800
    TEJAS_MAX_MACH = 1.8
    TEJAS_CEILING = 16500
    TEJAS_MAX_THRUST = 89.0
    TEJAS_DRAG_CD0 = 0.02

    temp, pressure_atm, rho, speed_of_sound = isa_atmosphere(altitude)
    aircraft_speed = mach * speed_of_sound

    if mach < 0.8:
        regime, regime_class = "SUBSONIC", "regime-subsonic"
    elif mach < 1.0:
        regime, regime_class = "TRANSONIC", "regime-transonic"
    else:
        regime, regime_class = "SUPERSONIC", "regime-supersonic"

    q = 0.5 * rho * aircraft_speed**2
    if mach < 0.8:
        cd = TEJAS_DRAG_CD0 + 0.06 * (mach**2)
    elif mach < 1.2:
        cd = TEJAS_DRAG_CD0 + 0.06 * (mach**2) + 0.2 * (mach - 0.8)**2
    else:
        cd = TEJAS_DRAG_CD0 + 0.06 * (mach**2) + 0.015 / (mach**2)

    cl = (TEJAS_MASS * 9.81) / (q * TEJAS_WING_AREA) if q > 0 else 0
    drag = q * TEJAS_WING_AREA * cd
    lift = q * TEJAS_WING_AREA * cl
    weight = TEJAS_MASS * 9.81
    thrust_required = drag
    g_load = lift / weight if weight > 0 else 0

    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div style="text-align:center"><span class="{regime_class} regime-badge">{regime}</span></div>', unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown('<p class="section-header">Tejas Mk1A Specs</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">GE F404</span><span class="spec-label">Engine</span></div>
      <div class="spec-item"><span class="spec-val">{TEJAS_MAX_THRUST} kN</span><span class="spec-label">Max Thrust</span></div>
      <div class="spec-item"><span class="spec-val">M {TEJAS_MAX_MACH}</span><span class="spec-label">Max Speed</span></div>
      <div class="spec-item"><span class="spec-val">{TEJAS_CEILING/1000:.1f} km</span><span class="spec-label">Ceiling</span></div>
      <div class="spec-item"><span class="spec-val">{TEJAS_WING_AREA} m²</span><span class="spec-label">Wing Area</span></div>
      <div class="spec-item"><span class="spec-val">{TEJAS_MASS/1000:.1f} t</span><span class="spec-label">Empty Wt</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">HAL Tejas Mk1A — Supersonic Flight Simulator</p>', unsafe_allow_html=True)

    with st.expander("About Tejas"):
        st.markdown("India's indigenous Light Combat Aircraft. Adjust Mach and altitude in the sidebar to see how flight physics change in real time.")

    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">{mach:.2f}</span><span class="label">Mach</span></div>
      <div class="hud-metric"><span class="value">{altitude/1000:.1f} km</span><span class="label">Altitude</span></div>
      <div class="hud-metric"><span class="value">{temp - 273.15:.0f}°C</span><span class="label">Outside Temp</span></div>
      <div class="hud-metric"><span class="value">{aircraft_speed:.0f}</span><span class="label">Speed m/s</span></div>
      <div class="hud-metric"><span class="value">{aircraft_speed*3.6:.0f}</span><span class="label">Speed km/h</span></div>
      <div class="hud-metric"><span class="value">{g_load:.1f}G</span><span class="label">G-Load</span></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("What do these numbers mean?"):
        st.markdown("**Mach** = speed / speed of sound. **Outside Temp** drops ~6.5 C every km up. **G-Load** = how many times your body weight you feel (1G = normal, fighter pilots pull up to 9G).")

    if mach >= 1.0:
        ha = np.degrees(np.arcsin(1 / mach))
        bs = 0.5 + 1.5 * (mach - 1.0)
        st.markdown(f'<div class="alert-box alert-boom">SONIC BOOM — Mach cone half-angle: {ha:.1f}° | Overpressure: {bs:.2f}</div>', unsafe_allow_html=True)
    elif mach >= 0.8:
        st.markdown('<div class="alert-box alert-transonic">TRANSONIC — Approaching the sound barrier, drag is spiking</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-box alert-normal">SUBSONIC — Normal flight conditions</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-header">Shockwave (Mach Cone)</p>', unsafe_allow_html=True)
        if mach >= 1.0:
            half_angle = np.degrees(np.arcsin(1 / mach))
            theta = np.radians(half_angle)
            phi = np.linspace(0, 2 * np.pi, 60)
            x_len = np.linspace(0, 8, 40)
            PHI, X = np.meshgrid(phi, x_len)
            R = X * np.tan(theta)
            Y, Z = R * np.cos(PHI), R * np.sin(PHI)
            intensity = min(1.0, (mach - 1.0) / 1.5)
            fig1 = go.Figure()
            fig1.add_trace(go.Surface(x=-X, y=Y, z=Z,
                colorscale=[[0, f'rgba(255,153,51,{0.3+0.4*intensity})'],
                            [0.5, f'rgba(255,180,80,{0.2+0.3*intensity})'],
                            [1, f'rgba(255,210,120,{0.1+0.15*intensity})']],
                showscale=False, opacity=0.6))
            fig1.add_trace(go.Scatter3d(x=[0.3], y=[0], z=[0], mode='markers+text',
                marker=dict(size=8, color=TEXT, symbol='diamond'),
                text=[f'TEJAS M{mach:.1f}'], textposition='top center',
                textfont=dict(color=TEXT, size=11)))
            fig1.update_layout(
                title=dict(text=f"3D Mach Cone — {half_angle:.1f}°",
                    font=dict(color=CHART_TITLE, family='Archivo')),
                scene=dict(
                    xaxis=dict(backgroundcolor='rgb(10,18,36)', gridcolor=CHART_GRID, color=CHART_AXIS),
                    yaxis=dict(backgroundcolor='rgb(10,18,36)', gridcolor=CHART_GRID, color=CHART_AXIS),
                    zaxis=dict(backgroundcolor='rgb(10,18,36)', gridcolor=CHART_GRID, color=CHART_AXIS),
                    bgcolor='rgb(10,18,36)', aspectmode='data'),
                paper_bgcolor='rgba(0,0,0,0)', height=500, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig1, use_container_width=True)
            with st.expander("How does a Mach cone work?"):
                st.markdown(f"When Tejas flies faster than sound, air piles up into a cone-shaped shockwave behind the jet — like the V-wake behind a boat. At Mach {mach:.1f}, the cone half-angle is **{half_angle:.1f} degrees**. Faster = narrower cone.")
        else:
            st.markdown(f'<div class="hud-card" style="text-align:center;padding:60px 20px;"><p style="font-family:Archivo,sans-serif;color:{MUTED};letter-spacing:1px;">NO SHOCKWAVE<br><span style="font-size:0.8rem;color:{MUTED};">Increase Mach above 1.0 to see the Mach cone form</span></p></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-header">Sonic Boom Pressure (N-Wave)</p>', unsafe_allow_html=True)
        x_wave = np.linspace(-10, 10, 1000)
        if mach >= 1.0:
            boom_strength = 0.5 + 1.5 * (mach - 1.0)
            sw, nwl = 0.3, 3.0 + 2.0 / mach
            fs = boom_strength * (1 / (1 + np.exp(-x_wave / (sw * 0.3))))
            rs = boom_strength * (1 / (1 + np.exp(-(x_wave - nwl) / (sw * 0.3))))
            ld = np.clip(boom_strength * (1 - x_wave / nwl), -boom_strength, boom_strength)
            mask = (x_wave >= -sw * 3) & (x_wave <= nwl + sw * 3)
            pw = np.ones_like(x_wave)
            pw[mask] = 1.0 + (fs[mask] - rs[mask]) * ld[mask] / boom_strength
            op = boom_strength * (rho / 1.225)**0.5
            tt = f"Sonic Boom N-Wave | ΔP ≈ {op:.2f}"
        else:
            cf = 1 / np.sqrt(max(1 - mach**2, 0.01))
            pw = 1.0 + 0.3 * cf * np.exp(-0.5 * (x_wave * (1 - mach))**2) * np.cos(3 * x_wave)
            tt = f"Subsonic Pressure | β = {1/cf:.3f}"
        lc = RED if mach >= 1.0 else ACCENT
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=x_wave, y=pw, mode='lines', line=dict(color=lc, width=2.5), name='Pressure'))
        fig2.add_hline(y=1.0, line_dash="dash", line_color="rgba(255,255,255,0.15)",
            annotation_text="P∞ (normal)", annotation_font=dict(color=MUTED))
        fig2.update_layout(title=dict(text=tt, font=dict(color=CHART_TITLE, family='Archivo', size=13)),
            xaxis_title="Position", yaxis_title="P / P∞")
        plotly_layout(fig2, height=500)
        st.plotly_chart(fig2, use_container_width=True)
        if mach >= 1.0:
            with st.expander("What is an N-wave?"):
                st.markdown("A sonic boom sounds like a double bang. Pressure spikes up (front shock), drops below normal, then spikes again (rear shock). This **N-shape** is why it's called an N-wave. The dashed line is normal atmospheric pressure.")
        else:
            with st.expander("About pressure"):
                st.markdown("Below Mach 1 there's no sonic boom. Pressure changes smoothly around the aircraft. The dashed line is normal atmospheric pressure (P-infinity).")

    st.markdown("---")
    cf1, cf2 = st.columns(2)
    with cf1:
        st.markdown('<p class="section-header">Four Forces of Flight</p>', unsafe_allow_html=True)
        fnames = ['LIFT', 'WEIGHT', 'THRUST', 'DRAG']
        fvals = [lift/1000, weight/1000, thrust_required/1000, drag/1000]
        fcols = [GREEN, RED, '#60a5fa', YELLOW]
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(y=fnames, x=fvals, orientation='h',
            marker=dict(color=fcols), text=[f'{v:.1f} kN' for v in fvals],
            textposition='outside', textfont=dict(color='#c0cfe0', size=13, family='JetBrains Mono'),
            hovertemplate='%{y}: %{x:.2f} kN<extra></extra>'))
        bal = "BALANCED" if abs(lift - weight) < weight * 0.01 else "UNBALANCED"
        fig3.add_annotation(x=max(fvals)*0.5, y=1.5, text=f"<b>{bal}</b>",
            font=dict(size=12, color=GREEN if bal == "BALANCED" else RED, family='Archivo'), showarrow=False)
        plotly_layout(fig3, showlegend=False)
        fig3.update_layout(yaxis=dict(color='#c0cfe0', tickfont=dict(size=13, family='Rajdhani')),
                           xaxis=dict(title="Force (kN)"), margin=dict(l=80, r=60, t=20, b=40))
        st.plotly_chart(fig3, use_container_width=True)
        with st.expander("What are the four forces?"):
            st.markdown(f"**Lift** (wings push up) vs **Weight** (gravity pulls down). **Thrust** (engine pushes forward) vs **Drag** (air resistance). For level flight at constant speed, Lift=Weight and Thrust=Drag. Currently: **{bal}**.")

    with cf2:
        st.markdown('<p class="section-header">Flight Envelope</p>', unsafe_allow_html=True)
        alts = np.linspace(0, 20000, 200)
        me = []
        for a in alts:
            t, p, r, spd = isa_atmosphere(a)
            vl = np.sqrt(2 * 80000 / r)
            ml = min(vl / spd, TEJAS_MAX_MACH)
            if a > TEJAS_CEILING:
                ml = max(0, ml * (1 - (a - TEJAS_CEILING) / 5000))
            me.append(ml)
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=me, y=alts/1000, mode='lines', fill='tozerox',
            line=dict(color=ACCENT, width=2), fillcolor='rgba(255,153,51,0.08)', name='Envelope'))
        fig4.add_trace(go.Scatter(x=[mach], y=[altitude/1000], mode='markers+text',
            marker=dict(size=14, color=TEXT, symbol='star-diamond'),
            text=[f'M{mach:.1f}'], textposition='top right',
            textfont=dict(color=TEXT, size=12, family='JetBrains Mono'), name='You'))
        fig4.add_vline(x=1.0, line_dash="dot", line_color="rgba(255,255,255,0.2)", annotation_text="Mach 1",
            annotation_font=dict(color=MUTED))
        plotly_layout(fig4)
        fig4.update_layout(xaxis=dict(title="Mach"), yaxis=dict(title="Altitude (km)"))
        st.plotly_chart(fig4, use_container_width=True)
        with st.expander("What is a flight envelope?"):
            st.markdown("The orange area is where Tejas **can** fly — every valid Mach + altitude combo. The star is your current position. Outside the envelope: either too slow to generate enough lift, or beyond structural/engine limits.")

    st.markdown("---")
    cd1, cd2 = st.columns(2)
    with cd1:
        st.markdown('<p class="section-header">Drag vs Mach</p>', unsafe_allow_html=True)
        mr = np.linspace(0.1, 1.8, 300)
        cdc = []
        for m in mr:
            if m < 0.8: c = TEJAS_DRAG_CD0 + 0.06*(m**2)
            elif m < 1.2: c = TEJAS_DRAG_CD0 + 0.06*(m**2) + 0.2*(m-0.8)**2
            else: c = TEJAS_DRAG_CD0 + 0.06*(m**2) + 0.015/(m**2)
            cdc.append(c)
        fig5 = go.Figure()
        fig5.add_vrect(x0=0.1, x1=0.8, fillcolor="rgba(74,222,128,0.03)", line_width=0,
            annotation_text="Subsonic", annotation_position="top left",
            annotation_font=dict(color='rgba(74,222,128,0.4)', size=9))
        fig5.add_vrect(x0=0.8, x1=1.2, fillcolor="rgba(255,153,51,0.03)", line_width=0,
            annotation_text="Transonic", annotation_position="top left",
            annotation_font=dict(color='rgba(255,153,51,0.4)', size=9))
        fig5.add_vrect(x0=1.2, x1=1.8, fillcolor="rgba(239,68,68,0.03)", line_width=0,
            annotation_text="Supersonic", annotation_position="top left",
            annotation_font=dict(color='rgba(239,68,68,0.4)', size=9))
        fig5.add_trace(go.Scatter(x=mr, y=cdc, mode='lines', line=dict(color=ACCENT, width=2.5), name='CD'))
        fig5.add_trace(go.Scatter(x=[mach], y=[cd], mode='markers', marker=dict(size=12, color=TEXT), name=f'CD={cd:.4f}'))
        plotly_layout(fig5, height=400)
        fig5.update_layout(xaxis=dict(title="Mach"), yaxis=dict(title="CD"))
        st.plotly_chart(fig5, use_container_width=True)
        with st.expander("What is drag coefficient?"):
            st.markdown("**Drag coefficient** measures air resistance. Watch it spike near Mach 1 — that's the **sound barrier** (transonic drag rise). Past Mach 1.2 it drops as the aircraft is fully supersonic. This spike is why breaking the sound barrier needs so much thrust.")

    with cd2:
        st.markdown('<p class="section-header">ISA Atmosphere Profile</p>', unsafe_allow_html=True)
        ap = np.linspace(0, 20000, 200)
        tp = [isa_atmosphere(a)[0] - 273.15 for a in ap]
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(x=tp, y=ap/1000, mode='lines', line=dict(color=ACCENT, width=2), name='Temperature'))
        fig6.add_trace(go.Scatter(x=[temp-273.15], y=[altitude/1000], mode='markers',
            marker=dict(size=10, color=TEXT, symbol='star'), name='You'))
        fig6.add_hline(y=11, line_dash="dot", line_color="rgba(255,153,51,0.3)",
            annotation_text="Tropopause (11 km)", annotation_font=dict(color=ACCENT, size=9))
        plotly_layout(fig6, height=400)
        fig6.update_layout(xaxis=dict(title="Temperature (°C)"), yaxis=dict(title="Altitude (km)"))
        st.plotly_chart(fig6, use_container_width=True)
        with st.expander("What is the ISA model?"):
            st.markdown("Temperature drops 6.5 C per km up to 11 km (**troposphere**), then stays flat at -56.5 C (**stratosphere**). This is the International Standard Atmosphere (ISA) — the global model pilots and engineers use to calculate aircraft performance.")

    if mach >= 1.0:
        st.markdown("---")
        st.markdown('<p class="section-header">Sonic Boom Ground Footprint</p>', unsafe_allow_html=True)
        ha2 = np.degrees(np.arcsin(1 / mach))
        bw = altitude * np.tan(np.radians(ha2)) * 2 / 1000
        gx = np.linspace(-bw/2, bw/2, 200)
        gi = np.exp(-2 * (gx / (bw/2))**2)
        bstr = 0.5 + 1.5 * (mach - 1.0)
        opg = bstr * gi * (1.225 / rho)**0.5
        fig7 = go.Figure()
        fig7.add_trace(go.Scatter(x=gx, y=opg, mode='lines', fill='tozeroy',
            line=dict(color=RED, width=2), fillcolor='rgba(239,68,68,0.1)'))
        fig7.add_annotation(x=0, y=max(opg), text=f"Peak ΔP ≈ {max(opg):.2f}<br>Width ≈ {bw:.1f} km",
            font=dict(color='#fca5a5', size=12, family='Rajdhani'), showarrow=True, arrowcolor=RED)
        plotly_layout(fig7, height=350)
        fig7.update_layout(xaxis=dict(title="Lateral Distance (km)"), yaxis=dict(title="Overpressure"))
        st.plotly_chart(fig7, use_container_width=True)
        with st.expander("How wide is the boom?"):
            st.markdown(f"Everyone inside this **{bw:.1f} km wide** strip on the ground hears the sonic boom. The peak is directly below the jet. Higher altitude = wider but weaker boom. Lower altitude = narrower but louder.")


# ================================================================
# CHANDRAYAAN 3
# ================================================================
elif page == "Chandrayaan 3":
    MU_EARTH = 3.986e14
    MU_MOON = 4.905e12
    R_EARTH = 6371
    R_MOON = 1737.4
    EARTH_MOON_DIST = 384400

    orbits = [
        {"name": "Parking Orbit", "perigee": 170, "apogee": 36500, "dv": 0, "date": "14 Jul 2023"},
        {"name": "Orbit Raise 1", "perigee": 173, "apogee": 41762, "dv": 38, "date": "15 Jul"},
        {"name": "Orbit Raise 2", "perigee": 226, "apogee": 41603, "dv": 25, "date": "17 Jul"},
        {"name": "Orbit Raise 3", "perigee": 228, "apogee": 51400, "dv": 42, "date": "18 Jul"},
        {"name": "Orbit Raise 4", "perigee": 233, "apogee": 71351, "dv": 35, "date": "20 Jul"},
        {"name": "Orbit Raise 5", "perigee": 236, "apogee": 127603, "dv": 50, "date": "25 Jul"},
        {"name": "Trans Lunar Injection", "perigee": 288, "apogee": 369328, "dv": 1090, "date": "1 Aug"},
    ]
    lunar_orbits = [
        {"name": "Lunar Orbit Insertion", "periselene": 164, "aposelene": 18074, "dv": 810, "date": "5 Aug"},
        {"name": "Lunar Orbit 2", "periselene": 170, "aposelene": 4313, "dv": 54, "date": "6 Aug"},
        {"name": "Lunar Orbit 3", "periselene": 174, "aposelene": 4313, "dv": 15, "date": "9 Aug"},
        {"name": "Circular Orbit", "periselene": 153, "aposelene": 163, "dv": 85, "date": "14 Aug"},
        {"name": "Pre-Landing Orbit", "periselene": 25, "aposelene": 134, "dv": 45, "date": "17 Aug"},
    ]

    st.sidebar.markdown('<p class="section-header">Chandrayaan 3</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">3,900 kg</span><span class="spec-label">Total Mass</span></div>
      <div class="spec-item"><span class="spec-val">LVM3</span><span class="spec-label">Launch Vehicle</span></div>
      <div class="spec-item"><span class="spec-val">1,752 kg</span><span class="spec-label">Propulsion Module</span></div>
      <div class="spec-item"><span class="spec-val">1,749.86 kg</span><span class="spec-label">Lander + Rover</span></div>
      <div class="spec-item"><span class="spec-val">26 kg</span><span class="spec-label">Pragyan Rover</span></div>
      <div class="spec-item"><span class="spec-val">40 days</span><span class="spec-label">Mission Duration</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    phase = st.sidebar.radio("Mission Phase", ["Earth Orbit Raising", "Lunar Orbit & Landing"], label_visibility="collapsed")

    st.markdown('<p class="section-header">Chandrayaan 3 — Lunar Landing Mission</p>', unsafe_allow_html=True)
    with st.expander("About Chandrayaan 3"):
        st.markdown("India's successful lunar landing mission. On **23 August 2023**, the Vikram lander touched down near the Moon's south pole, making India the **4th country** to soft-land on the Moon and the **1st to land near the south pole**. The Pragyan rover operated for 14 days, confirming the presence of sulphur on the lunar surface.")

    if phase == "Earth Orbit Raising":
        st.markdown('<div class="alert-box alert-info">Instead of flying directly to the Moon, ISRO gradually raised Earth orbit over 2 weeks. Each burn at perigee (closest point) stretches the apogee (farthest point) higher, until the spacecraft reaches lunar distance. This saves fuel compared to a direct shot.</div>', unsafe_allow_html=True)

        orbit_idx = st.slider("Mission Step", 0, len(orbits) - 1, 0,
            help="Step through each orbit raising maneuver")
        orb = orbits[orbit_idx]

        st.markdown(f"""
        <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
          <div class="hud-metric"><span class="value">{orb['name']}</span><span class="label">Maneuver</span></div>
          <div class="hud-metric"><span class="value">{orb['perigee']:,} km</span><span class="label">Perigee</span></div>
          <div class="hud-metric"><span class="value">{orb['apogee']:,} km</span><span class="label">Apogee</span></div>
          <div class="hud-metric"><span class="value">{orb['dv']} m/s</span><span class="label">Delta-v</span></div>
          <div class="hud-metric"><span class="value">{orb['date']}</span><span class="label">Date</span></div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("What is delta-v?"):
            st.markdown("Delta-v (change in velocity) is the currency of spaceflight. Every maneuver costs delta-v, and your fuel budget sets a hard limit. The vis-viva equation tells you the velocity at any point in an orbit: v = sqrt(GM * (2/r - 1/a)), where a is the semi-major axis.")

        fig_orb = go.Figure()
        theta = np.linspace(0, 2 * np.pi, 500)
        earth_x = R_EARTH * np.cos(theta)
        earth_y = R_EARTH * np.sin(theta)
        fig_orb.add_trace(go.Scatter(x=earth_x, y=earth_y, mode='lines',
            line=dict(color='#60a5fa', width=2), fill='toself',
            fillcolor='rgba(96,165,250,0.15)', name='Earth'))

        orbit_colors = ['rgba(255,153,51,0.25)', 'rgba(255,153,51,0.35)', 'rgba(255,153,51,0.45)',
                        'rgba(255,153,51,0.55)', 'rgba(255,153,51,0.65)', 'rgba(255,153,51,0.8)', ACCENT]

        for i, ob in enumerate(orbits[:orbit_idx + 1]):
            rp = R_EARTH + ob['perigee']
            ra = R_EARTH + ob['apogee']
            a = (rp + ra) / 2
            e = (ra - rp) / (ra + rp)
            r = a * (1 - e**2) / (1 + e * np.cos(theta))
            ox = r * np.cos(theta)
            oy = r * np.sin(theta)
            is_current = (i == orbit_idx)
            fig_orb.add_trace(go.Scatter(x=ox, y=oy, mode='lines',
                line=dict(color=orbit_colors[i], width=3 if is_current else 1.5,
                          dash='solid' if is_current else 'dot'),
                name=ob['name'], showlegend=is_current))

        if orbit_idx == len(orbits) - 1:
            moon_angle = np.pi * 0.3
            moon_x = EARTH_MOON_DIST * np.cos(moon_angle)
            moon_y = EARTH_MOON_DIST * np.sin(moon_angle)
            mc = R_MOON * 8 * np.cos(theta) + moon_x
            ms = R_MOON * 8 * np.sin(theta) + moon_y
            fig_orb.add_trace(go.Scatter(x=mc, y=ms, mode='lines',
                line=dict(color='#94a3b8', width=1.5), fill='toself',
                fillcolor='rgba(148,163,184,0.2)', name='Moon'))

        max_r = R_EARTH + orbits[orbit_idx]['apogee']
        pad = max_r * 0.15
        fig_orb.update_layout(
            title=dict(text=f"Earth Orbit: {orb['name']}",
                font=dict(color=CHART_TITLE, family='Archivo', size=14)),
            xaxis=dict(scaleanchor='y', range=[-max_r - pad, max_r + pad]),
            yaxis=dict(range=[-max_r - pad, max_r + pad]),
            showlegend=True, legend=dict(font=dict(color=MUTED, size=10)))
        plotly_layout(fig_orb, height=550)
        st.plotly_chart(fig_orb, use_container_width=True)

        with st.expander("Why raise orbits gradually?"):
            st.markdown("A single burn to the Moon would need enormous thrust. Instead, ISRO fires engines at perigee (closest point to Earth) for a few minutes each pass. Each burn stretches the orbit's far side (apogee) further out. After 5 raises, the apogee reaches 127,000+ km, and one final TLI burn sends the spacecraft on a trajectory that reaches the Moon's gravitational sphere of influence (~66,000 km from the Moon).")

        st.markdown('<p class="section-header">Delta-V Budget</p>', unsafe_allow_html=True)
        dv_names = [o['name'] for o in orbits[:orbit_idx + 1]]
        dv_vals = [o['dv'] for o in orbits[:orbit_idx + 1]]
        dv_cum = np.cumsum(dv_vals)
        fig_dv = go.Figure()
        fig_dv.add_trace(go.Bar(x=dv_names, y=dv_vals,
            marker=dict(color=[ACCENT if i == orbit_idx else 'rgba(255,153,51,0.4)' for i in range(len(dv_vals))]),
            text=[f'{v} m/s' for v in dv_vals], textposition='outside',
            textfont=dict(color=TEXT, size=11, family='JetBrains Mono'), name='Per Burn'))
        fig_dv.update_layout(
            title=dict(text="Delta-V per Maneuver",
                font=dict(color=CHART_TITLE, family='Archivo', size=13)),
            xaxis=dict(tickangle=-30), yaxis_title="Delta-V (m/s)")
        plotly_layout(fig_dv, height=380)
        st.plotly_chart(fig_dv, use_container_width=True)

        total_dv = sum(dv_vals)
        st.markdown(f"""
        <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
          <div class="hud-metric"><span class="value">{total_dv:,} m/s</span><span class="label">Total Delta-V Used</span></div>
          <div class="hud-metric"><span class="value">{orbit_idx + 1} / {len(orbits)}</span><span class="label">Burns Complete</span></div>
          <div class="hud-metric"><span class="value">{orb['apogee']:,} km</span><span class="label">Current Apogee</span></div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown('<div class="alert-box alert-info">After arriving at the Moon, Chandrayaan 3 fired engines to slow down and enter lunar orbit. Over several burns it circularized to a 100 km orbit, then lowered to 25 km perilune for the final powered descent to the surface.</div>', unsafe_allow_html=True)

        lunar_idx = st.slider("Lunar Phase", 0, len(lunar_orbits) - 1, 0,
            help="Step through lunar orbit maneuvers")
        lorb = lunar_orbits[lunar_idx]

        st.markdown(f"""
        <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
          <div class="hud-metric"><span class="value">{lorb['name']}</span><span class="label">Phase</span></div>
          <div class="hud-metric"><span class="value">{lorb['periselene']:,} km</span><span class="label">Periselene</span></div>
          <div class="hud-metric"><span class="value">{lorb['aposelene']:,} km</span><span class="label">Aposelene</span></div>
          <div class="hud-metric"><span class="value">{lorb['dv']} m/s</span><span class="label">Delta-v</span></div>
          <div class="hud-metric"><span class="value">{lorb['date']}</span><span class="label">Date</span></div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Periselene and aposelene?"):
            st.markdown("Same as perigee/apogee but for the Moon. Periselene = closest point to the lunar surface. Aposelene = farthest point. Named after Selene, the Greek Moon goddess.")

        fig_lunar = go.Figure()
        moon_surface_x = R_MOON * np.cos(theta)
        moon_surface_y = R_MOON * np.sin(theta)
        fig_lunar.add_trace(go.Scatter(x=moon_surface_x, y=moon_surface_y, mode='lines',
            line=dict(color='#94a3b8', width=2), fill='toself',
            fillcolor='rgba(148,163,184,0.15)', name='Moon'))

        lunar_colors = ['rgba(255,153,51,0.4)', 'rgba(255,153,51,0.5)', 'rgba(255,153,51,0.6)',
                        'rgba(74,222,128,0.6)', 'rgba(74,222,128,0.9)']

        for i, lo in enumerate(lunar_orbits[:lunar_idx + 1]):
            rp = R_MOON + lo['periselene']
            ra = R_MOON + lo['aposelene']
            a = (rp + ra) / 2
            e = (ra - rp) / (ra + rp)
            r = a * (1 - e**2) / (1 + e * np.cos(theta))
            ox = r * np.cos(theta)
            oy = r * np.sin(theta)
            is_current = (i == lunar_idx)
            fig_lunar.add_trace(go.Scatter(x=ox, y=oy, mode='lines',
                line=dict(color=lunar_colors[i], width=3 if is_current else 1.5,
                          dash='solid' if is_current else 'dot'),
                name=lo['name'], showlegend=is_current))

        if lunar_idx == len(lunar_orbits) - 1:
            land_angle = -np.pi / 2
            land_x = (R_MOON + 5) * np.cos(land_angle)
            land_y = (R_MOON + 5) * np.sin(land_angle)
            fig_lunar.add_trace(go.Scatter(x=[land_x], y=[land_y], mode='markers+text',
                marker=dict(size=12, color=GREEN, symbol='triangle-up'),
                text=['VIKRAM LANDING'], textposition='top center',
                textfont=dict(color=GREEN, size=11, family='Archivo'), showlegend=False))

        max_lr = R_MOON + lunar_orbits[lunar_idx]['aposelene']
        lpad = max_lr * 0.15
        fig_lunar.update_layout(
            title=dict(text=f"Lunar Orbit: {lorb['name']}",
                font=dict(color=CHART_TITLE, family='Archivo', size=14)),
            xaxis=dict(scaleanchor='y', range=[-max_lr - lpad, max_lr + lpad]),
            yaxis=dict(range=[-max_lr - lpad, max_lr + lpad]),
            showlegend=True, legend=dict(font=dict(color=MUTED, size=10)))
        plotly_layout(fig_lunar, height=550)
        st.plotly_chart(fig_lunar, use_container_width=True)

        st.markdown('<p class="section-header">Orbital Velocity</p>', unsafe_allow_html=True)
        rp_m = (R_MOON + lorb['periselene']) * 1000
        ra_m = (R_MOON + lorb['aposelene']) * 1000
        a_m = (rp_m + ra_m) / 2
        v_peri = np.sqrt(MU_MOON * (2 / rp_m - 1 / a_m))
        v_apo = np.sqrt(MU_MOON * (2 / ra_m - 1 / a_m))
        orbital_period = 2 * np.pi * np.sqrt(a_m**3 / MU_MOON)

        vc1, vc2 = st.columns(2)
        with vc1:
            angles = np.linspace(0, 2 * np.pi, 200)
            e_orb = (ra_m - rp_m) / (ra_m + rp_m)
            r_arr = a_m * (1 - e_orb**2) / (1 + e_orb * np.cos(angles))
            v_arr = np.sqrt(MU_MOON * (2 / r_arr - 1 / a_m))
            fig_vel = go.Figure()
            fig_vel.add_trace(go.Scatter(x=np.degrees(angles), y=v_arr,
                mode='lines', line=dict(color=GREEN, width=2.5), name='Velocity'))
            fig_vel.add_hline(y=v_peri, line_dash="dot", line_color="rgba(255,153,51,0.4)",
                annotation_text=f"Periselene: {v_peri:.0f} m/s",
                annotation_font=dict(color=ACCENT, size=9))
            fig_vel.add_hline(y=v_apo, line_dash="dot", line_color="rgba(148,163,184,0.4)",
                annotation_text=f"Aposelene: {v_apo:.0f} m/s",
                annotation_font=dict(color=MUTED, size=9))
            fig_vel.update_layout(title=dict(text="Velocity Around Orbit",
                font=dict(color=CHART_TITLE, family='Archivo', size=12)),
                xaxis_title="True Anomaly (degrees)", yaxis_title="Velocity (m/s)")
            plotly_layout(fig_vel, height=380)
            st.plotly_chart(fig_vel, use_container_width=True)
            with st.expander("Why does velocity change?"):
                st.markdown("In an elliptical orbit, the spacecraft moves fastest at periselene (closest to Moon) and slowest at aposelene (farthest). This is Kepler's second law: equal areas in equal times. The vis-viva equation gives the exact velocity at any point.")

        with vc2:
            dv_lunar_names = [o['name'] for o in lunar_orbits[:lunar_idx + 1]]
            dv_lunar_vals = [o['dv'] for o in lunar_orbits[:lunar_idx + 1]]
            fig_ldv = go.Figure()
            fig_ldv.add_trace(go.Bar(x=dv_lunar_names, y=dv_lunar_vals,
                marker=dict(color=[GREEN if i == lunar_idx else 'rgba(74,222,128,0.35)' for i in range(len(dv_lunar_vals))]),
                text=[f'{v} m/s' for v in dv_lunar_vals], textposition='outside',
                textfont=dict(color=TEXT, size=11, family='JetBrains Mono')))
            fig_ldv.update_layout(title=dict(text="Lunar Delta-V Budget",
                font=dict(color=CHART_TITLE, family='Archivo', size=12)),
                xaxis=dict(tickangle=-30), yaxis_title="Delta-V (m/s)")
            plotly_layout(fig_ldv, height=380)
            st.plotly_chart(fig_ldv, use_container_width=True)

        total_lunar_dv = sum(dv_lunar_vals)
        st.markdown(f"""
        <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
          <div class="hud-metric"><span class="value">{v_peri:.0f} m/s</span><span class="label">V at Periselene</span></div>
          <div class="hud-metric"><span class="value">{v_apo:.0f} m/s</span><span class="label">V at Aposelene</span></div>
          <div class="hud-metric"><span class="value">{orbital_period/60:.0f} min</span><span class="label">Orbital Period</span></div>
          <div class="hud-metric"><span class="value">{total_lunar_dv:,} m/s</span><span class="label">Total Lunar DV</span></div>
        </div>
        """, unsafe_allow_html=True)

        if lunar_idx == len(lunar_orbits) - 1:
            st.markdown("---")
            st.markdown('<p class="section-header">Powered Descent</p>', unsafe_allow_html=True)
            st.markdown('<div class="alert-box alert-boom">From 25 km altitude, Vikram fires its 4 throttleable engines (800N each) for a 19-minute powered descent. The lander drops from 1.68 km/s horizontal velocity to zero, hovering at 800m for hazard detection before final touchdown at < 2 m/s vertical speed.</div>', unsafe_allow_html=True)

            desc_time = np.linspace(0, 1140, 500)
            desc_alt = 25 * np.exp(-desc_time / 350) * (1 - 0.3 * (desc_time / 1140)**2)
            desc_alt = np.maximum(desc_alt, 0)
            desc_hvel = 1680 * (1 - (desc_time / 1140)**1.5)
            desc_hvel = np.maximum(desc_hvel, 0)

            dc1, dc2 = st.columns(2)
            with dc1:
                fig_da = go.Figure()
                fig_da.add_trace(go.Scatter(x=desc_time, y=desc_alt, mode='lines',
                    line=dict(color=ACCENT, width=3), name='Altitude'))
                fig_da.add_annotation(x=900, y=0.8, text="Hover @ 800m",
                    font=dict(color=YELLOW, size=10, family='Rajdhani'), showarrow=True, arrowcolor=YELLOW)
                fig_da.update_layout(title=dict(text="Descent Altitude Profile",
                    font=dict(color=CHART_TITLE, family='Archivo', size=12)),
                    xaxis_title="Time (s)", yaxis_title="Altitude (km)")
                plotly_layout(fig_da, height=380)
                st.plotly_chart(fig_da, use_container_width=True)

            with dc2:
                fig_dv2 = go.Figure()
                fig_dv2.add_trace(go.Scatter(x=desc_time, y=desc_hvel, mode='lines',
                    line=dict(color=RED, width=3), name='Horizontal Velocity'))
                fig_dv2.update_layout(title=dict(text="Velocity During Descent",
                    font=dict(color=CHART_TITLE, family='Archivo', size=12)),
                    xaxis_title="Time (s)", yaxis_title="Horizontal Velocity (m/s)")
                plotly_layout(fig_dv2, height=380)
                st.plotly_chart(fig_dv2, use_container_width=True)

            with st.expander("How does powered descent work?"):
                st.markdown("The hardest part of the mission. Vikram must kill 1.68 km/s of horizontal velocity while dropping 25 km, using only its onboard fuel and autonomous guidance. At 800m it hovers, scans the surface with hazard detection cameras, picks a safe spot, and descends vertically. The final 2 meters are in free fall at less than 2 m/s. Chandrayaan 2's Vikram lander failed at this exact phase in 2019.")

            st.markdown(f"""
            <div class="hud-card" style="text-align:center; padding:20px;">
              <span style="font-family:Archivo,sans-serif; font-size:1.2rem; font-weight:800; color:{GREEN}; letter-spacing:2px;">
              TOUCHDOWN: 23 AUGUST 2023, 18:04 IST</span><br>
              <span style="font-family:Rajdhani,sans-serif; font-size:1rem; color:#c0cfe0; letter-spacing:1px;">
              Shiv Shakti Point, 69.37 S, 32.35 E | South Polar Region</span>
            </div>
            """, unsafe_allow_html=True)


# ================================================================
# ISRO PSLV-XL
# ================================================================
elif page == "PSLV-XL":
    pslv = {
        "stages": [
            {"name": "PS1 + 6 Strap-ons", "thrust": 4846, "burn_time": 105, "mass_full": 295000, "mass_empty": 30000, "isp": 269},
            {"name": "PS2 (Vikas)", "thrust": 799, "burn_time": 158, "mass_full": 42000, "mass_empty": 5000, "isp": 293},
            {"name": "PS3 (Solid)", "thrust": 246, "burn_time": 112, "mass_full": 7600, "mass_empty": 1000, "isp": 294},
            {"name": "PS4 (Twin Engine)", "thrust": 15.2, "burn_time": 525, "mass_full": 2500, "mass_empty": 920, "isp": 318},
        ],
        "total_mass": 320000,
    }
    st.sidebar.markdown('<p class="section-header">PSLV-XL Specs</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">320 t</span><span class="spec-label">Liftoff Mass</span></div>
      <div class="spec-item"><span class="spec-val">44.4 m</span><span class="spec-label">Height</span></div>
      <div class="spec-item"><span class="spec-val">1,750 kg</span><span class="spec-label">Payload LEO</span></div>
      <div class="spec-item"><span class="spec-val">1,050 kg</span><span class="spec-label">Payload SSO</span></div>
      <div class="spec-item"><span class="spec-val">60+</span><span class="spec-label">Missions</span></div>
      <div class="spec-item"><span class="spec-val">4 stages</span><span class="spec-label">Configuration</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    show_stage_cards(pslv["stages"])
    st.markdown('<p class="section-header">ISRO PSLV-XL — Polar Satellite Launch Vehicle</p>', unsafe_allow_html=True)
    with st.expander("About PSLV"):
        st.markdown("ISRO's most reliable rocket with 60+ missions. PSLV launched Chandrayaan-1 (India's first Moon mission) and Mars Orbiter Mission (Mangalyaan). It uses a unique **alternating solid-liquid-solid-liquid** 4-stage design.")
    st.markdown('<div class="alert-box alert-info">A rocket has stages because fuel tanks are heavy — once empty, you drop them. Each dropped stage means less dead weight, so the remaining fuel accelerates you more efficiently.</div>', unsafe_allow_html=True)
    t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries = simulate_launch(pslv["stages"], pslv["total_mass"])
    show_launch_charts("PSLV-XL", t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries)


# ================================================================
# ISRO GSLV Mk III (LVM3)
# ================================================================
elif page == "GSLV Mk III (LVM3)":
    lvm3 = {
        "stages": [
            {"name": "S200 Boosters (x2)", "thrust": 5150, "burn_time": 130, "mass_full": 400000, "mass_empty": 62000, "isp": 274},
            {"name": "L110 (Vikas x2)", "thrust": 1598, "burn_time": 200, "mass_full": 116000, "mass_empty": 6700, "isp": 293},
            {"name": "C25 (CE-20 Cryo)", "thrust": 186, "burn_time": 584, "mass_full": 28000, "mass_empty": 3400, "isp": 443},
        ],
        "total_mass": 640000,
    }
    st.sidebar.markdown('<p class="section-header">LVM3 Specs</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">640 t</span><span class="spec-label">Liftoff Mass</span></div>
      <div class="spec-item"><span class="spec-val">43.4 m</span><span class="spec-label">Height</span></div>
      <div class="spec-item"><span class="spec-val">10,000 kg</span><span class="spec-label">Payload LEO</span></div>
      <div class="spec-item"><span class="spec-val">4,000 kg</span><span class="spec-label">Payload GTO</span></div>
      <div class="spec-item"><span class="spec-val">8+</span><span class="spec-label">Missions</span></div>
      <div class="spec-item"><span class="spec-val">3 stages</span><span class="spec-label">Configuration</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    show_stage_cards(lvm3["stages"])
    st.markdown('<p class="section-header">ISRO GSLV Mk III (LVM3) — India\'s Heavy-Lift Rocket</p>', unsafe_allow_html=True)
    with st.expander("About LVM3"):
        st.markdown("India's most powerful rocket. LVM3 launched Chandrayaan-3 (Moon landing, 2023) and will carry the **Gaganyaan** crew capsule for India's first human spaceflight. Its CE-20 cryogenic upper stage uses liquid hydrogen + oxygen — the most efficient chemical propulsion known.")
    st.markdown('<div class="alert-box alert-info"><b>Cryogenic engine (Isp 443s)</b> is nearly twice as fuel-efficient as solid motors (Isp ~270s). Isp (specific impulse) measures how many seconds one kg of fuel can produce one kg of thrust. Higher = better.</div>', unsafe_allow_html=True)
    t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries = simulate_launch(lvm3["stages"], lvm3["total_mass"])
    show_launch_charts("LVM3", t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries)


# ================================================================
# AGNIKUL COSMOS — AGNIBAAN
# ================================================================
elif page == "Agnikul Cosmos — Agnibaan":
    agnibaan = {
        "stages": [
            {"name": "Stage 1 (Agnilet Cluster)", "thrust": 120, "burn_time": 130, "mass_full": 10000, "mass_empty": 1200, "isp": 290},
            {"name": "Stage 2 (Agnilet)", "thrust": 25, "burn_time": 320, "mass_full": 3000, "mass_empty": 400, "isp": 310},
        ],
        "total_mass": 14000,
    }
    st.sidebar.markdown('<p class="section-header">Agnibaan Specs</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">14 t</span><span class="spec-label">Liftoff Mass</span></div>
      <div class="spec-item"><span class="spec-val">~18 m</span><span class="spec-label">Height</span></div>
      <div class="spec-item"><span class="spec-val">100 kg</span><span class="spec-label">Payload LEO</span></div>
      <div class="spec-item"><span class="spec-val">700 km</span><span class="spec-label">Target Orbit</span></div>
      <div class="spec-item"><span class="spec-val">2 stages</span><span class="spec-label">Configuration</span></div>
      <div class="spec-item"><span class="spec-val">Chennai</span><span class="spec-label">HQ</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    show_stage_cards(agnibaan["stages"])
    st.markdown('<p class="section-header">Agnikul Cosmos — Agnibaan Launch Vehicle</p>', unsafe_allow_html=True)
    with st.expander("About Agnikul Cosmos"):
        st.markdown("India's first private orbital rocket company, incubated at **IIT Madras**. Agnikul created the world's first **single-piece 3D-printed rocket engine** (Agnilet). Their SOrTeD sub-orbital test flight in May 2024 made history — the first private Indian rocket to launch from Indian soil.")
    with st.expander("What is a 3D-printed engine?"):
        st.markdown("Traditional rocket engines have 100+ parts welded together. Agnikul's Agnilet is printed as a single piece of metal — fewer failure points, faster to build, and cheaper. This could make space launches affordable for small satellites.")
    st.markdown('<div class="alert-box alert-transonic">Trajectory below is a simulation based on publicly available specifications. Agnibaan is still in development — actual flight data may differ.</div>', unsafe_allow_html=True)
    t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries = simulate_launch(agnibaan["stages"], agnibaan["total_mass"])
    show_launch_charts("Agnibaan", t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries)


# ================================================================
# SKYROOT — VIKRAM-1
# ================================================================
elif page == "Skyroot — Vikram-1":
    vikram1 = {
        "stages": [
            {"name": "Kalam-250 (Solid)", "thrust": 1000, "burn_time": 90, "mass_full": 36000, "mass_empty": 4000, "isp": 260},
            {"name": "Kalam-5 (Solid)", "thrust": 60, "burn_time": 115, "mass_full": 5500, "mass_empty": 700, "isp": 280},
            {"name": "Raman-2 (Liquid)", "thrust": 3.5, "burn_time": 420, "mass_full": 1500, "mass_empty": 300, "isp": 315},
        ],
        "total_mass": 55000,
    }
    st.sidebar.markdown('<p class="section-header">Vikram-1 Specs</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">55 t</span><span class="spec-label">Liftoff Mass</span></div>
      <div class="spec-item"><span class="spec-val">~24 m</span><span class="spec-label">Height</span></div>
      <div class="spec-item"><span class="spec-val">480 kg</span><span class="spec-label">Payload LEO</span></div>
      <div class="spec-item"><span class="spec-val">500 km</span><span class="spec-label">Target Orbit</span></div>
      <div class="spec-item"><span class="spec-val">3 stages</span><span class="spec-label">Configuration</span></div>
      <div class="spec-item"><span class="spec-val">Hyderabad</span><span class="spec-label">HQ</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    show_stage_cards(vikram1["stages"])
    st.markdown('<p class="section-header">Skyroot Aerospace — Vikram-1 Launch Vehicle</p>', unsafe_allow_html=True)
    with st.expander("About Skyroot"):
        st.markdown("Founded by ex-ISRO engineers, Skyroot launched **Vikram-S** in November 2022 — India's first-ever private rocket (mission \"Prarambh\", meaning \"The Beginning\"). Named after Dr. Vikram Sarabhai, the father of India's space programme. Their Raman upper-stage engine is also 3D-printed.")
    with st.expander("Why do private rockets matter?"):
        st.markdown("ISRO builds large rockets for government missions. Private companies like Skyroot build smaller, cheaper rockets for the booming small-satellite industry — companies need quick, affordable access to orbit for Earth observation, IoT, and telecom constellations.")
    st.markdown('<div class="alert-box alert-transonic">Trajectory below is a simulation based on publicly available specifications. Vikram-1 is still in development — actual flight data may differ.</div>', unsafe_allow_html=True)
    t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries = simulate_launch(vikram1["stages"], vikram1["total_mass"])
    show_launch_charts("Vikram-1", t_sim, alt_sim, vel_sim, acc_sim, mach_sim, stage_boundaries)


# ================================================================
# BRAHMOS MISSILE
# ================================================================
elif page == "BrahMos Missile":
    st.sidebar.markdown('<p class="section-header">BrahMos Controls</p>', unsafe_allow_html=True)
    brahmos_variant = st.sidebar.selectbox("Variant", ["BrahMos Block III", "BrahMos-II (Hypersonic)", "BrahMos-ER"],
        help="Block III: standard Mach 2.8 | ER: extended 800 km range | II: future Mach 7 hypersonic")
    specs = {
        "BrahMos Block III": {"speed_mach": 2.8, "range": 450, "weight": 3000, "warhead": 200, "altitude_cruise": 15000, "altitude_sea_skim": 10, "engine": "Ramjet"},
        "BrahMos-II (Hypersonic)": {"speed_mach": 7.0, "range": 600, "weight": 3500, "warhead": 200, "altitude_cruise": 40000, "altitude_sea_skim": 15, "engine": "Scramjet"},
        "BrahMos-ER": {"speed_mach": 2.8, "range": 800, "weight": 2800, "warhead": 200, "altitude_cruise": 15000, "altitude_sea_skim": 10, "engine": "Ramjet"},
    }
    sp = specs[brahmos_variant]
    target_range = st.sidebar.slider("Target Range (km)", 50, sp["range"], min(290, sp["range"]),
        help=f"Max range for {brahmos_variant}: {sp['range']} km")
    st.sidebar.markdown("---")
    st.sidebar.markdown('<p class="section-header">Specs</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">M {sp['speed_mach']}</span><span class="spec-label">Speed</span></div>
      <div class="spec-item"><span class="spec-val">{sp['range']} km</span><span class="spec-label">Range</span></div>
      <div class="spec-item"><span class="spec-val">{sp['weight']} kg</span><span class="spec-label">Weight</span></div>
      <div class="spec-item"><span class="spec-val">{sp['warhead']} kg</span><span class="spec-label">Warhead</span></div>
      <div class="spec-item"><span class="spec-val">{sp['engine']}</span><span class="spec-label">Engine</span></div>
      <div class="spec-item"><span class="spec-val">{sp['altitude_sea_skim']} m</span><span class="spec-label">Sea Skim</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<p class="section-header">BrahMos — World\'s Fastest Cruise Missile</p>', unsafe_allow_html=True)
    with st.expander("About BrahMos"):
        st.markdown(f"Joint India-Russia supersonic cruise missile. Named after rivers **Brahma**putra (India) and **Mos**kva (Russia). A **{sp['engine'].lower()}** engine sustains Mach {sp['speed_mach']} cruise speed — the fastest cruise missile in operational service.")
    cruise_alt = sp["altitude_cruise"]
    sea_skim_alt = sp["altitude_sea_skim"]
    cruise_speed = sp["speed_mach"] * 340
    climb_dist = min(target_range * 0.15, 40)
    dive_dist = min(target_range * 0.1, 30)
    cruise_dist = target_range - climb_dist - dive_dist
    n_pts = 500
    x_flight = np.linspace(0, target_range, n_pts)
    alt_flight = np.zeros(n_pts)
    for i, x in enumerate(x_flight):
        if x < climb_dist:
            frac = x / climb_dist
            alt_flight[i] = cruise_alt * (1 - np.cos(frac * np.pi / 2))
        elif x < climb_dist + cruise_dist:
            alt_flight[i] = cruise_alt
        else:
            frac = (x - climb_dist - cruise_dist) / dive_dist
            alt_flight[i] = cruise_alt * (1 - frac)**2
            if frac > 0.7:
                alt_flight[i] = max(alt_flight[i], sea_skim_alt)
    time_flight = x_flight * 1000 / cruise_speed
    fig_bm = go.Figure()
    fig_bm.add_trace(go.Scatter(x=x_flight, y=alt_flight/1000, mode='lines', fill='tozeroy',
        line=dict(color=RED, width=3), fillcolor='rgba(239,68,68,0.08)', name='Trajectory'))
    fig_bm.add_trace(go.Scatter(x=[0], y=[0], mode='markers+text',
        marker=dict(size=12, color=GREEN, symbol='triangle-up'),
        text=['LAUNCH'], textposition='top right', textfont=dict(color=GREEN, size=10, family='Archivo'), showlegend=False))
    fig_bm.add_trace(go.Scatter(x=[target_range], y=[0], mode='markers+text',
        marker=dict(size=14, color=RED, symbol='x'),
        text=['TARGET'], textposition='top left', textfont=dict(color=RED, size=10, family='Archivo'), showlegend=False))
    fig_bm.add_annotation(x=climb_dist + cruise_dist * 0.5, y=cruise_alt/1000 + 1,
        text=f"CRUISE: Mach {sp['speed_mach']} @ {cruise_alt/1000:.0f} km",
        font=dict(color=YELLOW, size=11, family='Rajdhani'), showarrow=False)
    fig_bm.update_layout(title=dict(text=f"{brahmos_variant} Flight Profile",
        font=dict(color=CHART_TITLE, family='Archivo', size=14)),
        xaxis_title="Range (km)", yaxis_title="Altitude (km)")
    plotly_layout(fig_bm, height=450)
    st.plotly_chart(fig_bm, use_container_width=True)
    with st.expander("Flight phases explained"):
        st.markdown(f"**3 phases:** (1) **Climb** — solid booster fires, missile climbs to {cruise_alt/1000:.0f} km, booster drops, {sp['engine'].lower()} ignites. (2) **Cruise** — sustained Mach {sp['speed_mach']} flight. (3) **Terminal dive** — missile drops to just {sea_skim_alt}m above sea (sea-skimming), nearly invisible to ship radar.")
    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">Mach {sp['speed_mach']}</span><span class="label">Speed</span></div>
      <div class="hud-metric"><span class="value">{cruise_speed:.0f} m/s</span><span class="label">Velocity</span></div>
      <div class="hud-metric"><span class="value">{cruise_speed*3.6:.0f}</span><span class="label">km/h</span></div>
      <div class="hud-metric"><span class="value">{time_flight[-1]:.0f}s</span><span class="label">Flight Time</span></div>
      <div class="hud-metric"><span class="value">{target_range} km</span><span class="label">Range</span></div>
      <div class="hud-metric"><span class="value">{sp['warhead']} kg</span><span class="label">Warhead</span></div>
    </div>
    """, unsafe_allow_html=True)
    react_time = dive_dist * 1000 / cruise_speed
    ke_tnt = 0.5 * sp['weight'] * cruise_speed**2 / 4.184e9
    st.markdown(f"""
    <div class="alert-box alert-boom">
    At {cruise_speed*3.6:.0f} km/h, a target at {target_range} km is hit in just <b>{time_flight[-1]:.0f} seconds</b>.
    A ship's defence system gets only <b>{react_time:.1f} seconds</b> to react in the terminal phase.
    Kinetic energy at impact ≈ <b>{ke_tnt:.1f} tonnes of TNT</b> — speed itself is a weapon.
    </div>
    """, unsafe_allow_html=True)
    if sp["engine"] == "Ramjet":
        with st.expander("How does a Ramjet work?"):
            st.markdown("A jet engine with zero moving parts. It uses the missile's own supersonic speed to ram-compress incoming air. Can't start from standstill (needs a booster first), but incredibly simple and powerful above Mach 2.")
    else:
        with st.expander("How does a Scramjet work?"):
            st.markdown("Supersonic Combustion Ramjet. Unlike a regular ramjet where air slows to subsonic inside the engine, a scramjet keeps airflow supersonic throughout. This enables Mach 5+ speeds but is extremely hard to engineer — fuel must ignite and burn in milliseconds.")


# ================================================================
# AMCA STEALTH FIGHTER
# ================================================================
elif page == "AMCA Stealth Fighter":
    st.sidebar.markdown('<p class="section-header">AMCA Controls</p>', unsafe_allow_html=True)
    radar_power_kw = st.sidebar.slider("Radar Power (kW)", 1, 200, 50,
        help="Transmitted power of the detecting radar system")
    radar_freq_ghz = st.sidebar.slider("Radar Frequency (GHz)", 1.0, 18.0, 10.0, 0.5,
        help="X-band (8-12 GHz) is most common for fighter radars")

    st.sidebar.markdown("---")
    st.sidebar.markdown('<p class="section-header">AMCA Specs</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">5th Gen</span><span class="spec-label">Generation</span></div>
      <div class="spec-item"><span class="spec-val">25 t</span><span class="spec-label">MTOW</span></div>
      <div class="spec-item"><span class="spec-val">M 1.8+</span><span class="spec-label">Max Speed</span></div>
      <div class="spec-item"><span class="spec-val">Twin</span><span class="spec-label">Engines</span></div>
      <div class="spec-item"><span class="spec-val">Internal</span><span class="spec-label">Weapons Bay</span></div>
      <div class="spec-item"><span class="spec-val">HAL/ADA</span><span class="spec-label">Developer</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">AMCA — Advanced Medium Combat Aircraft</p>', unsafe_allow_html=True)
    with st.expander("About AMCA"):
        st.markdown("India's upcoming 5th generation stealth fighter, designed by ADA (Aeronautical Development Agency) and HAL. Features internal weapons bays, radar-absorbent materials, and a planform designed to minimize radar cross section. First flight expected around 2025-2026. Will make India the 4th country to develop a domestic stealth fighter.")

    aircraft_data = [
        {"name": "Su-30MKI", "rcs": 10.0, "color": "#94a3b8", "gen": "4th Gen"},
        {"name": "HAL Tejas", "rcs": 1.5, "color": ACCENT, "gen": "4.5 Gen"},
        {"name": "Rafale", "rcs": 1.0, "color": "#60a5fa", "gen": "4.5 Gen"},
        {"name": "AMCA", "rcs": 0.1, "color": GREEN, "gen": "5th Gen"},
        {"name": "F-22 Raptor", "rcs": 0.0001, "color": RED, "gen": "5th Gen"},
        {"name": "F-35", "rcs": 0.001, "color": YELLOW, "gen": "5th Gen"},
    ]

    st.markdown('<div class="alert-box alert-info">Radar Cross Section (RCS) measures how visible an aircraft is to radar, in square metres. A smaller RCS means the aircraft appears as a much smaller target. Stealth aircraft use special shaping and materials to scatter radar waves away from the receiver.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-header">RCS Comparison (Log Scale)</p>', unsafe_allow_html=True)
        fig_rcs = go.Figure()
        names = [a['name'] for a in aircraft_data]
        rcs_vals = [a['rcs'] for a in aircraft_data]
        colors = [a['color'] for a in aircraft_data]
        fig_rcs.add_trace(go.Bar(y=names, x=rcs_vals, orientation='h',
            marker=dict(color=colors),
            text=[f'{v} m²' for v in rcs_vals], textposition='outside',
            textfont=dict(color=TEXT, size=11, family='JetBrains Mono')))
        fig_rcs.update_layout(xaxis=dict(type='log', title='RCS (m², log scale)'),
            yaxis=dict(autorange='reversed'))
        plotly_layout(fig_rcs, height=400)
        fig_rcs.update_layout(margin=dict(l=100, r=80))
        st.plotly_chart(fig_rcs, use_container_width=True)
        with st.expander("Why log scale?"):
            st.markdown("RCS values span 5 orders of magnitude: from 10 m² (Su-30) down to 0.0001 m² (F-22). A log scale lets you see all of them on one chart. Each grid line is 10x smaller than the previous one.")

    with col2:
        st.markdown('<p class="section-header">Radar Detection Range</p>', unsafe_allow_html=True)
        wavelength = 3e8 / (radar_freq_ghz * 1e9)
        gain = 30
        smin = 1e-13
        detect_ranges = []
        for a in aircraft_data:
            r4 = (radar_power_kw * 1000 * (10**(gain/10))**2 * wavelength**2 * a['rcs']) / ((4 * np.pi)**3 * smin)
            detect_ranges.append(r4**0.25 / 1000)
        fig_det = go.Figure()
        fig_det.add_trace(go.Bar(y=names, x=detect_ranges, orientation='h',
            marker=dict(color=colors),
            text=[f'{v:.0f} km' for v in detect_ranges], textposition='outside',
            textfont=dict(color=TEXT, size=11, family='JetBrains Mono')))
        fig_det.update_layout(xaxis=dict(title='Detection Range (km)'),
            yaxis=dict(autorange='reversed'))
        plotly_layout(fig_det, height=400)
        fig_det.update_layout(margin=dict(l=100, r=80))
        st.plotly_chart(fig_det, use_container_width=True)
        with st.expander("What is detection range?"):
            st.markdown(f"Using the radar equation with {radar_power_kw} kW at {radar_freq_ghz} GHz. Detection range scales with the **4th root** of RCS — so you need to reduce RCS by 16x to halve the detection distance. AMCA's low RCS means an enemy radar detects it much later than a conventional fighter.")

    st.markdown("---")
    st.markdown('<p class="section-header">Angular RCS Pattern</p>', unsafe_allow_html=True)
    angles = np.linspace(0, 360, 720)
    angles_rad = np.radians(angles)
    rcs_tejas = 1.5 * (1 + 0.8 * np.abs(np.cos(angles_rad)) + 2.5 * np.exp(-((angles - 0)**2) / 200) +
                 2.5 * np.exp(-((angles - 360)**2) / 200) + 1.5 * np.exp(-((angles - 180)**2) / 300))
    rcs_amca = 0.1 * (1 + 0.3 * np.abs(np.cos(angles_rad)) + 0.8 * np.exp(-((angles - 0)**2) / 100) +
                0.8 * np.exp(-((angles - 360)**2) / 100) + 0.5 * np.exp(-((angles - 180)**2) / 150))
    fig_ang = go.Figure()
    fig_ang.add_trace(go.Scatterpolar(r=rcs_tejas, theta=angles, mode='lines',
        line=dict(color=ACCENT, width=2), name='HAL Tejas', fill='toself',
        fillcolor='rgba(255,153,51,0.08)'))
    fig_ang.add_trace(go.Scatterpolar(r=rcs_amca, theta=angles, mode='lines',
        line=dict(color=GREEN, width=2), name='AMCA', fill='toself',
        fillcolor='rgba(74,222,128,0.08)'))
    fig_ang.update_layout(
        polar=dict(bgcolor=CHART_BG, radialaxis=dict(type='log', color=CHART_AXIS, gridcolor=CHART_GRID),
                   angularaxis=dict(color=CHART_AXIS, gridcolor=CHART_GRID)),
        paper_bgcolor='rgba(0,0,0,0)', height=500, showlegend=True,
        legend=dict(font=dict(color=MUTED, size=11)),
        title=dict(text="RCS vs Aspect Angle (Tejas vs AMCA)", font=dict(color=CHART_TITLE, family='Archivo', size=14)))
    st.plotly_chart(fig_ang, use_container_width=True)
    with st.expander("Reading the radar pattern"):
        st.markdown("0° is head-on (nose), 180° is tail-on. Stealth aircraft are designed to minimize the frontal RCS since that's the angle an enemy sees first. AMCA's angular shaping deflects radar energy to the sides instead of bouncing it back. Notice how AMCA's pattern is dramatically smaller than Tejas at every angle.")

    tejas_detect = detect_ranges[1]
    amca_detect = detect_ranges[3]
    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">{aircraft_data[1]['rcs']} m²</span><span class="label">Tejas RCS</span></div>
      <div class="hud-metric"><span class="value">{aircraft_data[3]['rcs']} m²</span><span class="label">AMCA RCS</span></div>
      <div class="hud-metric"><span class="value">{aircraft_data[1]['rcs']/aircraft_data[3]['rcs']:.0f}x</span><span class="label">RCS Reduction</span></div>
      <div class="hud-metric"><span class="value">{tejas_detect:.0f} km</span><span class="label">Tejas Detected</span></div>
      <div class="hud-metric"><span class="value">{amca_detect:.0f} km</span><span class="label">AMCA Detected</span></div>
      <div class="hud-metric"><span class="value">{tejas_detect - amca_detect:.0f} km</span><span class="label">Stealth Advantage</span></div>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# AKASH MISSILE
# ================================================================
elif page == "Akash Missile":
    st.sidebar.markdown('<p class="section-header">Akash Controls</p>', unsafe_allow_html=True)
    target_alt_km = st.sidebar.slider("Target Altitude (km)", 0.1, 20.0, 8.0, 0.1,
        help="Altitude of the incoming aircraft/missile")
    target_speed_mach = st.sidebar.slider("Target Speed (Mach)", 0.5, 3.5, 1.2, 0.1,
        help="Speed of the incoming threat")
    target_range_km = st.sidebar.slider("Target Range (km)", 5, 30, 20,
        help="Distance to target at launch")

    st.sidebar.markdown("---")
    st.sidebar.markdown('<p class="section-header">Akash Specs</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">M 2.5</span><span class="spec-label">Speed</span></div>
      <div class="spec-item"><span class="spec-val">30 km</span><span class="spec-label">Range</span></div>
      <div class="spec-item"><span class="spec-val">20 km</span><span class="spec-label">Ceiling</span></div>
      <div class="spec-item"><span class="spec-val">720 kg</span><span class="spec-label">Weight</span></div>
      <div class="spec-item"><span class="spec-val">Ramjet</span><span class="spec-label">Engine</span></div>
      <div class="spec-item"><span class="spec-val">DRDO</span><span class="spec-label">Developer</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Akash — Surface to Air Missile System</p>', unsafe_allow_html=True)
    with st.expander("About Akash"):
        st.markdown("India's indigenous medium-range surface-to-air missile, developed by DRDO. Uses a ramjet sustainer for sustained Mach 2.5 flight. The Rajendra phased array radar tracks multiple targets simultaneously. Akash can engage targets from treetop height up to 20 km altitude, out to 30 km range. In service with both the Indian Army and Air Force.")

    akash_speed = 2.5 * 340
    target_speed = target_speed_mach * 340
    n_pts = 300
    t_max = target_range_km * 1000 / akash_speed * 1.3
    t_arr = np.linspace(0, t_max, n_pts)

    akash_x = np.zeros(n_pts)
    akash_y = np.zeros(n_pts)
    target_x = np.full(n_pts, target_range_km)
    target_y = np.full(n_pts, target_alt_km)

    closing_speed = akash_speed + target_speed * 0.3
    t_intercept = target_range_km * 1000 / closing_speed
    intercept_x = target_range_km - target_speed * 0.3 * t_intercept / 1000
    intercept_y = target_alt_km

    for i, t in enumerate(t_arr):
        frac = min(t / t_intercept, 1.0)
        akash_x[i] = intercept_x * (1 - (1 - frac)**1.2) * frac**0.3 + intercept_x * frac**1.5 * 0.3
        akash_x[i] = min(intercept_x * frac**0.8 + intercept_x * 0.2 * frac**2, intercept_x)
        climb_frac = min(frac * 1.5, 1.0)
        akash_y[i] = intercept_y * (1 - np.cos(climb_frac * np.pi / 2))
        target_x[i] = target_range_km - target_speed * 0.3 * t / 1000

    st.markdown('<div class="alert-box alert-info">Akash uses proportional navigation: instead of flying straight at the target, it flies toward where the target will be. The missile continuously adjusts its heading to keep the line-of-sight rotation rate at zero, guaranteeing intercept.</div>', unsafe_allow_html=True)

    fig_int = go.Figure()
    fig_int.add_trace(go.Scatter(x=akash_x, y=akash_y, mode='lines',
        line=dict(color=GREEN, width=3), name='Akash Missile'))
    fig_int.add_trace(go.Scatter(x=target_x, y=target_y, mode='lines',
        line=dict(color=RED, width=2, dash='dash'), name='Target'))
    fig_int.add_trace(go.Scatter(x=[0], y=[0], mode='markers+text',
        marker=dict(size=12, color=ACCENT, symbol='triangle-up'),
        text=['LAUNCH'], textposition='top right',
        textfont=dict(color=ACCENT, size=10, family='Archivo'), showlegend=False))
    fig_int.add_trace(go.Scatter(x=[intercept_x], y=[intercept_y], mode='markers+text',
        marker=dict(size=14, color=YELLOW, symbol='star'),
        text=['INTERCEPT'], textposition='top left',
        textfont=dict(color=YELLOW, size=11, family='Archivo'), showlegend=False))
    fig_int.update_layout(title=dict(text="Intercept Trajectory",
        font=dict(color=CHART_TITLE, family='Archivo', size=14)),
        xaxis_title="Range (km)", yaxis_title="Altitude (km)")
    plotly_layout(fig_int, height=450)
    st.plotly_chart(fig_int, use_container_width=True)

    with st.expander("Proportional navigation explained"):
        st.markdown("The missile measures the angle to the target (line of sight). If the angle is changing, the missile turns proportionally to kill that rotation. When the angle stops changing, the missile is on a collision course. This is mathematically proven to be the optimal guidance law for constant-speed engagements.")

    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">{t_intercept:.1f}s</span><span class="label">Time to Intercept</span></div>
      <div class="hud-metric"><span class="value">{akash_speed:.0f} m/s</span><span class="label">Missile Speed</span></div>
      <div class="hud-metric"><span class="value">{target_speed:.0f} m/s</span><span class="label">Target Speed</span></div>
      <div class="hud-metric"><span class="value">{intercept_x:.1f} km</span><span class="label">Intercept Range</span></div>
      <div class="hud-metric"><span class="value">{intercept_y:.1f} km</span><span class="label">Intercept Alt</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p class="section-header">Kill Envelope</p>', unsafe_allow_html=True)
    env_ranges = np.linspace(0, 35, 200)
    max_alt_env = np.zeros_like(env_ranges)
    min_alt_env = np.zeros_like(env_ranges)
    for i, r in enumerate(env_ranges):
        if r <= 30:
            max_alt_env[i] = 20 * np.sqrt(1 - (max(r - 5, 0) / 25)**2) if r <= 30 else 0
            min_alt_env[i] = 0.05 if r <= 25 else 0.05 + (r - 25) * 0.4
        else:
            max_alt_env[i] = 0
            min_alt_env[i] = 0
    valid = max_alt_env > min_alt_env
    fig_env = go.Figure()
    fig_env.add_trace(go.Scatter(x=env_ranges[valid], y=max_alt_env[valid], mode='lines',
        line=dict(color=GREEN, width=2), name='Max Altitude'))
    fig_env.add_trace(go.Scatter(x=env_ranges[valid], y=min_alt_env[valid], mode='lines',
        line=dict(color=GREEN, width=2), fill='tonexty', fillcolor='rgba(74,222,128,0.1)', name='Min Altitude'))
    in_envelope = target_range_km <= 30 and target_alt_km <= 20
    marker_color = GREEN if in_envelope else RED
    fig_env.add_trace(go.Scatter(x=[target_range_km], y=[target_alt_km], mode='markers+text',
        marker=dict(size=14, color=marker_color, symbol='x'),
        text=['TARGET'], textposition='top right',
        textfont=dict(color=marker_color, size=11, family='Archivo'), showlegend=False))
    fig_env.update_layout(title=dict(text="Akash Kill Envelope",
        font=dict(color=CHART_TITLE, family='Archivo', size=14)),
        xaxis_title="Range (km)", yaxis_title="Altitude (km)")
    plotly_layout(fig_env, height=400)
    st.plotly_chart(fig_env, use_container_width=True)
    env_status = "INSIDE KILL ZONE" if in_envelope else "OUTSIDE ENVELOPE"
    env_class = "alert-boom" if in_envelope else "alert-normal"
    st.markdown(f'<div class="alert-box {env_class}">Target is <b>{env_status}</b> at {target_range_km} km range, {target_alt_km} km altitude</div>', unsafe_allow_html=True)
    with st.expander("What is a kill envelope?"):
        st.markdown("The green zone is where Akash can successfully intercept a target. Outside it: too far, too high, too low, or too fast. The envelope shape comes from the missile's speed, fuel, and manoeuvrability limits. Moving the target sliders shows whether a given threat is engageable.")


# ================================================================
# GAGANYAAN RE-ENTRY
# ================================================================
elif page == "Gaganyaan Re-entry":
    st.sidebar.markdown('<p class="section-header">Gaganyaan Controls</p>', unsafe_allow_html=True)
    entry_angle = st.sidebar.slider("Entry Angle (degrees)", -2.0, -8.0, -5.5, 0.1,
        help="Steeper = higher G-force and heating. Shallower = risk of skip-off.")
    orbit_alt = st.sidebar.slider("Orbit Altitude (km)", 300, 500, 400, 10,
        help="Gaganyaan target orbit: 400 km LEO")

    st.sidebar.markdown("---")
    st.sidebar.markdown('<p class="section-header">Gaganyaan Specs</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">3 crew</span><span class="spec-label">Capacity</span></div>
      <div class="spec-item"><span class="spec-val">8,200 kg</span><span class="spec-label">Module Mass</span></div>
      <div class="spec-item"><span class="spec-val">LVM3</span><span class="spec-label">Launch Vehicle</span></div>
      <div class="spec-item"><span class="spec-val">400 km</span><span class="spec-label">Target Orbit</span></div>
      <div class="spec-item"><span class="spec-val">7 days</span><span class="spec-label">Mission Duration</span></div>
      <div class="spec-item"><span class="spec-val">ISRO</span><span class="spec-label">Developer</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Gaganyaan — India\'s Human Spaceflight Programme</p>', unsafe_allow_html=True)
    with st.expander("About Gaganyaan"):
        st.markdown("India's first crewed spacecraft. The Crew Module is designed to carry 3 astronauts (called Vyomanauts) to low Earth orbit. The most critical phase is re-entry: the capsule hits the atmosphere at 7.8 km/s (28,000 km/h) and must decelerate to parachute speed without exceeding 4G or letting the heat shield temperature breach limits. Two uncrewed test flights (TV-D1 in Oct 2023 successfully tested the crew escape system) precede the crewed mission.")

    MU_E = 3.986e14
    R_E = 6.371e6
    v_orbit = np.sqrt(MU_E / (R_E + orbit_alt * 1000))
    v_entry = v_orbit * 0.99

    dt = 0.5
    alt, vel, gamma = orbit_alt * 1000, v_entry, np.radians(entry_angle)
    mass, cd, area, cl = 5000, 1.2, 5.0, 0.3
    nose_r = 1.0
    t_log, alt_log, vel_log, g_log, heat_log, temp_log, mach_log = [0], [alt/1000], [vel], [0], [0], [300], [vel/340]
    drogue_deployed, main_deployed = False, False
    drogue_t, main_t = None, None
    t = 0
    while alt > 0 and t < 2000:
        t += dt
        _, _, rho, a = isa_atmosphere(min(max(alt, 0), 20000)) if alt < 85000 else (200, 0.01, 1.225 * np.exp(-alt / 8500), 295)
        if alt >= 85000:
            rho = 1.225 * np.exp(-alt / 8500)
        q = 0.5 * rho * vel**2
        drag = q * cd * area
        lift = q * cl * area
        g_local = 9.81 * (R_E / (R_E + alt))**2
        if not drogue_deployed and alt < 15000 and vel < 200:
            drogue_deployed = True
            drogue_t = t
            cd = 2.5
            area = 15.0
            cl = 0
        if not main_deployed and alt < 5000 and vel < 80:
            main_deployed = True
            main_t = t
            cd = 3.5
            area = 50.0
        ax = -drag / mass - g_local * np.sin(gamma)
        ay = lift / mass - g_local * np.cos(gamma) + vel * np.cos(gamma) * vel / (R_E + alt)
        vel = max(vel + ax * dt, 0)
        if vel > 0:
            gamma = gamma + (ay / vel) * dt
        alt = alt + vel * np.sin(gamma) * dt
        g_force = abs(ax / 9.81)
        heat_flux = 1.83e-4 * np.sqrt(rho / nose_r) * vel**3 / 1e6
        stag_temp = 300 + heat_flux * 200
        t_log.append(t)
        alt_log.append(max(alt / 1000, 0))
        vel_log.append(vel)
        g_log.append(g_force)
        heat_log.append(heat_flux)
        temp_log.append(min(stag_temp, 3500))
        mach_log.append(vel / max(a, 295))
        if alt <= 0:
            break

    st.markdown(f'<div class="alert-box alert-boom">Entry velocity: <b>{v_entry:.0f} m/s</b> ({v_entry*3.6:.0f} km/h) at {entry_angle}° angle. The capsule must shed 99.9% of its kinetic energy as heat before parachute deployment.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_alt = go.Figure()
        fig_alt.add_trace(go.Scatter(x=t_log, y=alt_log, mode='lines',
            line=dict(color=ACCENT, width=3), name='Altitude'))
        if drogue_t:
            fig_alt.add_vline(x=drogue_t, line_dash="dot", line_color="rgba(74,222,128,0.4)")
            fig_alt.add_annotation(x=drogue_t, y=15, text="Drogue",
                font=dict(color=GREEN, size=9, family='Rajdhani'), showarrow=True, arrowcolor=GREEN)
        if main_t:
            fig_alt.add_vline(x=main_t, line_dash="dot", line_color="rgba(96,165,250,0.4)")
            fig_alt.add_annotation(x=main_t, y=5, text="Main Chute",
                font=dict(color='#60a5fa', size=9, family='Rajdhani'), showarrow=True, arrowcolor='#60a5fa')
        fig_alt.update_layout(title=dict(text="Re-entry Altitude Profile",
            font=dict(color=CHART_TITLE, family='Archivo', size=12)),
            xaxis_title="Time (s)", yaxis_title="Altitude (km)")
        plotly_layout(fig_alt, height=380)
        st.plotly_chart(fig_alt, use_container_width=True)

    with c2:
        fig_vel2 = go.Figure()
        fig_vel2.add_trace(go.Scatter(x=t_log, y=[v/1000 for v in vel_log], mode='lines',
            line=dict(color=RED, width=3), name='Velocity'))
        fig_vel2.update_layout(title=dict(text="Velocity During Re-entry",
            font=dict(color=CHART_TITLE, family='Archivo', size=12)),
            xaxis_title="Time (s)", yaxis_title="Velocity (km/s)")
        plotly_layout(fig_vel2, height=380)
        st.plotly_chart(fig_vel2, use_container_width=True)

    with st.expander("Why is re-entry so dangerous?"):
        st.markdown(f"At {v_entry:.0f} m/s, the capsule has kinetic energy equivalent to roughly {0.5 * mass * v_entry**2 / 4.184e9:.0f} tonnes of TNT. All of this must be converted to heat by air friction. The heat shield ablates (burns away in a controlled manner), carrying heat away from the capsule. If the entry angle is too steep, G-forces could injure the crew. Too shallow, and the capsule bounces off the atmosphere like a stone skipping on water.")

    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<p class="section-header">G-Force on Crew</p>', unsafe_allow_html=True)
        fig_gf = go.Figure()
        fig_gf.add_trace(go.Scatter(x=t_log, y=g_log, mode='lines',
            line=dict(color=YELLOW, width=2.5), name='G-force'))
        fig_gf.add_hline(y=4, line_dash="dash", line_color="rgba(239,68,68,0.4)",
            annotation_text="Crew limit ~4G", annotation_font=dict(color=RED, size=9))
        fig_gf.update_layout(title=dict(text="G-Force Profile",
            font=dict(color=CHART_TITLE, family='Archivo', size=12)),
            xaxis_title="Time (s)", yaxis_title="G-force")
        plotly_layout(fig_gf, height=380)
        st.plotly_chart(fig_gf, use_container_width=True)
        with st.expander("About G-force during re-entry"):
            st.markdown(f"Peak G-force: **{max(g_log):.1f}G**. Gaganyaan is designed for max 4G. Apollo astronauts experienced up to 6.5G. The entry angle directly controls peak G: steeper = higher G but shorter duration. Try adjusting the angle slider to see the tradeoff.")

    with c4:
        st.markdown('<p class="section-header">Heat Shield Temperature</p>', unsafe_allow_html=True)
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=t_log, y=temp_log, mode='lines',
            line=dict(color=RED, width=2.5), name='Stagnation Temp'))
        fig_temp.add_hline(y=2000, line_dash="dash", line_color="rgba(255,153,51,0.4)",
            annotation_text="Carbon phenolic limit ~2000°C", annotation_font=dict(color=ACCENT, size=9))
        fig_temp.update_layout(title=dict(text="Stagnation Point Temperature",
            font=dict(color=CHART_TITLE, family='Archivo', size=12)),
            xaxis_title="Time (s)", yaxis_title="Temperature (°C)")
        plotly_layout(fig_temp, height=380)
        st.plotly_chart(fig_temp, use_container_width=True)
        with st.expander("About heat shield temperature"):
            st.markdown(f"Peak temperature: **{max(temp_log):.0f}°C**. The Gaganyaan heat shield uses carbon-phenolic ablative material that can withstand up to ~2000°C. The surface material chars and vaporises, carrying heat away. The stagnation point (very tip of the shield) gets hottest because air compresses there the most.")

    peak_g = max(g_log)
    peak_temp = max(temp_log)
    peak_heat = max(heat_log)
    landing_vel = vel_log[-1]
    total_time = t_log[-1]
    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">{v_entry:.0f} m/s</span><span class="label">Entry Velocity</span></div>
      <div class="hud-metric"><span class="value">{peak_g:.1f}G</span><span class="label">Peak G-Force</span></div>
      <div class="hud-metric"><span class="value">{peak_temp:.0f}°C</span><span class="label">Peak Temp</span></div>
      <div class="hud-metric"><span class="value">{peak_heat:.1f} MW/m²</span><span class="label">Peak Heat Flux</span></div>
      <div class="hud-metric"><span class="value">{landing_vel:.1f} m/s</span><span class="label">Landing Speed</span></div>
      <div class="hud-metric"><span class="value">{total_time:.0f}s</span><span class="label">Total Time</span></div>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# COMPARE PLATFORMS
# ================================================================
elif page == "Compare Platforms":
    st.markdown('<p class="section-header">Compare Platforms</p>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-info">Select two platforms to compare their key specifications and performance side by side.</div>', unsafe_allow_html=True)

    platform_specs = {
        "HAL Tejas Mk1A": {"type": "Fighter", "speed_ms": 1.8*340, "range_km": 3000, "mass_kg": 9800, "ceiling_km": 16.5, "thrust_kn": 89, "origin": "HAL/ADA"},
        "BrahMos Block III": {"type": "Cruise Missile", "speed_ms": 2.8*340, "range_km": 450, "mass_kg": 3000, "ceiling_km": 15, "thrust_kn": 0, "origin": "BrahMos Aerospace"},
        "AMCA": {"type": "Stealth Fighter", "speed_ms": 1.8*340, "range_km": 3500, "mass_kg": 25000, "ceiling_km": 20, "thrust_kn": 200, "origin": "HAL/ADA"},
        "Akash": {"type": "SAM", "speed_ms": 2.5*340, "range_km": 30, "mass_kg": 720, "ceiling_km": 20, "thrust_kn": 0, "origin": "DRDO"},
        "PSLV-XL": {"type": "Launch Vehicle", "speed_ms": 7800, "range_km": 0, "mass_kg": 320000, "ceiling_km": 600, "thrust_kn": 4846, "origin": "ISRO"},
        "GSLV Mk III": {"type": "Heavy Lift LV", "speed_ms": 7900, "range_km": 0, "mass_kg": 640000, "ceiling_km": 600, "thrust_kn": 5150, "origin": "ISRO"},
        "Agnibaan": {"type": "Small Sat LV", "speed_ms": 7500, "range_km": 0, "mass_kg": 14000, "ceiling_km": 700, "thrust_kn": 120, "origin": "Agnikul Cosmos"},
        "Vikram-1": {"type": "Small Sat LV", "speed_ms": 7600, "range_km": 0, "mass_kg": 55000, "ceiling_km": 500, "thrust_kn": 1000, "origin": "Skyroot"},
    }
    names_list = list(platform_specs.keys())
    cc1, cc2 = st.columns(2)
    with cc1:
        p1 = st.selectbox("Platform 1", names_list, index=0)
    with cc2:
        p2 = st.selectbox("Platform 2", names_list, index=4)

    s1, s2 = platform_specs[p1], platform_specs[p2]

    st.markdown(f"""
    <div class="hud-card">
      <div style="display:grid; grid-template-columns:1fr auto 1fr; gap:10px; font-family:Rajdhani,sans-serif;">
        <div style="text-align:center;"><span style="font-family:Archivo; color:{ACCENT}; font-weight:800; font-size:1.1rem;">{p1}</span><br><span style="color:{MUTED}; font-size:0.8rem;">{s1['type']} | {s1['origin']}</span></div>
        <div style="text-align:center; color:{MUTED}; font-size:1.5rem; padding-top:5px;">vs</div>
        <div style="text-align:center;"><span style="font-family:Archivo; color:{GREEN}; font-weight:800; font-size:1.1rem;">{p2}</span><br><span style="color:{MUTED}; font-size:0.8rem;">{s2['type']} | {s2['origin']}</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    metrics = [
        ("Max Speed (m/s)", "speed_ms"), ("Mass (kg)", "mass_kg"),
        ("Max Alt/Ceiling (km)", "ceiling_km"), ("Thrust (kN)", "thrust_kn"),
    ]
    fig_comp = go.Figure()
    metric_names = [m[0] for m in metrics]
    vals1 = [s1[m[1]] for m in metrics]
    vals2 = [s2[m[1]] for m in metrics]
    max_vals = [max(v1, v2, 1) for v1, v2 in zip(vals1, vals2)]
    norm1 = [v / m * 100 for v, m in zip(vals1, max_vals)]
    norm2 = [v / m * 100 for v, m in zip(vals2, max_vals)]
    fig_comp.add_trace(go.Bar(y=metric_names, x=norm1, orientation='h', name=p1,
        marker=dict(color=ACCENT), text=[f'{v:,.0f}' for v in vals1],
        textposition='inside', textfont=dict(color='white', size=12, family='JetBrains Mono')))
    fig_comp.add_trace(go.Bar(y=metric_names, x=[-n for n in norm2], orientation='h', name=p2,
        marker=dict(color=GREEN), text=[f'{v:,.0f}' for v in vals2],
        textposition='inside', textfont=dict(color='white', size=12, family='JetBrains Mono')))
    fig_comp.update_layout(barmode='overlay',
        xaxis=dict(showticklabels=False, zeroline=True, zerolinecolor='rgba(255,255,255,0.2)'),
        yaxis=dict(autorange='reversed'),
        title=dict(text="Head to Head Comparison", font=dict(color=CHART_TITLE, family='Archivo', size=14)),
        legend=dict(font=dict(color=MUTED)))
    plotly_layout(fig_comp, height=400)
    fig_comp.update_layout(margin=dict(l=160))
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-header">Speed Comparison</p>', unsafe_allow_html=True)
    all_names = names_list
    all_speeds = [platform_specs[n]['speed_ms'] for n in all_names]
    speed_colors = [ACCENT if n == p1 else GREEN if n == p2 else 'rgba(255,255,255,0.15)' for n in all_names]
    fig_speed = go.Figure()
    fig_speed.add_trace(go.Bar(x=all_names, y=all_speeds, marker=dict(color=speed_colors),
        text=[f'{v:,.0f}' for v in all_speeds], textposition='outside',
        textfont=dict(color=TEXT, size=10, family='JetBrains Mono')))
    fig_speed.update_layout(title=dict(text="Max Speed Across All Platforms (m/s)",
        font=dict(color=CHART_TITLE, family='Archivo', size=13)),
        yaxis_title="Speed (m/s)", xaxis=dict(tickangle=-30))
    plotly_layout(fig_speed, height=400)
    st.plotly_chart(fig_speed, use_container_width=True)


# ================================================================
# SATELLITE ORBIT VISUALIZER
# ================================================================
elif page == "Satellite Orbit Visualizer":
    st.sidebar.markdown('<p class="section-header">Orbit Parameters</p>', unsafe_allow_html=True)
    sat_alt = st.sidebar.slider("Altitude (km)", 200, 36000, 600, 50,
        help="LEO: 200-2000 km, MEO: 2000-35786 km, GEO: 35,786 km")
    inclination = st.sidebar.slider("Inclination (degrees)", 0, 98, 28, 1,
        help="0° = equatorial, 90° = polar, 97-98° = sun-synchronous")

    MU_E = 3.986e14
    R_E = 6371
    r_orbit = (R_E + sat_alt) * 1000
    v_orbital = np.sqrt(MU_E / r_orbit)
    period = 2 * np.pi * np.sqrt(r_orbit**3 / MU_E)
    period_min = period / 60

    orbit_type = "LEO" if sat_alt < 2000 else "MEO" if sat_alt < 35000 else "GEO"
    if inclination >= 96 and inclination <= 99 and sat_alt < 1000:
        orbit_type = "Sun-Synchronous"
    elif abs(sat_alt - 35786) < 500 and inclination < 5:
        orbit_type = "Geostationary"

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">{orbit_type}</span><span class="spec-label">Orbit Type</span></div>
      <div class="spec-item"><span class="spec-val">{v_orbital:.0f} m/s</span><span class="spec-label">Velocity</span></div>
      <div class="spec-item"><span class="spec-val">{period_min:.1f} min</span><span class="spec-label">Period</span></div>
      <div class="spec-item"><span class="spec-val">{sat_alt} km</span><span class="spec-label">Altitude</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Satellite Orbit Visualizer</p>', unsafe_allow_html=True)
    with st.expander("About orbital mechanics"):
        st.markdown("Every satellite follows Kepler's laws: its speed and period depend only on altitude. Lower = faster. At 35,786 km (GEO), the period is exactly 24 hours, so the satellite appears stationary over one spot. Most Earth observation satellites orbit at 400-800 km in sun-synchronous orbits to image the same spot at the same local time each day.")

    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">{orbit_type}</span><span class="label">Classification</span></div>
      <div class="hud-metric"><span class="value">{v_orbital:.0f} m/s</span><span class="label">Orbital Velocity</span></div>
      <div class="hud-metric"><span class="value">{v_orbital*3.6:.0f} km/h</span><span class="label">Speed</span></div>
      <div class="hud-metric"><span class="value">{period_min:.1f} min</span><span class="label">Orbital Period</span></div>
      <div class="hud-metric"><span class="value">{24*60/period_min:.1f}</span><span class="label">Orbits per Day</span></div>
      <div class="hud-metric"><span class="value">{inclination}°</span><span class="label">Inclination</span></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-header">Ground Track</p>', unsafe_allow_html=True)
        n_orbits = min(3, max(1, int(24 * 60 / period_min)))
        t_track = np.linspace(0, n_orbits * period, 2000)
        omega_e = 2 * np.pi / 86400
        inc_rad = np.radians(inclination)
        lats = np.degrees(np.arcsin(np.sin(inc_rad) * np.sin(2 * np.pi * t_track / period)))
        lons = np.degrees(np.arctan2(np.sin(2 * np.pi * t_track / period) * np.cos(inc_rad),
                np.cos(2 * np.pi * t_track / period))) - np.degrees(omega_e * t_track)
        lons = ((lons + 180) % 360) - 180

        fig_gt = go.Figure()
        seg_lon, seg_lat = [lons[0]], [lats[0]]
        for i in range(1, len(lons)):
            if abs(lons[i] - lons[i-1]) > 180:
                fig_gt.add_trace(go.Scatter(x=seg_lon, y=seg_lat, mode='lines',
                    line=dict(color=ACCENT, width=2), showlegend=False))
                seg_lon, seg_lat = [], []
            seg_lon.append(lons[i])
            seg_lat.append(lats[i])
        if seg_lon:
            fig_gt.add_trace(go.Scatter(x=seg_lon, y=seg_lat, mode='lines',
                line=dict(color=ACCENT, width=2), showlegend=False))
        fig_gt.add_trace(go.Scatter(x=[lons[0]], y=[lats[0]], mode='markers',
            marker=dict(size=10, color=GREEN, symbol='star'), name='Start'))
        fig_gt.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.1)")
        fig_gt.update_layout(
            title=dict(text=f"Ground Track ({n_orbits} orbit{'s' if n_orbits > 1 else ''})",
                font=dict(color=CHART_TITLE, family='Archivo', size=13)),
            xaxis=dict(title="Longitude (°)", range=[-180, 180]),
            yaxis=dict(title="Latitude (°)", range=[-90, 90], scaleanchor='x'))
        plotly_layout(fig_gt, height=450)
        st.plotly_chart(fig_gt, use_container_width=True)
        with st.expander("Reading the ground track"):
            st.markdown(f"The sinusoidal pattern comes from the satellite's inclined orbit projected onto a flat map. The maximum latitude reached = inclination ({inclination}°). Earth rotates underneath, so each pass shifts westward. GEO satellites trace a single dot since they match Earth's rotation.")

    with col2:
        st.markdown('<p class="section-header">Orbit Altitude Context</p>', unsafe_allow_html=True)
        ref_orbits = [
            ("ISS", 408), ("Hubble", 540), ("Starlink", 550),
            ("IRNSS", 36000), ("GPS", 20200), ("GEO", 35786),
        ]
        ref_names = [r[0] for r in ref_orbits] + ["Your Satellite"]
        ref_alts = [r[1] for r in ref_orbits] + [sat_alt]
        ref_colors = ['rgba(255,255,255,0.2)'] * len(ref_orbits) + [ACCENT]
        fig_ctx = go.Figure()
        fig_ctx.add_trace(go.Bar(x=ref_names, y=ref_alts, marker=dict(color=ref_colors),
            text=[f'{a:,} km' for a in ref_alts], textposition='outside',
            textfont=dict(color=TEXT, size=10, family='JetBrains Mono')))
        fig_ctx.update_layout(title=dict(text="Altitude Comparison",
            font=dict(color=CHART_TITLE, family='Archivo', size=13)),
            yaxis=dict(type='log', title='Altitude (km, log)'), xaxis=dict(tickangle=-30))
        plotly_layout(fig_ctx, height=450)
        st.plotly_chart(fig_ctx, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-header">Indian Satellite Orbits</p>', unsafe_allow_html=True)
    indian_sats = [
        {"name": "Cartosat-3", "alt": 509, "inc": 97.5, "purpose": "Earth imaging (0.25m resolution)"},
        {"name": "RISAT-2BR1", "alt": 576, "inc": 37, "purpose": "Radar imaging (all-weather)"},
        {"name": "Oceansat-3", "alt": 742, "inc": 98.3, "purpose": "Ocean/weather monitoring"},
        {"name": "GSAT-30", "alt": 35786, "inc": 0, "purpose": "Telecommunications"},
        {"name": "NavIC (IRNSS)", "alt": 36000, "inc": 29, "purpose": "Regional navigation"},
        {"name": "Aditya-L1", "alt": 1500000, "inc": 0, "purpose": "Solar observation (L1 point)"},
    ]
    cols = st.columns(3)
    for i, sat in enumerate(indian_sats):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="spec-item" style="padding:12px; margin:4px 0;">
                <span class="spec-val" style="font-size:0.85rem;">{sat['name']}</span>
                <span class="spec-label">{sat['alt']:,} km | {sat['inc']}° | {sat['purpose']}</span>
            </div>
            """, unsafe_allow_html=True)


# ================================================================
# QUIZ
# ================================================================
elif page == "Quiz":
    st.markdown('<p class="section-header">Test Your Knowledge</p>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-info">10 questions covering the physics behind every platform in VAJRA. Pick your answer, then expand "Show Answer" to check.</div>', unsafe_allow_html=True)

    quiz_data = [
        {"q": "At Mach 1.5, what is the Mach cone half-angle?",
         "opts": ["30°", "41.8°", "60°", "90°"],
         "ans": 1, "explain": "Half-angle = arcsin(1/M) = arcsin(1/1.5) = 41.8°. The faster you go, the narrower the cone."},
        {"q": "Why does drag spike near Mach 1 (the sound barrier)?",
         "opts": ["Engine loses power", "Air can't move out of the way fast enough, creating shockwaves", "Wings lose lift", "Gravity increases"],
         "ans": 1, "explain": "Near Mach 1, air ahead can't 'warn' air further ahead to move aside. This creates shockwaves and wave drag, a massive spike in resistance called the transonic drag rise."},
        {"q": "What does Isp (specific impulse) measure?",
         "opts": ["Engine temperature", "Fuel efficiency — seconds of thrust per kg of fuel", "Maximum speed", "Engine weight"],
         "ans": 1, "explain": "Isp tells you how many seconds one kg of propellant can produce one kg of thrust. Higher Isp = more efficient. Cryogenic engines (Isp ~440s) are nearly 2x more efficient than solid motors (~270s)."},
        {"q": "Why does ISRO raise Chandrayaan's orbit gradually instead of flying directly to the Moon?",
         "opts": ["The rocket isn't powerful enough", "Gradual burns at perigee are more fuel-efficient than one large burn", "To take photos of Earth", "To test the engines"],
         "ans": 1, "explain": "Burning at perigee (closest point) gives the most efficient orbit change (Oberth effect). Small burns at perigee stretch the apogee further each time, requiring less total fuel than a single direct injection."},
        {"q": "What makes BrahMos nearly impossible to intercept?",
         "opts": ["It's invisible to radar", "Mach 2.8 speed + sea-skimming at 10m altitude gives defenders only seconds to react", "It flies too high", "It changes direction randomly"],
         "ans": 1, "explain": "At Mach 2.8 and 10m above sea level, BrahMos hugs the radar horizon. A ship's defence system gets only a few seconds from detection to impact — not enough time for most countermeasures."},
        {"q": "What is special about Agnikul's Agnilet engine?",
         "opts": ["It uses nuclear fuel", "It's the world's first single-piece 3D-printed rocket engine", "It's reusable 100 times", "It runs on hydrogen"],
         "ans": 1, "explain": "Traditional engines have 100+ parts welded together. Agnilet is 3D-printed as one piece of metal — fewer failure points, faster manufacturing, and lower cost."},
        {"q": "In the vis-viva equation v = sqrt(GM(2/r - 1/a)), what happens to velocity as r decreases?",
         "opts": ["Velocity decreases", "Velocity increases", "Velocity stays constant", "The satellite falls"],
         "ans": 1, "explain": "As r (distance from the central body) decreases, 2/r increases, making v larger. This is why satellites move fastest at their closest approach (perigee/periselene) — Kepler's second law."},
        {"q": "Why does the Gaganyaan capsule need a heat shield for re-entry?",
         "opts": ["Space is cold", "The capsule hits atmosphere at 7.8 km/s, compressing air to ~2000°C", "To protect from radiation", "To keep the interior pressurised"],
         "ans": 1, "explain": "At 7.8 km/s (28,000 km/h), air in front of the capsule can't move aside and gets compressed violently. This compression heats the air to ~2000°C. The ablative heat shield chars and vaporises, carrying heat away."},
        {"q": "How does stealth (low RCS) affect radar detection range?",
         "opts": ["Detection range halves with halved RCS", "Detection range scales with the 4th root of RCS, so 16x smaller RCS = half the range", "RCS doesn't affect range", "Lower RCS increases range"],
         "ans": 1, "explain": "The radar equation: range scales with RCS^(1/4). To halve detection distance, you need to reduce RCS by 2^4 = 16 times. AMCA's ~0.1 m² vs Tejas's ~1.5 m² means significantly reduced detection range."},
        {"q": "What orbit altitude gives a 24-hour period (geostationary)?",
         "opts": ["400 km", "2,000 km", "20,200 km", "35,786 km"],
         "ans": 3, "explain": "At 35,786 km, the orbital period equals Earth's rotation (24 hours). The satellite appears stationary over one point. India's GSAT communication satellites and NavIC navigation satellites use this orbit."},
    ]

    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}

    score = 0
    for i, qd in enumerate(quiz_data):
        st.markdown(f'<div class="hud-card"><p style="font-family:Archivo,sans-serif; color:{TEXT}; font-weight:700; margin-bottom:10px;">Q{i+1}. {qd["q"]}</p></div>', unsafe_allow_html=True)
        key = f"quiz_{i}"
        answer = st.radio(f"Q{i+1}", qd["opts"], key=key, label_visibility="collapsed")
        selected_idx = qd["opts"].index(answer)
        with st.expander("Show Answer"):
            if selected_idx == qd["ans"]:
                st.markdown(f'<span style="color:{GREEN}; font-family:Archivo; font-weight:700;">CORRECT!</span>', unsafe_allow_html=True)
                score += 1
            else:
                st.markdown(f'<span style="color:{RED}; font-family:Archivo; font-weight:700;">INCORRECT</span> — Answer: **{qd["opts"][qd["ans"]]}**', unsafe_allow_html=True)
            st.markdown(qd["explain"])

    st.markdown("---")
    pct = score / len(quiz_data) * 100
    grade_color = GREEN if pct >= 70 else YELLOW if pct >= 40 else RED
    st.markdown(f"""
    <div class="hud-card" style="text-align:center; padding:25px;">
      <span style="font-family:JetBrains Mono; font-size:2.5rem; font-weight:700; color:{grade_color};">{score}/{len(quiz_data)}</span><br>
      <span style="font-family:Rajdhani,sans-serif; font-size:1.1rem; color:{MUTED}; letter-spacing:2px; text-transform:uppercase;">
      {'Mission Specialist' if pct >= 90 else 'Flight Engineer' if pct >= 70 else 'Cadet' if pct >= 40 else 'Ground Crew'}</span>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# LIVE SATELLITE TRACKER
# ================================================================
elif page == "Live Satellite Tracker":

    @st.cache_data(ttl=3600)
    def fetch_tle_data():
        url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=indian&FORMAT=json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "VAJRA-Satellite-Tracker/1.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            return json.loads(resp.read()), True
        except Exception:
            return [], False

    FALLBACK_SATS = [
        {"OBJECT_NAME": "CARTOSAT-3", "TLE_LINE1": "1 44804U 19089A   24001.50000000  .00000180  00000-0  47500-4 0  9990", "TLE_LINE2": "2 44804  97.4960 100.2000 0010000  90.0000 270.0000 15.05000000 10000", "INCLINATION": 97.5, "PERIOD": 95.7, "APOAPSIS": 520, "PERIAPSIS": 505},
        {"OBJECT_NAME": "RISAT-2BR1", "TLE_LINE1": "1 44857U 19090A   24001.50000000  .00001200  00000-0  58000-4 0  9990", "TLE_LINE2": "2 44857  36.9950  50.0000 0015000 120.0000 240.0000 15.09000000 10000", "INCLINATION": 37.0, "PERIOD": 95.3, "APOAPSIS": 580, "PERIAPSIS": 570},
        {"OBJECT_NAME": "OCEANSAT-3", "TLE_LINE1": "1 54361U 22137A   24001.50000000  .00000100  00000-0  30000-4 0  9990", "TLE_LINE2": "2 54361  98.3500 200.0000 0008000  60.0000 300.0000 14.80000000 10000", "INCLINATION": 98.4, "PERIOD": 97.3, "APOAPSIS": 745, "PERIAPSIS": 738},
        {"OBJECT_NAME": "EOS-04 (RISAT-1A)", "TLE_LINE1": "1 51888U 22015A   24001.50000000  .00000150  00000-0  40000-4 0  9990", "TLE_LINE2": "2 51888  97.3800 150.0000 0012000  80.0000 280.0000 15.02000000 10000", "INCLINATION": 97.4, "PERIOD": 95.9, "APOAPSIS": 536, "PERIAPSIS": 520},
        {"OBJECT_NAME": "GSAT-30", "TLE_LINE1": "1 44998U 20005A   24001.50000000  .00000020  00000-0  10000-4 0  9990", "TLE_LINE2": "2 44998   0.0500  75.0000 0002000 270.0000  90.0000  1.00270000 10000", "INCLINATION": 0.05, "PERIOD": 1436.1, "APOAPSIS": 35800, "PERIAPSIS": 35770},
        {"OBJECT_NAME": "GSAT-31", "TLE_LINE1": "1 44034U 19010A   24001.50000000  .00000020  00000-0  10000-4 0  9990", "TLE_LINE2": "2 44034   0.0400  80.0000 0003000 260.0000 100.0000  1.00270000 10000", "INCLINATION": 0.04, "PERIOD": 1436.1, "APOAPSIS": 35800, "PERIAPSIS": 35770},
        {"OBJECT_NAME": "INSAT-3DR", "TLE_LINE1": "1 41752U 16055A   24001.50000000  .00000020  00000-0  10000-4 0  9990", "TLE_LINE2": "2 41752   0.1000  82.0000 0004000 250.0000 110.0000  1.00270000 10000", "INCLINATION": 0.1, "PERIOD": 1436.1, "APOAPSIS": 35800, "PERIAPSIS": 35770},
        {"OBJECT_NAME": "IRNSS-1A (NavIC)", "TLE_LINE1": "1 39199U 13034A   24001.50000000  .00000010  00000-0  10000-4 0  9990", "TLE_LINE2": "2 39199  28.7000  55.0000 0020000 200.0000 160.0000  1.00270000 10000", "INCLINATION": 28.7, "PERIOD": 1436.1, "APOAPSIS": 35900, "PERIAPSIS": 35680},
        {"OBJECT_NAME": "IRNSS-1B (NavIC)", "TLE_LINE1": "1 39635U 14012A   24001.50000000  .00000010  00000-0  10000-4 0  9990", "TLE_LINE2": "2 39635  30.0000  60.0000 0018000 190.0000 170.0000  1.00270000 10000", "INCLINATION": 30.0, "PERIOD": 1436.1, "APOAPSIS": 35880, "PERIAPSIS": 35700},
        {"OBJECT_NAME": "ASTROSAT", "TLE_LINE1": "1 40930U 15052A   24001.50000000  .00000500  00000-0  30000-4 0  9990", "TLE_LINE2": "2 40930   6.0000  40.0000 0010000 100.0000 260.0000 14.95000000 10000", "INCLINATION": 6.0, "PERIOD": 96.3, "APOAPSIS": 650, "PERIAPSIS": 640},
        {"OBJECT_NAME": "RESOURCESAT-2A", "TLE_LINE1": "1 41877U 16074A   24001.50000000  .00000100  00000-0  30000-4 0  9990", "TLE_LINE2": "2 41877  98.7300 300.0000 0005000  70.0000 290.0000 14.50000000 10000", "INCLINATION": 98.7, "PERIOD": 99.3, "APOAPSIS": 825, "PERIAPSIS": 815},
        {"OBJECT_NAME": "CHANDRAYAAN-3 MODULE", "TLE_LINE1": "1 57320U 23098A   24001.50000000  .00000050  00000-0  20000-4 0  9990", "TLE_LINE2": "2 57320  21.3000  30.0000 9600000 280.0000  10.0000  0.05000000 10000", "INCLINATION": 21.3, "PERIOD": 28800, "APOAPSIS": 380000, "PERIAPSIS": 200},
    ]

    sat_data, is_live = fetch_tle_data()
    if not sat_data:
        sat_data = FALLBACK_SATS
        is_live = False

    now = datetime.now(timezone.utc)
    jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second + now.microsecond / 1e6)

    positions = []
    for sat in sat_data:
        name = sat.get("OBJECT_NAME", "UNKNOWN")
        line1 = sat.get("TLE_LINE1", "")
        line2 = sat.get("TLE_LINE2", "")
        if not line1 or not line2:
            continue
        try:
            satellite = Satrec.twoline2rv(line1, line2, WGS72)
            e, r, v = satellite.sgp4(jd, fr)
            if e != 0:
                continue
            x, y, z = r
            dist = np.sqrt(x**2 + y**2 + z**2)
            alt = dist - 6371.0
            gmst = 280.46061837 + 360.98564736629 * (jd + fr - 2451545.0)
            gmst_rad = np.radians(gmst % 360)
            lat = np.degrees(np.arctan2(z, np.sqrt(x**2 + y**2)))
            lon_eci = np.degrees(np.arctan2(y, x))
            lon = (lon_eci - np.degrees(gmst_rad) + 180) % 360 - 180
            speed = np.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            inc = sat.get("INCLINATION", 0)
            period = sat.get("PERIOD", 0)
            apoapsis = sat.get("APOAPSIS", 0)
            periapsis = sat.get("PERIAPSIS", 0)
            orbit_type = "GEO" if alt > 34000 else "MEO" if alt > 2000 else "LEO"
            if inc and 96 <= float(inc) <= 99 and alt < 1000:
                orbit_type = "SSO"
            positions.append({
                "name": name, "lat": lat, "lon": lon, "alt": alt,
                "speed": speed, "inc": inc, "period": period,
                "apoapsis": apoapsis, "periapsis": periapsis,
                "orbit_type": orbit_type
            })
        except Exception:
            continue

    st.sidebar.markdown('<p class="section-header">Tracker Controls</p>', unsafe_allow_html=True)
    orbit_filter = st.sidebar.selectbox("Filter by Orbit", ["All", "LEO", "MEO", "GEO", "SSO"], label_visibility="visible")
    if orbit_filter != "All":
        filtered = [p for p in positions if p["orbit_type"] == orbit_filter]
    else:
        filtered = positions

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">{len(positions)}</span><span class="spec-label">Satellites Tracked</span></div>
      <div class="spec-item"><span class="spec-val">{len([p for p in positions if p['orbit_type']=='LEO'])}</span><span class="spec-label">LEO</span></div>
      <div class="spec-item"><span class="spec-val">{len([p for p in positions if p['orbit_type']=='GEO'])}</span><span class="spec-label">GEO</span></div>
      <div class="spec-item"><span class="spec-val">{'LIVE' if is_live else 'OFFLINE'}</span><span class="spec-label">Data Source</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Live Satellite Tracker</p>', unsafe_allow_html=True)
    if is_live:
        st.markdown('<div class="alert-box alert-info">Real-time positions from CelesTrak TLE data, propagated using SGP4. Auto-refreshes every hour.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-box alert-warning">Using reference orbital data. Live tracking activates when CelesTrak is reachable.</div>', unsafe_allow_html=True)

    with st.expander("How satellite tracking works"):
        st.markdown("Two-Line Element (TLE) sets describe a satellite's orbit in a compact format maintained by NORAD. The SGP4 algorithm propagates these elements forward in time, accounting for perturbations from atmospheric drag, Earth's oblateness (J2), and lunar/solar gravity. Given a TLE and a timestamp, SGP4 outputs the satellite's 3D position in the ECI (Earth-Centered Inertial) frame, which we convert to latitude/longitude by accounting for Earth's rotation (GMST).")

    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">{len(positions)}</span><span class="label">Satellites</span></div>
      <div class="hud-metric"><span class="value">{len(filtered)}</span><span class="label">Shown</span></div>
      <div class="hud-metric"><span class="value">{now.strftime('%H:%M:%S')} UTC</span><span class="label">Computed At</span></div>
      <div class="hud-metric"><span class="value">{'CelesTrak' if is_live else 'Reference'}</span><span class="label">Source</span></div>
    </div>
    """, unsafe_allow_html=True)

    if filtered:
        leos = [p for p in filtered if p["orbit_type"] in ("LEO", "SSO")]
        geos = [p for p in filtered if p["orbit_type"] == "GEO"]
        meos = [p for p in filtered if p["orbit_type"] == "MEO"]

        fig_map = go.Figure()

        if leos:
            fig_map.add_trace(go.Scattergeo(
                lat=[p["lat"] for p in leos],
                lon=[p["lon"] for p in leos],
                text=[f"{p['name']}<br>Alt: {p['alt']:.0f} km<br>Speed: {p['speed']:.1f} km/s<br>{p['orbit_type']}" for p in leos],
                hoverinfo="text",
                marker=dict(size=8, color=ACCENT, symbol="circle", line=dict(width=1, color="white")),
                name="LEO / SSO"
            ))

        if meos:
            fig_map.add_trace(go.Scattergeo(
                lat=[p["lat"] for p in meos],
                lon=[p["lon"] for p in meos],
                text=[f"{p['name']}<br>Alt: {p['alt']:.0f} km<br>Speed: {p['speed']:.1f} km/s<br>{p['orbit_type']}" for p in meos],
                hoverinfo="text",
                marker=dict(size=10, color=YELLOW, symbol="diamond", line=dict(width=1, color="white")),
                name="MEO"
            ))

        if geos:
            fig_map.add_trace(go.Scattergeo(
                lat=[p["lat"] for p in geos],
                lon=[p["lon"] for p in geos],
                text=[f"{p['name']}<br>Alt: {p['alt']:.0f} km<br>Speed: {p['speed']:.1f} km/s<br>{p['orbit_type']}" for p in geos],
                hoverinfo="text",
                marker=dict(size=12, color=GREEN, symbol="star", line=dict(width=1, color="white")),
                name="GEO"
            ))

        fig_map.update_geos(
            showcoastlines=True, coastlinecolor="rgba(255,255,255,0.15)",
            showland=True, landcolor="rgba(17,34,64,0.8)",
            showocean=True, oceancolor="rgba(8,16,30,0.9)",
            showlakes=False,
            showcountries=True, countrycolor="rgba(255,255,255,0.08)",
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
            lonaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)"),
            lataxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)"),
        )
        fig_map.update_layout(
            title=dict(text=f"Indian Satellites: Real-Time Ground Positions",
                font=dict(color=CHART_TITLE, family='Archivo', size=14)),
            legend=dict(font=dict(color=TEXT, family='Rajdhani', size=12),
                bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor=CHART_BG,
            height=550,
        )
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<p class="section-header">Altitude Distribution</p>', unsafe_allow_html=True)
            leo_count = len([p for p in positions if p["orbit_type"] in ("LEO", "SSO")])
            meo_count = len([p for p in positions if p["orbit_type"] == "MEO"])
            geo_count = len([p for p in positions if p["orbit_type"] == "GEO"])
            fig_pie = go.Figure(data=[go.Pie(
                labels=["LEO/SSO", "MEO", "GEO"],
                values=[leo_count, meo_count, geo_count],
                marker=dict(colors=[ACCENT, YELLOW, GREEN]),
                textfont=dict(family="JetBrains Mono", size=12, color="white"),
                hole=0.45
            )])
            fig_pie.update_layout(
                title=dict(text="Orbit Classification",
                    font=dict(color=CHART_TITLE, family='Archivo', size=13)),
                legend=dict(font=dict(color=TEXT, family='Rajdhani', size=12)),
            )
            plotly_layout(fig_pie, height=380)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.markdown('<p class="section-header">Speed vs Altitude</p>', unsafe_allow_html=True)
            non_deep = [p for p in positions if p["alt"] < 50000]
            if non_deep:
                fig_sv = go.Figure()
                fig_sv.add_trace(go.Scatter(
                    x=[p["alt"] for p in non_deep],
                    y=[p["speed"] for p in non_deep],
                    mode='markers+text',
                    text=[p["name"][:12] for p in non_deep],
                    textposition='top center',
                    textfont=dict(size=8, color=MUTED, family='JetBrains Mono'),
                    marker=dict(
                        size=10,
                        color=[p["alt"] for p in non_deep],
                        colorscale=[[0, ACCENT], [1, GREEN]],
                        showscale=True,
                        colorbar=dict(title=dict(text="Alt (km)", font=dict(color=MUTED, size=10)),
                            tickfont=dict(color=MUTED, size=9)),
                        line=dict(width=1, color="white")
                    ),
                    hovertext=[f"{p['name']}<br>{p['alt']:.0f} km<br>{p['speed']:.1f} km/s" for p in non_deep],
                    hoverinfo='text'
                ))
                r_vals = np.linspace(6571, 42157, 200)
                v_theory = np.sqrt(398600.4418 / r_vals)
                fig_sv.add_trace(go.Scatter(
                    x=r_vals - 6371, y=v_theory,
                    mode='lines', name='Theoretical (circular)',
                    line=dict(color='rgba(255,153,51,0.3)', dash='dash', width=1),
                    hoverinfo='skip'
                ))
                fig_sv.update_layout(
                    title=dict(text="Orbital Speed vs Altitude",
                        font=dict(color=CHART_TITLE, family='Archivo', size=13)),
                    xaxis=dict(title="Altitude (km)", type="log"),
                    yaxis=dict(title="Speed (km/s)"),
                )
                plotly_layout(fig_sv, height=380)
                st.plotly_chart(fig_sv, use_container_width=True)

        st.markdown("---")
        st.markdown('<p class="section-header">Satellite Details</p>', unsafe_allow_html=True)
        for p in sorted(filtered, key=lambda x: x["alt"]):
            orb_color = ACCENT if p["orbit_type"] in ("LEO", "SSO") else YELLOW if p["orbit_type"] == "MEO" else GREEN
            st.markdown(f"""
            <div class="hud-card" style="padding:10px 15px; margin:4px 0; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div style="min-width:200px;">
                    <span style="font-family:Archivo,sans-serif; color:{TEXT}; font-weight:700; font-size:0.9rem;">{p['name']}</span>
                    <span style="font-family:JetBrains Mono; color:{orb_color}; font-size:0.7rem; margin-left:8px; letter-spacing:1px;">{p['orbit_type']}</span>
                </div>
                <div style="display:flex; gap:20px; flex-wrap:wrap; font-family:JetBrains Mono; font-size:0.75rem; color:{MUTED};">
                    <span>ALT {p['alt']:.0f} km</span>
                    <span>SPD {p['speed']:.1f} km/s</span>
                    <span>LAT {p['lat']:.1f}°</span>
                    <span>LON {p['lon']:.1f}°</span>
                    <span>INC {p['inc']}°</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown(f'<div class="alert-box alert-warning">No satellites found for the selected filter.</div>', unsafe_allow_html=True)


# ================================================================
# ABOUT
# ================================================================
elif page == "About VAJRA":
    st.markdown('<p class="section-header">About VAJRA</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hud-card">
        <h3 style="font-family:Archivo,sans-serif; color:{TEXT}; font-weight:800; letter-spacing:1px; margin-top:0;">WHAT IS VAJRA?</h3>
        <p style="font-family:Rajdhani,sans-serif; color:#c0cfe0; font-size:1.1rem; line-height:1.8;">
        VAJRA is an interactive physics simulator showcasing <b style="color:{ACCENT};">India's indigenous aerospace capabilities</b>.
        Built with real engineering parameters, it lets you explore the physics behind India's most
        advanced defence and space systems — and learn what makes them work.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hud-card">
        <h3 style="font-family:Archivo,sans-serif; color:{TEXT}; font-weight:800; letter-spacing:1px; margin-top:0;">PLATFORMS</h3>
        <div class="specs-grid" style="grid-template-columns: 1fr 1fr; gap:12px;">
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">HAL TEJAS Mk1A</span>
            <span class="spec-label">Defence — Light Combat Aircraft</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">BRAHMOS</span>
            <span class="spec-label">Defence — Cruise Missile</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">ISRO PSLV-XL</span>
            <span class="spec-label">ISRO — Polar Satellite LV</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">ISRO GSLV Mk III</span>
            <span class="spec-label">ISRO — Heavy Lift Rocket</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">AMCA</span>
            <span class="spec-label">Defence — Stealth Fighter</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">AKASH</span>
            <span class="spec-label">Defence — Surface to Air Missile</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">CHANDRAYAAN 3</span>
            <span class="spec-label">ISRO — Lunar Landing Mission</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">GAGANYAAN</span>
            <span class="spec-label">ISRO — Human Spaceflight</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">AGNIKUL AGNIBAAN</span>
            <span class="spec-label">Private — 3D Printed Rocket</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">SKYROOT VIKRAM-1</span>
            <span class="spec-label">Private — Small Sat Launcher</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">LIVE SATELLITE TRACKER</span>
            <span class="spec-label">ISRO — Real-Time TLE Tracking</span>
          </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hud-card">
        <h3 style="font-family:Archivo,sans-serif; color:{TEXT}; font-weight:800; letter-spacing:1px; margin-top:0;">PHYSICS MODELS USED</h3>
        <div style="font-family:Rajdhani,sans-serif; color:#c0cfe0; font-size:1rem; line-height:2;">
        International Standard Atmosphere (ISA) — troposphere + stratosphere<br>
        Mach cone geometry — arcsin(1/M)<br>
        Sonic boom N-wave pressure profile<br>
        Tsiolkovsky rocket equation for multi-stage propulsion<br>
        Drag model with transonic wave drag rise<br>
        Dynamic pressure and aerodynamic force balance<br>
        Gravity-turn trajectory approximation<br>
        Prandtl-Glauert compressibility correction<br>
        Vis-viva equation for orbital velocity<br>
        Keplerian orbit geometry (elliptical transfer)<br>
        Radar equation for detection range<br>
        Radar cross section angular patterns<br>
        Proportional navigation guidance law<br>
        Sutton-Graves re-entry heating model<br>
        Atmospheric drag deceleration<br>
        Satellite ground track projection<br>
        SGP4 orbit propagation (TLE based real-time tracking)
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hud-card">
        <h3 style="font-family:Archivo,sans-serif; color:{ACCENT}; font-weight:800; letter-spacing:1px; margin-top:0;">COMING SOON</h3>
        <div style="font-family:Rajdhani,sans-serif; color:#c0cfe0; font-size:1rem; line-height:2;">
        Tejas Mk1A spotting log + community map<br>
        Mobile app (Play Store / App Store)
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- FOOTER ---
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; padding:15px;">
    <p style="font-family:'Archivo',sans-serif; color:rgba(240,244,248,0.3); font-size:0.7rem; letter-spacing:3px; font-weight:700;">
    VAJRA v8.0 — BUILT BY ATHARV SHUKLA</p>
    <p style="font-family:'Rajdhani',sans-serif; color:rgba(122,139,164,0.3); font-size:0.7rem; letter-spacing:2px;">
    AMITY INTERNATIONAL SCHOOL SEC 46 GURGAON | INDIAN AEROSPACE SIMULATOR</p>
</div>
""", unsafe_allow_html=True)
