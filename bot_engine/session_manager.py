import logging
from core.models import UserSession, BotMessage
from django.utils import timezone

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
            if not created and session.is_session_expired():
                logger.info(f"Session expired for {whatsapp_id}, clearing session")
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
    def authenticate_user(whatsapp_id, user_type, auth_token=None):
        try:
            session = SessionManager.get_or_create_session(whatsapp_id)
            session.user_type = user_type
            session.is_authenticated = True
            session.auth_token = auth_token
            session.save()
            logger.info(f"User authenticated: {whatsapp_id} as {user_type}")
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
