import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="VAJRA - HAL Tejas Sonic Boom Simulator", layout="wide", page_icon="⚡")

st.title("⚡ VAJRA - HAL Tejas Sonic Boom Simulator")
st.markdown("### Real-time supersonic flight physics simulator for the HAL Tejas Mk1A")

st.sidebar.header("Flight Parameters")
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
    pressure = 101325 * (temp / 288.15) ** 5.2561
else:
    temp = 216.65
    pressure = 22632 * np.exp(-0.00015769 * (altitude - 11000))

rho = pressure / (287.05 * temp)
speed_of_sound = np.sqrt(1.4 * 287.05 * temp)
aircraft_speed = mach * speed_of_sound

if mach < 0.8:
    regime = "Subsonic"
    regime_color = "green"
elif mach < 1.0:
    regime = "Transonic"
    regime_color = "orange"
else:
    regime = "Supersonic"
    regime_color = "red"

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

st.sidebar.markdown("---")
st.sidebar.markdown(f"### Flight Regime: :{regime_color}[{regime}]")
st.sidebar.metric("Speed of Sound", f"{speed_of_sound:.1f} m/s")
st.sidebar.metric("Aircraft Speed", f"{aircraft_speed:.1f} m/s ({aircraft_speed * 3.6:.0f} km/h)")
st.sidebar.metric("Air Density", f"{rho:.4f} kg/m³")
st.sidebar.metric("Dynamic Pressure", f"{q:.0f} Pa")

st.sidebar.markdown("---")
st.sidebar.markdown("### HAL Tejas Mk1A Specs")
st.sidebar.markdown(f"""
- **Engine:** GE F404-IN20
- **Max Thrust:** {TEJAS_MAX_THRUST} kN
- **Max Speed:** Mach {TEJAS_MAX_MACH}
- **Service Ceiling:** {TEJAS_CEILING:,} m
- **Wing Area:** {TEJAS_WING_AREA} m²
- **Empty Weight:** {TEJAS_MASS:,} kg
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Shockwave Cone Visualisation")
    if mach >= 1.0:
        half_angle = np.degrees(np.arcsin(1 / mach))
        theta = np.radians(half_angle)
        x = np.linspace(-10, 0, 100)
        y_upper = -np.tan(theta) * x
        y_lower = np.tan(theta) * x

        fig1 = go.Figure()
        intensity = min(1.0, (mach - 1.0) / 1.5)
        cone_color = f"rgba(255, {int(100 - 80 * intensity)}, {int(50 - 40 * intensity)}, 0.9)"

        fig1.add_trace(go.Scatter(
            x=x, y=y_upper, mode='lines',
            line=dict(color=cone_color, width=3),
            name='Shockwave Upper'
        ))
        fig1.add_trace(go.Scatter(
            x=x, y=y_lower, mode='lines',
            line=dict(color=cone_color, width=3),
            name='Shockwave Lower'
        ))
        fig1.add_trace(go.Scatter(
            x=x, y=y_upper, fill=None, mode='lines',
            line=dict(width=0), showlegend=False
        ))
        fig1.add_trace(go.Scatter(
            x=x, y=y_lower, fill='tonexty', mode='lines',
            line=dict(width=0),
            fillcolor=f"rgba(255, 80, 20, {0.08 + 0.12 * intensity})",
            showlegend=False
        ))
        fig1.add_trace(go.Scatter(
            x=[0], y=[0],
            mode='markers+text',
            marker=dict(size=16, color='#00BFFF', symbol='triangle-right'),
            text=['HAL Tejas'], textposition='top center',
            textfont=dict(color='white', size=12),
            name='Aircraft'
        ))

        fig1.update_layout(
            title=f"Mach Cone — Half Angle: {half_angle:.1f}° | Mach {mach:.2f}",
            xaxis_title="Distance (behind aircraft →)",
            yaxis_title="Lateral Spread",
            template="plotly_dark",
            yaxis=dict(scaleanchor="x", scaleratio=1),
            height=450
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No shockwave at subsonic speeds. Increase Mach to 1.0+ to see the cone.")

with col2:
    st.subheader("Pressure Wave — Sonic Boom N-Wave")
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
        pressure = np.ones_like(x_wave)
        pressure[mask] = 1.0 + (front_shock[mask] - rear_shock[mask]) * linear_drop[mask] / boom_strength

        overpressure = boom_strength * (rho / 1.225) ** 0.5
        title_text = f"Sonic Boom N-Wave | ΔP ≈ {overpressure:.2f} relative"
    else:
        comp_factor = 1 / np.sqrt(1 - mach ** 2) if mach < 0.99 else 10.0
        pressure = 1.0 + 0.3 * comp_factor * np.exp(-0.5 * (x_wave * (1 - mach)) ** 2) * np.cos(3 * x_wave)
        title_text = f"Subsonic Pressure Field | β = {1/comp_factor:.3f}"

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=x_wave, y=pressure, mode='lines',
        line=dict(color='cyan', width=2),
        fill='tozeroy', fillcolor='rgba(0, 255, 255, 0.1)',
        name='Pressure'
    ))
    fig2.add_hline(y=1.0, line_dash="dash", line_color="gray",
                   annotation_text="Ambient", annotation_position="top left")
    fig2.update_layout(
        title=title_text,
        xaxis_title="Position (relative to aircraft)",
        yaxis_title="Relative Pressure (P/P∞)",
        template="plotly_dark",
        height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Flight Forces & Data")
col3, col4, col5, col6 = st.columns(4)
col3.metric("Mach Number", f"{mach:.2f}")
col4.metric("Altitude", f"{altitude:,} m")
col5.metric("Temperature", f"{temp:.1f} K ({temp - 273.15:.1f} °C)")
col6.metric("Aircraft Speed", f"{aircraft_speed:.0f} m/s")

col7, col8, col9, col10 = st.columns(4)
col7.metric("Lift", f"{lift / 1000:.1f} kN")
col8.metric("Weight", f"{weight / 1000:.1f} kN")
col9.metric("Drag", f"{drag / 1000:.2f} kN")
col10.metric("Thrust Required", f"{thrust_required / 1000:.2f} kN")

st.markdown("---")

fcol1, fcol2 = st.columns(2)

with fcol1:
    st.subheader("Four Forces of Flight")
    fig3 = go.Figure()

    max_force = max(lift, weight, thrust_required, drag, 1)
    bar_scale = 3.0 / max_force

    forces = [
        ("Lift ↑", 0, lift * bar_scale, "rgba(0, 200, 100, 0.8)", 90),
        ("Weight ↓", 0, -weight * bar_scale, "rgba(255, 100, 100, 0.8)", 270),
        ("Thrust →", thrust_required * bar_scale, 0, "rgba(0, 150, 255, 0.8)", 0),
        ("Drag ←", -drag * bar_scale, 0, "rgba(255, 200, 0, 0.8)", 180),
    ]

    for name, dx, dy, color, _ in forces:
        fig3.add_annotation(
            x=dx, y=dy, ax=0, ay=0,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=2, arrowsize=1.5, arrowwidth=3,
            arrowcolor=color,
            text=name,
            font=dict(size=12, color=color),
        )

    fig3.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers',
        marker=dict(size=20, color='#00BFFF', symbol='diamond'),
        name='Aircraft CG',
        showlegend=False
    ))

    fig3.update_layout(
        template="plotly_dark",
        xaxis=dict(range=[-4, 4], showgrid=False, zeroline=True, title=""),
        yaxis=dict(range=[-4, 4], showgrid=False, zeroline=True, scaleanchor="x", title=""),
        height=400,
        showlegend=False,
        title="Force Balance Diagram"
    )
    st.plotly_chart(fig3, use_container_width=True)

with fcol2:
    st.subheader("Flight Envelope")
    altitudes = np.linspace(0, 20000, 200)
    mach_envelope = []
    for alt in altitudes:
        if alt <= 11000:
            t = 288.15 - 0.0065 * alt
            p = 101325 * (t / 288.15) ** 5.2561
        else:
            t = 216.65
            p = 22632 * np.exp(-0.00015769 * (alt - 11000))
        r = p / (287.05 * t)
        q_max = 0.5 * r * (TEJAS_MAX_MACH * np.sqrt(1.4 * 287.05 * t)) ** 2
        q_limit = 80000
        if q_max > q_limit:
            a = np.sqrt(1.4 * 287.05 * t)
            v_limit = np.sqrt(2 * q_limit / r)
            m_limit = min(v_limit / a, TEJAS_MAX_MACH)
        else:
            m_limit = TEJAS_MAX_MACH
        if alt > TEJAS_CEILING:
            m_limit = max(0, m_limit * (1 - (alt - TEJAS_CEILING) / 5000))
        mach_envelope.append(m_limit)

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=mach_envelope, y=altitudes,
        mode='lines', fill='tozerox',
        line=dict(color='#FF6B35', width=2),
        fillcolor='rgba(255, 107, 53, 0.15)',
        name='Flight Envelope'
    ))
    fig4.add_trace(go.Scatter(
        x=[mach], y=[altitude],
        mode='markers+text',
        marker=dict(size=14, color='#00BFFF', symbol='star'),
        text=[f'M{mach:.1f}'],
        textposition='top right',
        textfont=dict(color='white', size=11),
        name='Current State'
    ))
    fig4.add_vline(x=1.0, line_dash="dot", line_color="yellow",
                   annotation_text="Mach 1", annotation_position="top")
    fig4.update_layout(
        title="HAL Tejas Mk1A Performance Envelope",
        xaxis_title="Mach Number",
        yaxis_title="Altitude (m)",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig4, use_container_width=True)

if mach >= 1.0:
    half_angle = np.degrees(np.arcsin(1 / mach))
    st.error(f"⚡ SONIC BOOM — Shockwave half-angle: {half_angle:.1f}° | Overpressure ratio: {boom_strength:.2f}")
elif mach >= 0.8:
    st.warning("⚠️ Transonic regime — wave drag rising, compressibility effects significant")
else:
    st.success("✅ Subsonic flight — normal aerodynamic conditions")

if mach > TEJAS_MAX_MACH:
    st.error(f"⛔ Beyond HAL Tejas max speed of Mach {TEJAS_MAX_MACH} — structural limits exceeded")
if altitude > TEJAS_CEILING:
    st.warning(f"⚠️ Above service ceiling of {TEJAS_CEILING:,} m — engine performance degraded")
if thrust_required > TEJAS_MAX_THRUST * 1000:
    st.warning(f"⚠️ Required thrust ({thrust_required/1000:.1f} kN) exceeds max engine thrust ({TEJAS_MAX_THRUST} kN)")
