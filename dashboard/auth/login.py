"""
auth/login.py
-------------
Renders the glassmorphism Login + Registration page inside Streamlit.
Handles session state for the entire app's auth flow.
"""

import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from auth.auth_db import login_user, register_user


# ── IPL TEAMS (for dropdown) ──────────────────────────────────────────────────
IPL_TEAMS = [
    "", "Mumbai Indians", "Chennai Super Kings",
    "Royal Challengers Bengaluru", "Kolkata Knight Riders",
    "Delhi Capitals", "Rajasthan Royals", "Punjab Kings",
    "Sunrisers Hyderabad", "Lucknow Super Giants",
    "Gujarat Titans"
]


# ── SESSION DEFAULTS ──────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "authenticated": False,
        "user": None,
        "auth_tab": "login",       # "login" | "register"
        "auth_message": "",
        "auth_message_type": "",   # "success" | "error"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── MAIN RENDER ───────────────────────────────────────────────────────────────
def show_auth_page():
    """
    Call this from app.py when the user is NOT authenticated.
    Returns True if the user just logged in (so app.py can rerun).
    """
    init_session()

    # Full-page glassmorphism login layout
    # st.html() is used here because newer Streamlit versions strip <style> from st.markdown()
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: #060810 !important;
        font-family: 'DM Sans', sans-serif !important;
        color: #f0f0f0 !important;
    }
    [data-testid="stAppViewContainer"]::before {
        content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
        background:
            radial-gradient(ellipse 70% 55% at 18% 12%, rgba(26,143,255,.18) 0%, transparent 60%),
            radial-gradient(ellipse 55% 45% at 82% 88%, rgba(245,166,35,.13) 0%, transparent 55%),
            radial-gradient(ellipse 45% 40% at 62% 22%, rgba(255,77,141,.10) 0%, transparent 50%),
            #060810;
    }
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] { display:none !important; }

    /* Center the auth card */
    .auth-shell {
        display: flex; justify-content: center; align-items: flex-start;
        min-height: 85vh; padding-top: 5vh;
        position: relative; z-index: 2;
    }
    .auth-card {
        width: 100%; max-width: 440px;
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 24px;
        padding: 36px 36px 30px;
        backdrop-filter: blur(32px) saturate(160%);
        -webkit-backdrop-filter: blur(32px) saturate(160%);
        box-shadow: 0 0 0 1px rgba(255,255,255,0.04) inset,
                    0 32px 80px rgba(0,0,0,0.55);
        animation: fadeUp .6s cubic-bezier(.22,1,.36,1) both;
    }
    @keyframes fadeUp {
        from { opacity:0; transform:translateY(24px) scale(.98); }
        to   { opacity:1; transform:translateY(0) scale(1); }
    }
    .auth-logo {
        display:flex; align-items:center; gap:10px; margin-bottom:22px;
    }
    .auth-logo-icon {
        width:38px; height:38px; border-radius:11px;
        background:linear-gradient(135deg,#1a8fff,#ff4d8d);
        display:flex; align-items:center; justify-content:center;
        font-size:20px;
        box-shadow:0 4px 16px rgba(26,143,255,.35);
    }
    .auth-logo-text {
        font-family:'Syne',sans-serif; font-weight:800; font-size:19px;
        letter-spacing:-.3px;
    }
    .auth-logo-text span { color:#f5a623; }
    .auth-badge {
        display:inline-flex; align-items:center; gap:5px;
        background:rgba(245,166,35,.12);
        border:1px solid rgba(245,166,35,.25);
        border-radius:20px; padding:3px 10px;
        font-size:11px; color:#f5a623; font-weight:600;
        letter-spacing:.5px; margin-bottom:18px;
    }
    .auth-badge-dot {
        width:5px; height:5px; border-radius:50%;
        background:#f5a623; display:inline-block;
        animation: bdot 1.8s ease-in-out infinite;
    }
    @keyframes bdot { 0%,100%{opacity:1}50%{opacity:.4} }
    .auth-title {
        font-family:'Syne',sans-serif; font-weight:700; font-size:22px;
        margin-bottom:4px; letter-spacing:-.4px; color:#fff;
    }
    .auth-sub { font-size:13px; color:rgba(255,255,255,.45); margin-bottom:22px; }

    /* Streamlit widget overrides inside auth card */
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 11px !important;
        color: #fff !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(26,143,255,.55) !important;
        box-shadow: 0 0 0 3px rgba(26,143,255,.12) !important;
    }
    .stTextInput label, .stSelectbox label {
        color: rgba(255,255,255,.5) !important;
        font-size: 11px !important; font-weight:600 !important;
        letter-spacing:.6px !important; text-transform:uppercase !important;
    }
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg,#1a8fff,#0f62d4) !important;
        border: none !important; border-radius:12px !important;
        color:#fff !important; font-family:'Syne',sans-serif !important;
        font-weight:700 !important; font-size:15px !important;
        padding:12px !important;
        box-shadow:0 4px 20px rgba(26,143,255,.35) !important;
        transition:transform .15s,box-shadow .15s !important;
        letter-spacing:.2px !important;
    }
    .stButton > button:hover {
        transform:translateY(-2px) !important;
        box-shadow:0 6px 28px rgba(26,143,255,.5) !important;
    }
    .stRadio > div { flex-direction:row !important; gap:8px !important; }
    .stRadio label {
        background:rgba(255,255,255,.04) !important;
        border:1px solid rgba(255,255,255,.10) !important;
        border-radius:10px !important; padding:8px 20px !important;
        cursor:pointer !important; transition:all .2s !important;
        color:rgba(255,255,255,.5) !important; font-weight:500 !important;
    }
    .stRadio label:has(input:checked) {
        background:rgba(255,255,255,.09) !important;
        color:#fff !important;
        border-color:rgba(255,255,255,.18) !important;
    }
    .success-msg {
        background:rgba(62,207,142,.10); border:1px solid rgba(62,207,142,.25);
        border-radius:10px; padding:10px 14px; font-size:13px;
        color:#3ecf8e; margin:8px 0;
    }
    .error-msg {
        background:rgba(255,77,141,.10); border:1px solid rgba(255,77,141,.25);
        border-radius:10px; padding:10px 14px; font-size:13px;
        color:#ff4d8d; margin:8px 0;
    }
    .auth-divider {
        height:1px;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,.10),transparent);
        margin:20px 0;
    }
    ::-webkit-scrollbar{width:5px}
    ::-webkit-scrollbar-thumb{background:rgba(255,255,255,.10);border-radius:99px}
    </style>

    <div class="auth-shell">
      <div class="auth-card">
        <div class="auth-logo">
          <div class="auth-logo-icon">🏏</div>
          <div class="auth-logo-text">IPL <span>Insights</span></div>
        </div>
        <div class="auth-badge"><div class="auth-badge-dot"></div> 2026 Season Live</div>
    """)

    # ── Tab selector ──────────────────────────────────────────────────────────
    tab = st.radio(
        "", ["Sign In", "Register"],
        index=0 if st.session_state.auth_tab == "login" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.auth_tab = "login" if tab == "Sign In" else "register"

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    # ── Feedback message ──────────────────────────────────────────────────────
    if st.session_state.auth_message:
        css_class = "success-msg" if st.session_state.auth_message_type == "success" else "error-msg"
        icon = "✓" if st.session_state.auth_message_type == "success" else "✕"
        st.markdown(
            f'<div class="{css_class}">{icon} {st.session_state.auth_message}</div>',
            unsafe_allow_html=True
        )

    # ═════════════════════════════
    # LOGIN FORM
    # ═════════════════════════════
    if st.session_state.auth_tab == "login":
        st.markdown('<div class="auth-title">Welcome back 👋</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Sign in to access your IPL dashboard</div>', unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="you@example.com", key="login_email")
        password = st.text_input("Password", placeholder="••••••••", type="password", key="login_pass")

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

        if st.button("Continue →", key="btn_login"):
            success, msg, user = login_user(email, password)
            if success:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.auth_message = ""
                st.rerun()
            else:
                st.session_state.auth_message = msg
                st.session_state.auth_message_type = "error"
                st.rerun()

        st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align:center;font-size:12px;color:rgba(255,255,255,.4);">'
            'Don\'t have an account? Switch to <b style="color:#1a8fff">Register</b> above.</p>',
            unsafe_allow_html=True
        )

    # ═════════════════════════════
    # REGISTER FORM
    # ═════════════════════════════
    else:
        st.markdown('<div class="auth-title">Join IPL Insights 🏆</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Free access to stats, trends & win predictions</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            first = st.text_input("First Name", placeholder="Virat", key="reg_first")
        with col2:
            last = st.text_input("Last Name", placeholder="K", key="reg_last")

        reg_email    = st.text_input("Email", placeholder="you@example.com", key="reg_email")
        reg_password = st.text_input("Password", placeholder="Min 6 characters", type="password", key="reg_pass")
        fav_team     = st.selectbox("Favourite Team", IPL_TEAMS, key="reg_team")

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

        if st.button("Create Account →", key="btn_register"):
            full_name = f"{first.strip()} {last.strip()}".strip()
            success, msg = register_user(full_name, reg_email, reg_password, fav_team)
            st.session_state.auth_message = msg
            st.session_state.auth_message_type = "success" if success else "error"
            if success:
                st.session_state.auth_tab = "login"
            st.rerun()

        st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align:center;font-size:12px;color:rgba(255,255,255,.4);">'
            'Already have an account? Switch to <b style="color:#1a8fff">Sign In</b> above.</p>',
            unsafe_allow_html=True
        )

    st.markdown('</div></div>', unsafe_allow_html=True)


# ── LOGOUT ────────────────────────────────────────────────────────────────────
def logout():
    """Call from sidebar logout button."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.auth_message = ""
    st.rerun()