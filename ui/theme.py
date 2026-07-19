import streamlit as st

_NATIVE_TEXT_RULES = """
    [data-testid="stWidgetLabel"] p,
    .stTextInput label p, .stTextArea label p, .stSelectbox label p,
    .stCheckbox label p, .stRadio label p,
    .stTabs [data-baseweb="tab"] p,
    .stMarkdown p, .stMarkdown li, .stMarkdown span,
    .stExpander summary, .stExpander summary p, .stExpander summary span,
    [data-testid="stCaptionContainer"] p,
    .stForm label p, label p {{
        color: {text} !important;
    }}
    [data-testid="stCaptionContainer"] p {{ color: {muted} !important; }}
    .stButton button[kind="primary"] p,
    .stButton button[kind="primary"] {{ color: #FFFFFF !important; }}
"""

_RESPONSIVE = """
    @media (max-width: 640px) {
        .gat-auth-card { padding: 1rem; }
        .gat-banner { font-size: 0.9rem; letter-spacing: 1px; }
        .gat-log-box { max-height: 140px; font-size: 0.78rem; }
        .stButton button { width: 100%; }
    }
"""

BASE_CSS = """
<style>
    /* Full screen layout */
    .main .block-container {{
        max-width: 100% !important;
        padding: 0 1.5rem 1rem !important;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}

    /* Logo animation */
    @keyframes gatLogoIn {{
        0% {{ opacity: 0; transform: scale(0.85) translateY(-10px); }}
        100% {{ opacity: 1; transform: scale(1) translateY(0); }}
    }}
    @keyframes gatWordIn {{
        0% {{ opacity: 0; letter-spacing: 8px; }}
        100% {{ opacity: 1; letter-spacing: 2px; }}
    }}
    @keyframes gatPulse {{
        0%, 100% {{ box-shadow: 0 0 0 0 rgba(79,124,255,0); }}
        50% {{ box-shadow: 0 0 0 12px rgba(79,124,255,0.08); }}
    }}
    .gat-logo-animated {{ animation: gatLogoIn 0.7s cubic-bezier(0.22,1,0.36,1) both; }}
    .gat-word-animated {{ animation: gatWordIn 0.9s cubic-bezier(0.22,1,0.36,1) 0.2s both; }}
    .gat-logo-pulse {{ animation: gatPulse 2.5s ease-in-out infinite; border-radius: 50%; display:inline-block; }}

    /* Auth card */
    .gat-auth-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 18px;
        padding: 2rem 2.2rem;
        box-shadow: 0 4px 32px {card_shadow};
    }}

    /* Console dashboard */
    .gat-console {{
        font-family: 'Courier New', monospace;
        background: {console_bg};
        border: 1px solid {console_border};
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
    }}
    .gat-banner {{
        text-align: center;
        font-weight: 800;
        font-size: 1.1rem;
        letter-spacing: 2px;
        padding: 0.5rem 0;
        border-top: 2px solid {banner_border};
        border-bottom: 2px solid {banner_border};
        margin-bottom: 1.2rem;
        color: {banner_text};
        font-family: 'Courier New', monospace;
    }}
    .gat-section-label {{
        font-family: 'Courier New', monospace;
        font-weight: 700;
        color: {section_label};
        margin: 0.6rem 0 0.4rem 0;
        border-bottom: 1px dashed {section_border};
        padding-bottom: 0.2rem;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .gat-status-line {{
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: {status_text};
        padding: 0.18rem 0;
    }}
    .gat-log-box {{
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        background: {log_bg};
        border: 1px solid {log_border};
        border-radius: 8px;
        padding: 0.7rem 0.9rem;
        max-height: 200px;
        overflow-y: auto;
        color: {log_text};
        white-space: pre-wrap;
    }}

    /* Support footer */
    .gat-footer {{
        background: #0E1117;
        color: #C9CDD4;
        border-radius: 14px;
        padding: 1.6rem 2rem;
        margin-top: 2rem;
    }}
    .gat-footer a {{ color: #7B9BFF; text-decoration: none; }}
    .gat-footer a:hover {{ color: #A8C0FF; text-decoration: underline; }}
    .gat-footer-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1rem;
        align-items: start;
    }}
    .gat-contact-item {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.88rem;
        padding: 0.4rem 0;
    }}
    .gat-contact-icon {{
        font-size: 1.2rem;
        min-width: 1.6rem;
        text-align: center;
    }}

    /* Fade in */
    .gat-fade-in {{ animation: gatFadeIn 0.5s ease-out; }}
    @keyframes gatFadeIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Subtitle */
    .gat-subtitle {{ font-size: 0.82rem; color: {subtitle_color}; margin-top: -4px; }}
    .gat-tagline {{ text-align:center; color:{tagline_color}; font-size:0.95rem; margin-bottom:1.4rem; }}
    .gat-features {{ color:{feature_text}; font-size:0.9rem; }}

    /* Loader */
    .gat-loader-wrap {{ display:flex; align-items:center; justify-content:center; gap:0.6rem; padding:1rem 0; font-family:'Courier New',monospace; color:{loader_text}; }}
    .gat-loader-dot {{ width:9px; height:9px; border-radius:50%; background:linear-gradient(135deg,#4F7CFF,#8A5CF6); animation:gatBounce 1s infinite ease-in-out; }}
    .gat-loader-dot:nth-child(2){{animation-delay:.15s}}
    .gat-loader-dot:nth-child(3){{animation-delay:.3s}}
    @keyframes gatBounce {{ 0%,80%,100%{{transform:scale(0.6);opacity:0.5}} 40%{{transform:scale(1);opacity:1}} }}

    {native_text}
    {responsive}
</style>
"""

LIGHT_VARS = dict(
    card_bg="#FFFFFF", card_border="#E3E6EA", card_shadow="rgba(20,20,40,0.07)",
    console_bg="#FFFFFF", console_border="#D8DCE2",
    banner_border="#1A1D23", banner_text="#1A1D23",
    section_label="#374151", section_border="#B8BEC8",
    status_text="#1A1D23", log_bg="#F4F5F7", log_border="#D8DCE2", log_text="#374151",
    subtitle_color="#6B7280", tagline_color="#6B7280", feature_text="#374151",
    loader_text="#374151",
)

DARK_VARS = dict(
    card_bg="#1C1F26", card_border="#2A2E37", card_shadow="rgba(0,0,0,0.4)",
    console_bg="#1C1F26", console_border="#2A2E37",
    banner_border="#E5E7EB", banner_text="#F3F4F6",
    section_label="#D1D5DB", section_border="#3A3F4B",
    status_text="#E5E7EB", log_bg="#14161B", log_border="#2A2E37", log_text="#C7CBD3",
    subtitle_color="#9CA3AF", tagline_color="#9CA3AF", feature_text="#D1D5DB",
    loader_text="#C7CBD3",
)


def apply_theme():
    theme = st.session_state.get("theme", "light")
    vars_ = DARK_VARS if theme == "dark" else LIGHT_VARS
    native = _NATIVE_TEXT_RULES.format(
        text="#E5E7EB" if theme == "dark" else "#1A1D23",
        muted="#9CA3AF" if theme == "dark" else "#6B7280",
    )
    css = BASE_CSS.format(**vars_, native_text=native, responsive=_RESPONSIVE)
    if theme == "dark":
        css = css.replace("</style>", ".stApp{background-color:#0E1117;color:#E5E7EB}</style>")
    st.markdown(css, unsafe_allow_html=True)
