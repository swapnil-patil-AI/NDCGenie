"""
Compensation Calculator and Fraud Detection for NDC Genie
EU261/DOT compliance and payment fraud scoring.

Week 5-6 Implementation
Version: 1.0.0
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# AIRPORT COORDINATES (for distance calculation)
# ═══════════════════════════════════════════════════════════════════════════════

AIRPORT_COORDINATES = {
    # US
    "JFK": (40.6413, -73.7781), "LAX": (33.9416, -118.4085), "ORD": (41.9742, -87.9073),
    "DFW": (32.8998, -97.0403), "DEN": (39.8561, -104.6737), "SFO": (37.6213, -122.3790),
    "SEA": (47.4502, -122.3088), "ATL": (33.6407, -84.4277), "MIA": (25.7959, -80.2870),
    "BOS": (42.3656, -71.0096), "PHX": (33.4373, -112.0078), "IAH": (29.9902, -95.3368),
    "MSP": (44.8848, -93.2223), "DTW": (42.2162, -83.3554), "PHL": (39.8729, -75.2437),
    # Europe
    "LHR": (51.4700, -0.4543), "CDG": (49.0097, 2.5479), "FRA": (50.0379, 8.5622),
    "AMS": (52.3105, 4.7683), "MAD": (40.4983, -3.5676), "FCO": (41.8003, 12.2389),
    "MUC": (48.3537, 11.7750), "BCN": (41.2971, 2.0785), "LGW": (51.1537, -0.1821),
    # Middle East
    "DXB": (25.2532, 55.3657), "DOH": (25.2609, 51.6138), "AUH": (24.4331, 54.6511),
    # Asia
    "SIN": (1.3644, 103.9915), "HKG": (22.3080, 113.9185), "NRT": (35.7720, 140.3929),
    "PEK": (40.0799, 116.6031), "ICN": (37.4602, 126.4407), "BKK": (13.6900, 100.7501),
    # Oceania
    "SYD": (-33.9399, 151.1753), "MEL": (-37.6690, 144.8410), "AKL": (-37.0082, 174.7850),
    # Americas
    "YYZ": (43.6777, -79.6248), "MEX": (19.4361, -99.0719), "GRU": (-23.4356, -46.4731),
    "EZE": (-34.8222, -58.5358), "SCL": (-33.3930, -70.7858),
}


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class CompensationRegulation(Enum):
    """Compensation regulations"""
    EU261 = "EU Regulation 261/2004"
    DOT = "US DOT Regulations"
    APPR = "Canada Air Passenger Protection Regulations"
    UK261 = "UK261 (Post-Brexit EU261)"
    NONE = "No specific regulation applies"


class FraudRiskLevel(Enum):
    """Fraud risk levels"""
    LOW = ("Low", 0, 30, "Auto-approve")
    MEDIUM = ("Medium", 31, 60, "3DS verification required")
    HIGH = ("High", 61, 85, "Manual review required")
    CRITICAL = ("Critical", 86, 100, "Auto-decline")


class FraudIndicator(Enum):
    """Fraud risk indicators"""
    IP_MISMATCH = ("IP Geolocation Mismatch", 15, "IP country doesn't match billing country")
    VELOCITY = ("Velocity Check Failed", 20, "Multiple bookings in short time")
    BIN_MISMATCH = ("BIN Country Mismatch", 12, "Card issuing country differs from billing")
    DEVICE_NEW = ("New Device", 8, "First time device fingerprint")
    HIGH_VALUE = ("High Value Transaction", 10, "Transaction above normal threshold")
    ONE_WAY_INTL = ("One-way International", 12, "One-way ticket to high-risk destination")
    LAST_MINUTE = ("Last Minute Booking", 8, "Booking within 24 hours of departure")
    MULTIPLE_CARDS = ("Multiple Card Attempts", 18, "Several cards tried before success")
    NAME_MISMATCH = ("Name Mismatch", 15, "Cardholder name differs from passenger")
    EMAIL_DISPOSABLE = ("Disposable Email", 10, "Using temporary/disposable email")
    PROXY_VPN = ("Proxy/VPN Detected", 12, "Connection via proxy or VPN")
    FAILED_3DS = ("Failed 3DS", 20, "3D Secure authentication failed")
    PREVIOUS_CHARGEBACK = ("Previous Chargeback", 25, "Customer has chargeback history")
    KNOWN_FRAUD_BIN = ("Known Fraud BIN", 30, "Card BIN associated with fraud")


# ═══════════════════════════════════════════════════════════════════════════════
# DISTANCE CALCULATION
# ═══════════════════════════════════════════════════════════════════════════════

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in kilometers"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def get_flight_distance(origin: str, destination: str) -> Optional[float]:
    """Get distance between two airports in kilometers"""
    if origin in AIRPORT_COORDINATES and destination in AIRPORT_COORDINATES:
        lat1, lon1 = AIRPORT_COORDINATES[origin]
        lat2, lon2 = AIRPORT_COORDINATES[destination]
        return round(haversine_distance(lat1, lon1, lat2, lon2), 0)
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# EU261 COMPENSATION CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CompensationResult:
    """Result of compensation calculation"""
    eligible: bool
    regulation: str
    reason: str
    distance_km: float
    delay_minutes: int
    compensation_amount: float
    currency: str
    additional_rights: List[str]
    exceptions: List[str]
    calculation_details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EU261Calculator:
    """
    EU261/2004 Compensation Calculator
    
    Covers flights:
    - Departing from EU airport (any airline)
    - Arriving at EU airport (EU airline only)
    """
    
    # EU/EEA countries
    EU_COUNTRIES = {
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
        "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
        "SI", "ES", "SE",  # EU members
        "IS", "LI", "NO",  # EEA
        "CH",  # Switzerland (bilateral agreement)
    }
    
    # EU airlines (IATA codes) - simplified list
    EU_AIRLINES = {
        "BA", "AF", "LH", "KL", "IB", "AZ", "SK", "AY", "EI", "LX", "OS", "SN",
        "TP", "LO", "OK", "RO", "JU", "OU", "BT", "FR", "U2", "W6", "VY", "DY"
    }
    
    # Airport to country mapping
    AIRPORT_COUNTRIES = {
        "LHR": "GB", "LGW": "GB", "STN": "GB", "MAN": "GB", "EDI": "GB",  # UK (post-Brexit: UK261)
        "CDG": "FR", "ORY": "FR", "NCE": "FR", "LYS": "FR",
        "FRA": "DE", "MUC": "DE", "TXL": "DE", "DUS": "DE", "HAM": "DE",
        "AMS": "NL", "MAD": "ES", "BCN": "ES", "FCO": "IT", "MXP": "IT",
        "VIE": "AT", "ZRH": "CH", "BRU": "BE", "CPH": "DK", "ARN": "SE",
        "OSL": "NO", "HEL": "FI", "DUB": "IE", "LIS": "PT", "ATH": "GR",
        "WAW": "PL", "PRG": "CZ", "BUD": "HU",
        # Non-EU
        "JFK": "US", "LAX": "US", "ORD": "US", "DFW": "US", "DEN": "US",
        "SFO": "US", "SEA": "US", "ATL": "US", "MIA": "US", "BOS": "US",
        "DXB": "AE", "DOH": "QA", "SIN": "SG", "HKG": "HK", "NRT": "JP",
        "SYD": "AU", "YYZ": "CA", "MEX": "MX",
    }
    
    # Compensation amounts in EUR
    COMPENSATION_RATES = {
        "short": 250,   # < 1500 km
        "medium": 400,  # 1500-3500 km
        "long": 600,    # > 3500 km
    }
    
    # Delay thresholds for compensation
    DELAY_THRESHOLDS = {
        "short": 180,   # 3 hours for short-haul
        "medium": 180,  # 3 hours for medium-haul
        "long": 240,    # 4 hours for long-haul
    }
    
    def __init__(self):
        pass
    
    def is_eu_airport(self, airport_code: str) -> bool:
        """Check if airport is in EU/EEA"""
        country = self.AIRPORT_COUNTRIES.get(airport_code, "")
        return country in self.EU_COUNTRIES
    
    def is_uk_airport(self, airport_code: str) -> bool:
        """Check if airport is in UK"""
        country = self.AIRPORT_COUNTRIES.get(airport_code, "")
        return country == "GB"
    
    def is_eu_airline(self, airline_code: str) -> bool:
        """Check if airline is EU carrier"""
        return airline_code in self.EU_AIRLINES
    
    def get_distance_category(self, distance_km: float) -> str:
        """Get distance category"""
        if distance_km < 1500:
            return "short"
        elif distance_km <= 3500:
            return "medium"
        else:
            return "long"
    
    def calculate_compensation(self,
                               origin: str,
                               destination: str,
                               airline_code: str,
                               delay_minutes: int,
                               is_cancelled: bool = False,
                               is_denied_boarding: bool = False,
                               is_airline_fault: bool = True,
                               extraordinary_circumstances: bool = False,
                               advance_notice_days: int = 0,
                               alternative_arrival_delay: int = None) -> CompensationResult:
        """
        Calculate EU261 compensation.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            airline_code: Operating airline code
            delay_minutes: Arrival delay in minutes
            is_cancelled: Was flight cancelled
            is_denied_boarding: Was passenger denied boarding
            is_airline_fault: Is delay within airline's control
            extraordinary_circumstances: Weather, strike, security, etc.
            advance_notice_days: Days notice given for cancellation
            alternative_arrival_delay: Delay vs original when rerouted
        """
        
        # Determine applicable regulation
        origin_eu = self.is_eu_airport(origin)
        dest_eu = self.is_eu_airport(destination)
        origin_uk = self.is_uk_airport(origin)
        dest_uk = self.is_uk_airport(destination)
        eu_airline = self.is_eu_airline(airline_code)
        
        # Determine which regulation applies
        if origin_eu or (dest_eu and eu_airline):
            regulation = CompensationRegulation.EU261
        elif origin_uk or (dest_uk and airline_code == "BA"):  # Simplified UK261
            regulation = CompensationRegulation.UK261
        else:
            regulation = CompensationRegulation.NONE
        
        # Get flight distance
        distance = get_flight_distance(origin, destination)
        if distance is None:
            distance = 2000  # Default estimate
        
        distance_category = self.get_distance_category(distance)
        
        # Initialize result
        eligible = False
        reason = ""
        compensation = 0
        additional_rights = []
        exceptions = []
        
        # Check if regulation applies
        if regulation == CompensationRegulation.NONE:
            reason = "Flight not covered by EU261 (neither departing from EU nor arriving at EU on EU carrier)"
            return CompensationResult(
                eligible=False,
                regulation=regulation.value,
                reason=reason,
                distance_km=distance,
                delay_minutes=delay_minutes,
                compensation_amount=0,
                currency="EUR",
                additional_rights=[],
                exceptions=[],
                calculation_details={"distance_category": distance_category}
            )
        
        # Check extraordinary circumstances
        if extraordinary_circumstances:
            exceptions.append("Extraordinary circumstances may exempt airline from compensation")
            reason = "Extraordinary circumstances (weather, strike, security, etc.) - airline may be exempt"
        
        # Denied boarding - always compensated (unless voluntary)
        if is_denied_boarding:
            eligible = True
            compensation = self.COMPENSATION_RATES[distance_category]
            reason = f"Denied boarding compensation: €{compensation}"
            additional_rights = [
                "Choice of refund or re-routing",
                "Care (meals, refreshments, hotel if needed)",
                "2 phone calls/emails"
            ]
        
        # Cancellation
        elif is_cancelled:
            if advance_notice_days >= 14:
                eligible = False
                reason = "Cancellation notified more than 14 days in advance - no compensation"
            elif advance_notice_days >= 7:
                # Check re-routing criteria
                if alternative_arrival_delay and alternative_arrival_delay <= 240:
                    eligible = False
                    reason = "Cancellation 7-14 days notice with suitable alternative - no compensation"
                else:
                    eligible = True
                    compensation = self.COMPENSATION_RATES[distance_category]
            elif advance_notice_days > 0:
                # Less than 7 days
                if alternative_arrival_delay and alternative_arrival_delay <= 120:
                    eligible = False
                    reason = "Cancellation <7 days with suitable alternative (<2hr delay) - no compensation"
                else:
                    eligible = True
                    compensation = self.COMPENSATION_RATES[distance_category]
            else:
                # No advance notice (same day)
                eligible = True
                compensation = self.COMPENSATION_RATES[distance_category]
                reason = f"Cancellation without adequate notice: €{compensation}"
            
            additional_rights = [
                "Choice of: full refund OR re-routing",
                "Care during wait (meals, refreshments)",
                "Hotel if overnight stay required",
                "Transport to/from hotel"
            ]
        
        # Delay
        else:
            delay_threshold = self.DELAY_THRESHOLDS[distance_category]
            
            if delay_minutes >= delay_threshold:
                eligible = True
                compensation = self.COMPENSATION_RATES[distance_category]
                
                # 50% reduction for 3-4 hour delay on long-haul
                if distance_category == "long" and delay_minutes < 240:
                    compensation = compensation // 2
                
                reason = f"Delay of {delay_minutes} minutes exceeds {delay_threshold} minute threshold: €{compensation}"
                
                # Additional rights based on delay
                if delay_minutes >= 120:
                    additional_rights.append("Meals and refreshments")
                    additional_rights.append("2 phone calls/emails")
                if delay_minutes >= 300 or (delay_minutes >= 180 and datetime.now().hour >= 22):
                    additional_rights.append("Hotel accommodation if overnight")
                    additional_rights.append("Transport to/from hotel")
                if delay_minutes >= 300:
                    additional_rights.append("Right to refund if delay >5 hours and choose not to travel")
            else:
                reason = f"Delay of {delay_minutes} minutes below {delay_threshold} minute threshold - no compensation"
                
                # Still entitled to care
                if delay_minutes >= 120:
                    additional_rights.append("Meals and refreshments (care)")
        
        # Apply extraordinary circumstances exception
        if extraordinary_circumstances and eligible and is_airline_fault:
            exceptions.append("Compensation may be waived due to extraordinary circumstances")
        
        return CompensationResult(
            eligible=eligible and not extraordinary_circumstances,
            regulation=regulation.value,
            reason=reason,
            distance_km=distance,
            delay_minutes=delay_minutes,
            compensation_amount=compensation if eligible and not extraordinary_circumstances else 0,
            currency="EUR",
            additional_rights=additional_rights,
            exceptions=exceptions,
            calculation_details={
                "distance_category": distance_category,
                "origin_eu": origin_eu,
                "destination_eu": dest_eu,
                "eu_airline": eu_airline,
                "threshold_minutes": self.DELAY_THRESHOLDS.get(distance_category, 180)
            }
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FRAUD DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FraudAssessment:
    """Fraud risk assessment result"""
    assessment_id: str
    transaction_id: str
    timestamp: str
    
    # Scores
    risk_score: int
    risk_level: str
    risk_description: str
    
    # Indicators found
    indicators: List[Dict[str, Any]]
    
    # Recommendation
    recommended_action: str
    requires_3ds: bool
    requires_manual_review: bool
    auto_decline: bool
    
    # Additional data
    chargeback_probability: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FraudDetector:
    """Payment fraud detection and scoring"""
    
    # High-risk countries for one-way tickets
    HIGH_RISK_DESTINATIONS = {"NG", "GH", "RO", "BG", "UA", "RU", "PK", "BD"}
    
    # Disposable email domains
    DISPOSABLE_DOMAINS = {
        "tempmail.com", "throwaway.com", "mailinator.com", "guerrillamail.com",
        "10minutemail.com", "trashmail.com", "fakeinbox.com", "sharklasers.com"
    }
    
    def __init__(self):
        self.assessment_counter = 0
    
    def assess_transaction(self,
                          transaction_id: str,
                          amount: float,
                          currency: str,
                          card_bin: str,
                          card_country: str,
                          billing_country: str,
                          ip_address: str,
                          ip_country: str,
                          email: str,
                          passenger_names: List[str],
                          cardholder_name: str,
                          is_one_way: bool,
                          destination_country: str,
                          hours_to_departure: int,
                          device_fingerprint: str,
                          is_new_device: bool,
                          is_vpn: bool,
                          previous_chargebacks: int,
                          failed_attempts: int,
                          bookings_last_hour: int) -> FraudAssessment:
        """
        Assess a transaction for fraud risk.
        
        Returns risk score 0-100 and recommended action.
        """
        
        self.assessment_counter += 1
        indicators = []
        total_score = 0
        
        # Check each indicator
        
        # 1. IP/Billing country mismatch
        if ip_country != billing_country:
            indicator = FraudIndicator.IP_MISMATCH
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": f"IP country ({ip_country}) differs from billing ({billing_country})"
            })
            total_score += indicator.value[1]
        
        # 2. BIN country mismatch
        if card_country != billing_country:
            indicator = FraudIndicator.BIN_MISMATCH
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": f"Card issued in {card_country}, billing in {billing_country}"
            })
            total_score += indicator.value[1]
        
        # 3. Velocity check
        if bookings_last_hour >= 3:
            indicator = FraudIndicator.VELOCITY
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": f"{bookings_last_hour} bookings in last hour"
            })
            total_score += indicator.value[1]
        
        # 4. New device
        if is_new_device:
            indicator = FraudIndicator.DEVICE_NEW
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": indicator.value[2]
            })
            total_score += indicator.value[1]
        
        # 5. High value
        if amount > 3000:
            indicator = FraudIndicator.HIGH_VALUE
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": f"Transaction amount ${amount:,.2f} above threshold"
            })
            total_score += indicator.value[1]
        
        # 6. One-way to high-risk destination
        if is_one_way and destination_country in self.HIGH_RISK_DESTINATIONS:
            indicator = FraudIndicator.ONE_WAY_INTL
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": f"One-way ticket to high-risk destination ({destination_country})"
            })
            total_score += indicator.value[1]
        
        # 7. Last minute booking
        if hours_to_departure <= 24:
            indicator = FraudIndicator.LAST_MINUTE
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": f"Booking {hours_to_departure} hours before departure"
            })
            total_score += indicator.value[1]
        
        # 8. Multiple failed attempts
        if failed_attempts >= 2:
            indicator = FraudIndicator.MULTIPLE_CARDS
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": f"{failed_attempts} failed payment attempts"
            })
            total_score += indicator.value[1]
        
        # 9. Name mismatch (simplified)
        cardholder_parts = set(cardholder_name.upper().split())
        passenger_match = any(
            set(p.upper().split()) & cardholder_parts
            for p in passenger_names
        )
        if not passenger_match:
            indicator = FraudIndicator.NAME_MISMATCH
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": "Cardholder name doesn't match any passenger"
            })
            total_score += indicator.value[1]
        
        # 10. Disposable email
        email_domain = email.split("@")[-1].lower()
        if email_domain in self.DISPOSABLE_DOMAINS:
            indicator = FraudIndicator.EMAIL_DISPOSABLE
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": f"Disposable email domain: {email_domain}"
            })
            total_score += indicator.value[1]
        
        # 11. VPN/Proxy
        if is_vpn:
            indicator = FraudIndicator.PROXY_VPN
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": indicator.value[2]
            })
            total_score += indicator.value[1]
        
        # 12. Previous chargebacks
        if previous_chargebacks > 0:
            indicator = FraudIndicator.PREVIOUS_CHARGEBACK
            indicators.append({
                "code": indicator.name,
                "name": indicator.value[0],
                "score": indicator.value[1],
                "description": f"{previous_chargebacks} previous chargeback(s)"
            })
            total_score += indicator.value[1]
        
        # Cap score at 100
        total_score = min(100, total_score)
        
        # Determine risk level
        if total_score <= 30:
            risk_level = FraudRiskLevel.LOW
        elif total_score <= 60:
            risk_level = FraudRiskLevel.MEDIUM
        elif total_score <= 85:
            risk_level = FraudRiskLevel.HIGH
        else:
            risk_level = FraudRiskLevel.CRITICAL
        
        # Determine action
        requires_3ds = risk_level in [FraudRiskLevel.MEDIUM, FraudRiskLevel.HIGH]
        requires_manual = risk_level == FraudRiskLevel.HIGH
        auto_decline = risk_level == FraudRiskLevel.CRITICAL
        
        if auto_decline:
            action = "Decline transaction"
        elif requires_manual:
            action = "Route to manual review"
        elif requires_3ds:
            action = "Require 3D Secure verification"
        else:
            action = "Approve transaction"
        
        # Estimate chargeback probability
        chargeback_prob = min(0.95, (total_score / 100) * 0.5 + (previous_chargebacks * 0.15))
        
        return FraudAssessment(
            assessment_id=f"FRD-{datetime.now().strftime('%Y%m%d')}-{self.assessment_counter:05d}",
            transaction_id=transaction_id,
            timestamp=datetime.now().isoformat(),
            risk_score=total_score,
            risk_level=risk_level.value[0],
            risk_description=risk_level.value[3],
            indicators=indicators,
            recommended_action=action,
            requires_3ds=requires_3ds,
            requires_manual_review=requires_manual,
            auto_decline=auto_decline,
            chargeback_probability=round(chargeback_prob, 3),
            confidence=0.85  # Model confidence
        )
    
    def simulate_assessment(self, transaction_id: str, amount: float = None) -> FraudAssessment:
        """Generate a simulated fraud assessment with random risk factors"""
        
        if amount is None:
            amount = random.uniform(200, 5000)
        
        # Simulate random conditions
        countries = ["US", "UK", "CA", "DE", "FR", "IN", "NG", "RO", "BR", "AU"]
        
        billing_country = random.choice(countries[:6])  # Usually legitimate
        ip_country = billing_country if random.random() < 0.8 else random.choice(countries)
        card_country = billing_country if random.random() < 0.9 else random.choice(countries)
        
        is_high_risk = random.random() < 0.15
        
        return self.assess_transaction(
            transaction_id=transaction_id,
            amount=amount,
            currency="USD",
            card_bin="411111",
            card_country=card_country,
            billing_country=billing_country,
            ip_address="192.168.1.1",
            ip_country=ip_country,
            email=f"customer@{'tempmail.com' if is_high_risk and random.random() < 0.3 else 'gmail.com'}",
            passenger_names=["John Smith"],
            cardholder_name="John Smith" if random.random() < 0.85 else "Jane Doe",
            is_one_way=random.random() < 0.3,
            destination_country=random.choice(countries),
            hours_to_departure=random.randint(6, 720),
            device_fingerprint="abc123",
            is_new_device=random.random() < 0.3,
            is_vpn=random.random() < 0.1,
            previous_chargebacks=1 if is_high_risk and random.random() < 0.2 else 0,
            failed_attempts=random.randint(0, 3) if is_high_risk else 0,
            bookings_last_hour=random.randint(1, 5) if is_high_risk else 1
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

_calculator = None
_detector = None

def get_calculator() -> EU261Calculator:
    global _calculator
    if _calculator is None:
        _calculator = EU261Calculator()
    return _calculator


def get_fraud_detector() -> FraudDetector:
    global _detector
    if _detector is None:
        _detector = FraudDetector()
    return _detector


def calculate_eu261(origin: str, destination: str, airline: str, 
                    delay_minutes: int, **kwargs) -> CompensationResult:
    """Quick EU261 calculation"""
    return get_calculator().calculate_compensation(
        origin, destination, airline, delay_minutes, **kwargs
    )


def assess_fraud(transaction_id: str, amount: float = None) -> FraudAssessment:
    """Quick fraud assessment"""
    return get_fraud_detector().simulate_assessment(transaction_id, amount)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("EU261 COMPENSATION CALCULATOR")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        ("LHR", "JFK", "BA", 200, False, False, "3+ hour delay London to NYC"),
        ("JFK", "LHR", "AA", 200, False, False, "3+ hour delay NYC to London (non-EU carrier)"),
        ("CDG", "LAX", "AF", 250, False, False, "4+ hour delay Paris to LA"),
        ("ORD", "DFW", "AA", 180, False, False, "3 hour delay domestic US (no EU261)"),
        ("FRA", "DXB", "LH", 0, True, False, "Cancellation Frankfurt to Dubai"),
    ]
    
    calc = get_calculator()
    
    for origin, dest, airline, delay, cancelled, denied, desc in test_cases:
        result = calc.calculate_compensation(
            origin, dest, airline, delay, 
            is_cancelled=cancelled, is_denied_boarding=denied
        )
        print(f"\n📍 {desc}")
        print(f"   Route: {origin} → {dest} ({airline})")
        print(f"   Distance: {result.distance_km:,.0f} km")
        print(f"   Eligible: {'✅ Yes' if result.eligible else '❌ No'}")
        if result.eligible:
            print(f"   Compensation: €{result.compensation_amount}")
        print(f"   Reason: {result.reason}")
    
    print("\n" + "=" * 60)
    print("FRAUD DETECTION")
    print("=" * 60)
    
    detector = get_fraud_detector()
    
    for i in range(5):
        amount = random.uniform(300, 4000)
        assessment = detector.simulate_assessment(f"TXN-{i+1:04d}", amount)
        
        risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
        
        print(f"\n💳 Transaction {assessment.transaction_id}")
        print(f"   Amount: ${amount:,.2f}")
        print(f"   Risk Score: {assessment.risk_score}/100 {risk_emoji.get(assessment.risk_level, '')} {assessment.risk_level}")
        print(f"   Action: {assessment.recommended_action}")
        if assessment.indicators:
            print(f"   Indicators: {len(assessment.indicators)}")
            for ind in assessment.indicators[:3]:
                print(f"      - {ind['name']} (+{ind['score']})")
