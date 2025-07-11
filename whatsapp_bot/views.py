import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from bot_engine.session_manager import SessionManager
from .client import WhatsAppClient

logger = logging.getLogger('whatsapp_bot')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request):
    if request.method == "GET":
        return verify_webhook(request)
    elif request.method == "POST":
        return handle_whatsapp_message(request)

def verify_webhook(request):
    try:

        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        

        if not all([mode, token, challenge]):
            logger.warning("Webhook verification missing required parameters")
            return HttpResponse("Missing parameters", status=400)
        

        expected_token = settings.WHATSAPP_BUSINESS_API['WEBHOOK_VERIFY_TOKEN']
        

        if mode == 'subscribe' and token == expected_token:
            logger.info("Webhook verified successfully")
            return HttpResponse(challenge)
        else:
            logger.warning(f"Webhook verification failed: mode={mode}, token_match={token==expected_token}")
            return HttpResponse("Verification failed", status=403)
    except KeyError as e:
        logger.error(f"Webhook verification configuration error: {str(e)}")
        return HttpResponse("Configuration error", status=500)
    except Exception as e:
        logger.error(f"Webhook verification error: {str(e)}", exc_info=True)
        return HttpResponse("Error", status=500)

def handle_whatsapp_message(request):
    try:

        content_type = request.headers.get('Content-Type', '')
        if not content_type.startswith('application/json'):
            logger.warning(f"Invalid content type: {content_type}")
            return JsonResponse({"status": "error", "message": "Invalid content type"}, status=400)
        

        try:
            body = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook payload: {str(e)}")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        

        logger.debug(f"Received webhook data: {json.dumps(body, indent=2)}")
        

        if 'entry' not in body:
            logger.warning("Webhook payload missing 'entry' field")
            return JsonResponse({"status": "error", "message": "Missing entry field"}, status=400)
        

        message_processed = False
        for entry in body['entry']:
            if 'changes' not in entry:
                continue
                
            for change in entry['changes']:
                if change.get('field') == 'messages' and 'value' in change:
                    process_message_change(change['value'])
                    message_processed = True
        
        if message_processed:
            return JsonResponse({"status": "ok"})
        else:
            logger.info("No messages to process in webhook payload")
            return JsonResponse({"status": "no_messages"})
            
    except Exception as e:
        logger.error(f"Error handling WhatsApp message: {str(e)}", exc_info=True)
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)

def process_message_change(message_data):
    try:
        if 'messages' in message_data:
            for message in message_data['messages']:
                process_incoming_message(message, message_data.get('contacts', []))
        if 'statuses' in message_data:
            for status in message_data['statuses']:
                logger.debug(f"Message status update: {status}")
    except Exception as e:
        logger.error(f"Error processing message change: {str(e)}")

def process_incoming_message(message, contacts):
    try:
        message_id = message.get('id')
        from_number = message.get('from')
        message_type = message.get('type')
        contact_name = "Unknown"
        for contact in contacts:
            if contact.get('wa_id') == from_number:
                contact_name = contact.get('profile', {}).get('name', 'Unknown')
                break
        logger.info(f"Processing message from {contact_name} ({from_number})")
        SessionManager.log_message(from_number, json.dumps(message), 'incoming')
        response_text = ""
        if message_type == 'text':
            text_content = message.get('text', {}).get('body', '')
            response_text = process_text_message(from_number, text_content)
        elif message_type == 'interactive':
            interactive_data = message.get('interactive', {})
            response_text = process_interactive_message(from_number, interactive_data)
        elif message_type == 'button':
            button_data = message.get('button', {})
            response_text = process_button_message(from_number, button_data)
        if response_text:
            whatsapp_client = WhatsAppClient()
            whatsapp_client.send_message(from_number, response_text)
            whatsapp_client.mark_message_as_read(message_id)
            SessionManager.log_message(from_number, response_text, 'outgoing')
    except Exception as e:
        logger.error(f"Error processing incoming message: {str(e)}")

def process_text_message(from_number, text_content):
    try:
        session = SessionManager.get_or_create_session(from_number)
        current_state = session.current_state
        logger.debug(f"Processing text '{text_content}' from {from_number} in state {current_state}")
        if current_state == 'new':
            return handle_new_user(from_number, text_content)
        elif current_state == 'choosing_user_type':
            return handle_user_type_selection(from_number, text_content)
        elif current_state == 'patient_auth':
            return handle_patient_authentication(from_number, text_content)
        elif current_state == 'staff_auth':
            return handle_staff_authentication(from_number, text_content)
        else:
            return handle_authenticated_user(from_number, text_content)
    except Exception as e:
        logger.error(f"Error processing text message: {str(e)}")
        return "Sorry, I encountered an error. Please try again or type 'help' for assistance."

def process_interactive_message(from_number, interactive_data):
    try:
        interactive_type = interactive_data.get('type')
        if interactive_type == 'button_reply':
            button_id = interactive_data.get('button_reply', {}).get('id')
            return handle_button_interaction(from_number, button_id)
        elif interactive_type == 'list_reply':
            list_id = interactive_data.get('list_reply', {}).get('id')
            return handle_list_interaction(from_number, list_id)
        return "Interactive message received, but not handled yet."
    except Exception as e:
        logger.error(f"Error processing interactive message: {str(e)}")
        return "Sorry, I couldn't process that interaction."

def process_button_message(from_number, button_data):
    try:
        button_text = button_data.get('text', '')
        return process_text_message(from_number, button_text)
    except Exception as e:
        logger.error(f"Error processing button message: {str(e)}")
        return "Sorry, I couldn't process that button press."

def handle_button_interaction(from_number, button_id):
    if button_id == 'patient_access':
        return handle_user_type_selection(from_number, 'patient')
    elif button_id == 'staff_access':
        return handle_user_type_selection(from_number, 'staff')
    elif button_id == 'help_info':
        return handle_user_type_selection(from_number, 'help')
    return "Button interaction received."

def handle_list_interaction(from_number, list_id):
    session = SessionManager.get_or_create_session(from_number)
    if session.user_type == 'patient':
        if list_id == 'view_records':
            return handle_patient_commands(from_number, 'records')
        elif list_id == 'view_medicines':
            return handle_patient_commands(from_number, 'medicines')
        elif list_id == 'view_procedures':
            return handle_patient_commands(from_number, 'procedures')
        elif list_id == 'view_appointments':
            return handle_patient_commands(from_number, 'appointments')
    return "List interaction received."

def handle_new_user(from_number, text_content):
    SessionManager.update_session_state(from_number, 'choosing_user_type')
    return """🏥 Welcome to CARE WhatsApp Bot!
    
I can help you access your medical information and hospital services.

Please choose your role:
• Type 'patient' - For patients to view records
• Type 'staff' - For hospital staff
• Type 'help' - For more information

What are you?"""

def handle_user_type_selection(from_number, text_content):
    text_lower = text_content.lower().strip()
    if 'patient' in text_lower:
        SessionManager.update_session_state(from_number, 'patient_auth')
        return """👤 Patient Access
        
To access your medical records, I need to verify your identity.

Please provide your Patient ID or the phone number registered with the hospital.

Format: Patient ID (e.g., P123456) or Phone (e.g., +919876543210)"""
    elif 'staff' in text_lower:
        SessionManager.update_session_state(from_number, 'staff_auth')
        return """👨‍⚕️ Hospital Staff Access
        
Please provide your staff credentials to continue.

Format: StaffID:Password (e.g., STAFF123:password123)

Your credentials will be verified with the CARE system."""
    elif 'help' in text_lower:
        return """ℹ️ CARE WhatsApp Bot Help

🏥 **What is CARE?**
CARE is a centralized patient management system that helps hospitals manage patient records, appointments, and medical information.

👤 **For Patients:**
• View your medical records
• Check current medications
• See procedure history
• View upcoming appointments

👨‍⚕️ **For Hospital Staff:**
• Access patient information
• Send notifications to patients
• Quick patient lookups

🔒 **Privacy & Security:**
Your data is protected and only authorized information is shared based on your role.

Type 'patient' or 'staff' to get started!"""
    else:
        return "Please type 'patient' for patient access, 'staff' for hospital staff access, or 'help' for more information."

def handle_patient_authentication(from_number, text_content):

    patient_id = text_content.strip()
    if len(patient_id) < 5:
        return "Invalid Patient ID or phone number. Please provide a valid Patient ID (e.g., P123456) or registered phone number."
    
    try:

        

        SessionManager.authenticate_user(from_number, 'patient', patient_id)
        SessionManager.update_session_state(from_number, 'patient_menu')
        

        logger.info(f"Patient authenticated successfully: {from_number} with ID {patient_id}")
        
        return """✅ Authentication Successful!

Welcome to your CARE patient portal. Here's what you can do:

📋 **Available Commands:**
• 'records' - View your medical records
• 'medicines' - Check current medications  
• 'procedures' - View procedure history
• 'appointments' - See upcoming appointments
• 'help' - Show this menu again
• 'logout' - End session

What would you like to do?"""
    except Exception as e:
        logger.error(f"Error authenticating patient {from_number}: {str(e)}", exc_info=True)
        return "Sorry, we couldn't authenticate you at this time. Please try again later."

def handle_staff_authentication(from_number, text_content):

    if ':' not in text_content or len(text_content.strip()) < 8:
        return "Invalid staff credentials. Please use format: StaffID:Password (e.g., STAFF123:password123)"
    
    try:

        staff_id, password = text_content.strip().split(':', 1)
        

        if not staff_id or not password or len(password) < 6:
            return "Invalid credentials. Please check your StaffID and Password."
        

        SessionManager.authenticate_user(from_number, 'staff', staff_id)
        SessionManager.update_session_state(from_number, 'staff_menu')
        

        logger.info(f"Staff authenticated successfully: {from_number} with ID {staff_id}")
        
        return """✅ Staff Authentication Successful!

Welcome to CARE Staff Portal. Available commands:

🏥 **Staff Commands:**
• 'search [patient_id]' - Find patient information
• 'notify [patient_id] [message]' - Send notification
• 'patients' - List recent patients
• 'help' - Show this menu
• 'logout' - End session

Example: search P123456

What would you like to do?"""
    except ValueError:
        return "Invalid format. Please use: StaffID:Password"
    except Exception as e:
        logger.error(f"Error authenticating staff {from_number}: {str(e)}", exc_info=True)
        return "Sorry, we couldn't authenticate you at this time. Please try again later."

def handle_authenticated_user(from_number, text_content):
    session = SessionManager.get_or_create_session(from_number)
    if session.user_type == 'patient':
        return handle_patient_commands(from_number, text_content)
    elif session.user_type == 'staff':
        return handle_staff_commands(from_number, text_content)
    return "Your session is not recognized. Type 'logout' to restart."

def handle_patient_commands(from_number, text_content):
    text = text_content.lower().strip()
    if text == 'records':
        return "📄 Medical Records:\n- Diagnosis: Flu\n- Date: 2024-03-12\n- Notes: Rest and hydration."
    elif text == 'medicines':
        return "💊 Current Medicines:\n- Paracetamol\n- Vitamin C\n- Azithromycin"
    elif text == 'procedures':
        return "🛠 Procedures:\n- Chest X-Ray (2024-03-10)\n- Blood Test (2024-03-08)"
    elif text == 'appointments':
        return "📅 Upcoming Appointments:\n- Dr. Smith - 2024-03-20 at 10:00 AM"
    elif text == 'help':
        return """📋 Patient Commands:
• 'records' - View your medical records
• 'medicines' - Check medications  
• 'procedures' - View procedures
• 'appointments' - View appointments
• 'logout' - End session"""
    elif text == 'logout':
        SessionManager.logout_user(from_number)
        return "🔒 You have been logged out. Type 'patient' or 'staff' to login again."
    else:
        return "Command not recognized. Type 'help' to see available options."

def handle_staff_commands(from_number, text_content):
    text = text_content.strip()
    lower = text.lower()
    if lower.startswith('search '):
        patient_id = text[7:].strip()
        return f"🔍 Patient Search: {patient_id}\n- Name: John Doe\n- Last Visit: 2024-03-12\n- Notes: Follow-up in 2 weeks."
    elif lower.startswith('notify '):
        try:
            _, patient_id, *message_parts = text.split()
            message = ' '.join(message_parts)
            return f"📨 Notification sent to {patient_id}:\n'{message}'"
        except:
            return "Invalid notify format. Use: notify [patient_id] [message]"
    elif lower == 'patients':
        return "🧑‍🤝‍🧑 Recent Patients:\n- P123456 - John Doe\n- P234567 - Jane Smith\n- P345678 - Alice Johnson"
    elif lower == 'help':
        return """👨‍⚕️ Staff Commands:
• 'search [patient_id]' - Find patient
• 'notify [patient_id] [message]' - Send notification
• 'patients' - List patients
• 'logout' - End session"""
    elif lower == 'logout':
        SessionManager.logout_user(from_number)
        return "🔒 Staff session ended. Type 'staff' to login again."
    else:
        return "Unknown staff command. Type 'help' for options."