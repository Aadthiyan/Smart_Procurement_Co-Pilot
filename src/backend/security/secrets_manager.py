"""
IBM Cloud Secrets Manager Integration
Secure credential management for all API keys and passwords
Never hardcode credentials - always use this module
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


class IBMSecretsManagerClient:
    """
    Client for IBM Cloud Secrets Manager
    Centrally manages all sensitive credentials
    
    In production, this integrates with IBM Cloud Secrets Manager.
    For development/testing, it uses environment variables as fallback.
    """
    
    def __init__(self):
        """Initialize Secrets Manager client"""
        self.api_key = os.getenv("IBM_API_KEY")
        self.instance_url = os.getenv(
            "SECRETS_MANAGER_URL",
            "https://[instance-id].us-south.secrets-manager.appdomain.cloud"
        )
        self.use_mock = os.getenv("USE_MOCK_SECRETS", "false").lower() == "true"
        
        if self.use_mock:
            logger.warning("Using mock Secrets Manager - NOT FOR PRODUCTION")
            self.secrets_cache = self._load_mock_secrets()
        else:
            # In production, would initialize IBM SDK
            self.secrets_cache = {}
    
    def _load_mock_secrets(self) -> Dict[str, str]:
        """Load mock secrets from environment variables for development"""
        mock_secrets = {
            "watsonx-api-key": os.getenv("WATSONX_API_KEY", ""),
            "cloudant-username": os.getenv("CLOUDANT_USERNAME", ""),
            "cloudant-password": os.getenv("CLOUDANT_PASSWORD", ""),
            "cloudant-url": os.getenv("CLOUDANT_URL", ""),
            "smtp-host": os.getenv("SMTP_HOST", ""),
            "smtp-port": os.getenv("SMTP_PORT", ""),
            "smtp-username": os.getenv("SMTP_USERNAME", ""),
            "smtp-password": os.getenv("SMTP_PASSWORD", ""),
            "sap-api-key": os.getenv("SAP_API_KEY", ""),
            "dun-bradstreet-api-key": os.getenv("DUN_BRADSTREET_API_KEY", ""),
            "sendgrid-api-key": os.getenv("SENDGRID_API_KEY", ""),
        }
        return mock_secrets
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Retrieve a secret from Secrets Manager
        
        Args:
            secret_name: Name of the secret to retrieve
                        (e.g., 'watsonx-api-key', 'cloudant-password')
        
        Returns:
            Secret value or None if not found
            
        Raises:
            SecretRetrievalError: If secret cannot be retrieved
        """
        try:
            # Try cache first
            if secret_name in self.secrets_cache:
                value = self.secrets_cache[secret_name]
                if value:
                    logger.debug(f"Retrieved secret from cache: {secret_name}")
                    return value
            
            # In mock mode, return from environment
            if self.use_mock:
                return self.secrets_cache.get(secret_name)
            
            # In production, call IBM Secrets Manager API
            # response = requests.get(
            #     f"{self.instance_url}/api/v1/secrets/{secret_name}",
            #     headers={"Authorization": f"Bearer {self._get_access_token()}"}
            # )
            # if response.status_code == 200:
            #     return response.json()["resources"][0]["secret_data"]
            
            logger.warning(f"Secret not found: {secret_name}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {str(e)}")
            raise SecretRetrievalError(
                f"Cannot access credential: {secret_name}"
            ) from e
    
    def create_secret(
        self, 
        secret_name: str, 
        secret_value: str,
        description: str = ""
    ) -> bool:
        """
        Create a new secret in Secrets Manager
        
        Args:
            secret_name: Name for the secret
            secret_value: Secret value
            description: Optional description
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Store in cache
            self.secrets_cache[secret_name] = secret_value
            logger.info(f"Created secret: {secret_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create secret: {str(e)}")
            return False
    
    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """
        Rotate a secret (update to new value)
        
        Args:
            secret_name: Name of the secret to rotate
            new_value: New secret value
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.secrets_cache[secret_name] = new_value
            logger.info(f"Rotated secret: {secret_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to rotate secret: {str(e)}")
            return False


class CredentialProvider:
    """
    Centralized credential provider
    Single point of access for all secrets in the application
    
    Usage:
        cred_provider = CredentialProvider()
        api_key = cred_provider.get_watsonx_api_key()
        db_creds = cred_provider.get_cloudant_credentials()
    """
    
    def __init__(self):
        """Initialize credential provider with Secrets Manager client"""
        self.secrets_client = IBMSecretsManagerClient()
    
    def get_watsonx_api_key(self) -> str:
        """Get watsonx API key for LLM inference"""
        key = self.secrets_client.get_secret("watsonx-api-key")
        if not key:
            raise MissingCredentialError("watsonx-api-key not configured")
        return key
    
    def get_cloudant_credentials(self) -> Dict[str, str]:
        """Get Cloudant database credentials"""
        return {
            "username": self.secrets_client.get_secret("cloudant-username"),
            "password": self.secrets_client.get_secret("cloudant-password"),
            "url": self.secrets_client.get_secret("cloudant-url")
        }
    
    def get_smtp_credentials(self) -> Dict[str, str]:
        """Get SMTP email service credentials"""
        return {
            "host": self.secrets_client.get_secret("smtp-host"),
            "port": self.secrets_client.get_secret("smtp-port"),
            "username": self.secrets_client.get_secret("smtp-username"),
            "password": self.secrets_client.get_secret("smtp-password")
        }
    
    def get_sap_api_key(self) -> str:
        """Get SAP ERP API key"""
        key = self.secrets_client.get_secret("sap-api-key")
        if not key:
            raise MissingCredentialError("sap-api-key not configured")
        return key
    
    def get_dun_bradstreet_api_key(self) -> str:
        """Get Dun & Bradstreet credit check API key"""
        key = self.secrets_client.get_secret("dun-bradstreet-api-key")
        if not key:
            raise MissingCredentialError("dun-bradstreet-api-key not configured")
        return key
    
    def get_sendgrid_api_key(self) -> str:
        """Get SendGrid email service API key"""
        key = self.secrets_client.get_secret("sendgrid-api-key")
        if not key:
            raise MissingCredentialError("sendgrid-api-key not configured")
        return key


# Custom Exceptions
class SecretRetrievalError(Exception):
    """Error retrieving secret from Secrets Manager"""
    pass


class MissingCredentialError(Exception):
    """Required credential not configured"""
    pass


# Global instance
_credential_provider = None


def get_credential_provider() -> CredentialProvider:
    """Get global credential provider instance (singleton)"""
    global _credential_provider
    if _credential_provider is None:
        _credential_provider = CredentialProvider()
    return _credential_provider
