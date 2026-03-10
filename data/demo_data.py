"""
Demo Data Generator for NDC Genie
Generates realistic airline transaction data with complete lifecycle tracking.
"""

import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import json

from utils.config import app_config


@dataclass
class Customer:
    """Customer data model"""
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    loyalty_tier: str
    loyalty_points: int
    member_since: str
    preferred_language: str
    nationality: str
    passport_country: str
    total_bookings: int
    lifetime_value: float
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class Flight:
    """Flight data model"""
    flight_number: str
    airline_code: str
    airline_name: str
    origin: str
    origin_city: str
    destination: str
    destination_city: str
    departure_date: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    aircraft_type: str
    cabin_class: str
    fare_class: str
    passengers: int
    seat_numbers: List[str]
    meal_preference: str
    special_requests: List[str]


@dataclass
class Pricing:
    """Pricing data model"""
    base_fare: float
    taxes: float
    fuel_surcharge: float
    booking_fee: float
    insurance: float
    baggage_fee: float
    seat_selection_fee: float
    meal_upgrade: float
    discount_amount: float
    discount_code: Optional[str]
    total: float
    currency: str
    exchange_rate: float
    original_currency: str
    original_amount: float


@dataclass
class LifecycleStage:
    """Individual lifecycle stage data"""
    status: str
    timestamp: Optional[str]
    details: Optional[str]
    duration_seconds: Optional[int]
    attempts: int
    metadata: Dict[str, Any]


@dataclass
class ErrorInfo:
    """Error information for failed transactions"""
    error_stage: str
    error_code: str
    error_category: str
    error_message: str
    technical_details: str
    requires_action: bool
    escalation_level: Optional[str]
    suggested_resolution: str
    auto_retry_eligible: bool
    retry_count: int


@dataclass
class RefundInfo:
    """Refund information"""
    status: str
    refund_reference: str
    refund_amount: float
    refund_percentage: float
    refund_reason: str
    refund_type: str
    initiated_at: Optional[str]
    processed_at: Optional[str]
    expected_date: Optional[str]
    payment_method: str
    cancellation_fee: float
    processing_notes: str


@dataclass
class AgentNote:
    """Agent note/comment"""
    note_id: str
    agent_id: str
    agent_name: str
    timestamp: str
    note_type: str
    content: str
    is_internal: bool
    attachments: List[str]


@dataclass
class CommunicationLog:
    """Customer communication log"""
    comm_id: str
    channel: str
    direction: str
    timestamp: str
    subject: str
    summary: str
    agent_id: Optional[str]
    sentiment: str
    resolved: bool


class DemoDataGenerator:
    """Generates comprehensive demo data for the application"""
    
    # Name pools
    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
        "Raj", "Priya", "Arjun", "Aisha", "Mohammed", "Fatima", "Wei", "Mei",
        "Yuki", "Hiroshi", "Carlos", "Maria", "Juan", "Sofia", "Pierre", "Marie",
        "Hans", "Anna", "Ivan", "Olga", "Sven", "Ingrid", "Ahmed", "Layla"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "Patel", "Kumar", "Singh", "Chen", "Wang", "Kim", "Tanaka", "Suzuki",
        "Mueller", "Schneider", "Fischer", "Dubois", "Bernard", "Rossi", "Ferrari",
        "Santos", "Oliveira", "Petrov", "Ivanov", "Johansson", "Nielsen", "Hansen"
    ]
    
    NATIONALITIES = [
        "United States", "United Kingdom", "Canada", "Australia", "Germany",
        "France", "India", "China", "Japan", "Brazil", "Mexico", "Spain",
        "Italy", "Netherlands", "Sweden", "Singapore", "UAE", "South Korea"
    ]
    
    AIRCRAFT_TYPES = [
        "Boeing 737-800", "Boeing 777-300ER", "Boeing 787-9 Dreamliner",
        "Airbus A320neo", "Airbus A350-900", "Airbus A380-800",
        "Embraer E190", "Boeing 767-300ER"
    ]
    
    CABIN_CLASSES = ["Economy", "Premium Economy", "Business", "First"]
    FARE_CLASSES = ["Y", "B", "M", "H", "K", "L", "Q", "V", "W", "S", "N"]
    
    MEAL_PREFERENCES = [
        "Regular", "Vegetarian", "Vegan", "Halal", "Kosher", 
        "Gluten-Free", "Diabetic", "Low-Sodium", "Child Meal"
    ]
    
    SPECIAL_REQUESTS = [
        "Wheelchair assistance", "Unaccompanied minor", "Bassinet",
        "Extra legroom", "Quiet zone", "Pet in cabin", "Medical oxygen",
        "Special assistance required", "Connecting flight assistance"
    ]
    
    PAYMENT_METHODS = [
        "Visa ****4532", "Visa ****8821", "Mastercard ****7891", 
        "Mastercard ****3344", "Amex ****3456", "Amex ****9012",
        "PayPal", "Apple Pay", "Google Pay", "Bank Transfer",
        "Airline Credit", "Travel Voucher"
    ]
    
    COMMUNICATION_CHANNELS = ["Email", "Phone", "Chat", "Social Media", "SMS"]
    
    def __init__(self, seed: int = 42):
        """Initialize the generator with a seed for reproducibility"""
        random.seed(seed)
        self.transaction_counter = 0
        
    def generate_id(self, prefix: str, length: int = 8) -> str:
        """Generate a unique ID with prefix"""
        chars = string.ascii_uppercase + string.digits
        return f"{prefix}-{''.join(random.choices(chars, k=length))}"
    
    def generate_customer(self) -> Customer:
        """Generate a realistic customer profile"""
        first_name = random.choice(self.FIRST_NAMES)
        last_name = random.choice(self.LAST_NAMES)
        email_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "proton.me"]
        
        loyalty_tiers = ["None", "Bronze", "Silver", "Gold", "Platinum", "Diamond"]
        tier = random.choices(loyalty_tiers, weights=[30, 25, 20, 15, 7, 3])[0]
        
        tier_points = {
            "None": 0, "Bronze": random.randint(1000, 10000),
            "Silver": random.randint(10000, 25000), "Gold": random.randint(25000, 50000),
            "Platinum": random.randint(50000, 100000), "Diamond": random.randint(100000, 500000)
        }
        
        member_years = {"None": 0, "Bronze": 1, "Silver": 2, "Gold": 3, "Platinum": 5, "Diamond": 8}
        member_since = datetime.now() - timedelta(days=365 * member_years.get(tier, 0) + random.randint(0, 365))
        
        nationality = random.choice(self.NATIONALITIES)
        
        return Customer(
            customer_id=self.generate_id("CUST", 6),
            first_name=first_name,
            last_name=last_name,
            email=f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(email_domains)}",
            phone=f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            loyalty_tier=tier,
            loyalty_points=tier_points[tier],
            member_since=member_since.strftime("%Y-%m-%d"),
            preferred_language=random.choice(["English", "Spanish", "French", "German", "Chinese", "Japanese"]),
            nationality=nationality,
            passport_country=nationality,
            total_bookings=random.randint(1, 50) if tier != "None" else random.randint(0, 3),
            lifetime_value=round(random.uniform(500, 50000) if tier != "None" else random.uniform(0, 500), 2)
        )
    
    def generate_flight(self, airline: Dict) -> Flight:
        """Generate realistic flight details"""
        route = random.choice(app_config.ROUTES)
        
        # Generate realistic times
        departure_hour = random.randint(6, 22)
        departure_minute = random.choice([0, 15, 30, 45])
        
        # Calculate duration based on distance (rough estimate: 500 mph average)
        base_duration = int(route["distance"] / 8)  # minutes
        duration = base_duration + random.randint(-30, 60)
        
        departure_time = f"{departure_hour:02d}:{departure_minute:02d}"
        arrival_dt = datetime.strptime(departure_time, "%H:%M") + timedelta(minutes=duration)
        arrival_time = arrival_dt.strftime("%H:%M")
        
        # Generate seat numbers
        passengers = random.randint(1, 4)
        rows = list(range(1, 40))
        seats = ["A", "B", "C", "D", "E", "F"]
        seat_numbers = [f"{random.choice(rows)}{random.choice(seats)}" for _ in range(passengers)]
        
        cabin_class = random.choices(
            self.CABIN_CLASSES,
            weights=[60, 20, 15, 5]
        )[0]
        
        special_reqs = random.sample(
            self.SPECIAL_REQUESTS, 
            k=random.randint(0, 2)
        ) if random.random() > 0.7 else []
        
        return Flight(
            flight_number=f"{airline['code']}{random.randint(100, 9999)}",
            airline_code=airline["code"],
            airline_name=airline["name"],
            origin=route["origin"],
            origin_city=route["origin_city"],
            destination=route["destination"],
            destination_city=route["destination_city"],
            departure_date=(datetime.now() + timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration_minutes=duration,
            aircraft_type=random.choice(self.AIRCRAFT_TYPES),
            cabin_class=cabin_class,
            fare_class=random.choice(self.FARE_CLASSES),
            passengers=passengers,
            seat_numbers=seat_numbers,
            meal_preference=random.choice(self.MEAL_PREFERENCES),
            special_requests=special_reqs
        )
    
    def generate_pricing(self, flight: Flight) -> Pricing:
        """Generate realistic pricing breakdown"""
        # Base fare depends on cabin class and distance
        class_multipliers = {"Economy": 1, "Premium Economy": 1.8, "Business": 3.5, "First": 6}
        base_fare = random.randint(150, 800) * class_multipliers[flight.cabin_class] * flight.passengers
        
        taxes = round(base_fare * random.uniform(0.10, 0.20), 2)
        fuel_surcharge = round(base_fare * random.uniform(0.05, 0.15), 2)
        booking_fee = round(random.uniform(15, 35) * flight.passengers, 2)
        insurance = round(random.uniform(20, 50) * flight.passengers, 2) if random.random() > 0.5 else 0
        baggage_fee = round(random.uniform(30, 60) * flight.passengers, 2) if random.random() > 0.6 else 0
        seat_fee = round(random.uniform(10, 50) * flight.passengers, 2) if random.random() > 0.7 else 0
        meal_upgrade = round(random.uniform(15, 30) * flight.passengers, 2) if random.random() > 0.8 else 0
        
        # Discount
        has_discount = random.random() > 0.7
        discount_codes = ["SUMMER25", "LOYALTY10", "FIRST20", "FLASH15", "MEMBER5"]
        discount_amount = round((base_fare + taxes) * random.uniform(0.05, 0.20), 2) if has_discount else 0
        discount_code = random.choice(discount_codes) if has_discount else None
        
        total = round(
            base_fare + taxes + fuel_surcharge + booking_fee + 
            insurance + baggage_fee + seat_fee + meal_upgrade - discount_amount, 2
        )
        
        # Currency handling
        currencies = [("USD", 1.0), ("EUR", 0.92), ("GBP", 0.79), ("CAD", 1.36), ("AUD", 1.53)]
        orig_currency, rate = random.choice(currencies)
        
        return Pricing(
            base_fare=round(base_fare, 2),
            taxes=taxes,
            fuel_surcharge=fuel_surcharge,
            booking_fee=booking_fee,
            insurance=insurance,
            baggage_fee=baggage_fee,
            seat_selection_fee=seat_fee,
            meal_upgrade=meal_upgrade,
            discount_amount=discount_amount,
            discount_code=discount_code,
            total=total,
            currency="USD",
            exchange_rate=rate,
            original_currency=orig_currency,
            original_amount=round(total * rate, 2)
        )
    
    def generate_lifecycle(self, outcome: str, base_time: datetime) -> Dict[str, LifecycleStage]:
        """Generate detailed lifecycle stages based on outcome"""
        lifecycle = {}
        current_time = base_time
        
        # Search stage - always completed
        search_duration = random.randint(30, 300)
        lifecycle["search"] = LifecycleStage(
            status="completed",
            timestamp=current_time.isoformat(),
            details=f"Customer searched for flights - {random.randint(5, 25)} results shown",
            duration_seconds=search_duration,
            attempts=1,
            metadata={
                "results_count": random.randint(5, 25),
                "filters_applied": random.choice([
                    "direct flights only",
                    "price low to high",
                    "departure time morning",
                    "specific airline"
                ]),
                "device": random.choice(["desktop", "mobile", "tablet"]),
                "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"])
            }
        )
        current_time += timedelta(seconds=search_duration)
        
        # Selection stage
        if outcome == "abandoned":
            lifecycle["selection"] = LifecycleStage(
                status="not_reached",
                timestamp=None,
                details="Customer abandoned before selection",
                duration_seconds=None,
                attempts=0,
                metadata={"abandonment_point": "search_results"}
            )
            return lifecycle
        
        selection_duration = random.randint(60, 600)
        lifecycle["selection"] = LifecycleStage(
            status="completed",
            timestamp=current_time.isoformat(),
            details="Flight selected and added to cart",
            duration_seconds=selection_duration,
            attempts=random.randint(1, 3),
            metadata={
                "alternatives_viewed": random.randint(2, 8),
                "price_comparison": True,
                "fare_rules_viewed": random.choice([True, False])
            }
        )
        current_time += timedelta(seconds=selection_duration)
        
        # Booking stage
        if outcome == "booking_failed":
            failure = random.choice(app_config.ERROR_CATEGORIES["booking"])
            lifecycle["booking"] = LifecycleStage(
                status="failed",
                timestamp=current_time.isoformat(),
                details=failure,
                duration_seconds=random.randint(30, 180),
                attempts=random.randint(1, 3),
                metadata={
                    "error_code": f"BK-{random.randint(1000, 9999)}",
                    "passenger_details_valid": random.choice([True, False]),
                    "inventory_check": "failed"
                }
            )
            return lifecycle
        
        booking_duration = random.randint(120, 600)
        lifecycle["booking"] = LifecycleStage(
            status="completed",
            timestamp=current_time.isoformat(),
            details="Booking confirmed - passenger details verified",
            duration_seconds=booking_duration,
            attempts=1,
            metadata={
                "booking_ref": self.generate_id("", 6),
                "passenger_details_verified": True,
                "special_requests_logged": True
            }
        )
        current_time += timedelta(seconds=booking_duration)
        
        # Payment stage
        if outcome == "payment_failed":
            failure = random.choice(app_config.ERROR_CATEGORIES["payment"])
            lifecycle["payment"] = LifecycleStage(
                status="failed",
                timestamp=current_time.isoformat(),
                details=failure,
                duration_seconds=random.randint(10, 60),
                attempts=random.randint(1, 4),
                metadata={
                    "payment_method": random.choice(self.PAYMENT_METHODS),
                    "amount_attempted": random.uniform(200, 5000),
                    "gateway_response": failure,
                    "fraud_score": random.randint(0, 100),
                    "3ds_attempted": random.choice([True, False])
                }
            )
            return lifecycle
        
        payment_duration = random.randint(15, 90)
        lifecycle["payment"] = LifecycleStage(
            status="completed",
            timestamp=current_time.isoformat(),
            details="Payment processed successfully",
            duration_seconds=payment_duration,
            attempts=1,
            metadata={
                "payment_method": random.choice(self.PAYMENT_METHODS),
                "authorization_code": f"AUTH-{random.randint(100000, 999999)}",
                "transaction_id": self.generate_id("PAY", 10),
                "fraud_score": random.randint(0, 30),
                "3ds_verified": True
            }
        )
        current_time += timedelta(seconds=payment_duration)
        
        # Ticketing stage
        if outcome == "ticketing_failed":
            failure = random.choice(app_config.ERROR_CATEGORIES["ticketing"])
            lifecycle["ticketing"] = LifecycleStage(
                status="failed",
                timestamp=current_time.isoformat(),
                details=failure,
                duration_seconds=random.randint(5, 30),
                attempts=random.randint(1, 3),
                metadata={
                    "pnr_created": random.choice([True, False]),
                    "gds_response": failure,
                    "ticket_number": None
                }
            )
            return lifecycle
        
        ticketing_duration = random.randint(5, 30)
        pnr = self.generate_id("", 6)
        lifecycle["ticketing"] = LifecycleStage(
            status="completed",
            timestamp=current_time.isoformat(),
            details="E-ticket issued successfully",
            duration_seconds=ticketing_duration,
            attempts=1,
            metadata={
                "pnr": pnr,
                "e_ticket_number": f"098-{random.randint(1000000000, 9999999999)}",
                "itinerary_sent": True,
                "calendar_invite": random.choice([True, False])
            }
        )
        current_time += timedelta(seconds=ticketing_duration)
        
        # Confirmation stage
        lifecycle["confirmation"] = LifecycleStage(
            status="completed",
            timestamp=current_time.isoformat(),
            details="Confirmation email and SMS sent to customer",
            duration_seconds=random.randint(1, 5),
            attempts=1,
            metadata={
                "email_sent": True,
                "sms_sent": True,
                "app_notification": random.choice([True, False])
            }
        )
        
        # Refund stage (if applicable)
        if outcome in ["refund_initiated", "refund_completed", "refund_rejected"]:
            refund_time = current_time + timedelta(days=random.randint(1, 14))
            lifecycle["refund"] = LifecycleStage(
                status="completed" if outcome == "refund_completed" else "pending" if outcome == "refund_initiated" else "rejected",
                timestamp=refund_time.isoformat(),
                details=f"Refund {outcome.replace('refund_', '')}",
                duration_seconds=None,
                attempts=1,
                metadata={
                    "refund_reference": self.generate_id("REF", 8),
                    "processing_time_days": random.randint(3, 14)
                }
            )
        else:
            lifecycle["refund"] = LifecycleStage(
                status="not_applicable",
                timestamp=None,
                details=None,
                duration_seconds=None,
                attempts=0,
                metadata={}
            )
        
        return lifecycle
    
    def generate_error_info(self, outcome: str, lifecycle: Dict) -> Optional[ErrorInfo]:
        """Generate detailed error information for failed transactions"""
        if "failed" not in outcome:
            return None
        
        stage = outcome.replace("_failed", "")
        stage_data = lifecycle.get(stage, {})
        
        error_message = stage_data.details if isinstance(stage_data, LifecycleStage) else "Unknown error"
        
        suggested_resolutions = {
            "payment": [
                "Advise customer to use different payment method",
                "Verify card details and retry",
                "Contact card issuer for authorization",
                "Check for sufficient funds",
                "Try again without VPN/proxy"
            ],
            "booking": [
                "Search for alternative flights",
                "Clear session and restart booking",
                "Verify passenger details format",
                "Contact inventory team",
                "Check for system maintenance"
            ],
            "ticketing": [
                "Retry ticket issuance",
                "Contact GDS support",
                "Verify PNR status",
                "Manual ticket issuance required",
                "Escalate to ticketing team"
            ]
        }
        
        return ErrorInfo(
            error_stage=stage.capitalize(),
            error_code=f"ERR-{stage.upper()[:3]}-{random.randint(1000, 9999)}",
            error_category=stage,
            error_message=error_message,
            technical_details=f"Stack trace: {stage}_service.process() failed at line {random.randint(100, 500)}",
            requires_action=random.choice([True, False]),
            escalation_level=random.choice(["L1", "L2", "L3"]) if random.random() > 0.5 else None,
            suggested_resolution=random.choice(suggested_resolutions.get(stage, ["Contact support"])),
            auto_retry_eligible=stage in ["payment", "ticketing"],
            retry_count=random.randint(0, 3)
        )
    
    def generate_refund_info(self, outcome: str, pricing: Pricing, base_time: datetime) -> Optional[RefundInfo]:
        """Generate refund information for refund transactions"""
        if "refund" not in outcome:
            return None
        
        refund_reason = random.choice(app_config.REFUND_REASONS)
        
        # Calculate refund amount based on reason and timing
        refund_percentages = {
            "Flight cancelled by airline": 1.0,
            "Overbooking compensation": 1.0,
            "Force majeure event": 1.0,
            "Technical error during booking": 1.0,
            "Customer requested cancellation": random.uniform(0.5, 0.9),
            "Schedule change - customer opted out": 0.95,
            "Medical emergency": random.uniform(0.7, 0.95),
            "Duplicate booking": 1.0,
            "Price guarantee claim": random.uniform(0.1, 0.3),
            "Service not as described": random.uniform(0.5, 1.0),
            "Visa/travel document issues": random.uniform(0.6, 0.85),
            "Flight delay compensation": random.uniform(0.2, 0.5)
        }
        
        refund_pct = refund_percentages.get(refund_reason, 0.8)
        cancellation_fee = round(pricing.total * (1 - refund_pct), 2) if refund_pct < 1 else 0
        refund_amount = round(pricing.total - cancellation_fee, 2)
        
        initiated_at = base_time + timedelta(days=random.randint(1, 7))
        processed_at = initiated_at + timedelta(days=random.randint(1, 10)) if outcome == "refund_completed" else None
        expected_date = initiated_at + timedelta(days=random.randint(7, 21))
        
        status_map = {
            "refund_initiated": "Pending",
            "refund_completed": "Completed",
            "refund_rejected": "Rejected"
        }
        
        return RefundInfo(
            status=status_map.get(outcome, "Pending"),
            refund_reference=self.generate_id("REF", 8),
            refund_amount=refund_amount,
            refund_percentage=round(refund_pct * 100, 1),
            refund_reason=refund_reason,
            refund_type=random.choice(["Original Payment Method", "Airline Credit", "Bank Transfer"]),
            initiated_at=initiated_at.isoformat(),
            processed_at=processed_at.isoformat() if processed_at else None,
            expected_date=expected_date.strftime("%Y-%m-%d"),
            payment_method=random.choice(self.PAYMENT_METHODS),
            cancellation_fee=cancellation_fee,
            processing_notes=random.choice([
                "Standard processing",
                "Expedited due to airline cancellation",
                "Awaiting bank confirmation",
                "Manual review required",
                "Processing complete"
            ])
        )
    
    def generate_agent_notes(self, outcome: str, base_time: datetime) -> List[AgentNote]:
        """Generate agent notes for the transaction"""
        if random.random() > 0.6:  # 40% chance of having notes
            return []
        
        note_templates = {
            "payment_failed": [
                ("Initial Contact", "Customer contacted regarding failed payment. Advised to verify card details."),
                ("Follow-up", "Customer retried with different card. Still failing. Escalated to payment team."),
                ("Resolution", "Payment issue resolved. Customer used alternative payment method.")
            ],
            "booking_failed": [
                ("Initial Contact", "Booking failed due to inventory issue. Searching for alternatives."),
                ("Alternative Offered", "Offered alternative flight with similar timing. Customer considering."),
                ("Resolved", "Customer accepted alternative. New booking confirmed.")
            ],
            "refund_initiated": [
                ("Refund Request", "Customer requested refund due to schedule change."),
                ("Processing", "Refund request submitted to finance team."),
                ("Update", "Refund approved. Processing within 7-10 business days.")
            ],
            "completed": [
                ("Confirmation", "Booking confirmed. Customer received all documents."),
                ("Query", "Customer called to confirm baggage allowance. Information provided.")
            ]
        }
        
        templates = note_templates.get(outcome, note_templates["completed"])
        notes = []
        
        current_time = base_time + timedelta(hours=random.randint(1, 48))
        
        for note_type, content in templates[:random.randint(1, len(templates))]:
            agent_id = f"AGT-{random.randint(100, 999)}"
            notes.append(AgentNote(
                note_id=self.generate_id("NOTE", 6),
                agent_id=agent_id,
                agent_name=f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)[:1]}.",
                timestamp=current_time.isoformat(),
                note_type=note_type,
                content=content,
                is_internal=random.choice([True, False]),
                attachments=[]
            ))
            current_time += timedelta(hours=random.randint(2, 24))
        
        return notes
    
    def generate_communication_log(self, outcome: str, base_time: datetime) -> List[CommunicationLog]:
        """Generate customer communication history"""
        if random.random() > 0.5:  # 50% chance of communications
            return []
        
        comms = []
        current_time = base_time + timedelta(hours=random.randint(1, 72))
        
        comm_count = random.randint(1, 4)
        
        subjects = [
            "Booking Confirmation Query",
            "Payment Issue Follow-up", 
            "Refund Status Inquiry",
            "Flight Change Request",
            "Seat Selection Change",
            "Special Assistance Request"
        ]
        
        for _ in range(comm_count):
            channel = random.choice(self.COMMUNICATION_CHANNELS)
            comms.append(CommunicationLog(
                comm_id=self.generate_id("COMM", 6),
                channel=channel,
                direction=random.choice(["Inbound", "Outbound"]),
                timestamp=current_time.isoformat(),
                subject=random.choice(subjects),
                summary=f"Customer inquiry handled via {channel.lower()}. Issue {'resolved' if random.random() > 0.3 else 'pending'}.",
                agent_id=f"AGT-{random.randint(100, 999)}" if random.random() > 0.2 else None,
                sentiment=random.choice(["Positive", "Neutral", "Negative", "Frustrated", "Satisfied"]),
                resolved=random.choice([True, False])
            ))
            current_time += timedelta(hours=random.randint(1, 48))
        
        return comms
    
    def generate_transaction(self) -> Dict[str, Any]:
        """Generate a complete transaction record"""
        self.transaction_counter += 1
        
        # Determine outcome with realistic distribution
        outcomes = [
            "completed", "payment_failed", "booking_failed", "ticketing_failed",
            "refund_initiated", "refund_completed", "refund_rejected", "abandoned"
        ]
        weights = [45, 18, 12, 5, 8, 7, 2, 3]
        outcome = random.choices(outcomes, weights=weights)[0]
        
        # Generate base data
        airline = random.choice(app_config.AIRLINES)
        customer = self.generate_customer()
        flight = self.generate_flight(airline)
        pricing = self.generate_pricing(flight)
        
        base_time = datetime.now() - timedelta(days=random.randint(0, 45))
        
        # Generate lifecycle
        lifecycle = self.generate_lifecycle(outcome, base_time)
        
        # Determine status
        status_map = {
            "completed": "Completed",
            "payment_failed": "Failed",
            "booking_failed": "Failed",
            "ticketing_failed": "Failed",
            "refund_initiated": "Refund Pending",
            "refund_completed": "Refunded",
            "refund_rejected": "Refund Rejected",
            "abandoned": "Abandoned"
        }
        
        # Calculate SLA compliance
        sla_breach = False
        if "failed" in outcome:
            created_time = datetime.fromisoformat(lifecycle["search"].timestamp)
            hours_since_creation = (datetime.now() - created_time).total_seconds() / 3600
            sla_breach = hours_since_creation > app_config.SLA_RESPONSE_TIME
        
        # Determine priority
        priority = "Low"
        if outcome in ["payment_failed", "ticketing_failed"]:
            priority = random.choice(["High", "Critical"])
        elif outcome == "booking_failed":
            priority = random.choice(["Medium", "High"])
        elif "refund" in outcome:
            priority = "Medium"
        
        transaction = {
            "transaction_id": f"TXN-{datetime.now().strftime('%Y%m')}-{self.generate_id('', 10)}",
            "customer": asdict(customer),
            "flight": asdict(flight),
            "pricing": asdict(pricing),
            "lifecycle": {k: asdict(v) if isinstance(v, LifecycleStage) else v for k, v in lifecycle.items()},
            "status": status_map[outcome],
            "outcome": outcome,
            "priority": priority,
            "sla_breach": sla_breach,
            "error_info": asdict(self.generate_error_info(outcome, lifecycle)) if self.generate_error_info(outcome, lifecycle) else None,
            "refund_info": asdict(self.generate_refund_info(outcome, pricing, base_time)) if self.generate_refund_info(outcome, pricing, base_time) else None,
            "agent_notes": [asdict(note) for note in self.generate_agent_notes(outcome, base_time)],
            "communication_log": [asdict(comm) for comm in self.generate_communication_log(outcome, base_time)],
            "created_at": base_time.isoformat(),
            "last_updated": (base_time + timedelta(hours=random.randint(0, 72))).isoformat(),
            "assigned_agent": f"AGT-{random.randint(100, 999)}" if random.random() > 0.4 else None,
            "tags": random.sample(["VIP", "Urgent", "Repeat Issue", "Compensation", "Escalated", "First Contact"], k=random.randint(0, 2))
        }
        
        return transaction
    
    def generate_dataset(self, count: int = 200) -> List[Dict[str, Any]]:
        """Generate a complete dataset of transactions"""
        return [self.generate_transaction() for _ in range(count)]


def get_demo_data(count: int = 200, seed: int = 42) -> List[Dict[str, Any]]:
    """Get demo transaction data"""
    generator = DemoDataGenerator(seed=seed)
    return generator.generate_dataset(count)
