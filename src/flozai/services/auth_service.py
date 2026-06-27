"""
Authentication Service
Handles user authentication, session management, and account operations
"""
from typing import Optional, Dict, Any
from pydantic import EmailStr, BaseModel, Field
from datetime import datetime
from enum import Enum
import logging

from flozai.services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class AuthUser(BaseModel):
    """User authentication model"""
    id: str
    email: EmailStr
    created_at: datetime
    last_sign_in_at: Optional[datetime] = None
    email_confirmed_at: Optional[datetime] = None


class SignUpRequest(BaseModel):
    """Sign up request model"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class AuthError(Exception):
    """Custom authentication error"""
    pass


class AuthService:
    """
    Service for handling authentication operations.
    Uses Supabase Auth for session management.
    """

    def __init__(self):
        self.client = get_supabase_client()
        self.auth = self.client.auth

    async def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign up a new user.
        
        Args:
            email: User email address
            password: User password (min 8 characters)
            
        Returns:
            Dictionary containing user data and session
            
        Raises:
            AuthError: If sign up fails
            
        Example:
            >>> auth_service = AuthService()
            >>> user = await auth_service.sign_up("user@example.com", "password123")
            >>> print(user['user']['id'])
        """
        try:
            response = self.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user is None:
                raise AuthError("Sign up failed: No user returned")
            
            logger.info(f"User signed up: {email}")
            
            return {
                "user": response.user.model_dump() if hasattr(response.user, 'model_dump') else response.user,
                "session": response.session.model_dump() if response.session and hasattr(response.session, 'model_dump') else response.session
            }
        except Exception as e:
            logger.error(f"Sign up error for {email}: {str(e)}")
            raise AuthError(f"Sign up failed: {str(e)}")

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Log in an existing user.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Dictionary containing user data and session
            
        Raises:
            AuthError: If login fails
            
        Example:
            >>> auth_service = AuthService()
            >>> session = await auth_service.login("user@example.com", "password123")
            >>> print(session['session']['access_token'])
        """
        try:
            response = self.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user is None:
                raise AuthError("Login failed: Invalid credentials")
            
            logger.info(f"User logged in: {email}")
            
            return {
                "user": response.user.model_dump() if hasattr(response.user, 'model_dump') else response.user,
                "session": response.session.model_dump() if response.session and hasattr(response.session, 'model_dump') else response.session
            }
        except AuthError:
            raise
        except Exception as e:
            logger.error(f"Login error for {email}: {str(e)}")
            raise AuthError(f"Login failed: {str(e)}")

    async def logout(self, access_token: Optional[str] = None) -> bool:
        """
        Log out the current user.
        
        Args:
            access_token: Optional access token for session
            
        Returns:
            True if logout successful
            
        Raises:
            AuthError: If logout fails
        """
        try:
            self.auth.sign_out()
            logger.info("User logged out")
            return True
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            raise AuthError(f"Logout failed: {str(e)}")

    async def get_current_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get the current authenticated user.
        
        Args:
            access_token: JWT access token
            
        Returns:
            User data if authenticated, None otherwise
            
        Example:
            >>> auth_service = AuthService()
            >>> user = await auth_service.get_current_user(access_token)
            >>> if user:
            ...     print(f"Authenticated as: {user['email']}")
        """
        try:
            response = self.auth.get_user(access_token)
            if response is None:
                return None
            
            return response.model_dump() if hasattr(response, 'model_dump') else response
        except Exception as e:
            logger.warning(f"Failed to get current user: {str(e)}")
            return None

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh the access token using refresh token.
        
        Args:
            refresh_token: Refresh token from session
            
        Returns:
            New session with fresh access token
            
        Raises:
            AuthError: If token refresh fails
        """
        try:
            response = self.auth.refresh_session(refresh_token)
            
            if response.session is None:
                raise AuthError("Token refresh failed")
            
            return {
                "session": response.session.model_dump() if hasattr(response.session, 'model_dump') else response.session,
                "user": response.user.model_dump() if response.user and hasattr(response.user, 'model_dump') else response.user
            }
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise AuthError(f"Token refresh failed: {str(e)}")

    async def reset_password(self, email: str) -> bool:
        """
        Send password reset email.
        
        Args:
            email: User email address
            
        Returns:
            True if email sent successfully
            
        Raises:
            AuthError: If operation fails
        """
        try:
            self.auth.reset_password_for_email(email)
            logger.info(f"Password reset email sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Password reset error for {email}: {str(e)}")
            raise AuthError(f"Password reset failed: {str(e)}")

    async def update_user_email(self, access_token: str, new_email: str) -> Dict[str, Any]:
        """
        Update user email address.
        
        Args:
            access_token: JWT access token
            new_email: New email address
            
        Returns:
            Updated user data
            
        Raises:
            AuthError: If update fails
        """
        try:
            response = self.auth.update_user(
                {"email": new_email},
                access_token
            )
            
            if response.user is None:
                raise AuthError("Email update failed")
            
            logger.info(f"User email updated")
            
            return response.user.model_dump() if hasattr(response.user, 'model_dump') else response.user
        except Exception as e:
            logger.error(f"Email update error: {str(e)}")
            raise AuthError(f"Email update failed: {str(e)}")

    async def update_user_password(self, access_token: str, new_password: str) -> bool:
        """
        Update user password.
        
        Args:
            access_token: JWT access token
            new_password: New password (min 8 characters)
            
        Returns:
            True if update successful
            
        Raises:
            AuthError: If update fails
        """
        try:
            self.auth.update_user(
                {"password": new_password},
                access_token
            )
            logger.info("User password updated")
            return True
        except Exception as e:
            logger.error(f"Password update error: {str(e)}")
            raise AuthError(f"Password update failed: {str(e)}")
