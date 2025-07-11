import logging
import json
from core.models import UserSession, BotMessage
from django.utils import timezone
from utils.token_manager import TokenManager
from utils.constants import SessionExpiry

logger = logging.getLogger('whatsapp_bot')

class SessionManager:

    @staticmethod
    def get_or_create_session(whatsapp_id):
        try:
            session, created = UserSession.objects.get_or_create(
                whatsapp_id=whatsapp_id,
                defaults={
                    'current_state': 'new',
                    'session_data': {},
                }
            )
            if not created:
                if session.is_session_expired():
                    logger.info(f"Session expired for {whatsapp_id}, clearing session")
                    session.clear_session()
        
                elif session.auth_token and TokenManager.is_token_expired(session.auth_token):
                    logger.info(f"Session token expired for {whatsapp_id}, resetting session")
                    session.clear_session()
            logger.debug(f"Session {'created' if created else 'retrieved'} for {whatsapp_id}")
            return session
        except Exception as e:
            logger.error(f"Error managing session for {whatsapp_id}: {str(e)}")
            raise

    @staticmethod
    def update_session_state(whatsapp_id, new_state, data=None):
        try:
            session = SessionManager.get_or_create_session(whatsapp_id)
            session.update_session(state=new_state, data=data or {})
            logger.debug(f"Updated session state for {whatsapp_id}: {new_state}")
            return session
        except Exception as e:
            logger.error(f"Error updating session for {whatsapp_id}: {str(e)}")
            raise

    @staticmethod
    def authenticate_user(whatsapp_id, user_type, user_id, auth_token=None):
        try:
            # Use provided auth_token or generate a new one
            if not auth_token:
                auth_token = TokenManager.generate_token(
                    user_id=user_id,
                    user_type=user_type,
                    expiry_minutes=SessionExpiry.TOKEN_EXPIRY_MINUTES
                )
            
            session = SessionManager.get_or_create_session(whatsapp_id)
            session.user_type = user_type
            session.is_authenticated = True
            session.auth_token = auth_token
            
            # Store user ID in session data
            session_data = session.session_data
            session_data['user_id'] = user_id
            session.session_data = session_data
            
            session.save()
            logger.info(f"User authenticated: {whatsapp_id} as {user_type} with ID {user_id}")
            return session
        except Exception as e:
            logger.error(f"Error authenticating user {whatsapp_id}: {str(e)}")
            raise

    @staticmethod
    def log_message(whatsapp_id, message_content, message_type='incoming'):

        try:
            session = SessionManager.get_or_create_session(whatsapp_id)
            BotMessage.objects.create(
                session=session,
                message_type=message_type,
                message_content=message_content
            )
            logger.debug(f"Message logged: {whatsapp_id} - {message_type}")
        except Exception as e:
            logger.error(f"Error logging message for {whatsapp_id}: {str(e)}")

    @staticmethod
    def get_session_data(whatsapp_id, key=None):
        try:
            session = SessionManager.get_or_create_session(whatsapp_id)
            
    
            if session.auth_token and not TokenManager.is_token_expired(session.auth_token):
                # Refresh the token to extend session if user is active
                new_token = TokenManager.refresh_token(session.auth_token)
                if new_token:
                    session.auth_token = new_token
                    session.save()
                    logger.debug(f"Refreshed token for {whatsapp_id}")
            
            if key:
                return session.session_data.get(key)
            return session.session_data
        except Exception as e:
            logger.error(f"Error getting session data for {whatsapp_id}: {str(e)}")
            return None

    @staticmethod
    def clear_session(whatsapp_id):
        try:
            session = SessionManager.get_or_create_session(whatsapp_id)
            session.clear_session()
            logger.info(f"Session cleared for {whatsapp_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing session for {whatsapp_id}: {str(e)}")
            return False
            
    @staticmethod
    def logout_user(whatsapp_id):
        try:
            session = SessionManager.get_or_create_session(whatsapp_id)
            session.is_authenticated = False
            session.auth_token = None
            session.current_state = 'new'
            session.save()
            logger.info(f"User logged out: {whatsapp_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging out user {whatsapp_id}: {str(e)}")
            return False
