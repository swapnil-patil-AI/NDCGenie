"""
Corporate Travel Management and Advanced Analytics for NDC Genie
Business travel, policy compliance, and reporting.

Week 7-8 Implementation
Version: 1.0.0
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class TravelPolicyTier(Enum):
    """Employee travel policy tiers"""
    STANDARD = ("Standard", "Economy class, standard hotel rates")
    EXECUTIVE = ("Executive", "Premium economy, preferred hotels")
    VIP = ("VIP", "Business class, luxury hotels")
    C_SUITE = ("C-Suite", "First class, top-tier hotels, no restrictions")


class ApprovalStatus(Enum):
    """Booking approval status"""
    PENDING = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    AUTO_APPROVED = "Auto-Approved (Within Policy)"
    EXPIRED = "Approval Expired"


class PolicyViolation(Enum):
    """Types of travel policy violations"""
    CABIN_CLASS = ("Cabin Class", "Booked cabin class exceeds policy allowance")
    ADVANCE_BOOKING = ("Advance Booking", "Booking made less than required days in advance")
    HOTEL_RATE = ("Hotel Rate", "Hotel rate exceeds daily limit")
    PREFERRED_VENDOR = ("Preferred Vendor", "Non-preferred airline/hotel selected")
    TRIP_DURATION = ("Trip Duration", "Trip duration exceeds maximum allowed")
    COST_LIMIT = ("Cost Limit", "Total trip cost exceeds budget threshold")
    DESTINATION = ("Destination", "Travel to restricted destination")
    WEEKEND_STAY = ("Weekend Stay", "Unnecessary weekend stay included")


class BillingType(Enum):
    """Corporate billing types"""
    CENTRALIZED = "Centralized Billing"  # Company pays directly
    LODGE_CARD = "Lodge Card"  # Corporate card for travel
    GHOST_CARD = "Ghost Card"  # Virtual card number
    PERSONAL_REIMBURSE = "Personal Reimbursement"  # Employee pays, gets reimbursed


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Company:
    """Corporate client information"""
    company_id: str
    company_name: str
    industry: str
    contract_type: str  # "Enterprise", "SMB", "Startup"
    billing_type: str
    payment_terms: int  # Days
    credit_limit: float
    preferred_airlines: List[str]
    preferred_hotels: List[str]
    negotiated_rates: Dict[str, float]  # Discount percentages
    policy_rules: Dict[str, Any]
    account_manager: str
    contact_email: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TravelPolicy:
    """Corporate travel policy rules"""
    policy_id: str
    company_id: str
    tier: str
    
    # Flight rules
    domestic_cabin_class: str
    international_cabin_class: str
    international_threshold_hours: int
    advance_booking_days: int
    preferred_airlines_required: bool
    
    # Hotel rules
    max_hotel_rate: float
    preferred_hotels_required: bool
    
    # Approval rules
    requires_approval_above: float
    auto_approve_below: float
    approver_levels: List[Dict[str, Any]]
    
    # Restrictions
    max_trip_duration_days: int
    restricted_destinations: List[str]
    weekend_stay_allowed: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CorporateBooking:
    """Corporate booking with policy compliance"""
    booking_id: str
    pnr: str
    company_id: str
    company_name: str
    
    # Traveler
    employee_id: str
    employee_name: str
    employee_email: str
    department: str
    cost_center: str
    project_code: Optional[str]
    policy_tier: str
    
    # Trip details
    trip_purpose: str
    trip_start_date: str
    trip_end_date: str
    destinations: List[str]
    
    # Costs
    flight_cost: float
    hotel_cost: float
    other_costs: float
    total_cost: float
    currency: str
    
    # Policy compliance
    is_within_policy: bool
    violations: List[Dict[str, Any]]
    savings_vs_policy: float  # Positive = under budget
    
    # Approval
    requires_approval: bool
    approval_status: str
    approver_id: Optional[str]
    approver_name: Optional[str]
    approved_at: Optional[str]
    approval_notes: Optional[str]
    
    # Billing
    billing_type: str
    invoice_reference: Optional[str]
    payment_status: str
    
    # Timestamps
    created_at: str
    modified_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TravelAnalytics:
    """Travel spend and behavior analytics"""
    report_period: str  # "2024-Q4", "2024-01", etc.
    company_id: Optional[str]  # None for overall
    
    # Volume metrics
    total_bookings: int
    total_passengers: int
    total_trips: int
    
    # Spend metrics
    total_spend: float
    flight_spend: float
    hotel_spend: float
    other_spend: float
    average_trip_cost: float
    currency: str
    
    # Savings
    negotiated_savings: float
    policy_savings: float
    advance_booking_savings: float
    total_savings: float
    
    # Policy compliance
    in_policy_rate: float
    out_of_policy_bookings: int
    top_violations: List[Dict[str, Any]]
    
    # Patterns
    top_routes: List[Dict[str, Any]]
    top_destinations: List[Dict[str, Any]]
    top_airlines: List[Dict[str, Any]]
    booking_lead_time_avg_days: float
    
    # Department breakdown
    spend_by_department: Dict[str, float]
    spend_by_cost_center: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
# CORPORATE TRAVEL MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class CorporateTravelManager:
    """Manages corporate travel bookings and policies"""
    
    SAMPLE_COMPANIES = [
        {"name": "Acme Corporation", "industry": "Technology"},
        {"name": "Global Finance Inc", "industry": "Financial Services"},
        {"name": "HealthCare Plus", "industry": "Healthcare"},
        {"name": "Energy Solutions Ltd", "industry": "Energy"},
        {"name": "Retail Giants Co", "industry": "Retail"},
    ]
    
    DEPARTMENTS = [
        "Sales", "Marketing", "Engineering", "Finance", "Operations",
        "HR", "Legal", "R&D", "Customer Success", "Executive"
    ]
    
    TRIP_PURPOSES = [
        "Client Meeting", "Conference", "Training", "Site Visit",
        "Team Offsite", "Sales Pitch", "Due Diligence", "Audit",
        "Board Meeting", "Partner Meeting"
    ]
    
    def __init__(self):
        self.companies: Dict[str, Company] = {}
        self.policies: Dict[str, TravelPolicy] = {}
        self.bookings: Dict[str, CorporateBooking] = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize sample companies and policies"""
        for i, comp in enumerate(self.SAMPLE_COMPANIES):
            company_id = f"CORP-{i+1:03d}"
            
            company = Company(
                company_id=company_id,
                company_name=comp["name"],
                industry=comp["industry"],
                contract_type=random.choice(["Enterprise", "SMB"]),
                billing_type=random.choice([b.value for b in BillingType]),
                payment_terms=random.choice([15, 30, 45, 60]),
                credit_limit=random.uniform(50000, 500000),
                preferred_airlines=random.sample(["AA", "UA", "DL", "BA", "LH"], 3),
                preferred_hotels=random.sample(["Marriott", "Hilton", "Hyatt", "IHG"], 2),
                negotiated_rates={"flights": random.uniform(5, 15), "hotels": random.uniform(10, 25)},
                policy_rules={},
                account_manager=f"AM-{random.randint(100, 999)}",
                contact_email=f"travel@{comp['name'].lower().replace(' ', '')}.com"
            )
            self.companies[company_id] = company
            
            # Create policies for each tier
            for tier in TravelPolicyTier:
                policy = TravelPolicy(
                    policy_id=f"POL-{company_id}-{tier.name}",
                    company_id=company_id,
                    tier=tier.name,
                    domestic_cabin_class="Economy" if tier in [TravelPolicyTier.STANDARD] else "Premium Economy" if tier == TravelPolicyTier.EXECUTIVE else "Business",
                    international_cabin_class="Economy" if tier == TravelPolicyTier.STANDARD else "Premium Economy" if tier == TravelPolicyTier.EXECUTIVE else "Business",
                    international_threshold_hours=6,
                    advance_booking_days=14 if tier == TravelPolicyTier.STANDARD else 7,
                    preferred_airlines_required=tier == TravelPolicyTier.STANDARD,
                    max_hotel_rate=150 if tier == TravelPolicyTier.STANDARD else 250 if tier == TravelPolicyTier.EXECUTIVE else 500,
                    preferred_hotels_required=tier == TravelPolicyTier.STANDARD,
                    requires_approval_above=1000 if tier == TravelPolicyTier.STANDARD else 3000,
                    auto_approve_below=500 if tier == TravelPolicyTier.STANDARD else 1500,
                    approver_levels=[{"level": 1, "title": "Manager"}, {"level": 2, "title": "Director"}],
                    max_trip_duration_days=5 if tier == TravelPolicyTier.STANDARD else 10,
                    restricted_destinations=[],
                    weekend_stay_allowed=tier != TravelPolicyTier.STANDARD
                )
                self.policies[policy.policy_id] = policy
    
    def check_policy_compliance(self, 
                               company_id: str,
                               policy_tier: str,
                               cabin_class: str,
                               is_international: bool,
                               hotel_rate: float,
                               advance_days: int,
                               trip_duration: int,
                               total_cost: float,
                               airline: str,
                               includes_weekend: bool) -> Tuple[bool, List[Dict[str, Any]]]:
        """Check if booking complies with policy"""
        
        violations = []
        policy_id = f"POL-{company_id}-{policy_tier}"
        policy = self.policies.get(policy_id)
        
        if not policy:
            return True, []
        
        # Check cabin class
        allowed_cabin = policy.international_cabin_class if is_international else policy.domestic_cabin_class
        cabin_hierarchy = ["Economy", "Premium Economy", "Business", "First"]
        if cabin_hierarchy.index(cabin_class) > cabin_hierarchy.index(allowed_cabin):
            violations.append({
                "type": PolicyViolation.CABIN_CLASS.value[0],
                "description": f"Booked {cabin_class}, policy allows {allowed_cabin}",
                "severity": "High"
            })
        
        # Check advance booking
        if advance_days < policy.advance_booking_days:
            violations.append({
                "type": PolicyViolation.ADVANCE_BOOKING.value[0],
                "description": f"Booked {advance_days} days in advance, policy requires {policy.advance_booking_days}",
                "severity": "Medium"
            })
        
        # Check hotel rate
        if hotel_rate > policy.max_hotel_rate:
            violations.append({
                "type": PolicyViolation.HOTEL_RATE.value[0],
                "description": f"Hotel rate ${hotel_rate}/night exceeds limit of ${policy.max_hotel_rate}",
                "severity": "Medium"
            })
        
        # Check preferred airline
        company = self.companies.get(company_id)
        if policy.preferred_airlines_required and company:
            if airline not in company.preferred_airlines:
                violations.append({
                    "type": PolicyViolation.PREFERRED_VENDOR.value[0],
                    "description": f"Non-preferred airline {airline} selected",
                    "severity": "Low"
                })
        
        # Check trip duration
        if trip_duration > policy.max_trip_duration_days:
            violations.append({
                "type": PolicyViolation.TRIP_DURATION.value[0],
                "description": f"Trip is {trip_duration} days, max allowed is {policy.max_trip_duration_days}",
                "severity": "Medium"
            })
        
        # Check weekend stay
        if includes_weekend and not policy.weekend_stay_allowed:
            violations.append({
                "type": PolicyViolation.WEEKEND_STAY.value[0],
                "description": "Weekend stay not allowed for this policy tier",
                "severity": "Low"
            })
        
        is_compliant = len(violations) == 0
        return is_compliant, violations
    
    def create_booking(self,
                      pnr: str,
                      company_id: str,
                      employee_name: str,
                      department: str,
                      destinations: List[str],
                      trip_start: datetime,
                      trip_end: datetime,
                      flight_cost: float,
                      hotel_cost: float,
                      cabin_class: str = "Economy",
                      is_international: bool = False,
                      hotel_rate: float = 150,
                      airline: str = "AA") -> CorporateBooking:
        """Create a corporate booking with policy check"""
        
        company = self.companies.get(company_id)
        if not company:
            company_id = list(self.companies.keys())[0]
            company = self.companies[company_id]
        
        # Determine policy tier (random for demo)
        policy_tier = random.choice([t.name for t in TravelPolicyTier])
        
        # Calculate metrics
        trip_duration = (trip_end - trip_start).days
        advance_days = (trip_start - datetime.now()).days
        includes_weekend = any(
            (trip_start + timedelta(days=i)).weekday() >= 5 
            for i in range(trip_duration + 1)
        )
        
        total_cost = flight_cost + hotel_cost
        
        # Check policy compliance
        is_compliant, violations = self.check_policy_compliance(
            company_id, policy_tier, cabin_class, is_international,
            hotel_rate, advance_days, trip_duration, total_cost,
            airline, includes_weekend
        )
        
        # Determine approval requirement
        policy_id = f"POL-{company_id}-{policy_tier}"
        policy = self.policies.get(policy_id)
        
        requires_approval = not is_compliant or (policy and total_cost > policy.auto_approve_below)
        
        if requires_approval:
            if is_compliant:
                approval_status = ApprovalStatus.PENDING.value
            else:
                approval_status = ApprovalStatus.PENDING.value
        else:
            approval_status = ApprovalStatus.AUTO_APPROVED.value
        
        booking = CorporateBooking(
            booking_id=f"CB-{pnr}",
            pnr=pnr,
            company_id=company_id,
            company_name=company.company_name,
            employee_id=f"EMP-{random.randint(10000, 99999)}",
            employee_name=employee_name,
            employee_email=f"{employee_name.lower().replace(' ', '.')}@{company.company_name.lower().replace(' ', '')}.com",
            department=department,
            cost_center=f"CC-{department[:3].upper()}-{random.randint(100, 999)}",
            project_code=f"PRJ-{random.randint(1000, 9999)}" if random.random() < 0.5 else None,
            policy_tier=policy_tier,
            trip_purpose=random.choice(self.TRIP_PURPOSES),
            trip_start_date=trip_start.strftime("%Y-%m-%d"),
            trip_end_date=trip_end.strftime("%Y-%m-%d"),
            destinations=destinations,
            flight_cost=flight_cost,
            hotel_cost=hotel_cost,
            other_costs=random.uniform(50, 300),
            total_cost=total_cost,
            currency="USD",
            is_within_policy=is_compliant,
            violations=violations,
            savings_vs_policy=random.uniform(-200, 500),
            requires_approval=requires_approval,
            approval_status=approval_status,
            approver_id=f"MGR-{random.randint(100, 999)}" if requires_approval else None,
            approver_name=f"{random.choice(['John', 'Sarah', 'Mike', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}" if requires_approval else None,
            approved_at=None,
            approval_notes=None,
            billing_type=company.billing_type,
            invoice_reference=None,
            payment_status="Pending",
            created_at=datetime.now().isoformat(),
            modified_at=datetime.now().isoformat()
        )
        
        self.bookings[booking.booking_id] = booking
        return booking
    
    def generate_analytics(self, 
                          period: str,
                          company_id: str = None) -> TravelAnalytics:
        """Generate travel analytics for a period"""
        
        # Filter bookings
        bookings = list(self.bookings.values())
        if company_id:
            bookings = [b for b in bookings if b.company_id == company_id]
        
        if not bookings:
            # Generate sample data
            for _ in range(50):
                company = random.choice(list(self.companies.keys()))
                self.create_booking(
                    pnr=f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=6))}",
                    company_id=company,
                    employee_name=f"{random.choice(['John', 'Jane', 'Bob', 'Alice'])} {random.choice(['Smith', 'Doe', 'Johnson', 'Williams'])}",
                    department=random.choice(self.DEPARTMENTS),
                    destinations=[random.choice(["LAX", "JFK", "ORD", "LHR", "SFO"])],
                    trip_start=datetime.now() + timedelta(days=random.randint(5, 60)),
                    trip_end=datetime.now() + timedelta(days=random.randint(7, 65)),
                    flight_cost=random.uniform(300, 2000),
                    hotel_cost=random.uniform(200, 1500)
                )
            bookings = list(self.bookings.values())
        
        # Calculate metrics
        total_spend = sum(b.total_cost for b in bookings)
        flight_spend = sum(b.flight_cost for b in bookings)
        hotel_spend = sum(b.hotel_cost for b in bookings)
        other_spend = sum(b.other_costs for b in bookings)
        
        in_policy = sum(1 for b in bookings if b.is_within_policy)
        in_policy_rate = (in_policy / len(bookings) * 100) if bookings else 0
        
        # Top violations
        violation_counts = defaultdict(int)
        for b in bookings:
            for v in b.violations:
                violation_counts[v['type']] += 1
        
        top_violations = [
            {"type": k, "count": v} 
            for k, v in sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Spend by department
        dept_spend = defaultdict(float)
        for b in bookings:
            dept_spend[b.department] += b.total_cost
        
        # Top destinations
        dest_counts = defaultdict(int)
        for b in bookings:
            for d in b.destinations:
                dest_counts[d] += 1
        
        top_destinations = [
            {"destination": k, "count": v}
            for k, v in sorted(dest_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        return TravelAnalytics(
            report_period=period,
            company_id=company_id,
            total_bookings=len(bookings),
            total_passengers=len(bookings),  # Simplified
            total_trips=len(bookings),
            total_spend=round(total_spend, 2),
            flight_spend=round(flight_spend, 2),
            hotel_spend=round(hotel_spend, 2),
            other_spend=round(other_spend, 2),
            average_trip_cost=round(total_spend / len(bookings), 2) if bookings else 0,
            currency="USD",
            negotiated_savings=round(total_spend * 0.08, 2),
            policy_savings=round(sum(max(0, b.savings_vs_policy) for b in bookings), 2),
            advance_booking_savings=round(total_spend * 0.05, 2),
            total_savings=round(total_spend * 0.15, 2),
            in_policy_rate=round(in_policy_rate, 1),
            out_of_policy_bookings=len(bookings) - in_policy,
            top_violations=top_violations,
            top_routes=[],  # Would need route data
            top_destinations=top_destinations,
            top_airlines=[
                {"airline": "AA", "bookings": random.randint(10, 30)},
                {"airline": "UA", "bookings": random.randint(8, 25)},
                {"airline": "DL", "bookings": random.randint(5, 20)},
            ],
            booking_lead_time_avg_days=random.uniform(7, 21),
            spend_by_department=dict(dept_spend),
            spend_by_cost_center={}
        )
    
    def get_pending_approvals(self, company_id: str = None) -> List[CorporateBooking]:
        """Get bookings pending approval"""
        bookings = list(self.bookings.values())
        if company_id:
            bookings = [b for b in bookings if b.company_id == company_id]
        return [b for b in bookings if b.approval_status == ApprovalStatus.PENDING.value]
    
    def get_policy_violations_summary(self, company_id: str = None) -> Dict[str, Any]:
        """Get summary of policy violations"""
        bookings = list(self.bookings.values())
        if company_id:
            bookings = [b for b in bookings if b.company_id == company_id]
        
        violation_counts = defaultdict(int)
        violation_costs = defaultdict(float)
        
        for b in bookings:
            for v in b.violations:
                violation_counts[v['type']] += 1
                violation_costs[v['type']] += b.total_cost
        
        return {
            "total_violations": sum(violation_counts.values()),
            "total_bookings_with_violations": len([b for b in bookings if b.violations]),
            "violation_breakdown": [
                {
                    "type": k,
                    "count": violation_counts[k],
                    "total_cost": round(violation_costs[k], 2)
                }
                for k in sorted(violation_counts.keys(), key=lambda x: violation_counts[x], reverse=True)
            ]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

_manager = None

def get_corporate_manager() -> CorporateTravelManager:
    global _manager
    if _manager is None:
        _manager = CorporateTravelManager()
    return _manager


def create_corporate_booking(pnr: str, **kwargs) -> CorporateBooking:
    """Create a corporate booking"""
    return get_corporate_manager().create_booking(pnr, **kwargs)


def get_travel_analytics(period: str, company_id: str = None) -> TravelAnalytics:
    """Get travel analytics"""
    return get_corporate_manager().generate_analytics(period, company_id)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("CORPORATE TRAVEL MANAGEMENT")
    print("=" * 60)
    
    manager = get_corporate_manager()
    
    # Show companies
    print("\n📊 REGISTERED COMPANIES:")
    for comp in manager.companies.values():
        print(f"   {comp.company_name} ({comp.industry}) - {comp.contract_type}")
    
    # Create some bookings
    print("\n📋 CREATING SAMPLE BOOKINGS...")
    
    for i in range(10):
        company_id = random.choice(list(manager.companies.keys()))
        booking = manager.create_booking(
            pnr=f"TEST{i:03d}",
            company_id=company_id,
            employee_name=f"Employee {i+1}",
            department=random.choice(manager.DEPARTMENTS),
            destinations=[random.choice(["LAX", "JFK", "ORD", "LHR"])],
            trip_start=datetime.now() + timedelta(days=random.randint(5, 30)),
            trip_end=datetime.now() + timedelta(days=random.randint(7, 35)),
            flight_cost=random.uniform(300, 2000),
            hotel_cost=random.uniform(200, 1000),
            cabin_class=random.choice(["Economy", "Premium Economy", "Business"]),
            is_international=random.random() < 0.3
        )
    
    # Show pending approvals
    pending = manager.get_pending_approvals()
    print(f"\n⏳ PENDING APPROVALS: {len(pending)}")
    for b in pending[:3]:
        print(f"   {b.booking_id}: {b.employee_name} - ${b.total_cost:,.2f}")
        if b.violations:
            print(f"      Violations: {', '.join(v['type'] for v in b.violations)}")
    
    # Show policy violations summary
    violations = manager.get_policy_violations_summary()
    print(f"\n⚠️ POLICY VIOLATIONS: {violations['total_violations']}")
    for v in violations['violation_breakdown'][:3]:
        print(f"   {v['type']}: {v['count']} occurrences (${v['total_cost']:,.2f})")
    
    # Generate analytics
    analytics = manager.generate_analytics("2024-Q4")
    print(f"\n📈 ANALYTICS (2024-Q4):")
    print(f"   Total Bookings: {analytics.total_bookings}")
    print(f"   Total Spend: ${analytics.total_spend:,.2f}")
    print(f"   In-Policy Rate: {analytics.in_policy_rate}%")
    print(f"   Total Savings: ${analytics.total_savings:,.2f}")
    print(f"\n   Spend by Department:")
    for dept, spend in sorted(analytics.spend_by_department.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"      {dept}: ${spend:,.2f}")
