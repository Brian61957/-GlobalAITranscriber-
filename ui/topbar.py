import streamlit as st

LOGO_SVG = """
<svg width="32" height="32" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;">
    <defs><linearGradient id="tg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#4F7CFF"/>
        <stop offset="100%" stop-color="#8A5CF6"/>
    </linearGradient></defs>
    <circle cx="32" cy="32" r="30" fill="url(#tg)"/>
    <circle cx="32" cy="32" r="21" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.2"/>
    <ellipse cx="32" cy="32" rx="21" ry="9" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="1"/>
    <g stroke="#FFFFFF" stroke-width="3" stroke-linecap="round">
        <line x1="20" y1="27" x2="20" y2="37"/>
        <line x1="26" y1="21" x2="26" y2="43"/>
        <line x1="32" y1="24" x2="32" y2="40"/>
        <line x1="38" y1="17" x2="38" y2="47"/>
        <line x1="44" y1="27" x2="44" y2="37"/>
    </g>
</svg>
"""

SUPPORT_HTML = """
<div class="gat-footer" style="margin-top:1.5rem;">
    <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1rem;">
        <span style="font-size:0.78rem;letter-spacing:2px;text-transform:uppercase;color:#6B7280;">Support</span>
        <div style="display:flex;flex-wrap:wrap;gap:1.2rem;font-size:0.85rem;">
            <a href="https://wa.me/254723422441" target="_blank" class="gat-contact-item">
                <span class="gat-contact-icon">📱</span> 0723 422 441
            </a>
            <a href="mailto:kangorbrian28@gmail.com" class="gat-contact-item">
                <span class="gat-contact-icon">✉️</span> Email
            </a>
            <a href="https://t.me/+BsA8dvAh_lA2YzRk" target="_blank" class="gat-contact-item">
                <span class="gat-contact-icon">💬</span> Telegram Group
            </a>
        </div>
    </div>
</div>
"""


def render_topbar():
    left, right = st.columns([8, 1])

    with left:
        st.markdown(
            """<div style="display:flex;align-items:center;gap:0.7rem;padding:0.3rem 0 0.5rem;">
                <svg width="36" height="36" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="tg" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#4F7CFF"/>
                            <stop offset="100%" stop-color="#8A5CF6"/>
                        </linearGradient>
                    </defs>
                    <circle cx="32" cy="32" r="30" fill="url(#tg)"/>
                    <circle cx="32" cy="32" r="21" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.2"/>
                    <ellipse cx="32" cy="32" rx="21" ry="9" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="1"/>
                    <g stroke="#FFFFFF" stroke-width="3" stroke-linecap="round">
                        <line x1="20" y1="27" x2="20" y2="37"/>
                        <line x1="26" y1="21" x2="26" y2="43"/>
                        <line x1="32" y1="24" x2="32" y2="40"/>
                        <line x1="38" y1="17" x2="38" y2="47"/>
                        <line x1="44" y1="27" x2="44" y2="37"/>
                    </g>
                </svg>
                <div>
                    <div style="font-family:'Courier New',monospace;font-weight:900;font-size:1.05rem;letter-spacing:1px;line-height:1.2;">
                        <span style="color:#4F7CFF;">GLOBAL AI</span><span style="color:#1A1D23;"> TRANSCRIBER</span>
                    </div>
                    <div style="font-size:0.75rem;color:#6B7280;margin-top:1px;">
                        Understand · Transcribe · Review · Submit
                    </div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    with right:
        with st.popover("⋮", use_container_width=True):
            st.markdown(f"**Signed in as**")
            st.caption(st.session_state.get("user_email", ""))
            st.divider()
            st.markdown("**Appearance**")
            current = st.session_state.get("theme", "light")
            choice = st.radio("Theme", ["Light", "Dark"],
                              index=0 if current == "light" else 1,
                              label_visibility="collapsed", key="theme_radio")
            if choice.lower() != current:
                st.session_state.theme = choice.lower()
                st.rerun()
            st.divider()
            if st.button("🚪 Log out", use_container_width=True):
                for k in ("logged_in","user_email","browser_proc","stage","draft_text",
                          "profile_summary","error_message"):
                    st.session_state.pop(k, None)
                st.rerun()

    st.markdown('<hr style="margin:0 0 1rem;">', unsafe_allow_html=True)
