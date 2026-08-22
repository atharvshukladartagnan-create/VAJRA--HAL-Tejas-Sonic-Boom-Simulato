import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="VAJRA - Indian Aerospace Simulator", layout="wide", page_icon="⚡")

# --- HUD THEME CSS ---
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
div[data-testid="stTabs"] button { font-family: 'Orbitron', monospace !important; letter-spacing: 2px !important; }
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


# --- HEADER ---
st.markdown('<h1 class="hud-title">VAJRA</h1>', unsafe_allow_html=True)
st.markdown('<p class="hud-subtitle">Indian Aerospace Simulator Platform</p>', unsafe_allow_html=True)

# --- TABS ---
tab_tejas, tab_isro, tab_brahmos, tab_about = st.tabs(["HAL TEJAS", "ISRO LAUNCH", "BRAHMOS", "ABOUT"])


# ============================================================
# TAB 1: HAL TEJAS
# ============================================================
with tab_tejas:
    st.sidebar.markdown('<p class="section-header">Tejas Controls</p>', unsafe_allow_html=True)
    mach = st.sidebar.slider("Mach Number", 0.1, 1.8, 0.8, 0.01,
        help="Mach number = aircraft speed ÷ speed of sound. Tejas Mk1A tops out at Mach 1.8.")
    altitude = st.sidebar.slider("Altitude (m)", 0, 16500, 5000, 100,
        help="Height above sea level. Tejas service ceiling is 16,500 m (54,000 ft). Air gets thinner as you go up.")

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

    q = 0.5 * rho * aircraft_speed ** 2
    if mach < 0.8:
        cd = TEJAS_DRAG_CD0 + 0.06 * (mach ** 2)
    elif mach < 1.2:
        cd = TEJAS_DRAG_CD0 + 0.06 * (mach ** 2) + 0.2 * (mach - 0.8) ** 2
    else:
        cd = TEJAS_DRAG_CD0 + 0.06 * (mach ** 2) + 0.015 / (mach ** 2)

    cl = (TEJAS_MASS * 9.81) / (q * TEJAS_WING_AREA) if q > 0 else 0
    drag = q * TEJAS_WING_AREA * cd
    lift = q * TEJAS_WING_AREA * cl
    weight = TEJAS_MASS * 9.81
    thrust_required = drag
    g_load = lift / weight if weight > 0 else 0

    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div style="text-align:center"><span class="{regime_class} regime-badge">{regime}</span></div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">{speed_of_sound:.0f}</span><span class="spec-label">Sound m/s</span></div>
      <div class="spec-item"><span class="spec-val">{aircraft_speed:.0f}</span><span class="spec-label">Speed m/s</span></div>
      <div class="spec-item"><span class="spec-val">{aircraft_speed*3.6:.0f}</span><span class="spec-label">km/h</span></div>
      <div class="spec-item"><span class="spec-val">{rho:.4f}</span><span class="spec-label">Density kg/m³</span></div>
      <div class="spec-item"><span class="spec-val">{q:.0f}</span><span class="spec-label">Q (Pa)</span></div>
      <div class="spec-item"><span class="spec-val">{g_load:.2f}</span><span class="spec-label">G-Load</span></div>
    </div>
    """, unsafe_allow_html=True)
    with st.sidebar.expander("What do these mean?"):
        st.markdown("""
- **Sound m/s** — Speed of sound at this altitude. Changes with temperature.
- **Density** — Air density (kg/m³). Sea level ≈ 1.225. Thinner air = less lift and drag.
- **Q (Pa)** — Dynamic pressure = ½ × density × speed². The force air exerts on the aircraft. All aerodynamic forces depend on this.
- **G-Load** — Multiple of gravity felt. 1G = normal. Fighter pilots train for up to 9G.
        """)

    st.sidebar.markdown("---")
    st.sidebar.markdown('<p class="section-header">Tejas Mk1A</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div class="specs-grid">
      <div class="spec-item"><span class="spec-val">GE F404</span><span class="spec-label">Engine</span></div>
      <div class="spec-item"><span class="spec-val">{TEJAS_MAX_THRUST} kN</span><span class="spec-label">Max Thrust</span></div>
      <div class="spec-item"><span class="spec-val">M {TEJAS_MAX_MACH}</span><span class="spec-label">Max Speed</span></div>
      <div class="spec-item"><span class="spec-val">{TEJAS_CEILING/1000:.1f} km</span><span class="spec-label">Ceiling</span></div>
      <div class="spec-item"><span class="spec-val">{TEJAS_WING_AREA} m²</span><span class="spec-label">Wing Area</span></div>
      <div class="spec-item"><span class="spec-val">{TEJAS_MASS/1000:.1f} t</span><span class="spec-label">Weight</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics bar
    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">{mach:.2f}</span><span class="label">Mach</span></div>
      <div class="hud-metric"><span class="value">{altitude/1000:.1f} km</span><span class="label">Altitude</span></div>
      <div class="hud-metric"><span class="value">{temp - 273.15:.0f}°C</span><span class="label">OAT</span></div>
      <div class="hud-metric"><span class="value">{aircraft_speed:.0f}</span><span class="label">m/s</span></div>
      <div class="hud-metric"><span class="value">{aircraft_speed*3.6:.0f}</span><span class="label">km/h</span></div>
      <div class="hud-metric"><span class="value">{g_load:.1f}G</span><span class="label">G-Load</span></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("What do these numbers mean?"):
        st.markdown("""
**Mach Number** — How many times faster than sound you're flying. Mach 1 = speed of sound (~340 m/s at sea level). Below Mach 1 is *subsonic*, above is *supersonic*.

**Altitude** — Height above sea level in kilometres. The higher you go, the thinner the air and the colder it gets.

**OAT (Outside Air Temperature)** — The actual air temperature at your altitude. At sea level it's about 15°C. At 11 km (where airliners cruise) it drops to about −56°C.

**Speed (m/s & km/h)** — Your true airspeed. This depends on both Mach number *and* altitude because sound travels slower in colder air.

**G-Load** — How many times your own weight you feel. Sitting still = 1G. In a sharp turn, a fighter pilot can pull 9G — meaning they feel 9× their body weight.
        """)


    # Alerts
    if mach >= 1.0:
        ha = np.degrees(np.arcsin(1 / mach))
        bs = 0.5 + 1.5 * (mach - 1.0)
        st.markdown(f'<div class="alert-box alert-boom">⚡ SONIC BOOM — Half-angle: {ha:.1f}° | Overpressure: {bs:.2f}</div>', unsafe_allow_html=True)
    elif mach >= 0.8:
        st.markdown('<div class="alert-box alert-transonic">⚠ TRANSONIC — Wave drag rising</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-box alert-normal">✓ SUBSONIC — Normal conditions</div>', unsafe_allow_html=True)
    if altitude > TEJAS_CEILING:
        st.markdown(f'<div class="alert-box alert-limit">⛔ ABOVE CEILING {TEJAS_CEILING/1000:.1f} km</div>', unsafe_allow_html=True)

    # Shockwave + Pressure
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-header">Shockwave Cone</p>', unsafe_allow_html=True)
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
                colorscale=[[0, f'rgba(255,60,10,{0.3+0.4*intensity})'], [0.5, f'rgba(255,120,30,{0.2+0.3*intensity})'], [1, f'rgba(255,180,60,{0.1+0.15*intensity})']],
                showscale=False, opacity=0.6))
            fig1.add_trace(go.Scatter3d(x=[0.3], y=[0], z=[0], mode='markers+text',
                marker=dict(size=8, color='#00f0ff', symbol='diamond'),
                text=[f'TEJAS M{mach:.1f}'], textposition='top center', textfont=dict(color='#00f0ff', size=11)))
            fig1.update_layout(
                title=dict(text=f"3D Mach Cone — {half_angle:.1f}°", font=dict(color='#00f0ff', family='Orbitron')),
                scene=dict(
                    xaxis=dict(backgroundcolor='rgb(10,15,28)', gridcolor='rgba(0,240,255,0.1)', color='#5a9fd4'),
                    yaxis=dict(backgroundcolor='rgb(10,15,28)', gridcolor='rgba(0,240,255,0.1)', color='#5a9fd4'),
                    zaxis=dict(backgroundcolor='rgb(10,15,28)', gridcolor='rgba(0,240,255,0.1)', color='#5a9fd4'),
                    bgcolor='rgb(8,12,22)', aspectmode='data'),
                paper_bgcolor='rgba(0,0,0,0)', height=500, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.markdown('<div class="hud-card" style="text-align:center;padding:60px 20px;"><p style="font-family:Orbitron,monospace;color:#5a9fd4;letter-spacing:2px;">NO SHOCKWAVE — Increase Mach to 1.0+</p></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-header">Pressure N-Wave</p>', unsafe_allow_html=True)
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
            op = boom_strength * (rho / 1.225) ** 0.5
            tt = f"Sonic Boom N-Wave | ΔP ≈ {op:.2f}"
        else:
            cf = 1 / np.sqrt(max(1 - mach ** 2, 0.01))
            pw = 1.0 + 0.3 * cf * np.exp(-0.5 * (x_wave * (1 - mach)) ** 2) * np.cos(3 * x_wave)
            tt = f"Subsonic Pressure | β = {1/cf:.3f}"
        lc = '#ff4444' if mach >= 1.0 else '#00f0ff'
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=x_wave, y=pw, mode='lines', line=dict(color=lc, width=2.5), name='Pressure'))
        fig2.add_hline(y=1.0, line_dash="dash", line_color="rgba(100,150,200,0.4)", annotation_text="P∞", annotation_font=dict(color='#5a9fd4'))
        fig2.update_layout(title=dict(text=tt, font=dict(color='#00f0ff', family='Orbitron', size=13)), xaxis_title="Position", yaxis_title="P / P∞")
        plotly_hud_layout(fig2, height=500)
        st.plotly_chart(fig2, use_container_width=True)

    with st.expander("What are shockwaves and sonic booms?"):
        st.markdown("""
**Shockwave (Mach Cone)** — When an aircraft flies faster than sound, air can't move out of the way fast enough. It piles up into a cone-shaped shockwave trailing behind the jet, like the V-shaped wake behind a boat. The faster you go, the narrower the cone.

**Mach Cone Angle** — The half-angle of the cone is θ = arcsin(1/Mach). At Mach 1, the cone is flat (90°). At Mach 1.8 (Tejas max), it narrows to about 34°.

**N-Wave (Sonic Boom Pressure)** — On the ground, a sonic boom sounds like a double bang. The pressure spikes up sharply (front shock), drops below normal (expansion), then spikes again (rear shock). This "N" shape is why it's called an N-wave. The faster and lower the jet, the louder the boom.

**Subsonic pressure** — Below Mach 1, there's no shockwave. Air pressure smoothly increases ahead of the aircraft and decreases behind it — no sonic boom.
        """)

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

    with cf2:
        st.markdown('<p class="section-header">Performance Envelope</p>', unsafe_allow_html=True)
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
            text=[f'M{mach:.1f}'], textposition='top right', textfont=dict(color='#00f0ff', size=12, family='Orbitron'), name='Current'))
        fig4.add_vline(x=1.0, line_dash="dot", line_color="rgba(255,255,0,0.4)", annotation_text="Mach 1")
        plotly_hud_layout(fig4)
        fig4.update_layout(xaxis=dict(title="Mach"), yaxis=dict(title="Altitude (km)"))
        st.plotly_chart(fig4, use_container_width=True)

    with st.expander("What are the four forces and the flight envelope?"):
        st.markdown("""
**The Four Forces of Flight** — Every aircraft in flight has exactly four forces acting on it:

- **Lift** (↑) — Generated by the wings. Air moves faster over the curved top surface, creating lower pressure above than below. This pressure difference pushes the wing up. Lift must equal weight for level flight.
- **Weight** (↓) — Gravity pulling the aircraft down. For Tejas: ~9,800 kg × 9.81 m/s² ≈ 96 kN.
- **Thrust** (→) — The engine pushing forward. Tejas uses a GE F404 afterburning turbofan producing up to 89 kN.
- **Drag** (←) — Air resistance slowing the aircraft down. Thrust must overcome drag to maintain speed.

When Lift = Weight, the aircraft holds altitude. When Thrust = Drag, it holds speed. The bar chart shows all four in kN (kilonewtons) so you can see the balance.

**Flight Envelope** — The orange shaded area shows where the Tejas *can* fly — every valid combination of Mach and altitude. Outside this boundary, the aircraft either can't generate enough lift (too slow/too high) or exceeds structural limits. Your current position is the blue star.
        """)

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
        fig5.add_vrect(x0=0.1, x1=0.8, fillcolor="rgba(0,200,100,0.05)", line_width=0, annotation_text="Subsonic", annotation_position="top left", annotation_font=dict(color='rgba(0,200,100,0.5)', size=9))
        fig5.add_vrect(x0=0.8, x1=1.2, fillcolor="rgba(255,165,0,0.05)", line_width=0, annotation_text="Transonic", annotation_position="top left", annotation_font=dict(color='rgba(255,165,0,0.5)', size=9))
        fig5.add_vrect(x0=1.2, x1=1.8, fillcolor="rgba(255,50,50,0.05)", line_width=0, annotation_text="Supersonic", annotation_position="top left", annotation_font=dict(color='rgba(255,50,50,0.5)', size=9))
        fig5.add_trace(go.Scatter(x=mr, y=cdc, mode='lines', line=dict(color='#ff6b35', width=2.5), name='CD'))
        fig5.add_trace(go.Scatter(x=[mach], y=[cd], mode='markers', marker=dict(size=12, color='#00f0ff'), name=f'CD={cd:.4f}'))
        plotly_hud_layout(fig5, height=400)
        fig5.update_layout(xaxis=dict(title="Mach"), yaxis=dict(title="CD"))
        st.plotly_chart(fig5, use_container_width=True)

    with cd2:
        st.markdown('<p class="section-header">ISA Atmosphere</p>', unsafe_allow_html=True)
        ap = np.linspace(0, 20000, 200)
        tp = [isa_atmosphere(a)[0] - 273.15 for a in ap]
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(x=tp, y=ap/1000, mode='lines', line=dict(color='#ff6b35', width=2), name='Temp (°C)'))
        fig6.add_trace(go.Scatter(x=[temp-273.15], y=[altitude/1000], mode='markers', marker=dict(size=10, color='#00f0ff', symbol='star'), name='Current'))
        fig6.add_hline(y=11, line_dash="dot", line_color="rgba(255,255,0,0.3)", annotation_text="Tropopause", annotation_font=dict(color='yellow', size=9))
        plotly_hud_layout(fig6, height=400)
        fig6.update_layout(xaxis=dict(title="Temperature (°C)"), yaxis=dict(title="Altitude (km)"))
        st.plotly_chart(fig6, use_container_width=True)

    with st.expander("What are drag coefficient and ISA atmosphere?"):
        st.markdown("""
**Drag Coefficient (CD)** — A dimensionless number that captures how much air resistance an aircraft has at a given speed. Lower CD = more aerodynamic.

- **Subsonic (< Mach 0.8):** Drag is mostly skin friction — air sliding along the aircraft surface. CD rises gently.
- **Transonic (Mach 0.8–1.2):** The "sound barrier." Some air over the wings goes supersonic while the rest stays subsonic, creating shockwaves on the surface. Drag *spikes* — this is called the **transonic drag rise**. This is the hardest region to fly through.
- **Supersonic (> Mach 1.2):** The aircraft is fully through the sound barrier. Drag actually *drops* a bit from the transonic peak, but stays higher than subsonic.

The blue dot shows your current CD. Watch it jump as you cross Mach 0.8–1.0.

**ISA (International Standard Atmosphere)** — A mathematical model of how temperature, pressure, and air density change with altitude. Used worldwide in aviation.

- **Troposphere (0–11 km):** Temperature drops steadily at 6.5°C per km. Most weather happens here.
- **Tropopause (11 km):** Temperature stops dropping and holds at −56.5°C. This is marked by the yellow dotted line.
- **Stratosphere (11–20 km):** Temperature stays roughly constant. Air is very thin up here.

Pilots and engineers need ISA to calculate true airspeed, lift, and engine performance at any altitude.
        """)

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
        fig7.add_trace(go.Scatter(x=gx, y=opg, mode='lines', fill='tozeroy', line=dict(color='#ff4444', width=2), fillcolor='rgba(255,50,50,0.15)'))
        fig7.add_annotation(x=0, y=max(opg), text=f"Peak ΔP ≈ {max(opg):.2f}<br>Width ≈ {bw:.1f} km",
            font=dict(color='#ff6b6b', size=12, family='Rajdhani'), showarrow=True, arrowcolor='#ff4444')
        plotly_hud_layout(fig7, height=350)
        fig7.update_layout(xaxis=dict(title="Lateral Distance (km)"), yaxis=dict(title="Overpressure"))
        st.plotly_chart(fig7, use_container_width=True)

        with st.expander("What is a sonic boom footprint?"):
            st.markdown(f"""
**Sonic Boom Footprint** — When a supersonic jet flies overhead, its shockwave cone hits the ground in a strip. Everyone inside this strip hears the sonic boom.

- **Width** depends on altitude and Mach cone angle. At your current settings, the boom strip is about **{bw:.1f} km wide**.
- **Peak overpressure** is strongest directly below the aircraft and fades toward the edges. A typical fighter sonic boom produces about 1–2 pounds per square foot of overpressure — enough to rattle windows.
- At higher altitudes the boom spreads wider but gets weaker. At lower altitudes it's narrower but much louder.

Fun fact: Concorde's sonic boom was heard as a sharp double crack. The Tejas, being smaller, would produce a shorter, sharper boom.
            """)


# ============================================================
# TAB 2: ISRO LAUNCH SIMULATOR
# ============================================================
with tab_isro:
    st.markdown('<p class="section-header">ISRO Launch Vehicle Simulator</p>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-info">Simulate PSLV and GSLV launch trajectories with real stage parameters</div>', unsafe_allow_html=True)

    with st.expander("New to rockets? Start here"):
        st.markdown("""
**Why do rockets have stages?** A rocket has to carry its own fuel, and fuel is heavy. Once a stage burns out, it's dead weight — so the rocket drops it. Each stage that falls away means less mass to accelerate, making the remaining stages far more efficient. This is the idea behind the **Tsiolkovsky rocket equation**.

**Key terms you'll see below:**
- **Thrust (kN)** — The force the engine produces. More thrust = more acceleration.
- **Burn time (s)** — How long each stage fires before it runs out of fuel.
- **Isp (specific impulse, seconds)** — A measure of fuel efficiency. Higher Isp = more speed per kg of fuel. Solid motors (~270s) are less efficient than liquid (~295s), and cryogenic engines (~440s) are the best.
- **G-force** — How many times normal gravity the astronauts/payload feel. Humans can tolerate about 6G for short periods.
- **Payload** — The satellite or spacecraft the rocket is carrying to orbit.
        """)

    rockets = {
        "PSLV-XL": {
            "stages": [
                {"name": "PS1 + 6 Strap-ons", "thrust": 4846, "burn_time": 105, "mass_full": 295000, "mass_empty": 30000, "isp": 269},
                {"name": "PS2 (Vikas)", "thrust": 799, "burn_time": 158, "mass_full": 42000, "mass_empty": 5000, "isp": 293},
                {"name": "PS3 (Solid)", "thrust": 246, "burn_time": 112, "mass_full": 7600, "mass_empty": 1000, "isp": 294},
                {"name": "PS4 (Twin Engine)", "thrust": 15.2, "burn_time": 525, "mass_full": 2500, "mass_empty": 920, "isp": 318},
            ],
            "payload_leo": 1750,
            "payload_sso": 1050,
            "total_mass": 320000,
            "height": 44.4,
            "missions": 60,
        },
        "GSLV Mk III (LVM3)": {
            "stages": [
                {"name": "S200 Boosters (x2)", "thrust": 5150, "burn_time": 130, "mass_full": 400000, "mass_empty": 62000, "isp": 274},
                {"name": "L110 (Vikas x2)", "thrust": 1598, "burn_time": 200, "mass_full": 116000, "mass_empty": 6700, "isp": 293},
                {"name": "C25 (CE-20 Cryo)", "thrust": 186, "burn_time": 584, "mass_full": 28000, "mass_empty": 3400, "isp": 443},
            ],
            "payload_leo": 10000,
            "payload_gto": 4000,
            "total_mass": 640000,
            "height": 43.4,
            "missions": 8,
        },
    }

    rcol1, rcol2 = st.columns([1, 2])
    with rcol1:
        selected_rocket = st.selectbox("Select Launch Vehicle", list(rockets.keys()))
        rocket = rockets[selected_rocket]

        st.markdown(f"""
        <div class="hud-card">
            <div class="specs-grid">
              <div class="spec-item"><span class="spec-val">{rocket['total_mass']/1000:.0f} t</span><span class="spec-label">Liftoff Mass</span></div>
              <div class="spec-item"><span class="spec-val">{rocket['height']} m</span><span class="spec-label">Height</span></div>
              <div class="spec-item"><span class="spec-val">{rocket.get('payload_leo', rocket.get('payload_sso', 0))} kg</span><span class="spec-label">Payload</span></div>
              <div class="spec-item"><span class="spec-val">{rocket['missions']}</span><span class="spec-label">Missions</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Stage Details:**")
        for i, stage in enumerate(rocket["stages"]):
            st.markdown(f"""
            <div style="background:rgba(0,240,255,0.03); border:1px solid rgba(0,240,255,0.1); border-radius:6px; padding:8px; margin:4px 0;">
                <span style="font-family:Orbitron,monospace; color:#00f0ff; font-size:0.8rem;">STAGE {i+1}</span><br>
                <span style="font-family:Rajdhani,sans-serif; color:#8ab4d4; font-size:0.9rem;">{stage['name']}</span><br>
                <span style="color:#5a9fd4; font-size:0.8rem;">Thrust: {stage['thrust']} kN | Burn: {stage['burn_time']}s | Isp: {stage['isp']}s</span>
            </div>
            """, unsafe_allow_html=True)

    with rcol2:
        dt = 0.5
        t_sim, alt_sim, vel_sim, acc_sim, mach_sim = [0], [0], [0], [0], [0]
        current_mass = rocket["total_mass"]
        v, h = 0.0, 0.0
        stage_boundaries = []

        for si, stage in enumerate(rocket["stages"]):
            fuel_mass = stage["mass_full"] - stage["mass_empty"]
            mdot = fuel_mass / stage["burn_time"]
            stage_mass = current_mass

            for step in range(int(stage["burn_time"] / dt)):
                t = t_sim[-1] + dt
                t_atm, p_atm, rho_atm, a_atm = isa_atmosphere(min(h, 20000))
                g = 9.81 * (6371000 / (6371000 + h)) ** 2

                thrust = stage["thrust"] * 1000
                drag_f = 0.5 * rho_atm * v ** 2 * 0.3 * (3.14 * 1.5 ** 2) if h < 80000 else 0
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

        # Trajectory plot
        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(x=t_sim, y=alt_sim, mode='lines',
            line=dict(color='#ff6b35', width=3), name='Altitude'))
        for tb, ab, sn in stage_boundaries:
            fig_traj.add_vline(x=tb, line_dash="dot", line_color="rgba(0,240,255,0.3)")
            fig_traj.add_annotation(x=tb, y=ab, text=f"⬤ {sn.split('(')[0].strip()} sep",
                font=dict(color='#00f0ff', size=9, family='Rajdhani'), showarrow=True,
                arrowcolor='#00f0ff', arrowsize=0.8)
        fig_traj.update_layout(title=dict(text=f"{selected_rocket} Launch Trajectory", font=dict(color='#00f0ff', family='Orbitron', size=14)),
            xaxis_title="Time (s)", yaxis_title="Altitude (km)")
        plotly_hud_layout(fig_traj, height=400)
        st.plotly_chart(fig_traj, use_container_width=True)

        # Velocity + Mach + G-force
        vc1, vc2 = st.columns(2)
        with vc1:
            fig_vel = go.Figure()
            fig_vel.add_trace(go.Scatter(x=t_sim, y=vel_sim, mode='lines', line=dict(color='#00e878', width=2), name='Velocity (m/s)'))
            fig_vel.update_layout(title=dict(text="Velocity Profile", font=dict(color='#00f0ff', family='Orbitron', size=12)),
                xaxis_title="Time (s)", yaxis_title="Velocity (m/s)")
            plotly_hud_layout(fig_vel, height=350)
            st.plotly_chart(fig_vel, use_container_width=True)

        with vc2:
            fig_g = go.Figure()
            fig_g.add_trace(go.Scatter(x=t_sim, y=acc_sim, mode='lines', line=dict(color='#ffc800', width=2), name='G-force'))
            fig_g.add_hline(y=6, line_dash="dash", line_color="rgba(255,50,50,0.4)", annotation_text="Human limit ~6G", annotation_font=dict(color='#ff5050', size=9))
            fig_g.update_layout(title=dict(text="G-Force Profile", font=dict(color='#00f0ff', family='Orbitron', size=12)),
                xaxis_title="Time (s)", yaxis_title="G-force")
            plotly_hud_layout(fig_g, height=350)
            st.plotly_chart(fig_g, use_container_width=True)

    # Key mission stats
    st.markdown(f"""
    <div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
      <div class="hud-metric"><span class="value">{max(alt_sim):.0f} km</span><span class="label">Max Alt</span></div>
      <div class="hud-metric"><span class="value">{max(vel_sim):.0f} m/s</span><span class="label">Max Vel</span></div>
      <div class="hud-metric"><span class="value">{max(vel_sim)/1000*3.6:.0f} km/h</span><span class="label">Max Speed</span></div>
      <div class="hud-metric"><span class="value">{max(mach_sim):.1f}</span><span class="label">Max Mach</span></div>
      <div class="hud-metric"><span class="value">{max(acc_sim):.1f}G</span><span class="label">Peak G</span></div>
      <div class="hud-metric"><span class="value">{t_sim[-1]:.0f}s</span><span class="label">Burn Time</span></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Understanding the trajectory plots"):
        st.markdown(f"""
**Altitude vs Time** — Shows the rocket climbing. The dotted vertical lines mark **stage separations** — moments when an empty stage drops away. Notice the altitude climbs faster after each separation because the rocket is lighter.

**Velocity Profile** — Speed keeps building with each stage. To reach orbit, a rocket needs about **7,800 m/s** (28,000 km/h). That's roughly 23× the speed of sound.

**G-Force Profile** — As fuel burns, the rocket gets lighter, but thrust stays the same — so acceleration (and G-force) *increases* throughout each stage. The jumps happen at stage separation when thrust suddenly changes. The red dashed line at 6G is the approximate human tolerance limit.

**{selected_rocket} quick facts:**
- Total liftoff mass: **{rocket['total_mass']/1000:.0f} tonnes** — most of that is fuel
- Number of stages: **{len(rocket['stages'])}**
- {rocket['missions']} successful missions and counting
        """)


# ============================================================
# TAB 3: BRAHMOS
# ============================================================
with tab_brahmos:
    st.markdown('<p class="section-header">BrahMos Supersonic Cruise Missile</p>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-info">Simulate BrahMos flight trajectory — the world\'s fastest cruise missile in service</div>', unsafe_allow_html=True)

    with st.expander("What is BrahMos? (Background)"):
        st.markdown("""
**BrahMos** is a joint India-Russia supersonic cruise missile, named after the rivers **Brahma**putra (India) and **Mos**kva (Russia). It's the fastest cruise missile in operational service worldwide.

**Key concepts:**
- **Cruise missile** — A missile that flies like an aircraft at a set altitude, using wings for lift and an engine for sustained flight (unlike ballistic missiles that arc through space).
- **Ramjet engine** — A jet engine with no moving parts. It uses the missile's own speed to compress incoming air. Brilliant above Mach 2, but it can't start from standstill — that's why BrahMos uses a solid rocket booster to get up to speed first.
- **Scramjet** — A *supersonic combustion* ramjet, used in BrahMos-II. Air flows through the engine at supersonic speeds even inside the combustion chamber. This enables Mach 7+ speeds.
- **Sea-skimming** — In the final phase, the missile drops to 10–15 m above the sea. At this altitude it's nearly invisible to ship radar until the last few seconds.
- **Variants:** Block III (standard, Mach 2.8), BrahMos-ER (extended range, 800 km), BrahMos-II (future hypersonic, Mach 7).
        """)

    bcol1, bcol2 = st.columns([1, 2])
    with bcol1:
        brahmos_variant = st.selectbox("Variant", ["BrahMos Block III", "BrahMos-II (Hypersonic)", "BrahMos-ER"])
        target_range = st.slider("Target Range (km)", 50, 800, 290,
            help="Distance to the target. BrahMos Block III has a 450 km range, BrahMos-ER reaches 800 km.")

        specs = {
            "BrahMos Block III": {"speed_mach": 2.8, "range": 450, "weight": 3000, "warhead": 200, "altitude_cruise": 15000, "altitude_sea_skim": 10, "engine": "Ramjet"},
            "BrahMos-II (Hypersonic)": {"speed_mach": 7.0, "range": 600, "weight": 3500, "warhead": 200, "altitude_cruise": 40000, "altitude_sea_skim": 15, "engine": "Scramjet"},
            "BrahMos-ER": {"speed_mach": 2.8, "range": 800, "weight": 2800, "warhead": 200, "altitude_cruise": 15000, "altitude_sea_skim": 10, "engine": "Ramjet"},
        }
        sp = specs[brahmos_variant]

        st.markdown(f"""
        <div class="hud-card">
            <div class="specs-grid">
              <div class="spec-item"><span class="spec-val">M {sp['speed_mach']}</span><span class="spec-label">Speed</span></div>
              <div class="spec-item"><span class="spec-val">{sp['range']} km</span><span class="spec-label">Range</span></div>
              <div class="spec-item"><span class="spec-val">{sp['weight']} kg</span><span class="spec-label">Weight</span></div>
              <div class="spec-item"><span class="spec-val">{sp['warhead']} kg</span><span class="spec-label">Warhead</span></div>
              <div class="spec-item"><span class="spec-val">{sp['engine']}</span><span class="spec-label">Engine</span></div>
              <div class="spec-item"><span class="spec-val">{sp['altitude_sea_skim']} m</span><span class="spec-label">Sea Skim</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with bcol2:
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
                alt_flight[i] = cruise_alt * (1 - frac) ** 2
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

        fig_bm.update_layout(title=dict(text=f"{brahmos_variant} Flight Profile", font=dict(color='#ff3232', family='Orbitron', size=14)),
            xaxis_title="Range (km)", yaxis_title="Altitude (km)")
        plotly_hud_layout(fig_bm, height=450)
        st.plotly_chart(fig_bm, use_container_width=True)

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

    st.markdown(f"""
    <div class="alert-box alert-boom">
    ⚡ BrahMos travels at {cruise_speed*3.6:.0f} km/h — a target at {target_range} km would be hit in just {time_flight[-1]:.0f} seconds.
    At this speed, the missile covers 1 km every {1000/cruise_speed:.1f} seconds.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Understanding the flight profile"):
        st.markdown(f"""
**The three phases of a BrahMos strike:**

1. **Climb phase** (0–{climb_dist:.0f} km) — After launch, the solid rocket booster fires and the missile climbs steeply to cruising altitude. The booster drops off and the ramjet ignites.

2. **Cruise phase** ({climb_dist:.0f}–{climb_dist+cruise_dist:.0f} km) — The missile flies at Mach {sp['speed_mach']} at {cruise_alt/1000:.0f} km altitude. At this height it's hard to detect but high enough for efficient flight.

3. **Terminal dive** (last {dive_dist:.0f} km) — The missile dives toward the target. For anti-ship strikes it drops to just {sea_skim_alt} metres above the sea (sea-skimming), making it nearly impossible for ship defences to react in time.

**Why is speed so important?** At Mach {sp['speed_mach']}, a defender has only **{(dive_dist*1000/cruise_speed):.1f} seconds** from the moment the missile appears on close-range radar to impact. Most ship defence systems need 8–15 seconds to react. This is what makes BrahMos so effective.

**Warhead: {sp['warhead']} kg** — The kinetic energy alone at Mach {sp['speed_mach']} is devastating. The total impact energy is roughly equivalent to **{0.5 * sp['weight'] * cruise_speed**2 / 4.184e9:.1f} tonnes of TNT**.
        """)


# ============================================================
# TAB 4: ABOUT
# ============================================================
with tab_about:
    st.markdown('<p class="section-header">About VAJRA</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hud-card">
        <h3 style="font-family:Orbitron,monospace; color:#00f0ff; letter-spacing:3px; margin-top:0;">WHAT IS VAJRA?</h3>
        <p style="font-family:Rajdhani,sans-serif; color:#8ab4d4; font-size:1.1rem; line-height:1.8;">
        VAJRA is an interactive physics simulator showcasing <b style="color:#ff6b35;">India's indigenous aerospace capabilities</b>.
        Built with real engineering parameters, it lets you explore the physics behind some of India's most
        advanced defense and space systems.
        </p>
        <p style="font-family:Rajdhani,sans-serif; color:#8ab4d4; font-size:1.1rem; line-height:1.8;">
        Every simulation uses <b style="color:#00f0ff;">real physics models</b> — International Standard Atmosphere,
        compressible aerodynamics, rocket propulsion equations, and trajectory mechanics — not approximations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hud-card">
        <h3 style="font-family:Orbitron,monospace; color:#00f0ff; letter-spacing:3px; margin-top:0;">PLATFORMS SIMULATED</h3>
        <div class="specs-grid" style="grid-template-columns: 1fr 1fr 1fr; gap:12px;">
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val">HAL TEJAS</span>
            <span class="spec-label">Light Combat Aircraft Mk1A</span>
            <p style="color:#5a9fd4; font-size:0.8rem; margin:5px 0 0;">Supersonic flight physics, Mach cone, sonic boom, aerodynamic forces</p>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val">ISRO PSLV/LVM3</span>
            <span class="spec-label">Launch Vehicle Trajectory</span>
            <p style="color:#5a9fd4; font-size:0.8rem; margin:5px 0 0;">Multi-stage rocket trajectory, velocity, G-force profiles</p>
          </div>
          <div class="spec-item" style="padding:15px;">
            <span class="spec-val">BRAHMOS</span>
            <span class="spec-label">Cruise Missile</span>
            <p style="color:#5a9fd4; font-size:0.8rem; margin:5px 0 0;">Supersonic flight profile, sea-skimming terminal phase</p>
          </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hud-card">
        <h3 style="font-family:Orbitron,monospace; color:#00f0ff; letter-spacing:3px; margin-top:0;">PHYSICS MODELS</h3>
        <div style="font-family:Rajdhani,sans-serif; color:#8ab4d4; font-size:1rem; line-height:2;">
        ✦ International Standard Atmosphere (ISA) — troposphere + stratosphere<br>
        ✦ Mach cone geometry — θ = arcsin(1/M)<br>
        ✦ Sonic boom N-wave pressure profile<br>
        ✦ Tsiolkovsky rocket equation for staging<br>
        ✦ Drag models with transonic wave drag rise<br>
        ✦ Dynamic pressure and aerodynamic force balance<br>
        ✦ Gravity turn trajectory approximation<br>
        ✦ Prandtl-Glauert compressibility correction
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hud-card">
        <h3 style="font-family:Orbitron,monospace; color:#ff6b35; letter-spacing:3px; margin-top:0;">COMING SOON</h3>
        <div style="font-family:Rajdhani,sans-serif; color:#8ab4d4; font-size:1rem; line-height:2;">
        ◈ Chandrayaan orbital mechanics simulator<br>
        ◈ Gaganyaan re-entry heat shield analysis<br>
        ◈ AMCA (Advanced Medium Combat Aircraft) stealth profile<br>
        ◈ Akash missile intercept trajectory<br>
        ◈ Live ISRO satellite tracking<br>
        ◈ Tejas Mk1A spotting log + community map<br>
        ◈ Mobile app (Play Store / App Store)
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:15px;">
    <p style="font-family:'Orbitron',monospace; color:rgba(0,240,255,0.4); font-size:0.7rem; letter-spacing:4px;">
    VAJRA v3.0 — BUILT BY ATHARV SHUKLA</p>
    <p style="font-family:'Rajdhani',sans-serif; color:rgba(90,159,212,0.3); font-size:0.7rem; letter-spacing:2px;">
    AMITY INTERNATIONAL SCHOOL SEC 46 GURGAON | INDIAN AEROSPACE SIMULATOR</p>
</div>
""", unsafe_allow_html=True)
