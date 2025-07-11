import os
import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger('env_validator')

class EnvValidator:
    """
    Utility class for validating environment variables.
    
    This class provides methods to check if required environment variables are set
    and have valid values, helping to prevent runtime errors due to missing configuration.
    """
    
    @staticmethod
    def validate_env_vars(required_vars: List[str], optional_vars: Optional[List[str]] = None) -> Dict[str, Union[str, None]]:
        """
        Validates that all required environment variables are set.
        
        Args:
            required_vars: List of required environment variable names
            optional_vars: List of optional environment variable names
            
        Returns:
            Dict containing all environment variables (both required and optional) and their values
            
        Raises:
            ValueError: If any required environment variable is missing
        """
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        env_vars = {var: os.environ.get(var) for var in required_vars}
        
        if optional_vars:
            for var in optional_vars:
                env_vars[var] = os.environ.get(var)
        
        return env_vars
    
    @staticmethod
    def validate_whatsapp_env_vars() -> Dict[str, str]:
        """
        Validates WhatsApp API specific environment variables.
        
        Returns:
            Dict containing WhatsApp API environment variables and their values
            
        Raises:
            ValueError: If any required WhatsApp API environment variable is missing
        """
        required_vars = [
            'WHATSAPP_ACCESS_TOKEN',
            'WHATSAPP_PHONE_NUMBER_ID',
            'WHATSAPP_WEBHOOK_VERIFY_TOKEN'
        ]
        
        return EnvValidator.validate_env_vars(required_vars)
    
    @staticmethod
    def validate_care_api_env_vars() -> Dict[str, str]:
        """
        Validates CARE API specific environment variables.
        
        Returns:
            Dict containing CARE API environment variables and their values
            
        Raises:
            ValueError: If any required CARE API environment variable is missing
        """
        required_vars = [
            'CARE_API_BASE_URL',
            'CARE_API_KEY'
        ]
        
        return EnvValidator.validate_env_vars(required_vars)
    
    @staticmethod
    def validate_all_env_vars() -> Dict[str, Dict[str, str]]:
        """
        Validates all required environment variables for the application.
        
        Returns:
            Dict containing all environment variables grouped by category
            
        Raises:
            ValueError: If any required environment variable is missing
        """
        django_vars = EnvValidator.validate_env_vars(
            required_vars=['SECRET_KEY', 'DEBUG'],
            optional_vars=['ALLOWED_HOSTS']
        )
        
        whatsapp_vars = EnvValidator.validate_whatsapp_env_vars()
        care_api_vars = EnvValidator.validate_care_api_env_vars()
        
        return {
            'django': django_vars,
            'whatsapp': whatsapp_vars,
            'care_api': care_api_vars
        }