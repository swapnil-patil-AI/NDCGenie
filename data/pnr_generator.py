"""
PNR and E-Ticket Generator for NDC Genie
Generates realistic airline booking references and electronic tickets.

Week 1-2 Implementation
Version: 1.0.0
"""

import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field


# ═══════════════════════════════════════════════════════════════════════════════
# AIRLINE DATA
# ═══════════════════════════════════════════════════════════════════════════════

AIRLINES = {
    "AA": {"name": "American Airlines", "numeric_code": "001", "hub": "DFW"},
    "UA": {"name": "United Airlines", "numeric_code": "016", "hub": "ORD"},
    "DL": {"name": "Delta Air Lines", "numeric_code": "006", "hub": "ATL"},
    "WN": {"name": "Southwest Airlines", "numeric_code": "526", "hub": "DAL"},
    "B6": {"name": "JetBlue Airways", "numeric_code": "279", "hub": "JFK"},
    "AS": {"name": "Alaska Airlines", "numeric_code": "027", "hub": "SEA"},
    "NK": {"name": "Spirit Airlines", "numeric_code": "487", "hub": "FLL"},
    "F9": {"name": "Frontier Airlines", "numeric_code": "422", "hub": "DEN"},
    "BA": {"name": "British Airways", "numeric_code": "125", "hub": "LHR"},
    "LH": {"name": "Lufthansa", "numeric_code": "220", "hub": "FRA"},
    "AF": {"name": "Air France", "numeric_code": "057", "hub": "CDG"},
    "EK": {"name": "Emirates", "numeric_code": "176", "hub": "DXB"},
    "SQ": {"name": "Singapore Airlines", "numeric_code": "618", "hub": "SIN"},
    "QF": {"name": "Qantas", "numeric_code": "081", "hub": "SYD"},
    "AC": {"name": "Air Canada", "numeric_code": "014", "hub": "YYZ"},
}

AIRPORTS = {
    # US Major Hubs
    "JFK": {"city": "New York", "country": "US", "timezone": "America/New_York"},
    "LAX": {"city": "Los Angeles", "country": "US", "timezone": "America/Los_Angeles"},
    "ORD": {"city": "Chicago", "country": "US", "timezone": "America/Chicago"},
    "DFW": {"city": "Dallas", "country": "US", "timezone": "America/Chicago"},
    "DEN": {"city": "Denver", "country": "US", "timezone": "America/Denver"},
    "SFO": {"city": "San Francisco", "country": "US", "timezone": "America/Los_Angeles"},
    "SEA": {"city": "Seattle", "country": "US", "timezone": "America/Los_Angeles"},
    "ATL": {"city": "Atlanta", "country": "US", "timezone": "America/New_York"},
    "MIA": {"city": "Miami", "country": "US", "timezone": "America/New_York"},
    "BOS": {"city": "Boston", "country": "US", "timezone": "America/New_York"},
    # International
    "LHR": {"city": "London", "country": "UK", "timezone": "Europe/London"},
    "CDG": {"city": "Paris", "country": "FR", "timezone": "Europe/Paris"},
    "FRA": {"city": "Frankfurt", "country": "DE", "timezone": "Europe/Berlin"},
    "DXB": {"city": "Dubai", "country": "AE", "timezone": "Asia/Dubai"},
    "SIN": {"city": "Singapore", "country": "SG", "timezone": "Asia/Singapore"},
    "HKG": {"city": "Hong Kong", "country": "HK", "timezone": "Asia/Hong_Kong"},
    "NRT": {"city": "Tokyo", "country": "JP", "timezone": "Asia/Tokyo"},
    "SYD": {"city": "Sydney", "country": "AU", "timezone": "Australia/Sydney"},
    "YYZ": {"city": "Toronto", "country": "CA", "timezone": "America/Toronto"},
    "MEX": {"city": "Mexico City", "country": "MX", "timezone": "America/Mexico_City"},
}

# Common routes with typical durations (minutes)
ROUTES = [
    # Domestic US
    ("JFK", "LAX", 330), ("LAX", "JFK", 300), ("JFK", "SFO", 360), ("SFO", "JFK", 320),
    ("ORD", "LAX", 240), ("LAX", "ORD", 220), ("DFW", "JFK", 210), ("JFK", "DFW", 240),
    ("ATL", "LAX", 270), ("LAX", "ATL", 240), ("DEN", "JFK", 240), ("JFK", "DEN", 270),
    ("SEA", "LAX", 150), ("LAX", "SEA", 165), ("MIA", "JFK", 180), ("JFK", "MIA", 195),
    # Transatlantic
    ("JFK", "LHR", 420), ("LHR", "JFK", 480), ("JFK", "CDG", 450), ("CDG", "JFK", 510),
    ("ORD", "LHR", 480), ("LHR", "ORD", 540), ("LAX", "LHR", 600), ("LHR", "LAX", 660),
    # Transpacific
    ("LAX", "NRT", 690), ("NRT", "LAX", 630), ("SFO", "HKG", 840), ("HKG", "SFO", 780),
    ("LAX", "SYD", 900), ("SYD", "LAX", 840),
    # Middle East
    ("JFK", "DXB", 780), ("DXB", "JFK", 840), ("LAX", "DXB", 960), ("DXB", "LAX", 1020),
]

AIRCRAFT_TYPES = {
    "domestic_short": ["A320", "A321", "B737", "B737MAX", "E190"],
    "domestic_long": ["A321", "B737MAX", "B757"],
    "international": ["B777", "B787", "A350", "A380", "B747"],
}

CABIN_CLASSES = {
    "F": "First Class",
    "J": "Business Class",
    "W": "Premium Economy",
    "Y": "Economy",
}

FARE_CLASSES = {
    "First": ["F", "A", "P"],
    "Business": ["J", "C", "D", "I", "Z"],
    "Premium Economy": ["W", "E", "T"],
    "Economy": ["Y", "B", "M", "H", "K", "L", "Q", "V", "S", "N", "G"],
}

BOOKING_CHANNELS = [
    "Direct - Website",
    "Direct - Mobile App", 
    "Direct - Call Center",
    "OTA - Expedia",
    "OTA - Booking.com",
    "OTA - Kayak",
    "Travel Agent",
    "Corporate Portal",
    "GDS - Amadeus",
    "GDS - Sabre",
]

MEAL_CODES = {
    "AVML": "Asian Vegetarian",
    "BBML": "Baby Meal",
    "BLML": "Bland Meal",
    "CHML": "Child Meal",
    "DBML": "Diabetic Meal",
    "FPML": "Fruit Platter",
    "GFML": "Gluten Free",
    "HNML": "Hindu Meal",
    "KSML": "Kosher Meal",
    "LCML": "Low Calorie",
    "LFML": "Low Fat",
    "LSML": "Low Sodium",
    "MOML": "Muslim Meal",
    "NLML": "No Lactose",
    "RVML": "Raw Vegetarian",
    "SFML": "Seafood Meal",
    "VGML": "Vegan Meal",
    "VLML": "Vegetarian Lacto-Ovo",
    "VOML": "Vegetarian Oriental",
    "STD": "Standard Meal",
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PNRRecord:
    """Passenger Name Record - Core booking identifier"""
    pnr: str  # 6-character (e.g., "ABC123")
    record_locator: str  # Airline-specific
    gds_locator: Optional[str]
    created_at: str
    last_modified: str
    booking_channel: str
    booking_agent_id: Optional[str]
    agency_iata: Optional[str]
    office_id: Optional[str]
    ticketing_deadline: str
    ticket_status: str  # "Ticketed", "On Hold", "Cancelled"
    is_group_booking: bool
    group_name: Optional[str]
    contact_email: str
    contact_phone: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ETicket:
    """Electronic Ticket - 13-digit travel document"""
    ticket_number: str  # e.g., "016-1234567890"
    airline_code: str  # 3-digit numeric
    airline_name: str
    passenger_name: str
    issue_date: str
    issuing_agent: str
    original_issue: bool
    conjunction_tickets: List[str]
    fare_calculation: str
    endorsements: str
    tour_code: Optional[str]
    ticket_status: str  # "Open", "Used", "Void", "Refunded", "Exchanged"
    total_fare: float
    currency: str
    coupons: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FlightSegment:
    """Individual flight segment"""
    segment_id: str
    sequence_number: int
    flight_number: str
    marketing_carrier: str
    marketing_carrier_name: str
    operating_carrier: str
    operating_carrier_name: str
    codeshare: bool
    origin: str
    origin_city: str
    origin_country: str
    destination: str
    destination_city: str
    destination_country: str
    departure_date: str
    departure_time: str
    arrival_date: str
    arrival_time: str
    duration_minutes: int
    connection_time_minutes: Optional[int]
    aircraft_type: str
    cabin_class: str
    cabin_class_name: str
    booking_class: str
    fare_basis: str
    ticket_designator: Optional[str]
    status: str  # "Confirmed", "Waitlisted", "Cancelled"
    seat_assignment: Optional[str]
    meal_code: str
    meal_description: str
    baggage_allowance: str
    
    # Operational (real-time)
    flight_status: str
    gate: Optional[str]
    terminal: Optional[str]
    actual_departure: Optional[str]
    actual_arrival: Optional[str]
    delay_minutes: int
    delay_reason: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Itinerary:
    """Complete travel itinerary with segments"""
    itinerary_id: str
    pnr: str
    trip_type: str  # "One-Way", "Round-Trip", "Multi-City", "Open-Jaw"
    segments: List[FlightSegment]
    total_duration_minutes: int
    total_flight_time_minutes: int
    total_stops: int
    layover_airports: List[str]
    is_international: bool
    countries_visited: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['segments'] = [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.segments]
        return result


@dataclass
class Passenger:
    """Passenger information"""
    passenger_id: str
    pnr: str
    sequence_number: int
    name_prefix: str  # MR, MRS, MS, MSTR, MISS
    first_name: str
    middle_name: Optional[str]
    last_name: str
    suffix: Optional[str]
    date_of_birth: str
    gender: str
    passenger_type: str  # ADT, CHD, INF
    nationality: str
    passport_number: Optional[str]
    passport_expiry: Optional[str]
    passport_country: Optional[str]
    redress_number: Optional[str]
    known_traveler_number: Optional[str]
    loyalty_program: Optional[str]
    loyalty_number: Optional[str]
    loyalty_tier: Optional[str]
    contact_email: str
    contact_phone: str
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    special_requests: List[str]
    meal_preference: str
    seat_preference: str
    wheelchair_required: bool
    
    @property
    def full_name(self) -> str:
        parts = [self.name_prefix, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['full_name'] = self.full_name
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATOR CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class PNRGenerator:
    """Generates realistic PNR, E-tickets, and itineraries"""
    
    FIRST_NAMES_MALE = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard",
        "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew",
        "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
        "Raj", "Arjun", "Mohammed", "Wei", "Hiroshi", "Carlos", "Juan",
        "Pierre", "Hans", "Ivan", "Sven", "Ahmed", "Kenji", "Vikram"
    ]
    
    FIRST_NAMES_FEMALE = [
        "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth",
        "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty",
        "Margaret", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily",
        "Priya", "Aisha", "Mei", "Yuki", "Maria", "Sofia", "Marie",
        "Anna", "Olga", "Ingrid", "Layla", "Sakura", "Ananya"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin",
        "Patel", "Kumar", "Singh", "Chen", "Wang", "Kim", "Tanaka", "Suzuki",
        "Mueller", "Schneider", "Dubois", "Rossi", "Santos", "Petrov", "Hansen"
    ]
    
    def __init__(self):
        self.used_pnrs = set()
        self.used_ticket_numbers = set()
    
    def generate_pnr(self) -> str:
        """Generate unique 6-character PNR"""
        while True:
            # PNR format: Mix of letters and numbers, no ambiguous chars (0,O,1,I)
            chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
            pnr = ''.join(random.choices(chars, k=6))
            if pnr not in self.used_pnrs:
                self.used_pnrs.add(pnr)
                return pnr
    
    def generate_ticket_number(self, airline_code: str) -> str:
        """Generate 13-digit E-ticket number"""
        airline_info = AIRLINES.get(airline_code, {"numeric_code": "000"})
        numeric_code = airline_info["numeric_code"]
        
        while True:
            serial = ''.join(random.choices("0123456789", k=10))
            ticket_number = f"{numeric_code}-{serial}"
            if ticket_number not in self.used_ticket_numbers:
                self.used_ticket_numbers.add(ticket_number)
                return ticket_number
    
    def generate_flight_number(self, airline_code: str) -> str:
        """Generate realistic flight number"""
        # Different ranges for different route types
        num = random.randint(1, 9999)
        return f"{airline_code}{num}"
    
    def generate_seat(self, cabin_class: str) -> str:
        """Generate seat assignment"""
        if cabin_class in ["F", "J"]:  # First/Business - fewer rows
            row = random.randint(1, 10)
            seat = random.choice("ABCDEF")
        else:  # Economy
            row = random.randint(11, 45)
            seat = random.choice("ABCDEFGHJK")
        return f"{row}{seat}"
    
    def generate_fare_basis(self, cabin: str, is_refundable: bool) -> str:
        """Generate fare basis code"""
        fare_class = random.choice(FARE_CLASSES.get(cabin, ["Y"]))
        
        # Fare basis components
        season = random.choice(["H", "L", "K", ""])  # High/Low/Peak
        advance = random.choice(["7", "14", "21", ""])  # Advance purchase
        restrictions = "" if is_refundable else "NR"
        
        return f"{fare_class}{season}{advance}{restrictions}".strip() or fare_class
    
    def calculate_fare(self, segments: List[Dict], cabin: str, passengers: int) -> Dict[str, Any]:
        """Calculate realistic fare breakdown"""
        # Base fare by distance and cabin
        total_distance = sum(s.get('duration_minutes', 120) * 8 for s in segments)  # Rough km estimate
        
        base_multiplier = {
            "First Class": 4.5,
            "Business Class": 2.8,
            "Premium Economy": 1.6,
            "Economy": 1.0
        }.get(cabin, 1.0)
        
        base_fare = total_distance * 0.15 * base_multiplier
        base_fare = round(base_fare / 10) * 10  # Round to nearest 10
        
        # Add components
        taxes = round(base_fare * 0.12, 2)
        fuel_surcharge = round(base_fare * 0.08, 2)
        security_fee = 5.60 * len(segments)
        facility_charge = 4.50 * len(segments)
        
        per_passenger = base_fare + taxes + fuel_surcharge + security_fee + facility_charge
        total = round(per_passenger * passengers, 2)
        
        return {
            "base_fare": round(base_fare, 2),
            "taxes": round(taxes, 2),
            "fuel_surcharge": round(fuel_surcharge, 2),
            "security_fee": round(security_fee, 2),
            "facility_charge": round(facility_charge, 2),
            "per_passenger": round(per_passenger, 2),
            "passengers": passengers,
            "total": total,
            "currency": "USD"
        }
    
    def generate_passenger(self, pnr: str, sequence: int, 
                          passenger_type: str = "ADT") -> Passenger:
        """Generate a passenger"""
        gender = random.choice(["M", "F"])
        
        if gender == "M":
            first_name = random.choice(self.FIRST_NAMES_MALE)
            prefix = "MR" if passenger_type == "ADT" else "MSTR"
        else:
            first_name = random.choice(self.FIRST_NAMES_FEMALE)
            prefix = random.choice(["MRS", "MS"]) if passenger_type == "ADT" else "MISS"
        
        last_name = random.choice(self.LAST_NAMES)
        
        # Age based on passenger type
        if passenger_type == "ADT":
            birth_year = random.randint(1955, 2005)
        elif passenger_type == "CHD":
            birth_year = random.randint(2013, 2022)
        else:  # INF
            birth_year = random.randint(2023, 2024)
        
        dob = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
        
        # Loyalty
        has_loyalty = random.random() < 0.4
        loyalty_program = None
        loyalty_number = None
        loyalty_tier = None
        
        if has_loyalty:
            airline = random.choice(list(AIRLINES.keys()))
            loyalty_program = f"{AIRLINES[airline]['name']} Frequent Flyer"
            loyalty_number = ''.join(random.choices("0123456789", k=10))
            loyalty_tier = random.choice(["Blue", "Silver", "Gold", "Platinum", "Diamond"])
        
        return Passenger(
            passenger_id=f"PAX-{pnr}-{sequence}",
            pnr=pnr,
            sequence_number=sequence,
            name_prefix=prefix,
            first_name=first_name.upper(),
            middle_name=random.choice([None, random.choice(self.FIRST_NAMES_MALE if gender == "M" else self.FIRST_NAMES_FEMALE).upper()]),
            last_name=last_name.upper(),
            suffix=random.choice([None, None, None, "JR", "SR", "III"]),
            date_of_birth=dob.strftime("%Y-%m-%d"),
            gender=gender,
            passenger_type=passenger_type,
            nationality=random.choice(["US", "UK", "CA", "AU", "DE", "FR", "IN", "JP"]),
            passport_number=''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=9)) if random.random() < 0.7 else None,
            passport_expiry=(datetime.now() + timedelta(days=random.randint(180, 3650))).strftime("%Y-%m-%d") if random.random() < 0.7 else None,
            passport_country=random.choice(["US", "UK", "CA", "AU", "DE", "FR", "IN", "JP"]) if random.random() < 0.7 else None,
            redress_number=''.join(random.choices("0123456789", k=7)) if random.random() < 0.1 else None,
            known_traveler_number=''.join(random.choices("0123456789", k=9)) if random.random() < 0.2 else None,
            loyalty_program=loyalty_program,
            loyalty_number=loyalty_number,
            loyalty_tier=loyalty_tier,
            contact_email=f"{first_name.lower()}.{last_name.lower()}@email.com",
            contact_phone=f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            emergency_contact_name=f"{random.choice(self.FIRST_NAMES_MALE + self.FIRST_NAMES_FEMALE)} {last_name}" if random.random() < 0.5 else None,
            emergency_contact_phone=f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}" if random.random() < 0.5 else None,
            special_requests=random.sample(["Wheelchair", "Bassinet", "Unaccompanied Minor", "Pet in Cabin", "Extra Legroom"], k=random.randint(0, 2)),
            meal_preference=random.choice(list(MEAL_CODES.keys())),
            seat_preference=random.choice(["Window", "Aisle", "Middle", "No Preference"]),
            wheelchair_required=random.random() < 0.05
        )
    
    def generate_segment(self, segment_id: str, sequence: int, 
                        origin: str, destination: str, 
                        departure_datetime: datetime,
                        cabin: str = "Economy",
                        connection_time: Optional[int] = None) -> FlightSegment:
        """Generate a flight segment"""
        
        # Find route duration or estimate
        duration = None
        for route in ROUTES:
            if route[0] == origin and route[1] == destination:
                duration = route[2]
                break
        
        if duration is None:
            # Estimate based on whether domestic or international
            origin_country = AIRPORTS.get(origin, {}).get("country", "US")
            dest_country = AIRPORTS.get(destination, {}).get("country", "US")
            if origin_country == dest_country:
                duration = random.randint(90, 300)  # Domestic
            else:
                duration = random.randint(300, 900)  # International
        
        # Add some variation
        duration = duration + random.randint(-15, 30)
        
        # Select airline
        airline_code = random.choice(list(AIRLINES.keys()))
        airline_info = AIRLINES[airline_code]
        
        # Codeshare possibility
        is_codeshare = random.random() < 0.2
        if is_codeshare:
            operating_carrier = random.choice([k for k in AIRLINES.keys() if k != airline_code])
            operating_info = AIRLINES[operating_carrier]
        else:
            operating_carrier = airline_code
            operating_info = airline_info
        
        # Aircraft based on duration
        if duration < 180:
            aircraft = random.choice(AIRCRAFT_TYPES["domestic_short"])
        elif duration < 360:
            aircraft = random.choice(AIRCRAFT_TYPES["domestic_long"])
        else:
            aircraft = random.choice(AIRCRAFT_TYPES["international"])
        
        # Calculate arrival
        arrival_datetime = departure_datetime + timedelta(minutes=duration)
        
        # Cabin class
        cabin_code = [k for k, v in CABIN_CLASSES.items() if v == cabin][0] if cabin in CABIN_CLASSES.values() else "Y"
        
        # Fare class
        fare_class = random.choice(FARE_CLASSES.get(cabin, ["Y"]))
        fare_basis = self.generate_fare_basis(cabin, random.random() < 0.3)
        
        # Meal
        meal_code = random.choice(list(MEAL_CODES.keys()))
        
        # Baggage
        baggage = "2PC" if cabin in ["First Class", "Business Class"] else "1PC" if random.random() < 0.7 else "0PC"
        
        origin_info = AIRPORTS.get(origin, {"city": origin, "country": "US"})
        dest_info = AIRPORTS.get(destination, {"city": destination, "country": "US"})
        
        return FlightSegment(
            segment_id=segment_id,
            sequence_number=sequence,
            flight_number=self.generate_flight_number(airline_code),
            marketing_carrier=airline_code,
            marketing_carrier_name=airline_info["name"],
            operating_carrier=operating_carrier,
            operating_carrier_name=operating_info["name"],
            codeshare=is_codeshare,
            origin=origin,
            origin_city=origin_info["city"],
            origin_country=origin_info["country"],
            destination=destination,
            destination_city=dest_info["city"],
            destination_country=dest_info["country"],
            departure_date=departure_datetime.strftime("%Y-%m-%d"),
            departure_time=departure_datetime.strftime("%H:%M"),
            arrival_date=arrival_datetime.strftime("%Y-%m-%d"),
            arrival_time=arrival_datetime.strftime("%H:%M"),
            duration_minutes=duration,
            connection_time_minutes=connection_time,
            aircraft_type=aircraft,
            cabin_class=cabin_code,
            cabin_class_name=cabin,
            booking_class=fare_class,
            fare_basis=fare_basis,
            ticket_designator=None,
            status="Confirmed",
            seat_assignment=self.generate_seat(cabin_code),
            meal_code=meal_code,
            meal_description=MEAL_CODES[meal_code],
            baggage_allowance=baggage,
            flight_status="Scheduled",
            gate=None,
            terminal=random.choice(["1", "2", "3", "A", "B", "C", None]),
            actual_departure=None,
            actual_arrival=None,
            delay_minutes=0,
            delay_reason=None
        )
    
    def generate_itinerary(self, pnr: str, trip_type: str = "Round-Trip",
                          origin: str = None, destination: str = None,
                          departure_date: datetime = None,
                          cabin: str = "Economy",
                          with_connections: bool = None) -> Itinerary:
        """Generate complete itinerary with optional connections"""
        
        if origin is None:
            origin = random.choice(list(AIRPORTS.keys()))
        if destination is None:
            destination = random.choice([k for k in AIRPORTS.keys() if k != origin])
        if departure_date is None:
            departure_date = datetime.now() + timedelta(days=random.randint(1, 90))
        if with_connections is None:
            with_connections = random.random() < 0.4  # 40% have connections
        
        segments = []
        sequence = 1
        layovers = []
        
        # Outbound journey
        if with_connections and random.random() < 0.6:
            # Add connection point
            connection = random.choice([k for k in AIRPORTS.keys() if k not in [origin, destination]])
            
            # First leg
            dep_time = departure_date.replace(hour=random.randint(6, 20), minute=random.choice([0, 15, 30, 45]))
            seg1 = self.generate_segment(
                f"{pnr}-SEG-{sequence}", sequence, origin, connection, dep_time, cabin
            )
            segments.append(seg1)
            sequence += 1
            
            # Connection time (45 min to 3 hours)
            connection_minutes = random.randint(45, 180)
            layovers.append(connection)
            
            # Second leg
            arr_time = datetime.strptime(f"{seg1.arrival_date} {seg1.arrival_time}", "%Y-%m-%d %H:%M")
            dep_time2 = arr_time + timedelta(minutes=connection_minutes)
            seg2 = self.generate_segment(
                f"{pnr}-SEG-{sequence}", sequence, connection, destination, dep_time2, cabin, connection_minutes
            )
            segments.append(seg2)
            sequence += 1
        else:
            # Direct flight
            dep_time = departure_date.replace(hour=random.randint(6, 20), minute=random.choice([0, 15, 30, 45]))
            seg = self.generate_segment(
                f"{pnr}-SEG-{sequence}", sequence, origin, destination, dep_time, cabin
            )
            segments.append(seg)
            sequence += 1
        
        # Return journey for round-trip
        if trip_type == "Round-Trip":
            return_date = departure_date + timedelta(days=random.randint(2, 14))
            
            if with_connections and random.random() < 0.5:
                # Return with connection
                connection = random.choice([k for k in AIRPORTS.keys() if k not in [origin, destination]])
                
                dep_time = return_date.replace(hour=random.randint(6, 20), minute=random.choice([0, 15, 30, 45]))
                seg1 = self.generate_segment(
                    f"{pnr}-SEG-{sequence}", sequence, destination, connection, dep_time, cabin
                )
                segments.append(seg1)
                sequence += 1
                
                connection_minutes = random.randint(45, 180)
                if connection not in layovers:
                    layovers.append(connection)
                
                arr_time = datetime.strptime(f"{seg1.arrival_date} {seg1.arrival_time}", "%Y-%m-%d %H:%M")
                dep_time2 = arr_time + timedelta(minutes=connection_minutes)
                seg2 = self.generate_segment(
                    f"{pnr}-SEG-{sequence}", sequence, connection, origin, dep_time2, cabin, connection_minutes
                )
                segments.append(seg2)
            else:
                # Direct return
                dep_time = return_date.replace(hour=random.randint(6, 20), minute=random.choice([0, 15, 30, 45]))
                seg = self.generate_segment(
                    f"{pnr}-SEG-{sequence}", sequence, destination, origin, dep_time, cabin
                )
                segments.append(seg)
        
        # Calculate totals
        total_flight_time = sum(s.duration_minutes for s in segments)
        total_connection_time = sum(s.connection_time_minutes or 0 for s in segments)
        
        # Check if international
        countries = set()
        for seg in segments:
            countries.add(seg.origin_country)
            countries.add(seg.destination_country)
        
        return Itinerary(
            itinerary_id=f"ITN-{pnr}",
            pnr=pnr,
            trip_type=trip_type,
            segments=segments,
            total_duration_minutes=total_flight_time + total_connection_time,
            total_flight_time_minutes=total_flight_time,
            total_stops=len(layovers),
            layover_airports=layovers,
            is_international=len(countries) > 1,
            countries_visited=list(countries)
        )
    
    def generate_pnr_record(self, pnr: str, created_at: datetime = None) -> PNRRecord:
        """Generate PNR record"""
        if created_at is None:
            created_at = datetime.now() - timedelta(days=random.randint(1, 60))
        
        channel = random.choice(BOOKING_CHANNELS)
        
        # GDS locator if booked via GDS
        gds_locator = None
        if "GDS" in channel:
            gds_locator = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))
        
        # Agency info if travel agent
        agency_iata = None
        office_id = None
        if channel == "Travel Agent":
            agency_iata = ''.join(random.choices("0123456789", k=8))
            office_id = f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))}1234"
        
        return PNRRecord(
            pnr=pnr,
            record_locator=f"{random.choice(list(AIRLINES.keys()))}{pnr}",
            gds_locator=gds_locator,
            created_at=created_at.isoformat(),
            last_modified=datetime.now().isoformat(),
            booking_channel=channel,
            booking_agent_id=f"AGT{random.randint(1000, 9999)}" if random.random() < 0.3 else None,
            agency_iata=agency_iata,
            office_id=office_id,
            ticketing_deadline=(created_at + timedelta(days=random.randint(1, 3))).isoformat(),
            ticket_status=random.choices(["Ticketed", "On Hold", "Cancelled"], weights=[0.85, 0.10, 0.05])[0],
            is_group_booking=random.random() < 0.05,
            group_name=f"Group {random.randint(1000, 9999)}" if random.random() < 0.05 else None,
            contact_email=f"booking{random.randint(100, 999)}@email.com",
            contact_phone=f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        )
    
    def generate_eticket(self, pnr: str, passenger: Passenger, 
                        itinerary: Itinerary, fare: Dict) -> ETicket:
        """Generate E-ticket for a passenger"""
        
        # Use first segment's marketing carrier
        airline_code = itinerary.segments[0].marketing_carrier
        airline_info = AIRLINES.get(airline_code, {"numeric_code": "000", "name": "Unknown"})
        
        ticket_number = self.generate_ticket_number(airline_code)
        
        # Generate coupons for each segment
        coupons = []
        for seg in itinerary.segments:
            coupons.append({
                "coupon_number": len(coupons) + 1,
                "origin": seg.origin,
                "destination": seg.destination,
                "flight_number": seg.flight_number,
                "date": seg.departure_date,
                "class": seg.booking_class,
                "status": "Open",  # Open, Used, Void
                "fare_basis": seg.fare_basis
            })
        
        # Fare calculation (simplified)
        fare_calc = f"{itinerary.segments[0].origin} {airline_code} {itinerary.segments[-1].destination} {fare['base_fare']} USD"
        
        # Endorsements based on fare type
        if "NR" in itinerary.segments[0].fare_basis:
            endorsements = "NON-REF/CHG FEE APPLIES"
        else:
            endorsements = "FULLY REFUNDABLE"
        
        return ETicket(
            ticket_number=ticket_number,
            airline_code=airline_info["numeric_code"],
            airline_name=airline_info["name"],
            passenger_name=passenger.full_name,
            issue_date=datetime.now().strftime("%Y-%m-%d"),
            issuing_agent=f"AUTO/{random.choice(BOOKING_CHANNELS).replace(' - ', '/')}",
            original_issue=True,
            conjunction_tickets=[],
            fare_calculation=fare_calc,
            endorsements=endorsements,
            tour_code=f"IT{random.randint(10000, 99999)}" if random.random() < 0.1 else None,
            ticket_status="Open",
            total_fare=fare['per_passenger'],
            currency=fare['currency'],
            coupons=coupons
        )
    
    def generate_complete_booking(self, 
                                  num_passengers: int = None,
                                  trip_type: str = None,
                                  cabin: str = None,
                                  with_connections: bool = None) -> Dict[str, Any]:
        """Generate a complete booking with all components"""
        
        if num_passengers is None:
            num_passengers = random.choices([1, 2, 3, 4], weights=[0.4, 0.35, 0.15, 0.1])[0]
        if trip_type is None:
            trip_type = random.choices(["One-Way", "Round-Trip"], weights=[0.3, 0.7])[0]
        if cabin is None:
            cabin = random.choices(
                ["Economy", "Premium Economy", "Business Class", "First Class"],
                weights=[0.7, 0.15, 0.12, 0.03]
            )[0]
        
        # Generate PNR
        pnr = self.generate_pnr()
        
        # Generate PNR record
        pnr_record = self.generate_pnr_record(pnr)
        
        # Generate itinerary
        itinerary = self.generate_itinerary(pnr, trip_type, cabin=cabin, with_connections=with_connections)
        
        # Generate passengers
        passengers = []
        for i in range(num_passengers):
            pax_type = "ADT" if i == 0 or random.random() < 0.8 else random.choice(["ADT", "CHD"])
            passengers.append(self.generate_passenger(pnr, i + 1, pax_type))
        
        # Calculate fare
        fare = self.calculate_fare(
            [s.to_dict() for s in itinerary.segments],
            cabin,
            num_passengers
        )
        
        # Generate E-tickets
        etickets = []
        for pax in passengers:
            etickets.append(self.generate_eticket(pnr, pax, itinerary, fare))
        
        return {
            "pnr": pnr,
            "pnr_record": pnr_record.to_dict(),
            "itinerary": itinerary.to_dict(),
            "passengers": [p.to_dict() for p in passengers],
            "etickets": [t.to_dict() for t in etickets],
            "fare": fare,
            "booking_status": pnr_record.ticket_status,
            "cabin_class": cabin,
            "trip_type": trip_type
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

_generator = None

def get_generator() -> PNRGenerator:
    """Get singleton generator instance"""
    global _generator
    if _generator is None:
        _generator = PNRGenerator()
    return _generator


def generate_booking(**kwargs) -> Dict[str, Any]:
    """Generate a complete booking"""
    return get_generator().generate_complete_booking(**kwargs)


def generate_bookings(count: int = 10, **kwargs) -> List[Dict[str, Any]]:
    """Generate multiple bookings"""
    return [get_generator().generate_complete_booking(**kwargs) for _ in range(count)]


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json
    
    print("Generating sample booking...")
    booking = generate_booking(num_passengers=2, trip_type="Round-Trip", with_connections=True)
    
    print(f"\n✈️ PNR: {booking['pnr']}")
    print(f"📋 Status: {booking['booking_status']}")
    print(f"💺 Cabin: {booking['cabin_class']}")
    print(f"🔄 Trip Type: {booking['trip_type']}")
    
    print(f"\n👥 Passengers ({len(booking['passengers'])}):")
    for pax in booking['passengers']:
        print(f"   - {pax['full_name']} ({pax['passenger_type']})")
    
    print(f"\n🎫 E-Tickets:")
    for tkt in booking['etickets']:
        print(f"   - {tkt['ticket_number']} ({tkt['passenger_name']})")
    
    print(f"\n✈️ Itinerary ({len(booking['itinerary']['segments'])} segments):")
    for seg in booking['itinerary']['segments']:
        conn = f" [Connection: {seg['connection_time_minutes']}min]" if seg['connection_time_minutes'] else ""
        print(f"   {seg['sequence_number']}. {seg['flight_number']}: {seg['origin']} → {seg['destination']}")
        print(f"      {seg['departure_date']} {seg['departure_time']} - {seg['arrival_time']} ({seg['duration_minutes']}min){conn}")
    
    print(f"\n💰 Fare: ${booking['fare']['total']} {booking['fare']['currency']}")
    print(f"   Base: ${booking['fare']['base_fare']} × {booking['fare']['passengers']} pax")
