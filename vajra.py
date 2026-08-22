import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="VAJRA - HAL Tejas Sonic Boom Simulator", layout="wide", page_icon="⚡")

# --- HUD THEME CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 40%, #0a1628 100%);
}

.hud-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00f0ff, #00a8ff, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: 4px;
    text-shadow: 0 0 30px rgba(0,240,255,0.3);
    animation: glow 2s ease-in-out infinite alternate;
    margin-bottom: 0;
}

.hud-subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.15rem;
    color: #5a9fd4;
    text-align: center;
    letter-spacing: 6px;
    text-transform: uppercase;
    margin-top: 0;
}

@keyframes glow {
    from { filter: brightness(1); }
    to { filter: brightness(1.3); }
}

@keyframes pulse-border {
    0%, 100% { border-color: rgba(0,240,255,0.3); box-shadow: 0 0 15px rgba(0,240,255,0.1); }
    50% { border-color: rgba(0,240,255,0.7); box-shadow: 0 0 25px rgba(0,240,255,0.3); }
}

.hud-card {
    background: linear-gradient(145deg, rgba(10,22,40,0.9), rgba(5,10,20,0.95));
    border: 1px solid rgba(0,240,255,0.3);
    border-radius: 12px;
    padding: 20px;
    margin: 8px 0;
    animation: pulse-border 3s ease-in-out infinite;
}

.hud-metric {
    font-family: 'Orbitron', monospace;
    text-align: center;
    padding: 15px 10px;
}
.hud-metric .value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #00f0ff;
    text-shadow: 0 0 10px rgba(0,240,255,0.5);
    display: block;
}
.hud-metric .label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    color: #5a9fd4;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 4px;
    display: block;
}

.regime-badge {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    padding: 8px 20px;
    border-radius: 25px;
    text-align: center;
    font-weight: 700;
    letter-spacing: 3px;
    display: inline-block;
    margin: 5px auto;
}
.regime-subsonic {
    background: rgba(0,200,100,0.15);
    border: 2px solid #00c864;
    color: #00ff7f;
    box-shadow: 0 0 15px rgba(0,200,100,0.3);
}
.regime-transonic {
    background: rgba(255,165,0,0.15);
    border: 2px solid #ffa500;
    color: #ffb733;
    box-shadow: 0 0 15px rgba(255,165,0,0.3);
    animation: pulse-border-warn 1.5s ease-in-out infinite;
}
.regime-supersonic {
    background: rgba(255,50,50,0.15);
    border: 2px solid #ff3232;
    color: #ff4444;
    box-shadow: 0 0 20px rgba(255,50,50,0.4);
    animation: pulse-border-danger 1s ease-in-out infinite;
}

@keyframes pulse-border-warn {
    0%, 100% { box-shadow: 0 0 15px rgba(255,165,0,0.2); }
    50% { box-shadow: 0 0 30px rgba(255,165,0,0.5); }
}
@keyframes pulse-border-danger {
    0%, 100% { box-shadow: 0 0 15px rgba(255,50,50,0.3); }
    50% { box-shadow: 0 0 35px rgba(255,50,50,0.7); }
}

.tejas-svg-container {
    text-align: center;
    margin: 10px 0;
}

.specs-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    font-family: 'Rajdhani', sans-serif;
}
.spec-item {
    background: rgba(0,240,255,0.05);
    border: 1px solid rgba(0,240,255,0.15);
    border-radius: 8px;
    padding: 8px 12px;
    text-align: center;
}
.spec-item .spec-val {
    font-family: 'Orbitron', monospace;
    font-size: 1.05rem;
    color: #00f0ff;
    display: block;
}
.spec-item .spec-label {
    font-size: 0.7rem;
    color: #5a9fd4;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 1.1rem;
    color: #00f0ff;
    letter-spacing: 3px;
    border-bottom: 1px solid rgba(0,240,255,0.3);
    padding-bottom: 8px;
    margin-bottom: 15px;
    text-transform: uppercase;
}

.alert-box {
    font-family: 'Rajdhani', sans-serif;
    padding: 12px 20px;
    border-radius: 8px;
    margin: 5px 0;
    font-size: 1rem;
    letter-spacing: 1px;
}
.alert-boom {
    background: rgba(255,50,50,0.1);
    border-left: 4px solid #ff3232;
    color: #ff6b6b;
    animation: pulse-border-danger 1.5s ease-in-out infinite;
}
.alert-transonic {
    background: rgba(255,165,0,0.1);
    border-left: 4px solid #ffa500;
    color: #ffb733;
}
.alert-normal {
    background: rgba(0,200,100,0.1);
    border-left: 4px solid #00c864;
    color: #00ff7f;
}
.alert-limit {
    background: rgba(255,0,0,0.1);
    border-left: 4px solid #ff0000;
    color: #ff4444;
}

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060d18, #0a1628, #060d18);
    border-right: 1px solid rgba(0,240,255,0.2);
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 class="hud-title">VAJRA</h1>', unsafe_allow_html=True)
st.markdown('<p class="hud-subtitle">HAL Tejas Mk1A &bull; Sonic Boom Simulator</p>', unsafe_allow_html=True)

# --- SVG JET SILHOUETTE ---
tejas_svg = """
<div class="tejas-svg-container">
<svg width="320" height="80" viewBox="0 0 320 80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="jetGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#003366;stop-opacity:0.8"/>
      <stop offset="50%" style="stop-color:#00a8ff;stop-opacity:0.9"/>
      <stop offset="100%" style="stop-color:#00f0ff;stop-opacity:0.7"/>
    </linearGradient>
    <filter id="jetGlow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>
  <g transform="translate(40,40)" filter="url(#jetGlow)">
    <polygon points="240,0 200,-6 140,-8 80,-18 60,-22 50,-18 30,-10 0,-4 0,4 30,10 50,18 60,22 80,18 140,8 200,6"
             fill="url(#jetGrad)" stroke="#00f0ff" stroke-width="0.8" opacity="0.85"/>
    <polygon points="90,-18 70,-35 60,-35 75,-18" fill="#004488" stroke="#00a8ff" stroke-width="0.5" opacity="0.7"/>
    <polygon points="90,18 70,35 60,35 75,18" fill="#004488" stroke="#00a8ff" stroke-width="0.5" opacity="0.7"/>
    <polygon points="190,-6 175,-16 170,-16 182,-6" fill="#004488" stroke="#00a8ff" stroke-width="0.5" opacity="0.7"/>
    <polygon points="190,6 175,16 170,16 182,6" fill="#004488" stroke="#00a8ff" stroke-width="0.5" opacity="0.7"/>
    <circle cx="210" cy="0" r="3" fill="#00f0ff" opacity="0.6"/>
    <line x1="-5" y1="0" x2="-25" y2="-3" stroke="#ff6b35" stroke-width="2.5" opacity="0.7"/>
    <line x1="-5" y1="0" x2="-25" y2="3" stroke="#ff6b35" stroke-width="2.5" opacity="0.7"/>
    <line x1="-5" y1="0" x2="-30" y2="0" stroke="#ffaa00" stroke-width="1.5" opacity="0.5"/>
  </g>
</svg>
</div>
"""
st.markdown(tejas_svg, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown('<p class="section-header">Flight Controls</p>', unsafe_allow_html=True)
mach = st.sidebar.slider("Mach Number", 0.1, 3.0, 0.8, 0.01)
altitude = st.sidebar.slider("Altitude (m)", 0, 20000, 5000, 100)

TEJAS_WING_AREA = 38.4
TEJAS_MASS = 9800
TEJAS_MAX_MACH = 1.8
TEJAS_CEILING = 16500
TEJAS_MAX_THRUST = 89.0
TEJAS_DRAG_CD0 = 0.02

if altitude <= 11000:
    temp = 288.15 - 0.0065 * altitude
    pressure_atm = 101325 * (temp / 288.15) ** 5.2561
else:
    temp = 216.65
    pressure_atm = 22632 * np.exp(-0.00015769 * (altitude - 11000))

rho = pressure_atm / (287.05 * temp)
speed_of_sound = np.sqrt(1.4 * 287.05 * temp)
aircraft_speed = mach * speed_of_sound

if mach < 0.8:
    regime = "SUBSONIC"
    regime_class = "regime-subsonic"
elif mach < 1.0:
    regime = "TRANSONIC"
    regime_class = "regime-transonic"
else:
    regime = "SUPERSONIC"
    regime_class = "regime-supersonic"

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

# --- SIDEBAR INFO ---
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

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="section-header">Tejas Mk1A Specs</p>', unsafe_allow_html=True)
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

# --- HUD METRICS BAR ---
st.markdown(f"""
<div class="hud-card" style="display:flex; justify-content:space-around; flex-wrap:wrap;">
  <div class="hud-metric"><span class="value">{mach:.2f}</span><span class="label">Mach</span></div>
  <div class="hud-metric"><span class="value">{altitude/1000:.1f} km</span><span class="label">Altitude</span></div>
  <div class="hud-metric"><span class="value">{temp - 273.15:.0f}°C</span><span class="label">OAT</span></div>
  <div class="hud-metric"><span class="value">{aircraft_speed:.0f}</span><span class="label">Speed m/s</span></div>
  <div class="hud-metric"><span class="value">{aircraft_speed*3.6:.0f}</span><span class="label">km/h</span></div>
  <div class="hud-metric"><span class="value">{g_load:.1f}G</span><span class="label">G-Load</span></div>
</div>
""", unsafe_allow_html=True)

# --- STATUS ALERTS ---
if mach >= 1.0:
    half_angle_alert = np.degrees(np.arcsin(1 / mach))
    boom_s = 0.5 + 1.5 * (mach - 1.0)
    st.markdown(f'<div class="alert-box alert-boom">⚡ SONIC BOOM ACTIVE — Shockwave half-angle: {half_angle_alert:.1f}° | Overpressure: {boom_s:.2f}</div>', unsafe_allow_html=True)
elif mach >= 0.8:
    st.markdown('<div class="alert-box alert-transonic">⚠ TRANSONIC — Wave drag rising, compressibility effects significant</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="alert-box alert-normal">✓ SUBSONIC — Normal aerodynamic conditions</div>', unsafe_allow_html=True)

if mach > TEJAS_MAX_MACH:
    st.markdown(f'<div class="alert-box alert-limit">⛔ BEYOND MAX — Mach {TEJAS_MAX_MACH} structural limit exceeded</div>', unsafe_allow_html=True)
if altitude > TEJAS_CEILING:
    st.markdown(f'<div class="alert-box alert-limit">⛔ ABOVE CEILING — {TEJAS_CEILING/1000:.1f} km service ceiling exceeded</div>', unsafe_allow_html=True)
if thrust_required > TEJAS_MAX_THRUST * 1000:
    st.markdown(f'<div class="alert-box alert-limit">⛔ THRUST DEFICIT — Need {thrust_required/1000:.1f} kN, max available {TEJAS_MAX_THRUST} kN</div>', unsafe_allow_html=True)

# --- MAIN VISUALIZATIONS ---
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
        Y = R * np.cos(PHI)
        Z = R * np.sin(PHI)
        X_cone = -X

        intensity = min(1.0, (mach - 1.0) / 1.5)

        fig1 = go.Figure()
        fig1.add_trace(go.Surface(
            x=X_cone, y=Y, z=Z,
            colorscale=[
                [0, f'rgba(255, 60, 10, {0.3 + 0.4 * intensity})'],
                [0.5, f'rgba(255, 120, 30, {0.2 + 0.3 * intensity})'],
                [1, f'rgba(255, 180, 60, {0.1 + 0.15 * intensity})']
            ],
            showscale=False, opacity=0.6,
            name='Mach Cone'
        ))

        fig1.add_trace(go.Scatter3d(
            x=[0.3], y=[0], z=[0],
            mode='markers+text',
            marker=dict(size=8, color='#00f0ff', symbol='diamond'),
            text=[f'TEJAS M{mach:.1f}'],
            textposition='top center',
            textfont=dict(color='#00f0ff', size=11),
            name='Aircraft'
        ))

        fig1.update_layout(
            title=dict(text=f"3D Mach Cone — Half Angle: {half_angle:.1f}°", font=dict(color='#00f0ff', family='Orbitron')),
            scene=dict(
                xaxis=dict(title='X', backgroundcolor='rgb(10,15,28)', gridcolor='rgba(0,240,255,0.1)', color='#5a9fd4'),
                yaxis=dict(title='Y', backgroundcolor='rgb(10,15,28)', gridcolor='rgba(0,240,255,0.1)', color='#5a9fd4'),
                zaxis=dict(title='Z', backgroundcolor='rgb(10,15,28)', gridcolor='rgba(0,240,255,0.1)', color='#5a9fd4'),
                bgcolor='rgb(8,12,22)',
                aspectmode='data'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.markdown("""
        <div class="hud-card" style="text-align:center; padding:60px 20px;">
            <p style="font-family:'Orbitron',monospace; color:#5a9fd4; font-size:1rem; letter-spacing:2px;">
            NO SHOCKWAVE AT SUBSONIC SPEEDS</p>
            <p style="font-family:'Rajdhani',sans-serif; color:#3a6f94; font-size:0.9rem;">
            Increase Mach to 1.0+ to generate the 3D Mach cone</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown('<p class="section-header">Pressure Wave — N-Wave</p>', unsafe_allow_html=True)
    x_wave = np.linspace(-10, 10, 1000)

    if mach >= 1.0:
        boom_strength = 0.5 + 1.5 * (mach - 1.0)
        shock_width = 0.3
        n_wave_length = 3.0 + 2.0 / mach

        front_shock = boom_strength * (1 / (1 + np.exp(-x_wave / (shock_width * 0.3))))
        rear_shock = boom_strength * (1 / (1 + np.exp(-(x_wave - n_wave_length) / (shock_width * 0.3))))
        linear_drop = boom_strength * (1 - (x_wave / n_wave_length))
        linear_drop = np.clip(linear_drop, -boom_strength, boom_strength)

        mask = (x_wave >= -shock_width * 3) & (x_wave <= n_wave_length + shock_width * 3)
        pressure_wave = np.ones_like(x_wave)
        pressure_wave[mask] = 1.0 + (front_shock[mask] - rear_shock[mask]) * linear_drop[mask] / boom_strength

        overpressure = boom_strength * (rho / 1.225) ** 0.5
        title_text = f"Sonic Boom N-Wave | ΔP ≈ {overpressure:.2f}"
    else:
        comp_factor = 1 / np.sqrt(max(1 - mach ** 2, 0.01))
        pressure_wave = 1.0 + 0.3 * comp_factor * np.exp(-0.5 * (x_wave * (1 - mach)) ** 2) * np.cos(3 * x_wave)
        title_text = f"Subsonic Pressure Field | β = {1/comp_factor:.3f}"

    fig2 = go.Figure()

    color_above = 'rgba(255,80,50,0.3)' if mach >= 1.0 else 'rgba(0,180,255,0.15)'
    color_below = 'rgba(0,150,255,0.3)' if mach >= 1.0 else 'rgba(0,180,255,0.15)'
    line_color = '#ff4444' if mach >= 1.0 else '#00f0ff'

    fig2.add_trace(go.Scatter(
        x=x_wave, y=np.where(pressure_wave >= 1.0, pressure_wave, 1.0),
        mode='lines', line=dict(width=0), showlegend=False
    ))
    fig2.add_trace(go.Scatter(
        x=x_wave, y=np.ones_like(x_wave),
        mode='lines', line=dict(width=0), fill='tonexty',
        fillcolor=color_above, showlegend=False
    ))

    fig2.add_trace(go.Scatter(
        x=x_wave, y=pressure_wave, mode='lines',
        line=dict(color=line_color, width=2.5),
        name='Pressure'
    ))
    fig2.add_hline(y=1.0, line_dash="dash", line_color="rgba(100,150,200,0.4)",
                   annotation_text="P∞", annotation_font=dict(color='#5a9fd4'))

    fig2.update_layout(
        title=dict(text=title_text, font=dict(color='#00f0ff', family='Orbitron', size=13)),
        xaxis_title="Position",
        yaxis_title="P / P∞",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(8,12,22,0.9)',
        height=500,
        xaxis=dict(gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        yaxis=dict(gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        margin=dict(l=50, r=20, t=50, b=40)
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- FORCES & ENVELOPE ---
st.markdown("---")
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown('<p class="section-header">Four Forces of Flight</p>', unsafe_allow_html=True)

    fig3 = go.Figure()
    max_force = max(lift, weight, thrust_required, drag, 1)
    s = 3.0 / max_force

    force_colors = {
        'lift': '#00e878', 'weight': '#ff5050',
        'thrust': '#00b4ff', 'drag': '#ffc800'
    }

    fig3.add_trace(go.Scatter(
        x=[0, 0], y=[0, lift * s], mode='lines',
        line=dict(color=force_colors['lift'], width=6),
        name=f'Lift — {lift/1000:.1f} kN', showlegend=True
    ))
    fig3.add_trace(go.Scatter(
        x=[0, 0], y=[0, -weight * s], mode='lines',
        line=dict(color=force_colors['weight'], width=6),
        name=f'Weight — {weight/1000:.1f} kN', showlegend=True
    ))
    fig3.add_trace(go.Scatter(
        x=[0, thrust_required * s], y=[0, 0], mode='lines',
        line=dict(color=force_colors['thrust'], width=6),
        name=f'Thrust — {thrust_required/1000:.1f} kN', showlegend=True
    ))
    fig3.add_trace(go.Scatter(
        x=[0, -drag * s], y=[0, 0], mode='lines',
        line=dict(color=force_colors['drag'], width=6),
        name=f'Drag — {drag/1000:.1f} kN', showlegend=True
    ))

    fig3.add_annotation(x=0, y=lift * s + 0.3, text=f"<b>LIFT</b><br>{lift/1000:.1f} kN",
                        font=dict(size=13, color=force_colors['lift'], family='Rajdhani'),
                        showarrow=False)
    fig3.add_annotation(x=0, y=-weight * s - 0.3, text=f"<b>WEIGHT</b><br>{weight/1000:.1f} kN",
                        font=dict(size=13, color=force_colors['weight'], family='Rajdhani'),
                        showarrow=False)
    fig3.add_annotation(x=thrust_required * s + 0.3, y=0, text=f"<b>THRUST</b><br>{thrust_required/1000:.1f} kN",
                        font=dict(size=13, color=force_colors['thrust'], family='Rajdhani'),
                        showarrow=False, xanchor='left')
    fig3.add_annotation(x=-drag * s - 0.3, y=0, text=f"<b>DRAG</b><br>{drag/1000:.1f} kN",
                        font=dict(size=13, color=force_colors['drag'], family='Rajdhani'),
                        showarrow=False, xanchor='right')

    fig3.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers+text',
        marker=dict(size=22, color='#00f0ff', symbol='diamond',
                    line=dict(width=2, color='rgba(0,240,255,0.5)')),
        text=['TEJAS'], textposition='bottom center',
        textfont=dict(color='#00f0ff', size=10, family='Orbitron'),
        showlegend=False, hoverinfo='text', hovertext='Aircraft CG'
    ))

    fig3.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(8,12,22,0.9)',
        xaxis=dict(range=[-5, 5], showgrid=False, zeroline=True,
                   zerolinecolor='rgba(0,240,255,0.15)', showticklabels=False),
        yaxis=dict(range=[-5, 5], showgrid=False, zeroline=True,
                   zerolinecolor='rgba(0,240,255,0.15)', scaleanchor="x", showticklabels=False),
        height=450,
        legend=dict(
            font=dict(color='#8ab4d4', size=11, family='Rajdhani'),
            bgcolor='rgba(8,12,22,0.8)',
            bordercolor='rgba(0,240,255,0.2)',
            borderwidth=1,
            x=0.01, y=0.99, xanchor='left', yanchor='top'
        ),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_f2:
    st.markdown('<p class="section-header">Performance Envelope</p>', unsafe_allow_html=True)

    altitudes_env = np.linspace(0, 20000, 200)
    mach_envelope = []
    for alt in altitudes_env:
        if alt <= 11000:
            t = 288.15 - 0.0065 * alt
            p = 101325 * (t / 288.15) ** 5.2561
        else:
            t = 216.65
            p = 22632 * np.exp(-0.00015769 * (alt - 11000))
        r = p / (287.05 * t)
        q_limit = 80000
        a = np.sqrt(1.4 * 287.05 * t)
        v_limit = np.sqrt(2 * q_limit / r)
        m_limit = min(v_limit / a, TEJAS_MAX_MACH)
        if alt > TEJAS_CEILING:
            m_limit = max(0, m_limit * (1 - (alt - TEJAS_CEILING) / 5000))
        mach_envelope.append(m_limit)

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=mach_envelope, y=altitudes_env / 1000,
        mode='lines', fill='tozerox',
        line=dict(color='#ff6b35', width=2),
        fillcolor='rgba(255,107,53,0.1)',
        name='Envelope'
    ))
    fig4.add_trace(go.Scatter(
        x=[mach], y=[altitude / 1000],
        mode='markers+text',
        marker=dict(size=14, color='#00f0ff', symbol='star-diamond',
                    line=dict(width=2, color='rgba(0,240,255,0.5)')),
        text=[f'M{mach:.1f}'], textposition='top right',
        textfont=dict(color='#00f0ff', size=12, family='Orbitron'),
        name='Current'
    ))
    fig4.add_vline(x=1.0, line_dash="dot", line_color="rgba(255,255,0,0.4)",
                   annotation_text="Mach 1", annotation_font=dict(color='yellow', size=10))

    fig4.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(8,12,22,0.9)',
        xaxis=dict(title="Mach", gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        yaxis=dict(title="Altitude (km)", gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        height=450,
        margin=dict(l=50, r=20, t=20, b=40)
    )
    st.plotly_chart(fig4, use_container_width=True)

# --- DRAG CURVE & ATMOSPHERE ---
st.markdown("---")
col_d1, col_d2 = st.columns(2)

with col_d1:
    st.markdown('<p class="section-header">Drag Coefficient vs Mach</p>', unsafe_allow_html=True)
    mach_range = np.linspace(0.1, 3.0, 300)
    cd_curve = []
    for m in mach_range:
        if m < 0.8:
            c = TEJAS_DRAG_CD0 + 0.06 * (m ** 2)
        elif m < 1.2:
            c = TEJAS_DRAG_CD0 + 0.06 * (m ** 2) + 0.2 * (m - 0.8) ** 2
        else:
            c = TEJAS_DRAG_CD0 + 0.06 * (m ** 2) + 0.015 / (m ** 2)
        cd_curve.append(c)

    fig5 = go.Figure()

    fig5.add_vrect(x0=0.1, x1=0.8, fillcolor="rgba(0,200,100,0.05)", line_width=0,
                   annotation_text="Subsonic", annotation_position="top left",
                   annotation_font=dict(color='rgba(0,200,100,0.5)', size=10))
    fig5.add_vrect(x0=0.8, x1=1.2, fillcolor="rgba(255,165,0,0.05)", line_width=0,
                   annotation_text="Transonic", annotation_position="top left",
                   annotation_font=dict(color='rgba(255,165,0,0.5)', size=10))
    fig5.add_vrect(x0=1.2, x1=3.0, fillcolor="rgba(255,50,50,0.05)", line_width=0,
                   annotation_text="Supersonic", annotation_position="top left",
                   annotation_font=dict(color='rgba(255,50,50,0.5)', size=10))

    fig5.add_trace(go.Scatter(
        x=mach_range, y=cd_curve, mode='lines',
        line=dict(color='#ff6b35', width=2.5),
        name='CD'
    ))
    fig5.add_trace(go.Scatter(
        x=[mach], y=[cd], mode='markers',
        marker=dict(size=12, color='#00f0ff', symbol='circle',
                    line=dict(width=2, color='rgba(0,240,255,0.5)')),
        name=f'Current CD={cd:.4f}'
    ))

    fig5.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(8,12,22,0.9)',
        xaxis=dict(title="Mach", gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        yaxis=dict(title="CD", gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        height=400,
        margin=dict(l=50, r=20, t=20, b=40)
    )
    st.plotly_chart(fig5, use_container_width=True)

with col_d2:
    st.markdown('<p class="section-header">ISA Atmosphere Profile</p>', unsafe_allow_html=True)
    alt_profile = np.linspace(0, 20000, 200)
    temp_profile = []
    sos_profile = []
    rho_profile = []
    for a in alt_profile:
        if a <= 11000:
            t = 288.15 - 0.0065 * a
            p = 101325 * (t / 288.15) ** 5.2561
        else:
            t = 216.65
            p = 22632 * np.exp(-0.00015769 * (a - 11000))
        r = p / (287.05 * t)
        temp_profile.append(t - 273.15)
        sos_profile.append(np.sqrt(1.4 * 287.05 * t))
        rho_profile.append(r)

    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=temp_profile, y=alt_profile / 1000, mode='lines',
        line=dict(color='#ff6b35', width=2), name='Temperature (°C)'
    ))
    fig6.add_trace(go.Scatter(
        x=[t - 273.15 for t in [temp]], y=[altitude / 1000], mode='markers',
        marker=dict(size=10, color='#00f0ff', symbol='star'),
        name='Current Alt', showlegend=True
    ))

    fig6.add_hline(y=11, line_dash="dot", line_color="rgba(255,255,0,0.3)",
                   annotation_text="Tropopause 11km", annotation_font=dict(color='yellow', size=9))

    fig6.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(8,12,22,0.9)',
        xaxis=dict(title="Temperature (°C)", gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        yaxis=dict(title="Altitude (km)", gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        height=400,
        margin=dict(l=50, r=20, t=20, b=40)
    )
    st.plotly_chart(fig6, use_container_width=True)

# --- SONIC BOOM GROUND FOOTPRINT ---
if mach >= 1.0:
    st.markdown("---")
    st.markdown('<p class="section-header">Sonic Boom Ground Footprint</p>', unsafe_allow_html=True)

    boom_width = altitude * np.tan(np.radians(half_angle_alert))
    boom_carpet_width = boom_width * 2 / 1000

    ground_x = np.linspace(-boom_carpet_width / 2, boom_carpet_width / 2, 200)
    ground_intensity = np.exp(-2 * (ground_x / (boom_carpet_width / 2)) ** 2)
    overpressure_ground = boom_strength * ground_intensity * (1.225 / rho) ** 0.5

    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=ground_x, y=overpressure_ground, mode='lines',
        fill='tozeroy',
        line=dict(color='#ff4444', width=2),
        fillcolor='rgba(255,50,50,0.15)',
        name='Overpressure'
    ))
    fig7.add_annotation(
        x=0, y=max(overpressure_ground),
        text=f"Peak ΔP ≈ {max(overpressure_ground):.2f}<br>Carpet width ≈ {boom_carpet_width:.1f} km",
        font=dict(color='#ff6b6b', size=12, family='Rajdhani'),
        showarrow=True, arrowcolor='#ff4444'
    )

    fig7.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(8,12,22,0.9)',
        xaxis=dict(title="Lateral Distance (km)", gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        yaxis=dict(title="Relative Overpressure", gridcolor='rgba(0,240,255,0.08)', color='#5a9fd4'),
        height=350,
        margin=dict(l=50, r=20, t=20, b=40)
    )
    st.plotly_chart(fig7, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:15px;">
    <p style="font-family:'Orbitron',monospace; color:rgba(0,240,255,0.4); font-size:0.7rem; letter-spacing:4px;">
    VAJRA SIMULATOR v2.0 — BUILT BY ATHARV SHUKLA</p>
    <p style="font-family:'Rajdhani',sans-serif; color:rgba(90,159,212,0.3); font-size:0.7rem; letter-spacing:2px;">
    AMITY INTERNATIONAL SCHOOL SEC 46 GURGAON | AEROSPACE ENGINEERING PROJECT</p>
</div>
""", unsafe_allow_html=True)
