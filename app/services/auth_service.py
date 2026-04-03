import re
import bcrypt
from sqlalchemy import func
from app.models.models import *
import uuid
from app.schemas.auth_schema import * 
from app.core.config import settings
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import CustomAPIException
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload
import logging


logger = logging.getLogger(__name__)


class AuthService:
    """
    Service class for handling user authentication and related operations.

    Methods:
        validate_username: Checks if username is alphanumeric and starts with a letter.
        is_valid_email: Checks if email is valid using regex.
        validate_phone: Validates phone number format (India and generic).
        hash_password: Hashes a plaintext password with bcrypt.
        verify_password: Compares plaintext password against stored hash.
        create_access_token: Creates JWT access token with expiry.
        signup_user: Registers a new user with validation and hashed password.
        login_user: Authenticates user and returns access & refresh tokens.
        logout_user: Invalidates user's refresh token.
        get_user: Fetches user details for profile endpoint.
        delete_user: Deletes a user along with credentials and tasks.
    """


    def validate_username(self, username: str) -> bool:
        """Validate that username is alphanumeric and starts with a letter."""
        return bool(re.match("^[a-zA-Z][a-zA-Z0-9]*$", username))


    def is_valid_email(self, email: str) -> bool:
        """Validate email address format using regex."""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(email_regex, email))


    async def hash_password(self, password: str) -> str:
        """Hash plaintext password asynchronously using bcrypt."""
        hashed = await asyncio.to_thread(bcrypt.hashpw,
            password.encode('utf-8'),
            bcrypt.gensalt()  # Auto-generates and embeds salt
        )
        return hashed.decode('utf-8')


    async def verify_password(self, stored_hash: str, password: str) -> bool:
        """Verify plaintext password against stored hash asynchronously."""
        # (bcrypt stores the salt inside the hash so you can compare directly)
        return await asyncio.to_thread(bcrypt.checkpw, password.encode('utf-8'), stored_hash.encode('utf-8'))
    
    def validate_phone(self, country_code: str, phone: str) -> bool:
        """Validate phone number (India-specific + generic check)."""
        # digits only
        if not phone.isdigit():
            return False

        # India specific
        if country_code == "+91":
            return bool(re.fullmatch(r"[6-9]\d{9}", phone))

        # Generic fallback for other countries
        return 8 <= len(phone) <= 15

    def validate_password(self, password: str) -> bool:
        """Validate password strength (minimum length and basic complexity)."""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Za-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        return True


    async def signup_user(self, signup_data: SignupRequest, db: AsyncSession) -> SignupResponse:
        """
        Register a new user.

        Validates username, email, phone, and ensures unique username.
        Hashes password and creates User and UserCredentials entries.
        """
        # Validate username
        if not self.validate_username(signup_data.username):
            raise CustomAPIException(400,"Username must be alphanumeric, start with an alphabet, and contain no special characters.")

        # Validate phone number
        if not self.validate_phone(signup_data.country_code, signup_data.phone):
            raise CustomAPIException(400, "Invalid phone number")


        # Validate email
        if not self.is_valid_email(signup_data.email):
            raise CustomAPIException(400,"Invalid email address.")
        
        # Validate password strength
        if not self.validate_password(signup_data.password):
            raise CustomAPIException(400, "Password must be at least 8 characters long and include letters and numbers.")

        # Hash the password with auto-generated salt
        password_hash = await self.hash_password(signup_data.password)

        existing_user = await db.execute(
            select(UserCredentials).where(
                func.lower(UserCredentials.username) == signup_data.username.lower()
            )
        )
        if existing_user.scalar_one_or_none():
            raise CustomAPIException(409, "Username already exists")


        user = User(
            name=signup_data.name,
            email=signup_data.email.lower(),
            country_code = signup_data.country_code,
            phone = signup_data.phone,
            year_of_birth=signup_data.year_of_birth,
            gender=signup_data.gender
        )

        db.add(user)
        await db.flush()

        refresh_token_expiry = int((datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp())

        refresh_token = uuid.uuid4()

        user_credentials = UserCredentials(
            user_id=user.id,
            username=signup_data.username.lower(),
            password_hash=password_hash,
            refresh_token=refresh_token,
            refresh_token_expiry=refresh_token_expiry
        )

        
        # Database operations
        db.add(user_credentials)
        await db.commit()

        return SignupResponse(
            user_id=str(user.id),
            message="Signup successful"
        )


    def create_access_token(self, data: dict, expires_minutes: int):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow()
        })

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )



    async def login_user(self, login_data: LoginRequest, db: AsyncSession):
        """
        Authenticate user by username & password.

        Returns JWT access token and refresh token.
        """
        # Fetch user credentials with case-insensitive match
        user_credentials = (await db.execute(
            select(UserCredentials).options(joinedload(UserCredentials.r_cred_user)).where(func.lower(UserCredentials.username) == login_data.username.lower())
        )).unique().scalar_one_or_none()

        if not user_credentials:
            raise CustomAPIException(404, "Username does not exist.")

        # decoded_password = fernet.decrypt(login_data.password).decode()
        # Verify password
        if not await self.verify_password(user_credentials.password_hash, login_data.password):
            raise CustomAPIException(403, "Incorrect password.")

        # Convert UUID to string
        user_id_str = str(user_credentials.user_id)
        current_time = int(datetime.utcnow().timestamp())

        # Check if existing refresh token is still valid
        if user_credentials.refresh_token and user_credentials.refresh_token_expiry > current_time:
            # Use existing refresh token
            refresh_token_value = user_credentials.refresh_token
        else:
            # Generate new refresh token UUID and update expiry
            refresh_token_value = uuid.uuid4()
            new_expiry = int((datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp())
            
            # Update in database
            user_credentials.refresh_token = refresh_token_value
            user_credentials.refresh_token_expiry = new_expiry
            await db.commit()
            await db.refresh(user_credentials)

        access_token = self.create_access_token(
            data={"sub": user_id_str, "type": "access"},
            expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )


        return LoginResponse(
            user_id=user_id_str,
            username=user_credentials.username,
            name=user_credentials.r_cred_user.name,
            email=user_credentials.r_cred_user.email,
            access_token=access_token,
            refresh_token=str(refresh_token_value),
            token_type="bearer"
        )
    

    async def logout_user(self, db: AsyncSession, user_id):
        """Logout User by removing refresh token and its expiry"""
        
        new_expiry = int(datetime.utcnow().timestamp())
        
        result = await db.execute(
            update(UserCredentials)
            .where(UserCredentials.user_id == user_id)
            .values(
                refresh_token=uuid.uuid4(),
                refresh_token_expiry=new_expiry
            )
        )

        if result.rowcount == 0:
            raise CustomAPIException(404, "User session not found")

        await db.commit()
        
        return CommonMessageResponse(message="Logout successful")

    

    async def get_user(self, db: AsyncSession, user_id, refresh: bool = False): 
        """Fetch user profile details.""" 
        user = (
                    await db.execute(
                        select(User)
                        .options(joinedload(User.r_credentials))
                        .filter(User.id == user_id)
                    )
                ).scalar_one_or_none()

        if not user:
            raise CustomAPIException(404, "User not found")

        response = UserBaseResponse(
            user_id=str(user.id), 
            name=user.name,
            username=user.r_credentials.username,
            email=user.email, 
            year_of_birth=user.year_of_birth, 
            gender=str(user.gender),
            country_code= user.country_code,
            phone=user.phone
        )

        return response
    

    async def delete_user(self, db: AsyncSession, user_id: str):
        """Delete a user along with credentials and tasks"""
        
        result = await db.execute(
            delete(User).where(User.id == user_id)
        )

        if result.rowcount == 0:
            raise CustomAPIException(404, "User not found")

        await db.commit()
        return CommonMessageResponse(message="User deleted successfully")
