import streamlit as st
from auth.auth_manager import AuthManager
from ui.loading import branded_loader

TERMS_TEXT = """
**Terms of Service** — Use this tool responsibly and only for platforms you have legitimate access to. Submit only work you have reviewed.

**Privacy Policy** — Your email and hashed password are stored locally on your machine. Google sign-in only accesses your email address.
"""

FEATURES = [
    ("🌐", "Works on any transcription or translation platform"),
    ("🧠", "Reads and understands project instructions automatically"),
    ("🎙️", "Transcribes audio with Faster-Whisper (offline) or GPT-4o"),
    ("🗣️", "Speaker labeling — detects speaker changes automatically"),
    ("✍️", "Types transcripts at human speed into platform fields"),
    ("💾", "Remembers your login session across runs"),
    ("🔒", "Runs entirely on your own machine — your data stays with you"),
]

SUPPORT_HTML = """
<div class="gat-footer gat-fade-in">
    <div style="text-align:center;margin-bottom:1.2rem;">
        <span style="font-size:0.78rem;letter-spacing:2px;text-transform:uppercase;color:#6B7280;">Support & Community</span>
    </div>
    <div class="gat-footer-grid">
        <div>
            <div class="gat-contact-item">
                <span class="gat-contact-icon">📱</span>
                <span>WhatsApp: <a href="https://wa.me/254723422441" target="_blank">0723 422 441</a></span>
            </div>
            <div class="gat-contact-item">
                <span class="gat-contact-icon">✉️</span>
                <span><a href="mailto:kangorbrian28@gmail.com">kangorbrian28@gmail.com</a></span>
            </div>
            <div class="gat-contact-item">
                <span class="gat-contact-icon">💬</span>
                <span><a href="https://t.me/+BsA8dvAh_lA2YzRk" target="_blank">Join our Telegram group</a></span>
            </div>
        </div>
        <div style="font-size:0.82rem;color:#9CA3AF;padding-top:0.3rem;">
            Need help getting started? Join the Telegram group where the community shares tips, project URLs, and troubleshooting help.
        </div>
    </div>
</div>
"""


def render_auth_page():
    auth = AuthManager()

    # Splash logo
    st.markdown("""
    <div class="gat-fade-in" style="text-align:center;padding:2.5rem 0 1rem;">
        <div class="gat-logo-pulse" style="display:inline-block;margin-bottom:1rem;">
            <svg width="80" height="80" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" class="gat-logo-animated">
                <defs>
                    <linearGradient id="lg1" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#4F7CFF"/>
                        <stop offset="100%" stop-color="#8A5CF6"/>
                    </linearGradient>
                </defs>
                <circle cx="32" cy="32" r="30" fill="url(#lg1)"/>
                <circle cx="32" cy="32" r="21" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.2"/>
                <ellipse cx="32" cy="32" rx="21" ry="9" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="1"/>
                <line x1="11" y1="32" x2="53" y2="32" stroke="rgba(255,255,255,0.35)" stroke-width="1"/>
                <g stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round">
                    <line x1="20" y1="27" x2="20" y2="37"/>
                    <line x1="26" y1="21" x2="26" y2="43"/>
                    <line x1="32" y1="24" x2="32" y2="40"/>
                    <line x1="38" y1="17" x2="38" y2="47"/>
                    <line x1="44" y1="27" x2="44" y2="37"/>
                </g>
            </svg>
        </div>
        <div class="gat-word-animated" style="font-family:'Courier New',monospace;font-size:1.6rem;font-weight:900;letter-spacing:2px;">
            <span style="color:#4F7CFF;">GLOBAL AI</span><span style="color:#1A1D23;"> TRANSCRIBER</span>
        </div>
        <div style="color:#6B7280;font-size:0.95rem;margin-top:0.4rem;">
            Understand. Transcribe. Review. Submit — automatically.
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 2.2, 1])

    with center:
        st.markdown('<div class="gat-auth-card gat-fade-in">', unsafe_allow_html=True)

        tab_login, tab_signup, tab_about = st.tabs(["Log In", "Sign Up", "How It Works"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Log In", use_container_width=True, type="primary")

            if submitted:
                loader = branded_loader("Signing you in...")
                result = auth.login(email, password)
                loader.empty()
                if result.success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = result.email
                    st.rerun()
                else:
                    st.error(result.message)

            st.divider()
            _google_button(auth, "login")

        with tab_signup:
            with st.form("signup_form"):
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
                with st.expander("Terms of Service & Privacy Policy"):
                    st.markdown(TERMS_TEXT)
                accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy.")
                submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted:
                loader = branded_loader("Creating your account...")
                result = auth.signup(email, password, confirm, accepted)
                loader.empty()
                if result.success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = result.email
                    st.rerun()
                else:
                    st.error(result.message)

            st.divider()
            _google_button(auth, "signup")

        with tab_about:
            st.markdown("**What this tool does:**")
            for icon, text in FEATURES:
                st.markdown(f"{icon} {text}")
            st.caption("Every step is shown live in the dashboard. Nothing is submitted without your review.")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(SUPPORT_HTML, unsafe_allow_html=True)


def _google_button(auth, prefix):
    accepted = st.checkbox("I agree to the Terms and Privacy Policy.", key=f"{prefix}_gterms")
    st.caption("A browser window will open for Google sign-in. You'll return here automatically once approved.")
    if st.button("🔵 Continue with Google", use_container_width=True, key=f"{prefix}_gbtn"):
        if not accepted:
            st.error("Please accept the Terms and Privacy Policy first.")
        else:
            loader = branded_loader("Waiting for Google sign-in...")
            result = auth.google_signin(accepted)
            loader.empty()
            if result.success:
                st.session_state.logged_in = True
                st.session_state.user_email = result.email
                st.rerun()
            else:
                st.error(result.message)
