"""
Configuration settings for NDC Genie application.
Production-ready configuration with environment variable support.
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import timedelta
from enum import Enum


class TransactionStatus(Enum):
    """Transaction status enumeration"""
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"
    REFUND_PENDING = "Refund Pending"
    REFUND_REJECTED = "Refund Rejected"
    UNDER_INVESTIGATION = "Under Investigation"
    ABANDONED = "Abandoned"
    PARTIALLY_COMPLETED = "Partially Completed"


class Priority(Enum):
    """Priority level enumeration"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class LifecycleStageStatus(Enum):
    """Lifecycle stage status enumeration"""
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    NOT_REACHED = "not_reached"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class AppConfig:
    """Application configuration settings"""
    
    # Application Info
    APP_NAME: str = "NDC Genie"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Enterprise Airline Transaction Lifecycle Tracker"
    
    # API Configuration
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    MAX_TOKENS: int = 4096
    
    # Data Settings
    DEMO_TRANSACTION_COUNT: int = 200
    MAX_DISPLAY_TRANSACTIONS: int = 100
    PAGINATION_SIZE: int = 20
    
    # SLA Configuration (in hours)
    SLA_RESPONSE_TIME: int = 4
    SLA_RESOLUTION_TIME: int = 24
    SLA_REFUND_TIME: int = 72
    
    # Priority Levels
    PRIORITY_LEVELS: Dict[str, int] = field(default_factory=lambda: {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    })
    
    # Status Configurations
    TRANSACTION_STATUSES: List[str] = field(default_factory=lambda: [
        "Completed",
        "Failed", 
        "Refunded",
        "Refund Pending",
        "Refund Rejected",
        "Under Investigation",
        "Abandoned",
        "Partially Completed"
    ])
    
    LIFECYCLE_STAGES: List[str] = field(default_factory=lambda: [
        "search",
        "selection", 
        "booking",
        "payment",
        "ticketing",
        "confirmation",
        "refund"
    ])
    
    # Airlines Configuration
    AIRLINES: List[Dict] = field(default_factory=lambda: [
        {"code": "SW", "name": "SkyWings Airlines", "hub": "JFK"},
        {"code": "AG", "name": "AeroGlobal", "hub": "LAX"},
        {"code": "CJ", "name": "CloudJet Airways", "hub": "ORD"},
        {"code": "TA", "name": "TransAtlantic Air", "hub": "LHR"},
        {"code": "PV", "name": "Pacific Voyager", "hub": "SFO"},
        {"code": "SE", "name": "SunExpress", "hub": "MIA"},
        {"code": "NA", "name": "Northern Air", "hub": "SEA"},
        {"code": "EA", "name": "Emirates Atlantic", "hub": "DXB"}
    ])
    
    # Error Categories
    ERROR_CATEGORIES: Dict[str, List[str]] = field(default_factory=lambda: {
        "payment": [
            "Card declined - Insufficient funds",
            "Card declined - Expired card", 
            "Card declined - CVV mismatch",
            "Card declined - Invalid card number",
            "Payment gateway timeout",
            "3D Secure authentication failed",
            "Bank authorization declined",
            "Card flagged for fraud prevention",
            "Currency conversion error",
            "Payment processor unavailable",
            "Transaction limit exceeded",
            "Card issuer declined"
        ],
        "booking": [
            "Seat no longer available",
            "Flight sold out during booking",
            "Session timeout - booking expired",
            "System error during seat assignment",
            "Price changed during checkout",
            "Passenger details validation failed",
            "Duplicate booking detected",
            "Fare class unavailable",
            "Inventory sync error",
            "Special service request failed",
            "Meal preference unavailable"
        ],
        "ticketing": [
            "E-ticket generation failed",
            "Email delivery failed - Invalid address",
            "Email delivery failed - Mailbox full",
            "PNR creation error",
            "Ticketing system unavailable",
            "Document generation timeout",
            "GDS connection error",
            "Ticket number allocation failed"
        ],
        "system": [
            "Database connection timeout",
            "API rate limit exceeded",
            "Service temporarily unavailable",
            "Internal server error",
            "Cache synchronization failure"
        ]
    })
    
    # Refund Reasons
    REFUND_REASONS: List[str] = field(default_factory=lambda: [
        "Customer requested cancellation",
        "Flight cancelled by airline",
        "Schedule change - customer opted out",
        "Medical emergency",
        "Duplicate booking",
        "Price guarantee claim",
        "Service not as described",
        "Technical error during booking",
        "Visa/travel document issues",
        "Force majeure event",
        "Overbooking compensation",
        "Flight delay compensation"
    ])
    
    # Routes
    ROUTES: List[Dict] = field(default_factory=lambda: [
        {"origin": "JFK", "origin_city": "New York", "destination": "LAX", "destination_city": "Los Angeles", "distance": 2475},
        {"origin": "ORD", "origin_city": "Chicago", "destination": "MIA", "destination_city": "Miami", "distance": 1197},
        {"origin": "SFO", "origin_city": "San Francisco", "destination": "SEA", "destination_city": "Seattle", "distance": 679},
        {"origin": "DFW", "origin_city": "Dallas", "destination": "BOS", "destination_city": "Boston", "distance": 1551},
        {"origin": "ATL", "origin_city": "Atlanta", "destination": "DEN", "destination_city": "Denver", "distance": 1199},
        {"origin": "LHR", "origin_city": "London", "destination": "JFK", "destination_city": "New York", "distance": 3451},
        {"origin": "CDG", "origin_city": "Paris", "destination": "LAX", "destination_city": "Los Angeles", "distance": 5670},
        {"origin": "DXB", "origin_city": "Dubai", "destination": "SIN", "destination_city": "Singapore", "distance": 3657},
        {"origin": "SYD", "origin_city": "Sydney", "destination": "HKG", "destination_city": "Hong Kong", "distance": 4576},
        {"origin": "NRT", "origin_city": "Tokyo", "destination": "ICN", "destination_city": "Seoul", "distance": 758},
        {"origin": "FRA", "origin_city": "Frankfurt", "destination": "SFO", "destination_city": "San Francisco", "distance": 5685},
        {"origin": "AMS", "origin_city": "Amsterdam", "destination": "ORD", "destination_city": "Chicago", "distance": 4127}
    ])


@dataclass  
class UIConfig:
    """UI/Theme configuration"""
    
    # Color Palette
    PRIMARY_COLOR: str = "#1a365d"
    SECONDARY_COLOR: str = "#2b6cb0"
    ACCENT_COLOR: str = "#4299e1"
    SUCCESS_COLOR: str = "#38a169"
    WARNING_COLOR: str = "#d69e2e"
    DANGER_COLOR: str = "#e53e3e"
    INFO_COLOR: str = "#3182ce"
    
    # Status Colors
    STATUS_COLORS: Dict[str, str] = field(default_factory=lambda: {
        "Completed": "#38a169",
        "Failed": "#e53e3e",
        "Refunded": "#3182ce",
        "Refund Pending": "#d69e2e",
        "Refund Rejected": "#9b2c2c",
        "Under Investigation": "#805ad5",
        "Abandoned": "#718096",
        "Partially Completed": "#dd6b20"
    })
    
    # Priority Colors
    PRIORITY_COLORS: Dict[str, str] = field(default_factory=lambda: {
        "Critical": "#e53e3e",
        "High": "#dd6b20",
        "Medium": "#d69e2e",
        "Low": "#38a169"
    })


# Singleton instances
app_config = AppConfig()
ui_config = UIConfig()
