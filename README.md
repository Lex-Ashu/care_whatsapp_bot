# CARE WhatsApp Bot

## Overview
This WhatsApp bot integrates with the CARE (Coronasafe Resource Management) system to provide a conversational interface for patients and hospital staff. It enables users to access healthcare information and services through WhatsApp.

## Features
- **User Authentication**: Separate flows for patients and hospital staff
- **Patient Features**: Access to medical records, medicines, procedures, and appointments
- **Staff Features**: Patient search, notifications, and patient management
- **Session Management**: Maintains user context across conversations

## Setup Instructions

### Prerequisites
- Python 3.9+
- Django 4.2+
- WhatsApp Business API account
- Meta Developer account

### Installation
1. Clone the repository
   ```
   git clone <repository-url>
   cd care_whatsapp_bot
   ```

2. Create and activate a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables
   - Copy `.env.example` to `.env` (create if not exists)
   - Update the following variables:
     ```
     WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
     WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
     WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token
     CARE_API_BASE_URL=https://care.coronasafe.network/api/v1/
     CARE_API_KEY=your_care_api_key
     ```

5. Run migrations
   ```
   python manage.py migrate
   ```

6. Start the development server
   ```
   python manage.py runserver
   ```

### WhatsApp API Configuration

1. Create a Meta Developer account at [developers.facebook.com](https://developers.facebook.com/)
2. Set up a WhatsApp Business API application
3. Configure the webhook URL to point to your server:
   - For local development, use ngrok: `ngrok http 8000`
   - Webhook URL: `https://your-ngrok-url/whatsapp/webhook/`
   - Verify token: Use the same value as `WHATSAPP_WEBHOOK_VERIFY_TOKEN`

## Usage

### User Interaction Flow
1. Users send a message to the WhatsApp number
2. New users are prompted to identify as either a patient or staff member
3. Authentication is required based on user type
4. After authentication, users can access specific commands:
   - Patients: `records`, `medicines`, `procedures`, `appointments`, `help`, `logout`
   - Staff: `search`, `notify`, `patients`, `help`, `logout`

## Troubleshooting

### Common Issues

#### 401 Unauthorized Error
If you encounter a 401 error when sending messages:
1. Your WhatsApp API token may have expired
2. Generate a new token from the Meta Developer Portal
3. Update the token in your `.env` file and `settings.py`

#### Webhook Verification Failure
1. Ensure your webhook URL is publicly accessible
2. Verify that the token in your Meta Developer Portal matches `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
3. Check server logs for specific error messages

## Project Structure
- `whatsapp_bot/`: Core WhatsApp integration
  - `client.py`: WhatsApp API client
  - `views.py`: Webhook handling and message processing
- `bot_engine/`: Bot logic and session management
- `core/`: Data models and core functionality
- `care_wrapper/`: Integration with CARE API

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.