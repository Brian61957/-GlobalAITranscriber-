import streamlit as st

_ICON_SVG = """
<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4F7CFF"/>
      <stop offset="100%" stop-color="#8A5CF6"/>
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="30" fill="url(#g1)"/>
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
</svg>"""


def render_logo(size=56, font_size=22, centered=True, animated=False):
    theme = st.session_state.get("theme", "light")
    dark = theme == "dark"
    c1 = "#F3F4F6" if dark else "#1A1D23"
    c2 = "#8A9CFF" if dark else "#4F7CFF"
    icon_cls = "gat-logo-animated gat-logo-pulse" if animated else ""
    word_cls = "gat-word-animated" if animated else ""
    j = "center" if centered else "flex-start"
    icon = _ICON_SVG.format(size=size)
    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:{j};gap:0.7rem;margin-bottom:0.2rem;">
  <div class="{icon_cls}">{icon}</div>
  <div class="{word_cls}" style="font-family:'Courier New',monospace;font-weight:800;font-size:{font_size}px;letter-spacing:2px;line-height:1.1;">
    <span style="color:{c1};">GLOBAL AI</span><span style="color:{c2};">TRANSCRIBER</span>
  </div>
</div>""", unsafe_allow_html=True)


SUPPORT_FOOTER = """
<div class="gat-footer">
  <div style="text-align:center;margin-bottom:1rem;">
    <span style="color:#7B9BFF;font-weight:700;font-size:0.9rem;letter-spacing:1px;">SUPPORT &amp; COMMUNITY</span>
  </div>
  <div class="gat-footer-grid">
    <div>
      <div style="color:#9CA3AF;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Contact</div>
      <a href="https://wa.me/254723422441" class="gat-contact-item" style="display:flex;align-items:center;gap:0.5rem;color:#C9CDD4;text-decoration:none;margin-bottom:0.3rem;">
        <span class="gat-contact-icon">📱</span>
        <span>+254 723 422 441</span>
      </a>
      <a href="mailto:kangorbrian28@gmail.com" class="gat-contact-item" style="display:flex;align-items:center;gap:0.5rem;color:#C9CDD4;text-decoration:none;margin-bottom:0.3rem;">
        <span class="gat-contact-icon">✉️</span>
        <span>kangorbrian28@gmail.com</span>
      </a>
    </div>
    <div>
      <div style="color:#9CA3AF;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Community</div>
      <a href="https://t.me/+BsA8dvAh_lA2YzRk" class="gat-contact-item" style="display:flex;align-items:center;gap:0.5rem;color:#C9CDD4;text-decoration:none;margin-bottom:0.3rem;" target="_blank">
        <span class="gat-contact-icon">✈️</span>
        <span>Join Telegram Group</span>
      </a>
      <a href="https://wa.me/254723422441" class="gat-contact-item" style="display:flex;align-items:center;gap:0.5rem;color:#C9CDD4;text-decoration:none;" target="_blank">
        <span class="gat-contact-icon">💬</span>
        <span>WhatsApp Support</span>
      </a>
    </div>
    <div>
      <div style="color:#9CA3AF;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">What this tool does</div>
      <ul style="color:#C9CDD4;font-size:0.83rem;padding-left:1.1rem;margin:0;line-height:1.8;">
        <li>Opens any transcription platform automatically</li>
        <li>Reads and understands project instructions</li>
        <li>Downloads and transcribes audio with AI</li>
        <li>Types results into the platform humanly</li>
        <li>Loops through all clips until project ends</li>
        <li>Supports French, English, Swahili &amp; more</li>
      </ul>
    </div>
  </div>
  <div style="text-align:center;margin-top:1.2rem;padding-top:1rem;border-top:1px solid #2A2E37;color:#6B7280;font-size:0.78rem;">
    Global AI Transcriber &copy; 2026 &nbsp;·&nbsp; Built to think more than a human
  </div>
</div>
"""


def render_support_footer():
    st.markdown(SUPPORT_FOOTER, unsafe_allow_html=True)
