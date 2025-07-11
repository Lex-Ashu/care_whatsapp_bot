# Session States
class SessionState:
    NEW = 'new'
    USER_TYPE_SELECTION = 'user_type_selection'
    AUTHENTICATION = 'authentication'
    MAIN_MENU = 'main_menu'
    PATIENT_MENU = 'patient_menu'
    STAFF_MENU = 'staff_menu'
    RECORDS_VIEW = 'records_view'
    MEDICINES_VIEW = 'medicines_view'
    PROCEDURES_VIEW = 'procedures_view'
    APPOINTMENTS_VIEW = 'appointments_view'
    PATIENT_SEARCH = 'patient_search'
    PATIENT_DETAILS = 'patient_details'
    NOTIFICATION_SEND = 'notification_send'

# User Types
class UserType:
    PATIENT = 'patient'
    STAFF = 'staff'

# Message Types
class MessageType:
    INCOMING = 'incoming'
    OUTGOING = 'outgoing'
    TEMPLATE = 'template'
    INTERACTIVE = 'interactive'

# WhatsApp API Constants
class WhatsAppAPI:
    API_VERSION = 'v22.0'
    BASE_URL = f'https://graph.facebook.com/{API_VERSION}'
    MAX_TEXT_LENGTH = 4096
    MAX_BUTTONS = 3
    MESSAGE_TYPE_TEXT = 'text'
    MESSAGE_TYPE_TEMPLATE = 'template'
    MESSAGE_TYPE_INTERACTIVE = 'interactive'

# Session Expiry
class SessionExpiry:
    # Session expires after 24 hours of inactivity
    EXPIRY_HOURS = 24
    # Token expires after 24 hours (1440 minutes)
    TOKEN_EXPIRY_MINUTES = 1440
    # Token refresh extends by 24 hours (1440 minutes)
    TOKEN_REFRESH_MINUTES = 1440

# Command Keywords
class Command:
    HELP = 'help'
    LOGOUT = 'logout'
    RESTART = 'restart'
    RECORDS = 'records'
    MEDICINES = 'medicines'
    PROCEDURES = 'procedures'
    APPOINTMENTS = 'appointments'
    SEARCH = 'search'
    NOTIFY = 'notify'
    PATIENTS = 'patients'
    BACK = 'back'
    MENU = 'menu'