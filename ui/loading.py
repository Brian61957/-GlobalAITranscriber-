import streamlit as st


def branded_loader(message):
    """
    Renders a branded animated loader with a message, returns the
    placeholder so the caller can clear it (placeholder.empty()) once done.
    """
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <div class="gat-loader-wrap gat-fade-in">
            <div class="gat-loader-dot"></div>
            <div class="gat-loader-dot"></div>
            <div class="gat-loader-dot"></div>
            <span style="margin-left:0.4rem;">{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return placeholder
