import os

from auth.database import initialize_database, get_user_by_email, create_user
from auth.password_utils import hash_password, verify_password
from utils.logger import logger

initialize_database()

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


class AuthResult:
    def __init__(self, success, message="", email=None):
        self.success = success
        self.message = message
        self.email = email


class AuthManager:

    # --------------------------------------------------
    # Email + Password
    # --------------------------------------------------

    def signup(self, email, password, confirm_password, accepted_terms):

        email = (email or "").strip().lower()

        if not email or "@" not in email:
            return AuthResult(False, "Please enter a valid email address.")

        if not accepted_terms:
            return AuthResult(False, "You must accept the Terms and Privacy Policy to sign up.")

        if len(password) < 8:
            return AuthResult(False, "Password must be at least 8 characters.")

        if password != confirm_password:
            return AuthResult(False, "Passwords do not match.")

        if get_user_by_email(email):
            return AuthResult(False, "An account with this email already exists.")

        password_hash, salt = hash_password(password)

        create_user(
            email=email,
            password_hash=password_hash,
            password_salt=salt,
            provider="local",
            accepted_terms=True,
        )

        logger.info(f"New account created: {email}")

        return AuthResult(True, "Account created successfully.", email=email)

    def login(self, email, password):

        email = (email or "").strip().lower()

        user = get_user_by_email(email)

        if not user:
            return AuthResult(False, "No account found with this email.")

        if user["provider"] != "local":
            return AuthResult(
                False,
                f"This account was created with {user['provider'].title()}. Please use that sign-in option.",
            )

        if not verify_password(password, user["password_hash"], user["password_salt"]):
            return AuthResult(False, "Incorrect password.")

        logger.info(f"User logged in: {email}")

        return AuthResult(True, "Logged in successfully.", email=email)

    # --------------------------------------------------
    # Google Sign-In (reuses the app's existing OAuth client)
    # --------------------------------------------------

    def google_signin(self, accepted_terms):

        if not accepted_terms:
            return AuthResult(False, "You must accept the Terms and Privacy Policy to continue.")

        if not os.path.exists("credentials.json"):
            return AuthResult(
                False,
                "Google sign-in isn't configured yet — credentials.json is missing.",
            )

        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.oauth2.credentials import Credentials
            import requests as http

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                GOOGLE_SCOPES,
            )

            creds: Credentials = flow.run_local_server(port=0)

            response = http.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {creds.token}"},
                timeout=10,
            )
            response.raise_for_status()

            email = response.json().get("email")

            if not email:
                return AuthResult(False, "Google didn't return an email address.")

            email = email.strip().lower()

            user = get_user_by_email(email)

            if not user:
                create_user(
                    email=email,
                    password_hash=None,
                    password_salt=None,
                    provider="google",
                    accepted_terms=True,
                )
                logger.info(f"New Google account created: {email}")
            else:
                logger.info(f"Google user logged in: {email}")

            return AuthResult(True, "Signed in with Google.", email=email)

        except Exception as e:
            logger.exception("Google sign-in failed.")
            return AuthResult(False, f"Google sign-in failed: {e}")
