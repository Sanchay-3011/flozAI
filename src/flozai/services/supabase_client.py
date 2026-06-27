"""
Supabase Client Initialization
Reusable singleton client with proper error handling
"""
import os
from typing import Optional
from supabase import create_client, Client


class SupabaseClientManager:
    """
    Singleton manager for Supabase client.
    Handles initialization, error handling, and connection pooling.
    """
    _instance: Optional["SupabaseClientManager"] = None
    _client: Optional[Client] = None

    def __new__(cls) -> "SupabaseClientManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Supabase client from environment variables"""
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initialize Supabase client with validation.
        
        Raises:
            ValueError: If required environment variables are missing
        """
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing SUPABASE_URL or SUPABASE_KEY environment variables. "
                "Please set them in your .env file."
            )

        try:
            self._client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Supabase client: {str(e)}")

    @property
    def client(self) -> Client:
        """Get the Supabase client instance"""
        if self._client is None:
            self._initialize_client()
        return self._client

    def get_auth_client(self):
        """Get auth client for authentication operations"""
        return self.client.auth

    def get_db_client(self):
        """Get database client for CRUD operations"""
        return self.client.table

    @staticmethod
    def get_instance() -> "SupabaseClientManager":
        """Get or create the singleton instance"""
        return SupabaseClientManager()


# Global instance
_supabase_manager: Optional[SupabaseClientManager] = None


def get_supabase_client() -> Client:
    """
    Get the Supabase client.
    Use this function to access the client throughout the application.
    
    Returns:
        Client: Initialized Supabase client
        
    Example:
        >>> from flozai.services.supabase_client import get_supabase_client
        >>> client = get_supabase_client()
        >>> users = client.table('users').select('*').execute()
    """
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseClientManager()
    return _supabase_manager.client


def reset_supabase_client() -> None:
    """Reset the Supabase client (useful for testing)"""
    global _supabase_manager
    _supabase_manager = None
