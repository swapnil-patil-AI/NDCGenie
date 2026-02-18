"""
Flight Status and Disruption Management for NDC Genie
Real-time flight tracking and IROP (Irregular Operations) handling.

Week 3-4 Implementation
Version: 1.0.0
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class FlightStatus(Enum):
    """Real-time flight operational status"""
    SCHEDULED = "Scheduled"
    ON_TIME = "On Time"
    DELAYED = "Delayed"
    BOARDING = "Boarding"
    GATE_CLOSED = "Gate Closed"
    DEPARTED = "Departed"
    IN_FLIGHT = "In Flight"
    LANDING = "Landing"
    LANDED = "Landed"
    ARRIVED = "Arrived"
    CANCELLED = "Cancelled"
    DIVERTED = "Diverted"


class DelayReason(Enum):
    """Standardized IATA delay codes"""
    WEATHER = ("WX", "Weather", "Adverse weather conditions")
    AIR_TRAFFIC = ("AT", "Air Traffic Control", "ATC restrictions or flow control")
    LATE_AIRCRAFT = ("LA", "Late Aircraft", "Late arrival of inbound aircraft")
    TECHNICAL = ("TM", "Technical/Mechanical", "Aircraft technical issue")
    CREW = ("CR", "Crew", "Crew availability or legality")
    PASSENGER = ("PA", "Passenger", "Passenger-related delay")
    SECURITY = ("SE", "Security", "Security screening or incident")
    BAGGAGE = ("BG", "Baggage", "Baggage loading/handling")
    FUELING = ("FU", "Fueling", "Aircraft fueling delay")
    CATERING = ("CA", "Catering", "Catering loading delay")
    CARGO = ("CG", "Cargo", "Cargo/mail loading")
    RAMP = ("RP", "Ramp", "Ramp congestion or equipment")
    GATE = ("GT", "Gate", "Gate availability")
    DEICING = ("DI", "De-icing", "Aircraft de-icing required")
    BIRD_STRIKE = ("BS", "Bird Strike", "Bird strike investigation")
    MEDICAL = ("MD", "Medical", "Medical emergency")
    STRIKE = ("ST", "Industrial Action", "Strike or work action")
    GOVERNMENT = ("GV", "Government", "Government authority restrictions")


class DisruptionSeverity(Enum):
    """Disruption severity levels"""
    MINOR = "Minor"  # < 30 min delay
    MODERATE = "Moderate"  # 30-120 min delay
    MAJOR = "Major"  # 2-4 hour delay
    SEVERE = "Severe"  # > 4 hours or cancellation


class RecoveryAction(Enum):
    """Passenger recovery actions"""
    REBOOK_SAME_DAY = "Rebook on later same-day flight"
    REBOOK_NEXT_DAY = "Rebook on next available flight"
    REBOOK_PARTNER = "Rebook on partner airline"
    REFUND_FULL = "Full refund offered"
    REFUND_PARTIAL = "Partial refund offered"
    HOTEL_PROVIDED = "Hotel accommodation provided"
    MEAL_VOUCHER = "Meal voucher provided"
    TRANSPORT_PROVIDED = "Ground transportation provided"
    LOUNGE_ACCESS = "Airport lounge access"
    UPGRADE = "Complimentary upgrade offered"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FlightStatusUpdate:
    """Real-time flight status information"""
    flight_number: str
    flight_date: str
    airline_code: str
    airline_name: str
    origin: str
    origin_city: str
    destination: str
    destination_city: str
    
    # Scheduled times
    scheduled_departure: str
    scheduled_arrival: str
    
    # Actual/Estimated times
    estimated_departure: Optional[str]
    estimated_arrival: Optional[str]
    actual_departure: Optional[str]
    actual_arrival: Optional[str]
    
    # Status
    status: str
    status_code: str
    delay_minutes: int
    delay_reason_code: Optional[str]
    delay_reason: Optional[str]
    delay_description: Optional[str]
    
    # Airport info
    departure_terminal: Optional[str]
    departure_gate: Optional[str]
    arrival_terminal: Optional[str]
    arrival_gate: Optional[str]
    baggage_carousel: Optional[str]
    
    # Aircraft info
    aircraft_type: str
    aircraft_registration: Optional[str]
    
    # Progress (for in-flight)
    flight_progress_percent: Optional[int]
    altitude_feet: Optional[int]
    ground_speed_mph: Optional[int]
    heading: Optional[int]
    
    # Timestamps
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Disruption:
    """Flight disruption/IROP record"""
    disruption_id: str
    flight_number: str
    flight_date: str
    airline_code: str
    origin: str
    destination: str
    
    # Disruption details
    disruption_type: str  # Delay, Cancellation, Diversion
    severity: str
    delay_minutes: int
    is_cancelled: bool
    is_diverted: bool
    diversion_airport: Optional[str]
    
    # Cause
    cause_code: str
    cause_category: str
    cause_description: str
    is_airline_controllable: bool  # Important for EU261
    
    # Impact
    affected_passengers: int
    connecting_passengers_affected: int
    vip_passengers_affected: int
    unaccompanied_minors_affected: int
    wheelchair_passengers_affected: int
    
    # Recovery
    recovery_flights: List[Dict[str, Any]]
    passengers_rebooked: int
    passengers_refunded: int
    passengers_no_show: int
    
    # Services provided
    hotel_rooms_booked: int
    meal_vouchers_issued: int
    transport_arranged: int
    lounge_access_granted: int
    
    # Compensation
    eu261_eligible: bool
    eu261_eligible_passengers: int
    compensation_amount_per_pax: float
    total_compensation_liability: float
    
    # Timeline
    disruption_detected: str
    passengers_notified: str
    recovery_completed: Optional[str]
    
    # Notes
    operations_notes: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PassengerRecovery:
    """Individual passenger recovery action"""
    recovery_id: str
    pnr: str
    passenger_name: str
    original_flight: str
    original_date: str
    
    # Recovery action
    action_type: str
    new_flight: Optional[str]
    new_date: Optional[str]
    new_route: Optional[str]  # If via different connection
    
    # Status
    status: str  # Pending, Confirmed, Completed, Refused
    
    # Services
    hotel_name: Optional[str]
    hotel_confirmation: Optional[str]
    meal_voucher_amount: Optional[float]
    transport_details: Optional[str]
    
    # Compensation
    compensation_offered: float
    compensation_accepted: bool
    compensation_paid: bool
    
    # Communication
    notification_sent: bool
    notification_method: str  # SMS, Email, App, Phone
    notification_time: str
    customer_response: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
# FLIGHT STATUS SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class FlightStatusSimulator:
    """Simulates real-time flight status for demo purposes"""
    
    def __init__(self):
        self.flight_statuses: Dict[str, FlightStatusUpdate] = {}
        self.disruptions: Dict[str, Disruption] = {}
        self.recoveries: Dict[str, PassengerRecovery] = {}
    
    def simulate_flight_status(self, 
                               flight_number: str,
                               flight_date: str,
                               airline_code: str,
                               airline_name: str,
                               origin: str,
                               destination: str,
                               scheduled_departure: str,
                               scheduled_arrival: str,
                               aircraft_type: str = "A320") -> FlightStatusUpdate:
        """Generate simulated flight status"""
        
        # Parse scheduled times
        sched_dep = datetime.strptime(f"{flight_date} {scheduled_departure}", "%Y-%m-%d %H:%M")
        sched_arr = datetime.strptime(f"{flight_date} {scheduled_arrival}", "%Y-%m-%d %H:%M")
        now = datetime.now()
        
        # Determine status based on current time relative to schedule
        time_to_departure = (sched_dep - now).total_seconds() / 60  # minutes
        time_since_departure = (now - sched_dep).total_seconds() / 60
        flight_duration = (sched_arr - sched_dep).total_seconds() / 60
        
        # Random delay/issue probability
        has_delay = random.random() < 0.25
        is_cancelled = random.random() < 0.03
        
        delay_minutes = 0
        delay_reason_code = None
        delay_reason = None
        delay_description = None
        
        if is_cancelled:
            status = FlightStatus.CANCELLED
            delay_reason_enum = random.choice(list(DelayReason))
            delay_reason_code = delay_reason_enum.value[0]
            delay_reason = delay_reason_enum.value[1]
            delay_description = delay_reason_enum.value[2]
        elif has_delay:
            delay_minutes = random.choice([15, 30, 45, 60, 90, 120, 180, 240])
            delay_reason_enum = random.choice(list(DelayReason))
            delay_reason_code = delay_reason_enum.value[0]
            delay_reason = delay_reason_enum.value[1]
            delay_description = delay_reason_enum.value[2]
        
        # Determine status
        if is_cancelled:
            status = FlightStatus.CANCELLED
        elif time_to_departure > 180:  # More than 3 hours out
            status = FlightStatus.SCHEDULED
        elif time_to_departure > 60:  # 1-3 hours out
            status = FlightStatus.ON_TIME if not has_delay else FlightStatus.DELAYED
        elif time_to_departure > 30:  # 30-60 min out
            status = FlightStatus.ON_TIME if not has_delay else FlightStatus.DELAYED
        elif time_to_departure > 0:  # Within 30 min
            status = FlightStatus.BOARDING if random.random() < 0.7 else FlightStatus.DELAYED
        elif time_since_departure < flight_duration * 0.1:  # Just departed
            status = FlightStatus.DEPARTED
        elif time_since_departure < flight_duration * 0.9:  # In flight
            status = FlightStatus.IN_FLIGHT
        elif time_since_departure < flight_duration:  # About to land
            status = FlightStatus.LANDING
        elif time_since_departure < flight_duration + 15:  # Just landed
            status = FlightStatus.LANDED
        else:  # At gate
            status = FlightStatus.ARRIVED
        
        # Calculate estimated times
        est_dep = sched_dep + timedelta(minutes=delay_minutes) if delay_minutes else sched_dep
        est_arr = sched_arr + timedelta(minutes=delay_minutes) if delay_minutes else sched_arr
        
        # Actual times if departed
        actual_dep = None
        actual_arr = None
        if status in [FlightStatus.DEPARTED, FlightStatus.IN_FLIGHT, FlightStatus.LANDING, 
                      FlightStatus.LANDED, FlightStatus.ARRIVED]:
            actual_dep = est_dep.strftime("%H:%M")
        if status == FlightStatus.ARRIVED:
            actual_arr = est_arr.strftime("%H:%M")
        
        # Flight progress for in-flight
        progress = None
        altitude = None
        speed = None
        heading = None
        if status == FlightStatus.IN_FLIGHT:
            progress = int((time_since_departure / flight_duration) * 100)
            progress = min(95, max(5, progress))
            altitude = random.randint(30000, 42000)
            speed = random.randint(450, 580)
            heading = random.randint(0, 359)
        
        # Get city names
        from data.pnr_generator import AIRPORTS
        origin_city = AIRPORTS.get(origin, {}).get("city", origin)
        dest_city = AIRPORTS.get(destination, {}).get("city", destination)
        
        flight_status = FlightStatusUpdate(
            flight_number=flight_number,
            flight_date=flight_date,
            airline_code=airline_code,
            airline_name=airline_name,
            origin=origin,
            origin_city=origin_city,
            destination=destination,
            destination_city=dest_city,
            scheduled_departure=scheduled_departure,
            scheduled_arrival=scheduled_arrival,
            estimated_departure=est_dep.strftime("%H:%M") if delay_minutes else None,
            estimated_arrival=est_arr.strftime("%H:%M") if delay_minutes else None,
            actual_departure=actual_dep,
            actual_arrival=actual_arr,
            status=status.value,
            status_code=status.name,
            delay_minutes=delay_minutes,
            delay_reason_code=delay_reason_code,
            delay_reason=delay_reason,
            delay_description=delay_description,
            departure_terminal=random.choice(["1", "2", "3", "A", "B", "C"]),
            departure_gate=f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 50)}",
            arrival_terminal=random.choice(["1", "2", "3", "A", "B", "C"]),
            arrival_gate=f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 50)}" if status == FlightStatus.ARRIVED else None,
            baggage_carousel=str(random.randint(1, 20)) if status == FlightStatus.ARRIVED else None,
            aircraft_type=aircraft_type,
            aircraft_registration=f"N{random.randint(100, 999)}{random.choice(['AA', 'UA', 'DL', 'WN'])}",
            flight_progress_percent=progress,
            altitude_feet=altitude,
            ground_speed_mph=speed,
            heading=heading,
            last_updated=datetime.now().isoformat()
        )
        
        # Store for later retrieval
        key = f"{flight_number}_{flight_date}"
        self.flight_statuses[key] = flight_status
        
        return flight_status
    
    def create_disruption(self,
                         flight_number: str,
                         flight_date: str,
                         airline_code: str,
                         origin: str,
                         destination: str,
                         disruption_type: str = "Delay",
                         delay_minutes: int = 180,
                         affected_passengers: int = 150) -> Disruption:
        """Create a flight disruption record"""
        
        # Determine cause
        cause = random.choice(list(DelayReason))
        
        # Is it airline controllable?
        controllable_causes = ["TM", "CR", "BG", "CA", "CG", "RP", "GT"]
        is_controllable = cause.value[0] in controllable_causes
        
        # Determine severity
        if disruption_type == "Cancellation":
            severity = DisruptionSeverity.SEVERE.value
            is_cancelled = True
            delay_minutes = 0
        elif delay_minutes < 30:
            severity = DisruptionSeverity.MINOR.value
            is_cancelled = False
        elif delay_minutes < 120:
            severity = DisruptionSeverity.MODERATE.value
            is_cancelled = False
        elif delay_minutes < 240:
            severity = DisruptionSeverity.MAJOR.value
            is_cancelled = False
        else:
            severity = DisruptionSeverity.SEVERE.value
            is_cancelled = False
        
        # EU261 eligibility (simplified)
        # Eligible if: >3hr delay, airline controllable, within EU or EU carrier
        eu261_eligible = delay_minutes >= 180 and is_controllable
        
        # Compensation amount (EU261 rates)
        compensation = 0
        if eu261_eligible:
            # Simplified: would need actual distance
            compensation = random.choice([250, 400, 600])  # EUR
        
        connecting_affected = int(affected_passengers * 0.25)
        vip_affected = int(affected_passengers * 0.05)
        
        disruption = Disruption(
            disruption_id=f"DIS-{flight_number}-{flight_date.replace('-', '')}",
            flight_number=flight_number,
            flight_date=flight_date,
            airline_code=airline_code,
            origin=origin,
            destination=destination,
            disruption_type=disruption_type,
            severity=severity,
            delay_minutes=delay_minutes,
            is_cancelled=is_cancelled,
            is_diverted=False,
            diversion_airport=None,
            cause_code=cause.value[0],
            cause_category=cause.value[1],
            cause_description=cause.value[2],
            is_airline_controllable=is_controllable,
            affected_passengers=affected_passengers,
            connecting_passengers_affected=connecting_affected,
            vip_passengers_affected=vip_affected,
            unaccompanied_minors_affected=random.randint(0, 3),
            wheelchair_passengers_affected=random.randint(0, 5),
            recovery_flights=[],
            passengers_rebooked=int(affected_passengers * 0.7) if is_cancelled else 0,
            passengers_refunded=int(affected_passengers * 0.2) if is_cancelled else 0,
            passengers_no_show=int(affected_passengers * 0.1),
            hotel_rooms_booked=int(affected_passengers * 0.3) if delay_minutes > 360 or is_cancelled else 0,
            meal_vouchers_issued=affected_passengers if delay_minutes > 120 else 0,
            transport_arranged=int(affected_passengers * 0.1) if delay_minutes > 240 else 0,
            lounge_access_granted=vip_affected,
            eu261_eligible=eu261_eligible,
            eu261_eligible_passengers=affected_passengers if eu261_eligible else 0,
            compensation_amount_per_pax=compensation,
            total_compensation_liability=compensation * affected_passengers if eu261_eligible else 0,
            disruption_detected=datetime.now().isoformat(),
            passengers_notified=(datetime.now() + timedelta(minutes=15)).isoformat(),
            recovery_completed=None,
            operations_notes=[
                f"Disruption detected: {cause.value[1]}",
                f"Ops team notified",
                f"Customer service briefed"
            ]
        )
        
        # Store
        self.disruptions[disruption.disruption_id] = disruption
        
        return disruption
    
    def get_airport_departures(self, airport_code: str, 
                               date: str = None) -> List[FlightStatusUpdate]:
        """Get all departures from an airport"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        return [fs for fs in self.flight_statuses.values() 
                if fs.origin == airport_code and fs.flight_date == date]
    
    def get_airport_arrivals(self, airport_code: str,
                            date: str = None) -> List[FlightStatusUpdate]:
        """Get all arrivals to an airport"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        return [fs for fs in self.flight_statuses.values()
                if fs.destination == airport_code and fs.flight_date == date]
    
    def get_delayed_flights(self, min_delay: int = 30) -> List[FlightStatusUpdate]:
        """Get all flights with delays above threshold"""
        return [fs for fs in self.flight_statuses.values()
                if fs.delay_minutes >= min_delay]
    
    def get_cancelled_flights(self) -> List[FlightStatusUpdate]:
        """Get all cancelled flights"""
        return [fs for fs in self.flight_statuses.values()
                if fs.status == FlightStatus.CANCELLED.value]
    
    def get_operations_summary(self, date: str = None) -> Dict[str, Any]:
        """Get operations summary for a date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        flights = [fs for fs in self.flight_statuses.values() if fs.flight_date == date]
        
        on_time = sum(1 for f in flights if f.delay_minutes == 0 and f.status != FlightStatus.CANCELLED.value)
        delayed = sum(1 for f in flights if f.delay_minutes > 0)
        cancelled = sum(1 for f in flights if f.status == FlightStatus.CANCELLED.value)
        
        total = len(flights)
        otp = (on_time / total * 100) if total > 0 else 0
        
        delay_reasons = {}
        for f in flights:
            if f.delay_reason:
                delay_reasons[f.delay_reason] = delay_reasons.get(f.delay_reason, 0) + 1
        
        return {
            "date": date,
            "total_flights": total,
            "on_time": on_time,
            "delayed": delayed,
            "cancelled": cancelled,
            "on_time_performance": round(otp, 1),
            "average_delay_minutes": round(sum(f.delay_minutes for f in flights) / total, 1) if total > 0 else 0,
            "delay_reasons": delay_reasons,
            "disruptions": len([d for d in self.disruptions.values() if d.flight_date == date]),
            "total_compensation_liability": sum(d.total_compensation_liability for d in self.disruptions.values() if d.flight_date == date)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

_simulator = None

def get_simulator() -> FlightStatusSimulator:
    """Get singleton simulator instance"""
    global _simulator
    if _simulator is None:
        _simulator = FlightStatusSimulator()
    return _simulator


def simulate_daily_operations(num_flights: int = 50) -> Dict[str, Any]:
    """Simulate a full day of flight operations"""
    from data.pnr_generator import AIRLINES, AIRPORTS, ROUTES
    
    simulator = get_simulator()
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Generate flights throughout the day
    for i in range(num_flights):
        route = random.choice(ROUTES)
        airline = random.choice(list(AIRLINES.keys()))
        airline_name = AIRLINES[airline]["name"]
        
        dep_hour = random.randint(6, 22)
        dep_min = random.choice([0, 15, 30, 45])
        dep_time = f"{dep_hour:02d}:{dep_min:02d}"
        
        arr_time = (datetime.strptime(dep_time, "%H:%M") + timedelta(minutes=route[2])).strftime("%H:%M")
        
        flight_num = f"{airline}{random.randint(100, 9999)}"
        
        simulator.simulate_flight_status(
            flight_number=flight_num,
            flight_date=date,
            airline_code=airline,
            airline_name=airline_name,
            origin=route[0],
            destination=route[1],
            scheduled_departure=dep_time,
            scheduled_arrival=arr_time,
            aircraft_type=random.choice(["A320", "B737", "A321", "B777", "A350"])
        )
    
    # Create some disruptions
    num_disruptions = random.randint(2, 8)
    flights = list(simulator.flight_statuses.values())
    
    for _ in range(num_disruptions):
        flight = random.choice(flights)
        disruption_type = random.choices(["Delay", "Cancellation"], weights=[0.8, 0.2])[0]
        delay = random.choice([30, 60, 90, 120, 180, 240, 300]) if disruption_type == "Delay" else 0
        
        simulator.create_disruption(
            flight_number=flight.flight_number,
            flight_date=flight.flight_date,
            airline_code=flight.airline_code,
            origin=flight.origin,
            destination=flight.destination,
            disruption_type=disruption_type,
            delay_minutes=delay,
            affected_passengers=random.randint(80, 250)
        )
    
    return simulator.get_operations_summary(date)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Simulating daily operations...")
    summary = simulate_daily_operations(30)
    
    print(f"\n📊 OPERATIONS SUMMARY - {summary['date']}")
    print("=" * 50)
    print(f"Total Flights: {summary['total_flights']}")
    print(f"✅ On Time: {summary['on_time']} ({summary['on_time_performance']}%)")
    print(f"⚠️ Delayed: {summary['delayed']}")
    print(f"❌ Cancelled: {summary['cancelled']}")
    print(f"Average Delay: {summary['average_delay_minutes']} min")
    print(f"💰 Compensation Liability: €{summary['total_compensation_liability']:,.0f}")
    
    print(f"\n🔴 DISRUPTIONS: {summary['disruptions']}")
    
    simulator = get_simulator()
    
    print("\n⚠️ DELAYED FLIGHTS:")
    for flight in simulator.get_delayed_flights(60)[:5]:
        print(f"   {flight.flight_number}: {flight.origin}→{flight.destination} +{flight.delay_minutes}min ({flight.delay_reason})")
    
    print("\n❌ CANCELLED FLIGHTS:")
    for flight in simulator.get_cancelled_flights()[:5]:
        print(f"   {flight.flight_number}: {flight.origin}→{flight.destination} ({flight.delay_reason})")
