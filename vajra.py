import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="VAJRA - Indian Aerospace Simulator", layout="wide", page_icon="⚡")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 40%, #0a1628 100%); }
.hud-title {
    font-family: 'Orbitron', monospace; font-size: 2.8rem; font-weight: 900;
    background: linear-gradient(90deg, #00f0ff, #00a8ff, #ff6b35);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; letter-spacing: 4px;
    animation: glow 2s ease-in-out infinite alternate; margin-bottom: 0;
}
.hud-subtitle {
    font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; color: #5a9fd4;
    text-align: center; letter-spacing: 6px; text-transform: uppercase; margin-top: 0;
}
@keyframes glow { from { filter: brightness(1); } to { filter: brightness(1.3); } }
@keyframes pulse-border {
    0%, 100% { border-color: rgba(0,240,255,0.3); box-shadow: 0 0 15px rgba(0,240,255,0.1); }
    50% { border-color: rgba(0,240,255,0.7); box-shadow: 0 0 25px rgba(0,240,255,0.3); }
}
@keyframes pulse-border-warn {
    0%, 100% { box-shadow: 0 0 15px rgba(255,165,0,0.2); }
    50% { box-shadow: 0 0 30px rgba(255,165,0,0.5); }
}
@keyframes pulse-border-danger {
    0%, 100% { box-shadow: 0 0 15px rgba(255,50,50,0.3); }
    50% { box-shadow: 0 0 35px rgba(255,50,50,0.7); }
}
.hud-card {
    background: linear-gradient(145deg, rgba(10,22,40,0.9), rgba(5,10,20,0.95));
    border: 1px solid rgba(0,240,255,0.3); border-radius: 12px;
    padding: 20px; margin: 8px 0; animation: pulse-border 3s ease-in-out infinite;
}
.hud-metric { font-family: 'Orbitron', monospace; text-align: center; padding: 15px 10px; }
.hud-metric .value {
    font-size: 1.8rem; font-weight: 700; color: #00f0ff;
    text-shadow: 0 0 10px rgba(0,240,255,0.5); display: block;
}
.hud-metric .label {
    font-family: 'Rajdhani', sans-serif; font-size: 0.8rem; color: #5a9fd4;
    text-transform: uppercase; letter-spacing: 2px; margin-top: 4px; display: block;
}
.regime-badge {
    font-family: 'Orbitron', monospace; font-size: 1rem; padding: 8px 20px;
    border-radius: 25px; text-align: center; font-weight: 700;
    letter-spacing: 3px; display: inline-block; margin: 5px auto;
}
.regime-subsonic { background: rgba(0,200,100,0.15); border: 2px solid #00c864; color: #00ff7f; }
.regime-transonic { background: rgba(255,165,0,0.15); border: 2px solid #ffa500; color: #ffb733; animation: pulse-border-warn 1.5s ease-in-out infinite; }
.regime-supersonic { background: rgba(255,50,50,0.15); border: 2px solid #ff3232; color: #ff4444; animation: pulse-border-danger 1s ease-in-out infinite; }
.specs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-family: 'Rajdhani', sans-serif; }
.spec-item {
    background: rgba(0,240,255,0.05); border: 1px solid rgba(0,240,255,0.15);
    border-radius: 8px; padding: 8px 12px; text-align: center;
}
.spec-item .spec-val { font-family: 'Orbitron', monospace; font-size: 1.05rem; color: #00f0ff; display: block; }
.spec-item .spec-label { font-size: 0.7rem; color: #5a9fd4; text-transform: uppercase; letter-spacing: 1px; }
.section-header {
    font-family: 'Orbitron', monospace; font-size: 1.1rem; color: #00f0ff;
    letter-spacing: 3px; border-bottom: 1px solid rgba(0,240,255,0.3);
    padding-bottom: 8px; margin-bottom: 15px; text-transform: uppercase;
}
.alert-box { font-family: 'Rajdhani', sans-serif; padding: 12px 20px; border-radius: 8px; margin: 5px 0; font-size: 1rem; letter-spacing: 1px; }
.alert-boom { background: rgba(255,50,50,0.1); border-left: 4px solid #ff3232; color: #ff6b6b; animation: pulse-border-danger 1.5s ease-in-out infinite; }
.alert-transonic { background: rgba(255,165,0,0.1); border-left: 4px solid #ffa500; color: #ffb733; }
.alert-normal { background: rgba(0,200,100,0.1); border-left: 4px solid #00c864; color: #00ff7f; }
.alert-limit { background: rgba(255,0,0,0.1); border-left: 4px solid #ff0000; color: #ff4444; }
.alert-info { background: rgba(0,150,255,0.1); border-left: 4px solid #00a8ff; color: #5ac8fa; }
div[data-testid="stSidebar"] { background: linear-gradient(180deg, #060d18, #0a1628, #060d18); border-right: 1px solid rgba(0,240,255,0.2); }
</style>
""", unsafe_allow_html=True)


def plotly_hud_layout(fig, height=450, **kwargs):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(8,12,22,0.9)',
        height=height, margin=dict(l=50, r=20, t=40, b=40),
        xaxis=dict(gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        yaxis=dict(gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
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
        line=dict(color='#ff6b35', width=3), name='Altitude'))
    for tb, ab, sn in stage_boundaries:
        fig_traj.add_vline(x=tb, line_dash="dot", line_color="rgba(0,240,255,0.3)")
        fig_traj.add_annotation(x=tb, y=ab, text=f"{sn.split('(')[0].strip()} sep",
            font=dict(color='#00f0ff', size=9, family='Rajdhani'), showarrow=True,
            arrowcolor='#00f0ff', arrowsize=0.8)
    fig_traj.update_layout(title=dict(text=f"{name} Launch Trajectory",
        font=dict(color='#00f0ff', family='Orbitron', size=14)),
        xaxis_title="Time (s)", yaxis_title="Altitude (km)")
    plotly_hud_layout(fig_traj, height=400)
    st.plotly_chart(fig_traj, use_container_width=True)

    with st.expander("What am I looking at?"):
        st.markdown("The orange curve shows the rocket climbing through the atmosphere. Dotted lines mark **stage separations** — when an empty fuel tank is dropped so the rocket gets lighter and accelerates faster.")

    vc1, vc2 = st.columns(2)
    with vc1:
        fig_vel = go.Figure()
        fig_vel.add_trace(go.Scatter(x=t_sim, y=vel_sim, mode='lines',
            line=dict(color='#00e878', width=2), name='Velocity'))
        fig_vel.update_layout(title=dict(text="Velocity Profile",
            font=dict(color='#00f0ff', family='Orbitron', size=12)),
            xaxis_title="Time (s)", yaxis_title="Velocity (m/s)")
        plotly_hud_layout(fig_vel, height=350)
        st.plotly_chart(fig_vel, use_container_width=True)
        with st.expander("About velocity"):
            st.markdown("Speed builds with each stage. To reach orbit you need ~7,800 m/s (28,000 km/h) — 23x the speed of sound.")
    with vc2:
        fig_g = go.Figure()
        fig_g.add_trace(go.Scatter(x=t_sim, y=acc_sim, mode='lines',
            line=dict(color='#ffc800', width=2), name='G-force'))
        fig_g.add_hline(y=6, line_dash="dash", line_color="rgba(255,50,50,0.4)",
            annotation_text="Human limit ~6G", annotation_font=dict(color='#ff5050', size=9))
        fig_g.update_layout(title=dict(text="G-Force Profile",
            font=dict(color='#00f0ff', family='Orbitron', size=12)),
            xaxis_title="Time (s)", yaxis_title="G-force")
        plotly_hud_layout(fig_g, height=350)
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
        <div style="background:rgba(0,240,255,0.03); border:1px solid rgba(0,240,255,0.1); border-radius:6px; padding:8px; margin:4px 0;">
            <span style="font-family:Orbitron,monospace; color:#00f0ff; font-size:0.75rem;">STAGE {i+1}</span><br>
            <span style="font-family:Rajdhani,sans-serif; color:#8ab4d4; font-size:0.85rem;">{stage['name']}</span><br>
            <span style="color:#5a9fd4; font-size:0.75rem;">Thrust: {stage['thrust']} kN | Burn: {stage['burn_time']}s | Isp: {stage['isp']}s</span>
        </div>
        """, unsafe_allow_html=True)


# --- HEADER ---
st.markdown('<h1 class="hud-title">VAJRA</h1>', unsafe_allow_html=True)
st.markdown('<p class="hud-subtitle">Indian Aerospace Simulator Platform</p>', unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown('<p class="section-header">Navigate</p>', unsafe_allow_html=True)

category = st.sidebar.selectbox("Category", ["Defence", "ISRO", "Private Space", "About"], label_visibility="collapsed")

if category == "Defence":
    page = st.sidebar.radio("Platform", ["HAL Tejas Mk1A", "BrahMos Missile"], label_visibility="collapsed")
elif category == "ISRO":
    page = st.sidebar.radio("Rocket", ["PSLV-XL", "GSLV Mk III (LVM3)"], label_visibility="collapsed")
elif category == "Private Space":
    page = st.sidebar.radio("Company", ["Agnikul Cosmos — Agnibaan", "Skyroot — Vikram-1"], label_visibility="collapsed")
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

    # --- Main content ---
    st.markdown('<p class="section-header">HAL Tejas Mk1A — Supersonic Flight Simulator</p>', unsafe_allow_html=True)

    with st.expander("About Tejas"):
        st.markdown("India's indigenous Light Combat Aircraft. Adjust Mach and altitude in the sidebar to see how flight physics change in real time.")

    # Metrics bar
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

    # Alerts
    if mach >= 1.0:
        ha = np.degrees(np.arcsin(1 / mach))
        bs = 0.5 + 1.5 * (mach - 1.0)
        st.markdown(f'<div class="alert-box alert-boom">SONIC BOOM — Mach cone half-angle: {ha:.1f}° | Overpressure: {bs:.2f}</div>', unsafe_allow_html=True)
    elif mach >= 0.8:
        st.markdown('<div class="alert-box alert-transonic">TRANSONIC — Approaching the sound barrier, drag is spiking</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-box alert-normal">SUBSONIC — Normal flight conditions</div>', unsafe_allow_html=True)

    # Shockwave + Pressure
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
                colorscale=[[0, f'rgba(255,60,10,{0.3+0.4*intensity})'],
                            [0.5, f'rgba(255,120,30,{0.2+0.3*intensity})'],
                            [1, f'rgba(255,180,60,{0.1+0.15*intensity})']],
                showscale=False, opacity=0.6))
            fig1.add_trace(go.Scatter3d(x=[0.3], y=[0], z=[0], mode='markers+text',
                marker=dict(size=8, color='#00f0ff', symbol='diamond'),
                text=[f'TEJAS M{mach:.1f}'], textposition='top center',
                textfont=dict(color='#00f0ff', size=11)))
            fig1.update_layout(
                title=dict(text=f"3D Mach Cone — {half_angle:.1f}°",
                    font=dict(color='#00f0ff', family='Orbitron')),
                scene=dict(
                    xaxis=dict(backgroundcolor='rgb(10,15,28)', gridcolor='rgba(0,240,255,0.1)', color='#5a9fd4'),
                    yaxis=dict(backgroundcolor='rgb(10,15,28)', gridcolor='rgba(0,240,255,0.1)', color='#5a9fd4'),
                    zaxis=dict(backgroundcolor='rgb(10,15,28)', gridcolor='rgba(0,240,255,0.1)', color='#5a9fd4'),
                    bgcolor='rgb(8,12,22)', aspectmode='data'),
                paper_bgcolor='rgba(0,0,0,0)', height=500, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig1, use_container_width=True)
            with st.expander("How does a Mach cone work?"):
                st.markdown(f"When Tejas flies faster than sound, air piles up into a cone-shaped shockwave behind the jet — like the V-wake behind a boat. At Mach {mach:.1f}, the cone half-angle is **{half_angle:.1f} degrees**. Faster = narrower cone.")
        else:
            st.markdown('<div class="hud-card" style="text-align:center;padding:60px 20px;"><p style="font-family:Orbitron,monospace;color:#5a9fd4;letter-spacing:2px;">NO SHOCKWAVE<br><span style="font-size:0.8rem;color:#7ab8d4;">Increase Mach above 1.0 to see the Mach cone form</span></p></div>', unsafe_allow_html=True)

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
        lc = '#ff4444' if mach >= 1.0 else '#00f0ff'
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=x_wave, y=pw, mode='lines', line=dict(color=lc, width=2.5), name='Pressure'))
        fig2.add_hline(y=1.0, line_dash="dash", line_color="rgba(100,150,200,0.4)",
            annotation_text="P∞ (normal)", annotation_font=dict(color='#5a9fd4'))
        fig2.update_layout(title=dict(text=tt, font=dict(color='#00f0ff', family='Orbitron', size=13)),
            xaxis_title="Position", yaxis_title="P / P∞")
        plotly_hud_layout(fig2, height=500)
        st.plotly_chart(fig2, use_container_width=True)
        if mach >= 1.0:
            with st.expander("What is an N-wave?"):
                st.markdown("A sonic boom sounds like a double bang. Pressure spikes up (front shock), drops below normal, then spikes again (rear shock). This **N-shape** is why it's called an N-wave. The dashed line is normal atmospheric pressure.")
        else:
            with st.expander("About pressure"):
                st.markdown("Below Mach 1 there's no sonic boom. Pressure changes smoothly around the aircraft. The dashed line is normal atmospheric pressure (P-infinity).")

    # Forces + Envelope
    st.markdown("---")
    cf1, cf2 = st.columns(2)
    with cf1:
        st.markdown('<p class="section-header">Four Forces of Flight</p>', unsafe_allow_html=True)
        fnames = ['LIFT ↑', 'WEIGHT ↓', 'THRUST →', 'DRAG ←']
        fvals = [lift/1000, weight/1000, thrust_required/1000, drag/1000]
        fcols = ['#00e878', '#ff5050', '#00b4ff', '#ffc800']
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(y=fnames, x=fvals, orientation='h',
            marker=dict(color=fcols), text=[f'{v:.1f} kN' for v in fvals],
            textposition='outside', textfont=dict(color='#c0d8ef', size=14, family='Orbitron'),
            hovertemplate='%{y}: %{x:.2f} kN<extra></extra>'))
        bal = "BALANCED" if abs(lift - weight) < weight * 0.01 else "UNBALANCED"
        fig3.add_annotation(x=max(fvals)*0.5, y=1.5, text=f"<b>L/W: {bal}</b>",
            font=dict(size=12, color='#00e878' if bal == "BALANCED" else '#ff5050', family='Orbitron'), showarrow=False)
        plotly_hud_layout(fig3, showlegend=False)
        fig3.update_layout(yaxis=dict(color='#c0d8ef', tickfont=dict(size=14, family='Rajdhani')),
                           xaxis=dict(title="Force (kN)"), margin=dict(l=100, r=60, t=20, b=40))
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
            line=dict(color='#ff6b35', width=2), fillcolor='rgba(255,107,53,0.1)', name='Envelope'))
        fig4.add_trace(go.Scatter(x=[mach], y=[altitude/1000], mode='markers+text',
            marker=dict(size=14, color='#00f0ff', symbol='star-diamond'),
            text=[f'M{mach:.1f}'], textposition='top right',
            textfont=dict(color='#00f0ff', size=12, family='Orbitron'), name='You'))
        fig4.add_vline(x=1.0, line_dash="dot", line_color="rgba(255,255,0,0.4)", annotation_text="Mach 1")
        plotly_hud_layout(fig4)
        fig4.update_layout(xaxis=dict(title="Mach"), yaxis=dict(title="Altitude (km)"))
        st.plotly_chart(fig4, use_container_width=True)
        with st.expander("What is a flight envelope?"):
            st.markdown("The orange area is where Tejas **can** fly — every valid Mach + altitude combo. The blue star is your current position. Outside the envelope: either too slow to generate enough lift, or beyond structural/engine limits.")

    # Drag + Atmosphere
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
        fig5.add_vrect(x0=0.1, x1=0.8, fillcolor="rgba(0,200,100,0.05)", line_width=0,
            annotation_text="Subsonic", annotation_position="top left",
            annotation_font=dict(color='rgba(0,200,100,0.5)', size=9))
        fig5.add_vrect(x0=0.8, x1=1.2, fillcolor="rgba(255,165,0,0.05)", line_width=0,
            annotation_text="Transonic", annotation_position="top left",
            annotation_font=dict(color='rgba(255,165,0,0.5)', size=9))
        fig5.add_vrect(x0=1.2, x1=1.8, fillcolor="rgba(255,50,50,0.05)", line_width=0,
            annotation_text="Supersonic", annotation_position="top left",
            annotation_font=dict(color='rgba(255,50,50,0.5)', size=9))
        fig5.add_trace(go.Scatter(x=mr, y=cdc, mode='lines', line=dict(color='#ff6b35', width=2.5), name='CD'))
        fig5.add_trace(go.Scatter(x=[mach], y=[cd], mode='markers', marker=dict(size=12, color='#00f0ff'), name=f'CD={cd:.4f}'))
        plotly_hud_layout(fig5, height=400)
        fig5.update_layout(xaxis=dict(title="Mach"), yaxis=dict(title="CD"))
        st.plotly_chart(fig5, use_container_width=True)
        with st.expander("What is drag coefficient?"):
            st.markdown("**Drag coefficient** measures air resistance. Watch it spike near Mach 1 — that's the **sound barrier** (transonic drag rise). Past Mach 1.2 it drops as the aircraft is fully supersonic. This spike is why breaking the sound barrier needs so much thrust.")

    with cd2:
        st.markdown('<p class="section-header">ISA Atmosphere Profile</p>', unsafe_allow_html=True)
        ap = np.linspace(0, 20000, 200)
        tp = [isa_atmosphere(a)[0] - 273.15 for a in ap]
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(x=tp, y=ap/1000, mode='lines', line=dict(color='#ff6b35', width=2), name='Temperature'))
        fig6.add_trace(go.Scatter(x=[temp-273.15], y=[altitude/1000], mode='markers',
            marker=dict(size=10, color='#00f0ff', symbol='star'), name='You'))
        fig6.add_hline(y=11, line_dash="dot", line_color="rgba(255,255,0,0.3)",
            annotation_text="Tropopause (11 km)", annotation_font=dict(color='yellow', size=9))
        plotly_hud_layout(fig6, height=400)
        fig6.update_layout(xaxis=dict(title="Temperature (°C)"), yaxis=dict(title="Altitude (km)"))
        st.plotly_chart(fig6, use_container_width=True)
        with st.expander("What is the ISA model?"):
            st.markdown("Temperature drops 6.5 C per km up to 11 km (**troposphere**), then stays flat at -56.5 C (**stratosphere**). This is the International Standard Atmosphere (ISA) — the global model pilots and engineers use to calculate aircraft performance.")

    # Sonic boom footprint
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
            line=dict(color='#ff4444', width=2), fillcolor='rgba(255,50,50,0.15)'))
        fig7.add_annotation(x=0, y=max(opg), text=f"Peak ΔP ≈ {max(opg):.2f}<br>Width ≈ {bw:.1f} km",
            font=dict(color='#ff6b6b', size=12, family='Rajdhani'), showarrow=True, arrowcolor='#ff4444')
        plotly_hud_layout(fig7, height=350)
        fig7.update_layout(xaxis=dict(title="Lateral Distance (km)"), yaxis=dict(title="Overpressure"))
        st.plotly_chart(fig7, use_container_width=True)
        with st.expander("How wide is the boom?"):
            st.markdown(f"Everyone inside this **{bw:.1f} km wide** strip on the ground hears the sonic boom. The peak is directly below the jet. Higher altitude = wider but weaker boom. Lower altitude = narrower but louder.")


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
      <div class="spec-item"><span class="spec-val">{sp['altitude_sea_skim']} m</span><span class="spec-label">Sea Skim Alt</span></div>
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
        line=dict(color='#ff3232', width=3), fillcolor='rgba(255,50,50,0.1)', name='Trajectory'))
    fig_bm.add_trace(go.Scatter(x=[0], y=[0], mode='markers+text',
        marker=dict(size=12, color='#00e878', symbol='triangle-up'),
        text=['LAUNCH'], textposition='top right', textfont=dict(color='#00e878', size=10, family='Orbitron'), showlegend=False))
    fig_bm.add_trace(go.Scatter(x=[target_range], y=[0], mode='markers+text',
        marker=dict(size=14, color='#ff3232', symbol='x'),
        text=['TARGET'], textposition='top left', textfont=dict(color='#ff3232', size=10, family='Orbitron'), showlegend=False))
    fig_bm.add_annotation(x=climb_dist + cruise_dist * 0.5, y=cruise_alt/1000 + 1,
        text=f"CRUISE: Mach {sp['speed_mach']} @ {cruise_alt/1000:.0f} km",
        font=dict(color='#ffc800', size=11, family='Rajdhani'), showarrow=False)
    fig_bm.update_layout(title=dict(text=f"{brahmos_variant} Flight Profile",
        font=dict(color='#ff3232', family='Orbitron', size=14)),
        xaxis_title="Range (km)", yaxis_title="Altitude (km)")
    plotly_hud_layout(fig_bm, height=450)
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
# ABOUT
# ================================================================
elif page == "About VAJRA":
    st.markdown('<p class="section-header">About VAJRA</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hud-card">
        <h3 style="font-family:Orbitron,monospace; color:#00f0ff; letter-spacing:3px; margin-top:0;">WHAT IS VAJRA?</h3>
        <p style="font-family:Rajdhani,sans-serif; color:#8ab4d4; font-size:1.1rem; line-height:1.8;">
        VAJRA is an interactive physics simulator showcasing <b style="color:#ff6b35;">India's indigenous aerospace capabilities</b>.
        Built with real engineering parameters, it lets you explore the physics behind India's most
        advanced defence and space systems — and learn what makes them work.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hud-card">
        <h3 style="font-family:Orbitron,monospace; color:#00f0ff; letter-spacing:3px; margin-top:0;">PLATFORMS</h3>
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
            <span class="spec-val" style="font-size:0.85rem;">AGNIKUL AGNIBAAN</span>
            <span class="spec-label">Private — 3D Printed Rocket</span>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val" style="font-size:0.85rem;">SKYROOT VIKRAM-1</span>
            <span class="spec-label">Private — Small Sat Launcher</span>
          </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hud-card">
        <h3 style="font-family:Orbitron,monospace; color:#00f0ff; letter-spacing:3px; margin-top:0;">PHYSICS MODELS USED</h3>
        <div style="font-family:Rajdhani,sans-serif; color:#8ab4d4; font-size:1rem; line-height:2;">
        International Standard Atmosphere (ISA) — troposphere + stratosphere<br>
        Mach cone geometry — arcsin(1/M)<br>
        Sonic boom N-wave pressure profile<br>
        Tsiolkovsky rocket equation for multi-stage propulsion<br>
        Drag model with transonic wave drag rise<br>
        Dynamic pressure and aerodynamic force balance<br>
        Gravity-turn trajectory approximation<br>
        Prandtl-Glauert compressibility correction
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hud-card">
        <h3 style="font-family:Orbitron,monospace; color:#ff6b35; letter-spacing:3px; margin-top:0;">COMING SOON</h3>
        <div style="font-family:Rajdhani,sans-serif; color:#8ab4d4; font-size:1rem; line-height:2;">
        Chandrayaan orbital mechanics simulator<br>
        Gaganyaan re-entry heat shield analysis<br>
        AMCA stealth aircraft profile<br>
        Akash missile intercept trajectory<br>
        Live ISRO satellite tracking<br>
        Tejas Mk1A spotting log + community map<br>
        Mobile app (Play Store / App Store)
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:15px;">
    <p style="font-family:'Orbitron',monospace; color:rgba(0,240,255,0.4); font-size:0.7rem; letter-spacing:4px;">
    VAJRA v4.1 — BUILT BY ATHARV SHUKLA</p>
    <p style="font-family:'Rajdhani',sans-serif; color:rgba(90,159,212,0.3); font-size:0.7rem; letter-spacing:2px;">
    AMITY INTERNATIONAL SCHOOL SEC 46 GURGAON | INDIAN AEROSPACE SIMULATOR</p>
</div>
""", unsafe_allow_html=True)
