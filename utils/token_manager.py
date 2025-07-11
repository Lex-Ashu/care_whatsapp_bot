import logging
import time
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from utils.constants import SessionExpiry

logger = logging.getLogger('token_manager')

class TokenManager:
    
    @staticmethod
    def generate_token(user_id, user_type, expiry_minutes=SessionExpiry.TOKEN_EXPIRY_MINUTES):
        try:
            payload = {
                'user_id': user_id,
                'user_type': user_type,
                'exp': datetime.utcnow() + timedelta(minutes=expiry_minutes),
                'iat': datetime.utcnow(),
                'jti': str(int(time.time() * 1000))  # Unique token ID
            }
            
            token = jwt.encode(
                payload,
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            
            logger.debug(f"Generated token for {user_type} user {user_id}")
            return token
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            raise
    
    @staticmethod
    def validate_token(token):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return None
    
    @staticmethod
    def is_token_expired(token):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            return False
        except jwt.ExpiredSignatureError:
            return True
        except jwt.InvalidTokenError:
            return True
        except Exception as e:
            logger.error(f"Error checking token expiration: {str(e)}")
            return True
    
    @staticmethod
    def refresh_token(token, extend_minutes=SessionExpiry.TOKEN_REFRESH_MINUTES):
        try:
            # First validate the token
            payload = TokenManager.validate_token(token)
            if not payload:
                logger.warning("Cannot refresh invalid token")
                return None
            
            # Create new payload with extended expiration
            payload['exp'] = datetime.utcnow() + timedelta(minutes=extend_minutes)
            payload['iat'] = datetime.utcnow()  # Update issued at time
            payload['jti'] = str(int(time.time() * 1000))  # New token ID
            
            # Generate new token
            new_token = jwt.encode(
                payload,
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            
            logger.debug(f"Refreshed token for {payload.get('user_type')} user {payload.get('user_id')}")
            return new_token
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None