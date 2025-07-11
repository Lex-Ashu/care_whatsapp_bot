import logging
import requests
import json
from typing import Dict, Any, Optional, List, Union
from django.conf import settings

logger = logging.getLogger('care_api')

class CAREAPIClient:
    """
    Client for interacting with the CARE (Coronasafe Resource Management) API.
    
    This client handles all communication with the CARE system, including:
    - User authentication (patients and staff)
    - Retrieving patient medical records
    - Retrieving medication information
    - Retrieving procedure history
    - Retrieving appointment information
    - Staff operations (patient search, notifications, etc.)
    """
    
    def __init__(self):
        """
        Initialize the CARE API client with configuration from settings.
        """
        self.base_url = settings.CARE_API_SETTINGS['BASE_URL']
        self.api_key = settings.CARE_API_SETTINGS['API_KEY']
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                     params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the CARE API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data (for POST/PUT)
            params: Query parameters (for GET)
            headers: Additional headers
            
        Returns:
            Response data as dictionary
            
        Raises:
            Exception: If the API request fails
        """
        url = f"{self.base_url}/{endpoint}"
        request_headers = self.headers.copy()
        
        if headers:
            request_headers.update(headers)
        
        try:
            response = None
            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=request_headers, json=data, params=params)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=request_headers, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=request_headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Return JSON response if content exists, otherwise empty dict
            if response.text:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CARE API request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Response content: {e.response.text}")

            raise
    

    
    def authenticate_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Authenticate a patient with the CARE system.
        
        Args:
            patient_id: Patient ID or registered phone number
            
        Returns:
            Patient information and authentication status
            
        Raises:
            Exception: If authentication fails
        """
        try:

            auth_response = self._make_request('POST', 'api/v1/auth/login/', {
                'username': patient_id,
                'password': None,  # For patient authentication, we might use OTP or other methods
                'user_type': 'patient'
            })
            

            token = auth_response.get('access', '')
            refresh_token = auth_response.get('refresh', '')
            
            if not token:
                logger.error(f"Failed to get authentication token for patient: {patient_id}")
                return {'authenticated': False}
            

            patient_headers = {**self.headers, 'Authorization': f'Bearer {token}'}
            patient_response = self._make_request(
                'POST', 
                'api/v1/patient/search_retrieve/', 
                {'identifier': patient_id},
                headers=patient_headers
            )
            
            # Return patient information with authentication status
            return {
                'authenticated': True,
                'patient_id': patient_response.get('external_id', patient_id),
                'name': patient_response.get('name', 'Unknown'),
                'phone': patient_response.get('phone_number', ''),
                'email': patient_response.get('email', ''),
                'token': token,
                'refresh_token': refresh_token
            }
        except Exception as e:
            logger.error(f"Patient authentication failed: {str(e)}")
            return {'authenticated': False, 'error': str(e)}
    
    def authenticate_staff(self, staff_id: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a staff member with the CARE system.
        
        Args:
            staff_id: Staff ID or username
            password: Staff password
            
        Returns:
            Staff information and authentication status
            
        Raises:
            Exception: If authentication fails
        """
        try:
            # Call the login endpoint to get a JWT token
            auth_response = self._make_request('POST', 'api/v1/auth/login/', {
                'username': staff_id,
                'password': password,
                'user_type': 'staff'
            })
            

            token = auth_response.get('access', '')
            refresh_token = auth_response.get('refresh', '')
            
            if not token:
                logger.error(f"Failed to get authentication token for staff: {staff_id}")
                return {'authenticated': False}
            

            staff_headers = {**self.headers, 'Authorization': f'Bearer {token}'}
            staff_response = self._make_request(
                'GET', 
                'api/v1/staff/me/', 
                headers=staff_headers
            )
            
            # Return staff information with authentication status
            return {
                'authenticated': True,
                'staff_id': staff_response.get('username', staff_id),
                'name': staff_response.get('name', 'Unknown'),
                'role': staff_response.get('role', ''),
                'department': staff_response.get('department', ''),
                'token': token,
                'refresh_token': refresh_token
            }
        except Exception as e:
            logger.error(f"Staff authentication failed: {str(e)}")
            return {'authenticated': False, 'error': str(e)}
    
    # Patient data methods
    
    def get_patient_records(self, patient_id: str, token: str = None) -> Dict[str, Any]:
        """
        Get patient medical records from the CARE system.
        
        Args:
            patient_id: Patient ID or external ID
            token: Authentication token (optional)
            
        Returns:
            Patient medical records
            
        Raises:
            Exception: If retrieval fails
        """
        try:

            headers = self.headers
            if token:
                headers = {**headers, 'Authorization': f'Bearer {token}'}
            


            records_response = self._make_request(
                'GET',
                f'api/v1/patient/{patient_id}/records/',
                headers=headers
            )
            

            formatted_records = []
            for record in records_response.get('results', []):
                formatted_records.append({
                    'id': record.get('id', ''),
                    'date': record.get('date', ''),
                    'doctor': record.get('doctor_name', ''),
                    'diagnosis': record.get('diagnosis', ''),
                    'notes': record.get('notes', '')
                })
            
            return {
                'patient_id': patient_id,
                'records': formatted_records
            }
        except Exception as e:
            logger.error(f"Failed to get patient records: {str(e)}")
            return {'error': str(e), 'records': []}
    
    def get_patient_medications(self, patient_id: str, token: str = None) -> List[Dict[str, Any]]:
        """
        Get current medications for a patient.
        
        Args:
            patient_id: Patient ID or external ID
            token: Authentication token (optional)
            
        Returns:
            List of medications
        """
        try:

            headers = self.headers
            if token:
                headers = {**headers, 'Authorization': f'Bearer {token}'}
            

            medications_response = self._make_request(
                'GET',
                f'api/v1/patient/{patient_id}/medication/',
                headers=headers
            )
            

            formatted_medications = []
            for med in medications_response.get('results', []):
                formatted_medications.append({
                    'id': med.get('id', ''),
                    'name': med.get('name', ''),
                    'dosage': med.get('dosage', ''),
                    'frequency': med.get('frequency', ''),
                    'start_date': med.get('start_date', ''),
                    'end_date': med.get('end_date', ''),
                    'prescriber': med.get('prescriber_name', '')
                })
            
            return formatted_medications
        except Exception as e:
            logger.error(f"Failed to get patient medications: {str(e)}")
            return []
    
    def get_patient_procedures(self, patient_id: str, token: str = None) -> List[Dict[str, Any]]:
        """
        Get procedures for a patient.
        
        Args:
            patient_id: Patient ID or external ID
            token: Authentication token (optional)
            
        Returns:
            List of procedures
        """
        try:

            headers = self.headers
            if token:
                headers = {**headers, 'Authorization': f'Bearer {token}'}
            

            procedures_response = self._make_request(
                'GET',
                f'api/v1/patient/{patient_id}/procedure/',
                headers=headers
            )
            

            formatted_procedures = []
            for proc in procedures_response.get('results', []):
                formatted_procedures.append({
                    'id': proc.get('id', ''),
                    'name': proc.get('name', ''),
                    'date': proc.get('scheduled_date', ''),
                    'status': proc.get('status', ''),
                    'provider': proc.get('provider_name', ''),
                    'location': proc.get('location', ''),
                    'notes': proc.get('notes', '')
                })
            
            return formatted_procedures
        except Exception as e:
            logger.error(f"Failed to get patient procedures: {str(e)}")
            return []
    
    def get_patient_appointments(self, patient_id: str, token: str = None) -> List[Dict[str, Any]]:
        """
        Get appointments for a patient.
        
        Args:
            patient_id: Patient ID or external ID
            token: Authentication token (optional)
            
        Returns:
            List of appointments
        """
        try:

            headers = self.headers
            if token:
                headers = {**headers, 'Authorization': f'Bearer {token}'}
            

            appointments_response = self._make_request(
                'GET',
                f'api/v1/patient/{patient_id}/get_appointments/',
                headers=headers
            )
            

            formatted_appointments = []
            for appt in appointments_response.get('results', []):
                formatted_appointments.append({
                    'id': appt.get('id', ''),
                    'date': appt.get('date', ''),
                    'time': appt.get('time', ''),
                    'doctor': appt.get('doctor_name', ''),
                    'department': appt.get('department', ''),
                    'status': appt.get('status', ''),
                    'location': appt.get('location', ''),
                    'notes': appt.get('notes', '')
                })
            
            return formatted_appointments
        except Exception as e:
            logger.error(f"Failed to get patient appointments: {str(e)}")
            return []
    

    
    def search_patient(self, query: str, token: str = None) -> List[Dict[str, Any]]:
        """
        Search for patients by name, ID, or phone number.
        
        Args:
            query: Search query
            token: Authentication token (optional)
            
        Returns:
            List of matching patients
        """
        try:

            headers = self.headers
            if token:
                headers = {**headers, 'Authorization': f'Bearer {token}'}
            

            search_response = self._make_request(
                'POST',
                'api/v1/patient/search/',
                {'search_query': query},
                headers=headers
            )
            

            formatted_patients = []
            for patient in search_response.get('results', []):
                formatted_patients.append({
                    'id': patient.get('external_id', ''),
                    'name': patient.get('name', ''),
                    'phone': patient.get('phone_number', ''),
                    'email': patient.get('email', ''),
                    'address': patient.get('address', ''),
                    'date_of_birth': patient.get('date_of_birth', '')
                })
            
            return formatted_patients
        except Exception as e:
            logger.error(f"Failed to search patients: {str(e)}")
            return []
    
    def send_patient_notification(self, patient_id: str, message: str, token: str = None) -> Dict[str, Any]:
        """
        Send a notification to a patient.
        
        Args:
            patient_id: Patient ID or external ID
            message: Notification message
            token: Authentication token (optional)
            
        Returns:
            Notification status
        """
        try:

            headers = self.headers
            if token:
                headers = {**headers, 'Authorization': f'Bearer {token}'}
            

            notification_response = self._make_request(
                'POST',
                f'api/v1/patient/{patient_id}/notification/',
                {
                    'message': message,
                    'type': 'message',
                    'priority': 'normal'
                },
                headers=headers
            )
            
            return {
                'success': True,
                'message': 'Notification sent successfully',
                'timestamp': datetime.now().isoformat(),
                'notification_id': notification_response.get('id', str(uuid.uuid4()))
            }
        except Exception as e:
            logger.error(f"Failed to send patient notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_recent_patients(self, token: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get a list of recently seen patients.
        
        Args:
            token: Authentication token (optional)
            limit: Maximum number of patients to return
            
        Returns:
            List of recent patients
        """
        try:

            headers = self.headers
            if token:
                headers = {**headers, 'Authorization': f'Bearer {token}'}
            

            patients_response = self._make_request(
                'GET',
                'api/v1/patient/recent/',
                params={'limit': limit},
                headers=headers
            )
            

            formatted_patients = []
            for patient in patients_response.get('results', []):
                formatted_patients.append({
                    'patient_id': patient.get('external_id', ''),
                    'name': patient.get('name', ''),
                    'last_visit': patient.get('last_visit_date', ''),
                    'reason': patient.get('last_visit_reason', ''),
                    'phone': patient.get('phone_number', ''),
                    'email': patient.get('email', '')
                })
            
            return formatted_patients[:limit]
        except Exception as e:
            logger.error(f"Failed to get recent patients: {str(e)}")
            return []