"""
Data Validation Utilities for NDC Genie
Ensures data integrity and provides validation functions.
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __bool__(self):
        return self.is_valid


class TransactionValidator:
    """Validates transaction data structures"""
    
    # Required fields at each level
    REQUIRED_ROOT_FIELDS = [
        'transaction_id', 'customer', 'flight', 'pricing', 
        'lifecycle', 'status', 'priority', 'created_at'
    ]
    
    REQUIRED_CUSTOMER_FIELDS = [
        'customer_id', 'first_name', 'last_name', 'email'
    ]
    
    REQUIRED_FLIGHT_FIELDS = [
        'flight_number', 'origin', 'destination', 
        'departure_date', 'passengers'
    ]
    
    REQUIRED_PRICING_FIELDS = [
        'base_fare', 'total', 'currency'
    ]
    
    VALID_STATUSES = [
        'Completed', 'Failed', 'Refunded', 'Refund Pending',
        'Refund Rejected', 'Under Investigation', 'Abandoned',
        'Partially Completed'
    ]
    
    VALID_PRIORITIES = ['Critical', 'High', 'Medium', 'Low']
    
    VALID_CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SGD', 'AED']
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[\d\s-]{10,20}$')
    TRANSACTION_ID_PATTERN = re.compile(r'^TXN-\d{6}-[A-Z0-9]{10,}$')
    
    @classmethod
    def validate_transaction(cls, txn: Dict[str, Any]) -> ValidationResult:
        """Validate a complete transaction"""
        errors = []
        warnings = []
        
        # Check root fields
        for field in cls.REQUIRED_ROOT_FIELDS:
            if field not in txn:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return ValidationResult(False, errors, warnings)
        
        # Validate transaction ID format
        if not cls.TRANSACTION_ID_PATTERN.match(txn.get('transaction_id', '')):
            warnings.append(f"Transaction ID format may be non-standard: {txn.get('transaction_id')}")
        
        # Validate status
        if txn.get('status') not in cls.VALID_STATUSES:
            errors.append(f"Invalid status: {txn.get('status')}")
        
        # Validate priority
        if txn.get('priority') not in cls.VALID_PRIORITIES:
            errors.append(f"Invalid priority: {txn.get('priority')}")
        
        # Validate customer
        customer_result = cls.validate_customer(txn.get('customer', {}))
        errors.extend(customer_result.errors)
        warnings.extend(customer_result.warnings)
        
        # Validate flight
        flight_result = cls.validate_flight(txn.get('flight', {}))
        errors.extend(flight_result.errors)
        warnings.extend(flight_result.warnings)
        
        # Validate pricing
        pricing_result = cls.validate_pricing(txn.get('pricing', {}))
        errors.extend(pricing_result.errors)
        warnings.extend(pricing_result.warnings)
        
        # Validate lifecycle
        lifecycle_result = cls.validate_lifecycle(txn.get('lifecycle', {}))
        errors.extend(lifecycle_result.errors)
        warnings.extend(lifecycle_result.warnings)
        
        # Cross-validation checks
        if txn.get('status') == 'Failed' and not txn.get('error_info'):
            warnings.append("Failed transaction has no error_info")
        
        if txn.get('status') in ['Refunded', 'Refund Pending'] and not txn.get('refund_info'):
            warnings.append("Refund transaction has no refund_info")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @classmethod
    def validate_customer(cls, customer: Dict[str, Any]) -> ValidationResult:
        """Validate customer data"""
        errors = []
        warnings = []
        
        for field in cls.REQUIRED_CUSTOMER_FIELDS:
            if field not in customer:
                errors.append(f"Missing customer field: {field}")
        
        if errors:
            return ValidationResult(False, errors, warnings)
        
        # Validate email format
        email = customer.get('email', '')
        if email and not cls.EMAIL_PATTERN.match(email):
            warnings.append(f"Invalid email format: {email}")
        
        # Validate phone format
        phone = customer.get('phone', '')
        if phone and not cls.PHONE_PATTERN.match(phone):
            warnings.append(f"Phone format may be invalid: {phone}")
        
        # Validate loyalty tier
        valid_tiers = ['None', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond']
        if customer.get('loyalty_tier') and customer.get('loyalty_tier') not in valid_tiers:
            warnings.append(f"Unknown loyalty tier: {customer.get('loyalty_tier')}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @classmethod
    def validate_flight(cls, flight: Dict[str, Any]) -> ValidationResult:
        """Validate flight data"""
        errors = []
        warnings = []
        
        for field in cls.REQUIRED_FLIGHT_FIELDS:
            if field not in flight:
                errors.append(f"Missing flight field: {field}")
        
        if errors:
            return ValidationResult(False, errors, warnings)
        
        # Validate airport codes (3 letters)
        origin = flight.get('origin', '')
        destination = flight.get('destination', '')
        
        if len(origin) != 3 or not origin.isalpha():
            warnings.append(f"Origin airport code may be invalid: {origin}")
        
        if len(destination) != 3 or not destination.isalpha():
            warnings.append(f"Destination airport code may be invalid: {destination}")
        
        if origin == destination:
            errors.append("Origin and destination cannot be the same")
        
        # Validate passengers
        passengers = flight.get('passengers', 0)
        if not isinstance(passengers, int) or passengers < 1:
            errors.append("Passengers must be a positive integer")
        elif passengers > 9:
            warnings.append(f"Large passenger count: {passengers}")
        
        # Validate departure date
        try:
            dep_date = flight.get('departure_date', '')
            if dep_date:
                datetime.strptime(dep_date, '%Y-%m-%d')
        except ValueError:
            errors.append(f"Invalid departure date format: {dep_date}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @classmethod
    def validate_pricing(cls, pricing: Dict[str, Any]) -> ValidationResult:
        """Validate pricing data"""
        errors = []
        warnings = []
        
        for field in cls.REQUIRED_PRICING_FIELDS:
            if field not in pricing:
                errors.append(f"Missing pricing field: {field}")
        
        if errors:
            return ValidationResult(False, errors, warnings)
        
        # Validate numeric fields
        base_fare = pricing.get('base_fare', 0)
        total = pricing.get('total', 0)
        
        if not isinstance(base_fare, (int, float)) or base_fare < 0:
            errors.append("Base fare must be a non-negative number")
        
        if not isinstance(total, (int, float)) or total < 0:
            errors.append("Total must be a non-negative number")
        
        if total < base_fare:
            warnings.append("Total is less than base fare (discounts applied?)")
        
        # Validate currency
        currency = pricing.get('currency', '')
        if currency not in cls.VALID_CURRENCIES:
            warnings.append(f"Currency may be invalid: {currency}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @classmethod
    def validate_lifecycle(cls, lifecycle: Dict[str, Any]) -> ValidationResult:
        """Validate lifecycle data"""
        errors = []
        warnings = []
        
        required_stages = ['search', 'selection', 'booking', 'payment', 'ticketing']
        
        for stage in required_stages:
            if stage not in lifecycle:
                warnings.append(f"Missing lifecycle stage: {stage}")
        
        # Validate stage progression logic
        stage_order = ['search', 'selection', 'booking', 'payment', 'ticketing', 'confirmation']
        found_incomplete = False
        
        for stage in stage_order:
            stage_data = lifecycle.get(stage, {})
            if isinstance(stage_data, dict):
                status = stage_data.get('status', 'not_reached')
                
                if found_incomplete and status == 'completed':
                    warnings.append(f"Stage {stage} is completed but previous stage was incomplete")
                
                if status in ['failed', 'not_reached', 'pending']:
                    found_incomplete = True
        
        return ValidationResult(len(errors) == 0, errors, warnings)


class DataSanitizer:
    """Sanitizes input data for safety and consistency"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """Sanitize a string value"""
        if not isinstance(value, str):
            return str(value) if value is not None else ""
        
        # Remove null bytes and control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        # Truncate to max length
        if len(value) > max_length:
            value = value[:max_length] + "..."
        
        return value.strip()
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize and normalize email address"""
        if not email:
            return ""
        
        email = email.lower().strip()
        # Remove any characters that shouldn't be in an email
        email = re.sub(r'[<>"\']', '', email)
        return email
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Sanitize phone number"""
        if not phone:
            return ""
        
        # Keep only digits, +, -, and spaces
        phone = re.sub(r'[^\d+\-\s]', '', phone)
        return phone.strip()
    
    @staticmethod
    def sanitize_amount(amount: Any) -> float:
        """Sanitize monetary amount"""
        if isinstance(amount, (int, float)):
            return round(max(0, float(amount)), 2)
        
        if isinstance(amount, str):
            try:
                # Remove currency symbols and commas
                cleaned = re.sub(r'[,$€£¥]', '', amount)
                return round(max(0, float(cleaned)), 2)
            except ValueError:
                return 0.0
        
        return 0.0
    
    @classmethod
    def sanitize_transaction(cls, txn: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize an entire transaction record"""
        if not isinstance(txn, dict):
            return {}
        
        sanitized = txn.copy()
        
        # Sanitize customer data
        if 'customer' in sanitized and isinstance(sanitized['customer'], dict):
            customer = sanitized['customer']
            customer['first_name'] = cls.sanitize_string(customer.get('first_name', ''), 100)
            customer['last_name'] = cls.sanitize_string(customer.get('last_name', ''), 100)
            customer['email'] = cls.sanitize_email(customer.get('email', ''))
            customer['phone'] = cls.sanitize_phone(customer.get('phone', ''))
        
        # Sanitize pricing data
        if 'pricing' in sanitized and isinstance(sanitized['pricing'], dict):
            pricing = sanitized['pricing']
            for field in ['base_fare', 'taxes', 'total', 'discount_amount']:
                if field in pricing:
                    pricing[field] = cls.sanitize_amount(pricing[field])
        
        return sanitized


def validate_api_key_format(api_key: str) -> Tuple[bool, str]:
    """
    Validate Anthropic API key format
    Returns (is_valid, message)
    """
    if not api_key:
        return False, "API key is required"
    
    if not isinstance(api_key, str):
        return False, "API key must be a string"
    
    api_key = api_key.strip()
    
    if len(api_key) < 20:
        return False, "API key is too short"
    
    if not api_key.startswith('sk-ant-'):
        return False, "API key should start with 'sk-ant-'"
    
    # Check for invalid characters
    if not re.match(r'^sk-ant-[a-zA-Z0-9_-]+$', api_key):
        return False, "API key contains invalid characters"
    
    return True, "API key format is valid"


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string"""
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
        'CAD': 'C$', 'AUD': 'A$', 'CHF': 'CHF ', 'SGD': 'S$', 'AED': 'AED '
    }
    
    symbol = symbols.get(currency, f'{currency} ')
    
    if currency == 'JPY':
        return f"{symbol}{amount:,.0f}"
    
    return f"{symbol}{amount:,.2f}"


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable string"""
    if minutes < 60:
        return f"{minutes}m"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours}h"
    
    return f"{hours}h {mins}m"


def format_datetime(dt_str: str, format: str = "short") -> str:
    """Format datetime string for display"""
    if not dt_str:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        
        if format == "short":
            return dt.strftime("%Y-%m-%d %H:%M")
        elif format == "date":
            return dt.strftime("%Y-%m-%d")
        elif format == "time":
            return dt.strftime("%H:%M:%S")
        elif format == "full":
            return dt.strftime("%B %d, %Y at %I:%M %p")
        elif format == "relative":
            now = datetime.now()
            diff = now - dt.replace(tzinfo=None)
            
            if diff.days > 30:
                return dt.strftime("%Y-%m-%d")
            elif diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600} hours ago"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60} minutes ago"
            else:
                return "Just now"
        
        return dt.strftime("%Y-%m-%d %H:%M")
    
    except (ValueError, AttributeError):
        return dt_str[:19] if len(dt_str) > 19 else dt_str
