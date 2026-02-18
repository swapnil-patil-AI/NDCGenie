"""
Enhanced Data Models for NDC Genie
Real-world airline industry data structures for enterprise scenarios.

Version: 2.0.0
"""

import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS FOR STANDARDIZED VALUES
# ═══════════════════════════════════════════════════════════════════════════════

class BookingChannel(Enum):
    """How the booking was made"""
    DIRECT_WEB = "Direct - Website"
    DIRECT_APP = "Direct - Mobile App"
    DIRECT_CALL = "Direct - Call Center"
    OTA_EXPEDIA = "OTA - Expedia"
    OTA_BOOKING = "OTA - Booking.com"
    OTA_KAYAK = "OTA - Kayak"
    OTA_SKYSCANNER = "OTA - Skyscanner"
    TRAVEL_AGENT = "Travel Agent"
    CORPORATE_PORTAL = "Corporate Portal"
    NDC_API = "NDC API"
    GDS_AMADEUS = "GDS - Amadeus"
    GDS_SABRE = "GDS - Sabre"
    GDS_TRAVELPORT = "GDS - Travelport"


class FlightStatus(Enum):
    """Real-time flight operational status"""
    SCHEDULED = "Scheduled"
    ON_TIME = "On Time"
    DELAYED = "Delayed"
    BOARDING = "Boarding"
    DEPARTED = "Departed"
    IN_FLIGHT = "In Flight"
    LANDED = "Landed"
    ARRIVED = "Arrived"
    CANCELLED = "Cancelled"
    DIVERTED = "Diverted"


class DisruptionType(Enum):
    """Types of flight disruptions (IROP)"""
    WEATHER = "Weather"
    MECHANICAL = "Mechanical Issue"
    CREW = "Crew Availability"
    AIR_TRAFFIC = "Air Traffic Control"
    SECURITY = "Security"
    MEDICAL = "Medical Emergency"
    STRIKE = "Industrial Action"
    VOLCANO = "Volcanic Activity"
    BIRD_STRIKE = "Bird Strike"
    LATE_AIRCRAFT = "Late Inbound Aircraft"


class BaggageStatus(Enum):
    """Baggage tracking status"""
    CHECKED_IN = "Checked In"
    SECURITY_SCREENED = "Security Screened"
    LOADED = "Loaded on Aircraft"
    IN_TRANSIT = "In Transit"
    TRANSFER = "Transfer Point"
    ARRIVED = "Arrived"
    ON_CAROUSEL = "On Carousel"
    COLLECTED = "Collected"
    DELAYED = "Delayed"
    MISHANDLED = "Mishandled"
    LOST = "Lost"
    FOUND = "Found"
    DELIVERED = "Delivered"


class CompensationType(Enum):
    """Regulatory compensation types"""
    EU261_DELAY = "EU261 - Delay Compensation"
    EU261_CANCEL = "EU261 - Cancellation Compensation"
    EU261_DENIED = "EU261 - Denied Boarding"
    DOT_DELAY = "DOT - Tarmac Delay"
    DOT_BUMPING = "DOT - Involuntary Bumping"
    MCAA_APPR = "Canada APPR Compensation"
    GOODWILL = "Goodwill Gesture"
    MILES_COMPENSATION = "Miles/Points Compensation"
    VOUCHER = "Travel Voucher"


class FraudRiskLevel(Enum):
    """Fraud detection risk levels"""
    LOW = "Low Risk"
    MEDIUM = "Medium Risk"
    HIGH = "High Risk"
    BLOCKED = "Blocked - Manual Review"


# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PNRRecord:
    """
    Passenger Name Record - The core airline booking identifier.
    This is the primary reference used across all airline systems.
    """
    pnr: str  # 6-character alphanumeric (e.g., "ABC123")
    record_locator: str  # Airline-specific reference
    gds_locator: Optional[str]  # GDS reference if booked via GDS
    created_at: str
    last_modified: str
    booking_channel: str
    booking_agent_id: Optional[str]
    agency_iata: Optional[str]  # Travel agency IATA code
    office_id: Optional[str]  # PCC/Office ID
    ticketing_deadline: str
    ticket_status: str  # "Ticketed", "On Hold", "Cancelled"
    is_group_booking: bool
    group_name: Optional[str]
    
    
@dataclass
class ETicket:
    """
    Electronic Ticket - The actual travel document.
    13-digit number: 3-digit airline code + 10-digit serial
    """
    ticket_number: str  # e.g., "016-1234567890"
    airline_code: str  # 3-digit IATA numeric code
    issue_date: str
    issuing_agent: str
    original_issue: bool  # False if reissued
    conjunction_tickets: List[str]  # For multi-ticket bookings
    fare_calculation: str  # Linear fare calculation
    endorsements: str  # Ticket restrictions
    tour_code: Optional[str]
    ticket_status: str  # "Open", "Used", "Void", "Refunded", "Exchanged"
    coupons: List[Dict[str, Any]]  # Flight coupons with status


@dataclass
class FlightSegment:
    """
    Individual flight segment within an itinerary.
    Supports multi-leg journeys with connections.
    """
    segment_id: str
    sequence_number: int
    flight_number: str
    marketing_carrier: str  # Selling airline
    operating_carrier: str  # Actual flying airline
    codeshare: bool
    origin: str  # IATA airport code
    destination: str  # IATA airport code
    departure_datetime: str
    arrival_datetime: str
    duration_minutes: int
    connection_time_minutes: Optional[int]  # Time to next segment
    aircraft_type: str
    aircraft_registration: Optional[str]
    cabin_class: str
    booking_class: str  # Fare class letter
    fare_basis: str  # Full fare basis code
    ticket_designator: Optional[str]
    status: str  # "Confirmed", "Waitlisted", "Cancelled"
    seat_assignment: Optional[str]
    meal_code: str
    
    # Real-time operational data
    flight_status: str
    actual_departure: Optional[str]
    actual_arrival: Optional[str]
    delay_minutes: int
    delay_reason: Optional[str]
    gate: Optional[str]
    terminal: Optional[str]


@dataclass
class Itinerary:
    """
    Complete travel itinerary with multiple segments.
    Represents the full journey (outbound + return).
    """
    itinerary_id: str
    trip_type: str  # "One-Way", "Round-Trip", "Multi-City", "Open-Jaw"
    segments: List[FlightSegment]
    total_duration_minutes: int
    total_stops: int
    layover_airports: List[str]
    is_international: bool
    requires_visa: bool
    transit_visa_required: List[str]  # Countries requiring transit visa


@dataclass 
class BaggageRecord:
    """
    Baggage tracking with bag tag details.
    Critical for lost baggage handling.
    """
    bag_tag_number: str  # 10-digit license plate number
    pnr: str
    passenger_name: str
    segment_from: str
    segment_to: str
    bag_type: str  # "Checked", "Cabin", "Special"
    weight_kg: float
    dimensions: str
    special_handling: List[str]  # "Fragile", "Heavy", "Oversized"
    status: str
    status_history: List[Dict[str, Any]]
    last_seen_location: str
    last_seen_time: str
    expected_carousel: Optional[str]
    claim_reference: Optional[str]  # If claim filed
    delivery_address: Optional[str]  # For delayed bag delivery


@dataclass
class FlightDisruption:
    """
    Flight disruption/IROP (Irregular Operations) record.
    Tracks delays, cancellations, and recovery actions.
    """
    disruption_id: str
    flight_number: str
    original_date: str
    disruption_type: str
    disruption_cause: str
    delay_minutes: int
    is_cancelled: bool
    is_diverted: bool
    diversion_airport: Optional[str]
    
    # Impact assessment
    affected_passengers: int
    connecting_pax_affected: int
    misconnections: int
    
    # Recovery actions
    recovery_flight: Optional[str]
    rebooked_passengers: int
    hotel_provided: bool
    meal_voucher_provided: bool
    transportation_provided: bool
    
    # Compensation
    compensation_eligible: bool
    compensation_type: Optional[str]
    compensation_amount: Optional[float]
    compensation_status: str  # "Pending", "Approved", "Paid", "Denied"


@dataclass
class Compensation:
    """
    Compensation record for regulatory compliance.
    Covers EU261, DOT, Canada APPR, etc.
    """
    compensation_id: str
    pnr: str
    regulation: str  # "EU261", "DOT", "APPR", "Goodwill"
    reason: str
    flight_number: str
    flight_date: str
    
    # Eligibility
    delay_minutes: int
    distance_km: int
    is_eligible: bool
    eligibility_reason: str
    
    # Amounts
    entitled_amount: float
    offered_amount: float
    accepted_amount: Optional[float]
    currency: str
    
    # Alternatives offered
    alternative_flight_offered: bool
    voucher_offered: bool
    voucher_amount: Optional[float]
    miles_offered: int
    
    # Status
    claim_status: str  # "Pending", "Under Review", "Approved", "Paid", "Denied", "Appealed"
    claim_submitted: str
    claim_resolved: Optional[str]
    payment_method: Optional[str]
    payment_reference: Optional[str]


@dataclass
class FraudAssessment:
    """
    Fraud detection and risk assessment.
    Critical for payment security.
    """
    assessment_id: str
    transaction_id: str
    timestamp: str
    
    # Risk scoring
    risk_score: int  # 0-100
    risk_level: str
    
    # Risk factors detected
    risk_factors: List[Dict[str, Any]]
    # Examples:
    # - IP geolocation mismatch
    # - Multiple failed attempts
    # - High-risk destination
    # - Velocity check failed
    # - Device fingerprint mismatch
    # - BIN country mismatch
    
    # Recommendations
    recommended_action: str  # "Approve", "3DS Required", "Manual Review", "Decline"
    auto_decision: bool
    manual_review_required: bool
    reviewer_id: Optional[str]
    review_outcome: Optional[str]
    review_notes: Optional[str]
    
    # Chargeback risk
    chargeback_probability: float
    previous_chargebacks: int


@dataclass
class CorporateBooking:
    """
    Corporate/Business travel booking details.
    Includes policy compliance and approval workflow.
    """
    corporate_id: str
    company_name: str
    company_account: str
    cost_center: str
    project_code: Optional[str]
    department: str
    
    # Traveler info
    employee_id: str
    employee_grade: str
    travel_policy_tier: str  # "Standard", "Executive", "VIP"
    
    # Policy compliance
    is_within_policy: bool
    policy_violations: List[str]
    requires_approval: bool
    approval_status: str  # "Pending", "Approved", "Rejected"
    approver_id: Optional[str]
    approved_at: Optional[str]
    
    # Budget
    trip_budget: float
    actual_cost: float
    savings_vs_policy: float
    
    # Billing
    billing_type: str  # "Centralized", "Lodge Card", "Ghost Card", "Personal Reimbursement"
    invoice_reference: Optional[str]
    payment_terms: str


@dataclass
class AncillaryService:
    """
    Ancillary services and extras purchased.
    Significant revenue stream for airlines.
    """
    service_id: str
    pnr: str
    segment_id: Optional[str]  # If segment-specific
    service_type: str
    service_code: str  # IATA ancillary code (e.g., "0B5" for prepaid bags)
    description: str
    quantity: int
    unit_price: float
    total_price: float
    currency: str
    status: str  # "Confirmed", "Pending", "Cancelled", "Used"
    
    # Common ancillary types:
    # - Checked baggage
    # - Seat selection
    # - Priority boarding
    # - Lounge access
    # - In-flight WiFi
    # - Meals/beverages
    # - Fast track security
    # - Travel insurance
    # - Car rental
    # - Hotel booking


@dataclass
class FareRules:
    """
    Fare rules governing ticket changes and refunds.
    Critical for customer service operations.
    """
    fare_basis: str
    rule_category: str
    
    # Change rules
    changes_permitted: bool
    change_fee: float
    change_fee_waived_for: List[str]  # "Elite", "Disruption", etc.
    same_day_change_fee: float
    
    # Cancellation rules
    cancellation_permitted: bool
    cancellation_fee: float
    refund_type: str  # "Full", "Partial", "Credit Only", "Non-Refundable"
    refund_validity_days: int
    
    # Rebooking rules
    rebook_required_within_days: int
    rebook_same_airline_only: bool
    fare_difference_applies: bool
    
    # Validity
    ticket_validity_days: int
    min_stay_days: Optional[int]
    max_stay_days: Optional[int]
    advance_purchase_days: int
    
    # Blackout dates
    blackout_dates: List[str]
    peak_season_surcharge: float


@dataclass
class CustomerSatisfaction:
    """
    Customer satisfaction and feedback tracking.
    Includes NPS and CSAT scores.
    """
    survey_id: str
    pnr: str
    customer_id: str
    survey_type: str  # "Post-Flight", "Post-Service", "Annual"
    submitted_at: str
    
    # Scores
    nps_score: int  # -100 to 100 (Promoter/Passive/Detractor)
    csat_score: float  # 1-5
    effort_score: float  # Customer Effort Score
    
    # Category ratings
    booking_experience: int
    check_in_experience: int
    boarding_experience: int
    cabin_crew: int
    seat_comfort: int
    food_beverage: int
    entertainment: int
    arrival_experience: int
    value_for_money: int
    
    # Verbatim feedback
    positive_feedback: str
    negative_feedback: str
    suggestions: str
    
    # Follow-up
    requires_followup: bool
    followup_status: str
    followup_notes: Optional[str]


# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED TRANSACTION WITH ALL RELATED DATA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EnhancedTransaction:
    """
    Complete transaction with all real-world data points.
    This is the master record linking all related entities.
    """
    # Core identifiers
    transaction_id: str
    pnr: str
    booking_reference: str
    
    # Booking details
    booking_channel: str
    booking_source: str
    booking_datetime: str
    ticketing_datetime: Optional[str]
    
    # Linked records
    pnr_record: PNRRecord
    e_tickets: List[ETicket]
    itinerary: Itinerary
    passengers: List[Dict[str, Any]]
    pricing: Dict[str, Any]
    payment: Dict[str, Any]
    
    # Ancillaries
    ancillary_services: List[AncillaryService]
    baggage_records: List[BaggageRecord]
    
    # Corporate (if applicable)
    corporate_booking: Optional[CorporateBooking]
    
    # Risk & Compliance
    fraud_assessment: FraudAssessment
    fare_rules: FareRules
    
    # Disruptions & Compensation
    disruptions: List[FlightDisruption]
    compensations: List[Compensation]
    
    # Customer data
    customer_satisfaction: Optional[CustomerSatisfaction]
    
    # Status & Lifecycle
    transaction_status: str
    lifecycle_stages: List[Dict[str, Any]]
    
    # Agent interactions
    agent_notes: List[Dict[str, Any]]
    communication_logs: List[Dict[str, Any]]
    
    # Timestamps
    created_at: str
    updated_at: str
    
    # Flags
    is_priority: bool
    requires_attention: bool
    sla_status: str
    escalation_level: Optional[str]
