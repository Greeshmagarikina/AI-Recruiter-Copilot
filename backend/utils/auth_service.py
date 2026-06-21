# auth_service.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize the persistent connection client instance singleton
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class AuthenticationManager:
    @staticmethod
    def sign_up_recruiter(email: str, password: str):
        """Creates a secure production-grade recruiter account in Supabase Auth."""
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            return response
        except Exception as e:
            return f"Registration Failed: {str(e)}"

    @staticmethod
    def sign_in_recruiter(email: str, password: str):
        """Authenticates active credentials and establishes a user session state."""
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            return response
        except Exception as e:
            return f"Authentication Failed: {str(e)}"

    @staticmethod
    def sign_out_recruiter():
        """Termines active user session maps safely."""
        supabase.auth.sign_out()