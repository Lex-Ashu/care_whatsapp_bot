import logging
import json
from typing import Dict, Any, Optional, List, Tuple

from bot_engine.session_manager import SessionManager
from whatsapp_bot.client import WhatsAppClient
from care_wrapper.client import CAREAPIClient
from utils.constants import SessionState, UserType, Command
from core.models import UserSession

logger = logging.getLogger('whatsapp_bot')

class IMBotService:
    """
    Instant Messaging Bot Service - Core orchestration layer for the WhatsApp bot.
    
    This service handles the business logic for processing messages, managing user sessions,
    and coordinating between the WhatsApp API client and the CARE API integration.
    
    It serves as the central component that implements the bot's conversational flow and
    business rules, separating these concerns from the webhook handling and API client code.
    """
    
    def __init__(self):
        self.whatsapp_client = WhatsAppClient()
        self.session_manager = SessionManager
        self.care_api_client = CAREAPIClient()
        
    def process_message(self, from_number: str, message_data: Dict[str, Any]) -> str:
        """
        Process an incoming message and generate an appropriate response.
        
        Args:
            from_number: The WhatsApp ID of the sender
            message_data: The message data containing type and content
            
        Returns:
            The response text to be sent back to the user
        """
        try:
    
            self.session_manager.log_message(from_number, json.dumps(message_data), 'incoming')
            
    
            message_type = message_data.get('type')
            response_text = ""
            
    
            if message_type == 'text':
                text_content = message_data.get('text', {}).get('body', '')
                response_text = self._process_text_message(from_number, text_content)
            elif message_type == 'interactive':
                interactive_data = message_data.get('interactive', {})
                response_text = self._process_interactive_message(from_number, interactive_data)
            elif message_type == 'button':
                button_data = message_data.get('button', {})
                response_text = self._process_button_message(from_number, button_data)
            else:
                response_text = "I can only process text and interactive messages at the moment."
                
    
            if response_text:
                self.session_manager.log_message(from_number, response_text, 'outgoing')
                
            return response_text
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return "Sorry, I encountered an error. Please try again or type 'help' for assistance."
    
    def _process_text_message(self, from_number: str, text_content: str) -> str:
        """
        Process a text message based on the user's current session state.
        
        Args:
            from_number: The WhatsApp ID of the sender
            text_content: The text content of the message
            
        Returns:
            The response text to be sent back to the user
        """
        try:
            session = self.session_manager.get_or_create_session(from_number)
            current_state = session.current_state
            logger.debug(f"Processing text '{text_content}' from {from_number} in state {current_state}")
            
    
            if text_content.lower() == Command.LOGOUT:
                return self._handle_logout(from_number)
            elif text_content.lower() == Command.HELP:
                return self._get_help_message(session)
            elif text_content.lower() == Command.RESTART:
                self.session_manager.clear_session(from_number)
                return self._handle_new_user(from_number)
            
    
            if current_state == SessionState.NEW:
                return self._handle_new_user(from_number)
            elif current_state == SessionState.USER_TYPE_SELECTION:
                return self._handle_user_type_selection(from_number, text_content)
            elif current_state == 'patient_auth':
                return self._handle_patient_authentication(from_number, text_content)
            elif current_state == 'staff_auth':
                return self._handle_staff_authentication(from_number, text_content)
            else:
                return self._handle_authenticated_user(from_number, text_content)
        except Exception as e:
            logger.error(f"Error processing text message: {str(e)}", exc_info=True)
            return "Sorry, I encountered an error. Please try again or type 'help' for assistance."
    
    def _process_interactive_message(self, from_number: str, interactive_data: Dict[str, Any]) -> str:
        """
        Process an interactive message (buttons, lists).
        
        Args:
            from_number: The WhatsApp ID of the sender
            interactive_data: The interactive data from the message
            
        Returns:
            The response text to be sent back to the user
        """
        try:
            interactive_type = interactive_data.get('type')
            if interactive_type == 'button_reply':
                button_id = interactive_data.get('button_reply', {}).get('id')
                return self._handle_button_interaction(from_number, button_id)
            elif interactive_type == 'list_reply':
                list_id = interactive_data.get('list_reply', {}).get('id')
                return self._handle_list_interaction(from_number, list_id)
            return "Interactive message received, but not handled yet."
        except Exception as e:
            logger.error(f"Error processing interactive message: {str(e)}", exc_info=True)
            return "Sorry, I couldn't process that interaction."
    
    def _process_button_message(self, from_number: str, button_data: Dict[str, Any]) -> str:
        """
        Process a button message.
        
        Args:
            from_number: The WhatsApp ID of the sender
            button_data: The button data from the message
            
        Returns:
            The response text to be sent back to the user
        """
        try:
            button_text = button_data.get('text', '')
            return self._process_text_message(from_number, button_text)
        except Exception as e:
            logger.error(f"Error processing button message: {str(e)}", exc_info=True)
            return "Sorry, I couldn't process that button press."
    
    def _handle_new_user(self, from_number: str) -> str:
        """
        Handle a new user or reset session.
        
        Args:
            from_number: The WhatsApp ID of the user
            
        Returns:
            Welcome message with options
        """
        self.session_manager.update_session_state(from_number, 'choosing_user_type')
        return """🏥 Welcome to CARE WhatsApp Bot!
        
I can help you access your medical information and hospital services.

Please choose your role:
• Type 'patient' - For patients to view records
• Type 'staff' - For hospital staff
• Type 'help' - For more information

What are you?"""
    
    def _handle_user_type_selection(self, from_number: str, text_content: str) -> str:
        """
        Handle user type selection (patient, staff, help).
        
        Args:
            from_number: The WhatsApp ID of the user
            text_content: The text message content
            
        Returns:
            Response based on user type selection
        """
        text_lower = text_content.lower().strip()
        if 'patient' in text_lower:
            self.session_manager.update_session_state(from_number, 'patient_auth')
            return """👤 Patient Access
            
To access your medical records, I need to verify your identity.

Please provide your Patient ID or the phone number registered with the hospital.

Format: Patient ID (e.g., P123456) or Phone (e.g., +919876543210)"""
        elif 'staff' in text_lower:
            self.session_manager.update_session_state(from_number, 'staff_auth')
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
    
    def _handle_patient_authentication(self, from_number: str, text_content: str) -> str:
        """
        Handle patient authentication.
        
        Args:
            from_number: The WhatsApp ID of the user
            text_content: The text message containing patient ID or phone
            
        Returns:
            Authentication result message
        """

        patient_id = text_content.strip()
        if len(patient_id) < 5:
            return "Invalid Patient ID or phone number. Please provide a valid Patient ID (e.g., P123456) or registered phone number."
        
        try:
    
            auth_result = self.care_api_client.authenticate_patient(patient_id)
            
            if auth_result.get('authenticated', False):
                # Store authentication token in session
                auth_token = auth_result.get('token', '')
                patient_name = auth_result.get('name', 'Patient')
                
        
                self.session_manager.authenticate_user(from_number, 'patient', patient_id, auth_token)
                self.session_manager.update_session_state(from_number, 'patient_menu')
                
        
                logger.info(f"Patient authenticated successfully: {from_number} with ID {patient_id}")
                
                return f"""✅ Authentication Successful!

Welcome {patient_name} to your CARE patient portal. Here's what you can do:

📋 **Available Commands:**
• 'records' - View your medical records
• 'medicines' - Check current medications  
• 'procedures' - View procedure history
• 'appointments' - See upcoming appointments
• 'help' - Show this menu again
• 'logout' - End session

What would you like to do?"""
            else:
                logger.warning(f"Failed patient authentication attempt: {from_number} with ID {patient_id}")
                return "❌ Authentication failed. Please check your Patient ID or phone number and try again."
        except Exception as e:
            logger.error(f"Error authenticating patient {from_number}: {str(e)}", exc_info=True)
            return "Sorry, we couldn't authenticate you at this time. Please try again later."
    
    def _handle_staff_authentication(self, from_number: str, text_content: str) -> str:
        """
        Handle staff authentication.
        
        Args:
            from_number: The WhatsApp ID of the user
            text_content: The text message containing staff credentials
            
        Returns:
            Authentication result message
        """

        if ':' not in text_content or len(text_content.strip()) < 8:
            return "Invalid staff credentials. Please use format: StaffID:Password (e.g., STAFF123:password123)"
        
        try:
            # Parse credentials
            staff_id, password = text_content.strip().split(':', 1)
            
    
            if not staff_id or not password or len(password) < 6:
                return "Invalid credentials. Please check your StaffID and Password."
            
    
            auth_result = self.care_api_client.authenticate_staff(staff_id, password)
            
            if auth_result.get('authenticated', False):
                # Store authentication token in session
                auth_token = auth_result.get('token', '')
                staff_name = auth_result.get('name', 'Staff Member')
                staff_role = auth_result.get('role', 'Staff')
                
        
                self.session_manager.authenticate_user(from_number, 'staff', staff_id, auth_token)
                self.session_manager.update_session_state(from_number, 'staff_menu')
                
                # Store additional staff info in session
                session = self.session_manager.get_or_create_session(from_number)
                session_data = session.session_data
                session_data['staff_role'] = staff_role
                session_data['staff_name'] = staff_name
                session.session_data = session_data
                session.save()
                
        
                logger.info(f"Staff authenticated successfully: {from_number} with ID {staff_id}")
                
                return f"""✅ Staff Authentication Successful!

Welcome {staff_name} ({staff_role}) to CARE Staff Portal. Available commands:

🏥 **Staff Commands:**
• 'search [patient_id]' - Find patient information
• 'notify [patient_id] [message]' - Send notification
• 'patients' - List recent patients
• 'help' - Show this menu
• 'logout' - End session

Example: search P123456

What would you like to do?"""
            else:
                logger.warning(f"Failed staff authentication attempt: {from_number} with ID {staff_id}")
                return "❌ Authentication failed. Please check your Staff ID and Password and try again."
        except ValueError:
            return "Invalid format. Please use: StaffID:Password"
        except Exception as e:
            logger.error(f"Error authenticating staff {from_number}: {str(e)}", exc_info=True)
            return "Sorry, we couldn't authenticate you at this time. Please try again later."
    
    def _handle_authenticated_user(self, from_number: str, text_content: str) -> str:
        """
        Handle commands from authenticated users.
        
        Args:
            from_number: The WhatsApp ID of the user
            text_content: The text message content
            
        Returns:
            Response to the user's command
        """
        session = self.session_manager.get_or_create_session(from_number)
        if session.user_type == 'patient':
            return self._handle_patient_commands(from_number, text_content)
        elif session.user_type == 'staff':
            return self._handle_staff_commands(from_number, text_content)
        return "Your session is not recognized. Type 'logout' to restart."
    
    def _handle_patient_commands(self, from_number: str, text_content: str) -> str:
        """
        Handle commands from authenticated patients.
        
        Args:
            from_number: The WhatsApp ID of the user
            text_content: The text message content
            
        Returns:
            Response to the patient's command
        """
        text = text_content.lower().strip()
        session = self.session_manager.get_or_create_session(from_number)
        patient_id = session.session_data.get('user_id', '')
        auth_token = session.auth_token
        
        if not patient_id or not auth_token:
            return "Your session has expired. Please type 'logout' and authenticate again."
        
        try:
            if text == 'records':
                records = self.care_api_client.get_patient_records(patient_id, auth_token)
                if not records:
                    return "📄 No medical records found."
                
                # Format records for display
                records_text = "📄 **Medical Records:**\n\n"
                for record in records:
                    records_text += f"**Date:** {record.get('date')}\n"
                    records_text += f"**Diagnosis:** {record.get('diagnosis')}\n"
                    records_text += f"**Doctor:** {record.get('doctor')}\n"
                    if record.get('notes'):
                        records_text += f"**Notes:** {record.get('notes')}\n"
                    records_text += "\n"
                
                return records_text
                
            elif text == 'medicines':
                medications = self.care_api_client.get_patient_medications(patient_id, auth_token)
                if not medications:
                    return "💊 No current medications found."
                
                # Format medications for display
                meds_text = "💊 **Current Medications:**\n\n"
                for med in medications:
                    meds_text += f"**{med.get('name')}** - {med.get('dosage')}\n"
                    meds_text += f"Take: {med.get('frequency')}\n"
                    meds_text += f"Duration: {med.get('start_date')} to {med.get('end_date')}\n\n"
                
                return meds_text
                
            elif text == 'procedures':
                procedures = self.care_api_client.get_patient_procedures(patient_id, auth_token)
                if not procedures:
                    return "🛠 No procedures found."
                
                # Format procedures for display
                proc_text = "🛠 **Procedures:**\n\n"
                for proc in procedures:
                    proc_text += f"**{proc.get('name')}** - {proc.get('date')}\n"
                    proc_text += f"Doctor: {proc.get('doctor')}\n"
                    proc_text += f"Result: {proc.get('result')}\n"
                    if proc.get('notes'):
                        proc_text += f"Notes: {proc.get('notes')}\n"
                    proc_text += "\n"
                
                return proc_text
                
            elif text == 'appointments':
                appointments = self.care_api_client.get_patient_appointments(patient_id, auth_token)
                if not appointments:
                    return "📅 No upcoming appointments found."
                
                # Format appointments for display
                appt_text = "📅 **Upcoming Appointments:**\n\n"
                for appt in appointments:
                    appt_text += f"**{appt.get('date')} at {appt.get('time')}**\n"
                    appt_text += f"Doctor: {appt.get('doctor')}\n"
                    appt_text += f"Department: {appt.get('department')}\n"
                    appt_text += f"Reason: {appt.get('reason')}\n\n"
                
                return appt_text
                
            elif text == 'help':
                return """📋 **Patient Commands:**
• 'records' - View your medical records
• 'medicines' - Check medications  
• 'procedures' - View procedures
• 'appointments' - View appointments
• 'logout' - End session"""
            elif text == 'logout':
                return self._handle_logout(from_number)
            else:
                return "Command not recognized. Type 'help' to see available options."
        except Exception as e:
            logger.error(f"Error handling patient command: {str(e)}", exc_info=True)
            return "Sorry, I encountered an error processing your request. Please try again later."
    
    def _handle_staff_commands(self, from_number: str, text_content: str) -> str:
        """
        Handle commands from authenticated staff members.
        
        Args:
            from_number: The WhatsApp ID of the user
            text_content: The text message content
            
        Returns:
            Response to the staff member's command
        """
        text = text_content.strip()
        lower = text.lower()
        session = self.session_manager.get_or_create_session(from_number)
        staff_id = session.session_data.get('user_id', '')
        auth_token = session.auth_token
        
        if not staff_id or not auth_token:
            return "Your session has expired. Please type 'logout' and authenticate again."
        
        try:
            if lower.startswith('search '):
                patient_id = text[7:].strip()

                patient_info = self.care_api_client.search_patient(patient_id, auth_token)
                
                if not patient_info:
                    return f"No patient found with ID: {patient_id}"
                
                # Format patient info for display
                response = f"🔍 **Patient {patient_id} found:**\n"
                response += f"**Name:** {patient_info.get('name', 'Unknown')}\n"
                response += f"**Age:** {patient_info.get('age', 'Unknown')}\n"
                response += f"**Gender:** {patient_info.get('gender', 'Unknown')}\n"
                response += f"**Last Visit:** {patient_info.get('last_visit', 'Unknown')}\n"
                
                if patient_info.get('recent_diagnosis'):
                    response += f"**Recent Diagnosis:** {patient_info.get('recent_diagnosis')}\n"
                
                return response
            
            elif lower.startswith('notify '):
                try:
                    _, patient_id, *message_parts = text.split()
                    message = ' '.join(message_parts)
                    
                    # Send notification via CARE API
                    result = self.care_api_client.send_patient_notification(patient_id, message, auth_token)
                    
                    if result.get('success'):
                        return f"✅ Notification sent to patient {patient_id}:\n\"{message}\""
                    else:
                        return f"❌ Failed to send notification: {result.get('error', 'Unknown error')}"
                except:
                    return "Invalid notify format. Use: notify [patient_id] [message]"
            
            elif lower == 'patients':

                recent_patients = self.care_api_client.get_recent_patients(auth_token)
                
                if not recent_patients:
                    return "No recent patients found."
                
                # Format recent patients for display
                response = "🧑‍🤝‍🧑 **Recent Patients:**\n\n"
                for patient in recent_patients:
                    response += f"**ID:** {patient.get('id')}\n"
                    response += f"**Name:** {patient.get('name')}\n"
                    response += f"**Visit Date:** {patient.get('visit_date')}\n"
                    response += f"**Reason:** {patient.get('reason')}\n\n"
                
                return response
            
            elif lower == 'help':
                return """👨‍⚕️ **Staff Commands:**
• 'search [patient_id]' - Find patient
• 'notify [patient_id] [message]' - Send notification
• 'patients' - List patients
• 'logout' - End session"""
            
            elif lower == 'logout':
                return self._handle_logout(from_number)
            
            else:
                return "Command not recognized. Type 'help' to see available options."
        except Exception as e:
            logger.error(f"Error handling staff command: {str(e)}", exc_info=True)
            return "Sorry, I encountered an error processing your request. Please try again later."
    
    def _handle_button_interaction(self, from_number: str, button_id: str) -> str:
        """
        Handle button interactions.
        
        Args:
            from_number: The WhatsApp ID of the user
            button_id: The button ID that was clicked
            
        Returns:
            Response to the button interaction
        """
        if button_id == 'patient_access':
            return self._handle_user_type_selection(from_number, 'patient')
        elif button_id == 'staff_access':
            return self._handle_user_type_selection(from_number, 'staff')
        elif button_id == 'help_info':
            return self._handle_user_type_selection(from_number, 'help')
        return "Button interaction received."
    
    def _handle_list_interaction(self, from_number: str, list_id: str) -> str:
        """
        Handle list interactions from the user.
        
        Args:
            from_number: The WhatsApp ID of the user
            list_id: The ID of the selected list item
            
        Returns:
            Response to the list selection
        """
        session = self.session_manager.get_or_create_session(from_number)
        user_id = session.session_data.get('user_id', '')
        auth_token = session.auth_token
        
        if not user_id or not auth_token:
            return "Your session has expired. Please type 'logout' and authenticate again."
        
        try:

            if list_id == 'patient_records':

                records = self.care_api_client.get_patient_records(user_id, auth_token)
                if not records:
                    return "📄 No medical records found."
                
                # Format records for display
                records_text = "📄 **Medical Records:**\n\n"
                for record in records:
                    records_text += f"**Date:** {record.get('date')}\n"
                    records_text += f"**Diagnosis:** {record.get('diagnosis')}\n"
                    records_text += f"**Doctor:** {record.get('doctor')}\n"
                    if record.get('notes'):
                        records_text += f"**Notes:** {record.get('notes')}\n"
                    records_text += "\n"
                
                return records_text
                
            elif list_id == 'patient_medicines':

                medications = self.care_api_client.get_patient_medications(user_id, auth_token)
                if not medications:
                    return "💊 No current medications found."
                
                # Format medications for display
                meds_text = "💊 **Current Medications:**\n\n"
                for med in medications:
                    meds_text += f"**{med.get('name')}** - {med.get('dosage')}\n"
                    meds_text += f"Take: {med.get('frequency')}\n"
                    meds_text += f"Duration: {med.get('start_date')} to {med.get('end_date')}\n\n"
                
                return meds_text
                
            elif list_id == 'patient_procedures':

                procedures = self.care_api_client.get_patient_procedures(user_id, auth_token)
                if not procedures:
                    return "🛠 No procedures found."
                
                # Format procedures for display
                proc_text = "🛠 **Procedures:**\n\n"
                for proc in procedures:
                    proc_text += f"**{proc.get('name')}** - {proc.get('date')}\n"
                    proc_text += f"Doctor: {proc.get('doctor')}\n"
                    proc_text += f"Result: {proc.get('result')}\n"
                    if proc.get('notes'):
                        proc_text += f"Notes: {proc.get('notes')}\n"
                    proc_text += "\n"
                
                return proc_text
                
            elif list_id == 'patient_appointments':

                appointments = self.care_api_client.get_patient_appointments(user_id, auth_token)
                if not appointments:
                    return "📅 No upcoming appointments found."
                
                # Format appointments for display
                appt_text = "📅 **Upcoming Appointments:**\n\n"
                for appt in appointments:
                    appt_text += f"**{appt.get('date')} at {appt.get('time')}**\n"
                    appt_text += f"Doctor: {appt.get('doctor')}\n"
                    appt_text += f"Department: {appt.get('department')}\n"
                    appt_text += f"Reason: {appt.get('reason')}\n\n"
                
                return appt_text
            

            elif list_id == 'help':
                return self._get_help_message(session)
            

            else:
                return "Unrecognized selection. Please try again or type 'help' for assistance."
        except Exception as e:
            logger.error(f"Error handling list interaction: {str(e)}", exc_info=True)
            return "Sorry, I encountered an error processing your request. Please try again later."
    
    def _handle_logout(self, from_number: str) -> str:
        """
        Handle user logout.
        
        Args:
            from_number: The WhatsApp ID of the user
            
        Returns:
            Logout confirmation message
        """
        self.session_manager.logout_user(from_number)
        return "🔒 You have been logged out. Type 'patient' or 'staff' to login again."
    
    def _get_help_message(self, session: UserSession) -> str:
        """
        Get help message based on user's current state.
        
        Args:
            session: The user's session
            
        Returns:
            Contextual help message
        """
        if not session.is_authenticated:
            return self._handle_user_type_selection(session.whatsapp_id, 'help')
        elif session.user_type == 'patient':
            return self._handle_patient_commands(session.whatsapp_id, 'help')
        elif session.user_type == 'staff':
            return self._handle_staff_commands(session.whatsapp_id, 'help')
        return "Type 'patient' or 'staff' to get started, or 'logout' to end your session."