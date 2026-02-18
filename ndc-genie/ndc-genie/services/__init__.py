"""
NDC Genie Services
Real-time flight operations, compensation, fraud detection, and corporate travel.
"""

from services.flight_status import (
    get_simulator,
    simulate_daily_operations,
    FlightStatusSimulator,
    FlightStatusUpdate,
    Disruption
)

from services.compensation import (
    get_calculator,
    get_fraud_detector,
    calculate_eu261,
    assess_fraud,
    EU261Calculator,
    FraudDetector,
    CompensationResult,
    FraudAssessment
)

from services.corporate import (
    get_corporate_manager,
    create_corporate_booking,
    get_travel_analytics,
    CorporateTravelManager,
    CorporateBooking,
    TravelAnalytics
)

__all__ = [
    # Flight Status
    'get_simulator', 'simulate_daily_operations', 'FlightStatusSimulator',
    'FlightStatusUpdate', 'Disruption',
    # Compensation & Fraud
    'get_calculator', 'get_fraud_detector', 'calculate_eu261', 'assess_fraud',
    'EU261Calculator', 'FraudDetector', 'CompensationResult', 'FraudAssessment',
    # Corporate
    'get_corporate_manager', 'create_corporate_booking', 'get_travel_analytics',
    'CorporateTravelManager', 'CorporateBooking', 'TravelAnalytics'
]
