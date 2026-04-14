"""F1 Race Strategy Agent — Streamlit UI.

Polished dark-themed dashboard with F1 styling, chat interface,
strategy visualizations, and ReAct loop display.
"""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.graph_objects as go
from agents.coordinator import CoordinatorAgent
from memory.memory_store import MemoryStore
from core.react_loop import ReActLogger
from config import CIRCUITS
from tools.tire_model import TIRE_COMPOUNDS

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="F1 Race Strategy Agent",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — F1 Dark Theme ─────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #e10600 0%, #ff3333 50%, #e10600 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(225, 6, 0, 0.3);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 2px;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }

    .strategy-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #e10600;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .strategy-card h3 {
        color: #e10600;
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    .strategy-card p {
        color: #ddd;
        margin: 0.2rem 0;
        font-size: 0.9rem;
    }

    .react-step {
        padding: 0.6rem 1rem;
        border-left: 3px solid;
        margin: 0.4rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.85rem;
    }
    .react-thought { border-color: #ffd700; background: rgba(255,215,0,0.08); }
    .react-action { border-color: #00d4aa; background: rgba(0,212,170,0.08); }
    .react-observation { border-color: #64b5f6; background: rgba(100,181,246,0.08); }
    .react-answer { border-color: #e10600; background: rgba(225,6,0,0.08); }

    .metric-card {
        background: linear-gradient(145deg, #1a1a2e, #0f3460);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(225,6,0,0.3);
    }
    .metric-card .label { color: #aaa; font-size: 0.8rem; text-transform: uppercase; }
    .metric-card .value { color: #e10600; font-size: 1.5rem; font-weight: 700; }

    .agent-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 4px;
    }
    .badge-coordinator { background: #e10600; color: white; }
    .badge-weather { background: #0066ff; color: white; }
    .badge-racedata { background: #00cc00; color: white; }
    .badge-strategy { background: #ffd700; color: #111; }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Session State Init ─────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

memory = MemoryStore()

# ── Header ─────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏎️ F1 RACE STRATEGY AGENT</h1>
    <p>Multi-Agent AI System — Real-time Weather • Historical Data • Tire Simulation</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Race Settings")

    circuit_options = {
        k: f"{v['name']} ({v['location']})" for k, v in CIRCUITS.items()
    }
    selected_circuit = st.selectbox(
        "🏁 Circuit",
        options=list(circuit_options.keys()),
        format_func=lambda x: circuit_options[x],
        index=list(circuit_options.keys()).index("silverstone"),
    )

    circuit_info = CIRCUITS[selected_circuit]
    default_laps = circuit_info["laps"]
    custom_laps = st.number_input(
        "🔄 Race Laps", min_value=10, max_value=100,
        value=default_laps, step=1,
    )

    st.markdown("---")
    st.markdown("### 📊 Circuit Info")
    st.markdown(f"**{circuit_info['name']}**")
    st.markdown(f"📍 {circuit_info['location']}, {circuit_info['country']}")
    st.markdown(f"🏁 {custom_laps} laps")
    st.markdown(f"⏱️ Base lap: {circuit_info['base_lap_time']}s")
    st.markdown(f"🛞 Abrasiveness: {'█' * int(circuit_info['abrasiveness'] * 10)}░ {circuit_info['abrasiveness']}")

    st.markdown("---")
    st.markdown("### 💾 Memory")
    past = memory.get_past_strategies(limit=5)
    if past:
        for s in past:
            st.caption(f"🏁 {s['circuit']} — {s['strategy'][:40]}...")
    else:
        st.caption("No past strategies yet")

    sessions = memory.get_all_sessions()
    if sessions:
        st.markdown(f"💬 {len(sessions)} past session(s)")

    st.markdown("---")
    st.markdown("### 🤖 Agents")
    st.markdown('<span class="agent-badge badge-coordinator">Coordinator</span>', unsafe_allow_html=True)
    st.markdown('<span class="agent-badge badge-weather">Weather Agent</span>', unsafe_allow_html=True)
    st.markdown('<span class="agent-badge badge-racedata">Race Data Agent</span>', unsafe_allow_html=True)
    st.markdown('<span class="agent-badge badge-strategy">Strategy Agent</span>', unsafe_allow_html=True)

# ── Main Chat Area ─────────────────────────────────────────────────
col_chat, col_viz = st.columns([3, 2])

with col_chat:
    st.markdown("### 💬 Strategy Chat")

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant", avatar="🏎️").write(msg["content"])

    # Chat input
    user_input = st.chat_input(
        f"Ask about pit strategy for {circuit_info['name']}..."
    )

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.chat_message("assistant", avatar="🏎️"):
            with st.spinner("🏎️ Agents analyzing race conditions..."):
                react_logger = ReActLogger()
                coordinator = CoordinatorAgent(
                    memory=memory, react_logger=react_logger
                )

                # Include circuit context in query
                enhanced_query = (
                    f"{user_input} "
                    f"[Circuit: {selected_circuit}, Laps: {custom_laps}]"
                )

                result = coordinator.run(
                    enhanced_query,
                    context={"circuit_key": selected_circuit, "total_laps": custom_laps},
                    session_id=st.session_state.session_id,
                )

                st.session_state.last_result = result
                st.write(result["answer"])

        st.session_state.messages.append({
            "role": "assistant", "content": result["answer"]
        })
        st.rerun()

# ── Visualization Panel ────────────────────────────────────────────
with col_viz:
    result = st.session_state.last_result

    if result:
        st.markdown("### 📊 Strategy Visualization")

        # ── Tire Strategy Timeline ──
        strategies = result["strategy"]["strategies"][:4]
        best = result["strategy"]["best_strategy"]

        fig = go.Figure()
        for i, strategy in enumerate(strategies):
            y_pos = len(strategies) - i - 1
            for stint in strategy["stints"]:
                compound = stint["compound"]
                tc = TIRE_COMPOUNDS[compound]
                fig.add_trace(go.Bar(
                    x=[stint["stint_length"]],
                    y=[f"#{strategy['rank']} ({strategy['num_stops']}-stop)"],
                    base=stint["start_lap"] - 1,
                    orientation='h',
                    marker=dict(
                        color=tc["color"],
                        line=dict(color="#333", width=1),
                    ),
                    text=f"{tc['name']}<br>L{stint['start_lap']}-{stint['end_lap']}",
                    textposition="inside",
                    textfont=dict(
                        color="black" if compound in ("medium", "hard") else "white",
                        size=10,
                    ),
                    hovertemplate=(
                        f"<b>{tc['name']}</b><br>"
                        f"Laps {stint['start_lap']}-{stint['end_lap']}<br>"
                        f"Stint: {stint['stint_length']} laps<br>"
                        f"Avg: {stint['average_lap_time']}s/lap<br>"
                        f"<extra></extra>"
                    ),
                    showlegend=False,
                ))

        fig.update_layout(
            title=dict(text="Tire Strategy Comparison", font=dict(size=14)),
            barmode="stack",
            xaxis=dict(title="Lap", range=[0, result["total_laps"]]),
            yaxis=dict(title=""),
            height=250,
            margin=dict(l=10, r=10, t=40, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(26,26,46,0.5)",
            font=dict(color="#ddd"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Metrics Row ──
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("🏆 Best Strategy", f"{best['num_stops']}-stop")
        with m2:
            mins = int(best["total_race_time"] // 60)
            secs = best["total_race_time"] % 60
            st.metric("⏱️ Race Time", f"{mins}m {secs:.0f}s")
        with m3:
            weather = result["weather"]
            st.metric("🌡️ Temperature", f"{weather['temperature_c']}°C")

        # ── Strategy Rankings ──
        st.markdown("#### 🏁 Strategy Rankings")
        for s in strategies[:4]:
            delta_str = f"+{s['delta_to_best']:.1f}s" if s['delta_to_best'] > 0 else "⭐ BEST"
            badge = "🥇" if s["rank"] == 1 else "🥈" if s["rank"] == 2 else "🥉" if s["rank"] == 3 else "  "
            st.markdown(
                f"{badge} **#{s['rank']}** {s['name']}  \n"
                f"&nbsp;&nbsp;&nbsp;{s['num_stops']}-stop | "
                f"{s['total_race_time']:.1f}s | {delta_str}"
            )

        # ── Lap Time Prediction Chart ──
        if best.get("all_lap_times"):
            lap_fig = go.Figure()
            laps = [lt["lap"] for lt in best["all_lap_times"]]
            times = [lt["time"] for lt in best["all_lap_times"]]

            # Color each point by tire compound stint
            colors = []
            for lt in best["all_lap_times"]:
                lap = lt["lap"]
                for stint in best["stints"]:
                    if stint["start_lap"] <= lap <= stint["end_lap"]:
                        colors.append(TIRE_COMPOUNDS[stint["compound"]]["color"])
                        break
                else:
                    colors.append("#999")

            lap_fig.add_trace(go.Scatter(
                x=laps, y=times,
                mode="markers+lines",
                marker=dict(color=colors, size=4),
                line=dict(color="rgba(225,6,0,0.5)", width=1),
                hovertemplate="Lap %{x}<br>Time: %{y:.2f}s<extra></extra>",
            ))
            lap_fig.update_layout(
                title=dict(text="Predicted Lap Times", font=dict(size=14)),
                xaxis=dict(title="Lap"),
                yaxis=dict(title="Lap Time (s)"),
                height=220,
                margin=dict(l=10, r=10, t=40, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(26,26,46,0.5)",
                font=dict(color="#ddd"),
                showlegend=False,
            )
            st.plotly_chart(lap_fig, use_container_width=True)

    else:
        st.markdown("### 📊 Strategy Visualization")
        st.info("Ask a question to see strategy visualizations here! 👈")

        st.markdown("#### 💡 Try asking:")
        st.markdown("""
        - *What's the best pit strategy for this race?*
        - *Should I go 1-stop or 2-stop?*
        - *How does the weather affect my strategy?*
        - *Compare aggressive vs conservative strategies*
        """)

# ── ReAct Loop Display ─────────────────────────────────────────────
if result:
    with st.expander("🧠 ReAct Reasoning Trace (Thought → Action → Observation → Answer)", expanded=False):
        step_styles = {
            "thought": ("🤔", "react-thought", "Thought"),
            "action": ("⚡", "react-action", "Action"),
            "observation": ("👁️", "react-observation", "Observation"),
            "answer": ("✅", "react-answer", "Answer"),
        }

        for step in result["react_steps"]:
            icon, css_class, label = step_styles.get(
                step["step_type"], ("📌", "react-thought", "Step")
            )
            agent_badge_class = {
                "Coordinator": "badge-coordinator",
                "Weather Agent": "badge-weather",
                "Race Data Agent": "badge-racedata",
                "Strategy Agent": "badge-strategy",
            }.get(step["agent"], "badge-coordinator")

            st.markdown(
                f'<div class="react-step {css_class}">'
                f'<span class="agent-badge {agent_badge_class}">{step["agent"]}</span> '
                f'{icon} <b>{label}</b><br>'
                f'{step["content"][:300]}'
                f'</div>',
                unsafe_allow_html=True,
            )

# ── Footer ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#666;font-size:0.8rem;">'
    '🏎️ F1 Race Strategy Agent — Multi-Agent AI System | '
    'Weather API • F1 Data API • Tire Simulation • Groq LLM'
    '</p>',
    unsafe_allow_html=True,
)
