"""
demo_data.py - NDC Genie Demo Data Generator

Generates realistic NDC short-sell transaction data.

NDC Short-Sell Flow:
  Shopping  → returns shopping_offer_ids[] (1–200 offers)
  OfferPrice → takes 1 shopping_offer_id → returns priced_offer_id
  SeatAvail  → returns seat_offer_ids[]
  ServiceAvail → returns service_offer_ids[]
  OrderCreate → takes priced_offer_id + seat_offer_ids + service_offer_ids → creates order_id

Each flow stage carries forward the transaction_id and relevant offer IDs from previous stages.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional
import hashlib


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AIRLINES = [
    ("SkyWings Airlines", "SW"),
    ("AeroJet", "AJ"),
    ("BlueSky Air", "BS"),
    ("Pacific Wings", "PW"),
    ("Atlantic Express", "AE"),
    ("Northern Star", "NS"),
    ("SunRise Air", "SR"),
    ("CloudHopper", "CH"),
]

AIRPORTS = [
    "JFK", "LAX", "ORD", "DFW", "DEN", "SFO", "SEA", "MIA",
    "BOS", "ATL", "LHR", "CDG", "FRA", "AMS", "DXB", "SIN",
    "HKG", "NRT", "SYD", "YYZ", "GRU", "MEX",
]

CABIN_CLASSES = ["Economy", "Premium Economy", "Business", "First"]
LOYALTY_TIERS = ["Standard", "Silver", "Gold", "Platinum"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Apple Pay", "Bank Transfer"]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Wei", "Priya", "Mohammed", "Fatima",
    "Yuki", "Carlos", "Ana", "Luca", "Sofia", "Pierre",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
    "Thompson", "Young", "Walker", "Robinson", "Patel", "Nakamura", "Santos", "Müller",
    "Dubois", "Rossi", "Kim", "Chen", "Ali", "Singh",
]

ERROR_SCENARIOS = [
    {
        "stage": "Payment",
        "code": "ERR-PAY-001",
        "message": "Card declined - Insufficient funds",
        "resolution": "Advise customer to use different payment method or check account balance",
    },
    {
        "stage": "Payment",
        "code": "ERR-PAY-002",
        "message": "Payment gateway timeout",
        "resolution": "Retry payment or use alternative payment method",
    },
    {
        "stage": "Ticketing",
        "code": "ERR-TKT-001",
        "message": "GDS ticketing failure - Queue full",
        "resolution": "Manually requeue ticket issuance",
    },
    {
        "stage": "Ticketing",
        "code": "ERR-TKT-002",
        "message": "Fare basis mismatch during ticketing",
        "resolution": "Reprice itinerary and rebook",
    },
    {
        "stage": "Booking",
        "code": "ERR-BKG-001",
        "message": "Seat inventory unavailable",
        "resolution": "Offer alternative flights or cabin class",
    },
    {
        "stage": "OfferPrice",
        "code": "ERR-OFP-001",
        "message": "Offer expired before pricing",
        "resolution": "Initiate new shopping request to refresh offer",
    },
    {
        "stage": "OrderCreate",
        "code": "ERR-ORD-001",
        "message": "Offer ID mismatch in OrderCreate request",
        "resolution": "Re-validate priced offer ID and resubmit",
    },
]

# ---------------------------------------------------------------------------
# ID Generators
# ---------------------------------------------------------------------------

def _rand_upper(n: int, rng: random.Random) -> str:
    return "".join(rng.choices(string.ascii_uppercase + string.digits, k=n))


def generate_transaction_id(rng: random.Random, date: datetime) -> str:
    """TXN-YYYYMM-XXXXXXXX"""
    suffix = _rand_upper(8, rng)
    return f"TXN-{date.strftime('%Y%m')}-{suffix}"


def generate_shopping_offer_ids(rng: random.Random, txn_id: str, count: int) -> list[str]:
    """
    Shopping returns 1–200 offer IDs.
    Format: SHP-<txn_suffix>-<index>-<random>
    """
    txn_suffix = txn_id.split("-")[-1]
    return [f"SHP-{txn_suffix}-{i+1:03d}-{_rand_upper(4, rng)}" for i in range(count)]


def generate_priced_offer_id(rng: random.Random, shopping_offer_id: str) -> str:
    """
    OfferPrice picks one shopping offer and returns a single priced offer ID.
    Format: OFP-<shopping_suffix>-<random>
    """
    suffix = shopping_offer_id.split("-")[-1]
    return f"OFP-{suffix}-{_rand_upper(6, rng)}"


def generate_seat_offer_ids(rng: random.Random, txn_id: str, count: int) -> list[str]:
    """
    SeatAvailability returns 1–N seat offer IDs (one per passenger/segment).
    Format: SAV-<txn_suffix>-<seat_code>-<random>
    """
    txn_suffix = txn_id.split("-")[-1]
    seat_codes = ["WDW", "MID", "AIS", "EXT", "BLK"]
    return [
        f"SAV-{txn_suffix}-{rng.choice(seat_codes)}-{_rand_upper(4, rng)}"
        for _ in range(count)
    ]


def generate_service_offer_ids(rng: random.Random, txn_id: str, count: int) -> list[str]:
    """
    ServiceAvailability returns ancillary service offer IDs.
    Format: SVC-<txn_suffix>-<service_code>-<random>
    """
    txn_suffix = txn_id.split("-")[-1]
    service_codes = ["BAG", "MEAL", "UPGD", "LONG", "INSUR", "WIFI"]
    return [
        f"SVC-{txn_suffix}-{rng.choice(service_codes)}-{_rand_upper(4, rng)}"
        for _ in range(count)
    ]


def generate_order_id(rng: random.Random, txn_id: str) -> str:
    """
    OrderCreate returns a single order ID.
    Format: ORD-<txn_suffix>-<random>
    """
    txn_suffix = txn_id.split("-")[-1]
    return f"ORD-{txn_suffix}-{_rand_upper(8, rng)}"


def generate_pnr(rng: random.Random) -> str:
    return _rand_upper(6, rng)


def generate_eticket(rng: random.Random) -> str:
    airline_code = str(rng.randint(100, 999))
    number = "".join([str(rng.randint(0, 9)) for _ in range(10)])
    return f"{airline_code}-{number}"


# ---------------------------------------------------------------------------
# NDC Flow Stage Builder
# ---------------------------------------------------------------------------

# Flow stages in order — each stage is only present if the transaction reached it
NDC_STAGES = ["Shopping", "OfferPrice", "SeatAvail", "ServiceAvail", "OrderCreate"]

# Status at the deepest stage reached
TERMINAL_STATUSES = {
    "success": "Completed",
    "failed": "Failed",
    "pending": "In Progress",
    "refunded": "Refunded",
}


def _build_ndc_ids(rng: random.Random, txn_id: str, deepest_stage: str, status: str) -> dict:
    """
    Build the NDC ID chain for a transaction depending on how far it progressed.

    Returns a dict with keys present only for stages that were reached:
      shopping_offer_ids    - list (Shopping stage)
      selected_shopping_offer_id - str (OfferPrice uses one of these)
      priced_offer_id       - str (OfferPrice stage)
      seat_offer_ids        - list (SeatAvail stage)
      service_offer_ids     - list (ServiceAvail stage)
      order_id              - str (OrderCreate stage)
    """
    stage_index = NDC_STAGES.index(deepest_stage)
    ids = {}

    # Shopping is always first — generate offer IDs
    shopping_count = rng.randint(3, 30)
    ids["shopping_offer_ids"] = generate_shopping_offer_ids(rng, txn_id, shopping_count)
    ids["shopping_offer_count"] = shopping_count

    if stage_index >= 1:  # OfferPrice
        selected = rng.choice(ids["shopping_offer_ids"])
        ids["selected_shopping_offer_id"] = selected
        ids["priced_offer_id"] = generate_priced_offer_id(rng, selected)

    if stage_index >= 2:  # SeatAvail
        seat_count = rng.randint(1, 4)
        ids["seat_offer_ids"] = generate_seat_offer_ids(rng, txn_id, seat_count)

    if stage_index >= 3:  # ServiceAvail
        svc_count = rng.randint(1, 5)
        ids["service_offer_ids"] = generate_service_offer_ids(rng, txn_id, svc_count)

    if stage_index >= 4:  # OrderCreate
        ids["order_id"] = generate_order_id(rng, txn_id)

    return ids


# ---------------------------------------------------------------------------
# Main Transaction Generator
# ---------------------------------------------------------------------------

class DemoDataGenerator:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def _random_date(self, days_back: int = 90) -> datetime:
        offset = self.rng.randint(0, days_back * 24 * 60)
        return datetime.now() - timedelta(minutes=offset)

    def _random_customer(self) -> dict:
        first = self.rng.choice(FIRST_NAMES)
        last = self.rng.choice(LAST_NAMES)
        email_domain = self.rng.choice(["gmail.com", "yahoo.com", "outlook.com", "company.com"])
        return {
            "customer_id": f"CUST-{self.rng.randint(10000, 99999)}",
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}@{email_domain}",
            "phone": f"+1-{self.rng.randint(200,999)}-{self.rng.randint(100,999)}-{self.rng.randint(1000,9999)}",
            "loyalty_tier": self.rng.choice(LOYALTY_TIERS),
            "loyalty_points": self.rng.randint(0, 200000),
            "member_since": (datetime.now() - timedelta(days=self.rng.randint(30, 3000))).strftime("%Y-%m-%d"),
            "lifetime_value": round(self.rng.uniform(100, 50000), 2),
        }

    def _random_flight(self) -> dict:
        airline_name, code = self.rng.choice(AIRLINES)
        origin, destination = self.rng.sample(AIRPORTS, 2)
        dep_date = datetime.now() + timedelta(days=self.rng.randint(-30, 180))
        return {
            "flight_number": f"{code}{self.rng.randint(100, 9999)}",
            "airline_name": airline_name,
            "origin": origin,
            "destination": destination,
            "departure_date": dep_date.strftime("%Y-%m-%d"),
            "departure_time": f"{self.rng.randint(0,23):02d}:{self.rng.choice(['00','15','30','45'])}",
            "cabin_class": self.rng.choice(CABIN_CLASSES),
            "passengers": self.rng.randint(1, 4),
        }

    def _random_pricing(self, cabin: str, pax: int) -> dict:
        base_map = {"Economy": 200, "Premium Economy": 500, "Business": 1200, "First": 3000}
        base = base_map.get(cabin, 300) * pax * self.rng.uniform(0.7, 2.5)
        taxes = base * self.rng.uniform(0.1, 0.25)
        fees = self.rng.uniform(10, 80)
        total = base + taxes + fees
        return {
            "base_fare": round(base, 2),
            "taxes": round(taxes, 2),
            "fees": round(fees, 2),
            "total": round(total, 2),
            "currency": "USD",
            "payment_method": self.rng.choice(PAYMENT_METHODS),
        }

    def generate_transaction(self, created_at: Optional[datetime] = None) -> dict:
        rng = self.rng
        if created_at is None:
            created_at = self._random_date()

        txn_id = generate_transaction_id(rng, created_at)

        # Decide how far this transaction got in the NDC flow
        # Weights: more transactions complete full flow, some fail at various stages
        stage_weights = [5, 15, 10, 10, 60]  # Shopping, OfferPrice, Seat, Service, OrderCreate
        deepest_stage = rng.choices(NDC_STAGES, weights=stage_weights, k=1)[0]
        stage_index = NDC_STAGES.index(deepest_stage)

        # Decide terminal status
        if deepest_stage == "OrderCreate":
            status_weights = {"Completed": 70, "Failed": 15, "In Progress": 5, "Refunded": 10}
        elif deepest_stage in ("SeatAvail", "ServiceAvail"):
            status_weights = {"Failed": 40, "In Progress": 50, "Completed": 10, "Refunded": 0}
        elif deepest_stage == "OfferPrice":
            status_weights = {"Failed": 60, "In Progress": 40, "Completed": 0, "Refunded": 0}
        else:  # Shopping only
            status_weights = {"Failed": 30, "In Progress": 70, "Completed": 0, "Refunded": 0}

        status_choices = list(status_weights.keys())
        status_wts = list(status_weights.values())
        status = rng.choices(status_choices, weights=status_wts, k=1)[0]

        # Priority
        priority_weights = {"Critical": 5, "High": 20, "Medium": 50, "Low": 25}
        priority = rng.choices(list(priority_weights.keys()), weights=list(priority_weights.values()), k=1)[0]

        # Build NDC ID chain
        ndc_ids = _build_ndc_ids(rng, txn_id, deepest_stage, status)

        # Build lifecycle
        lifecycle = _build_lifecycle(rng, created_at, deepest_stage, status, ndc_ids)

        # Error info (only for failed transactions)
        error_info = None
        if status == "Failed":
            err = rng.choice(ERROR_SCENARIOS)
            error_info = {
                "error_stage": err["stage"],
                "error_code": err["code"],
                "error_message": err["message"],
                "suggested_resolution": err["resolution"],
                "occurred_at": (created_at + timedelta(minutes=rng.randint(1, 30))).isoformat(),
            }

        # Refund info
        refund_info = None
        if status == "Refunded":
            flight = lifecycle.get("_flight_ref", {})
            pricing = lifecycle.get("_pricing_ref", {})
            refund_pct = rng.uniform(0.5, 1.0)
            refund_amount = round(pricing.get("total", 500) * refund_pct, 2)
            refund_info = {
                "refund_id": f"REF-{txn_id.split('-')[-1]}-{_rand_upper(6, rng)}",
                "refund_amount": refund_amount,
                "refund_reason": rng.choice([
                    "Customer cancellation",
                    "Schedule change",
                    "Flight cancellation",
                    "Duplicate booking",
                    "Medical emergency",
                ]),
                "refund_status": rng.choice(["Pending", "Processing", "Completed"]),
                "initiated_at": (created_at + timedelta(hours=rng.randint(1, 48))).isoformat(),
            }

        customer = self._random_customer()
        flight = self._random_flight()
        pricing = self._random_pricing(flight["cabin_class"], flight["passengers"])

        sla_breach = (
            status in ("Failed", "In Progress")
            and (datetime.now() - created_at).total_seconds() > 4 * 3600
            and priority in ("Critical", "High")
        )

        return {
            "transaction_id": txn_id,
            "created_at": created_at.isoformat(),
            "updated_at": (created_at + timedelta(minutes=rng.randint(1, 120))).isoformat(),
            "status": status,
            "priority": priority,
            "sla_breach": sla_breach,

            # NDC Flow tracking
            "ndc_flow": {
                "deepest_stage": deepest_stage,
                "stage_index": stage_index,
                **ndc_ids,
            },

            "customer": customer,
            "flight": flight,
            "pricing": pricing,
            "lifecycle": lifecycle,
            "error_info": error_info,
            "refund_info": refund_info,
        }

    def generate_many(self, count: int = 200) -> list[dict]:
        transactions = []
        for _ in range(count):
            t = self.generate_transaction()
            transactions.append(t)
        return transactions


def _build_lifecycle(
    rng: random.Random,
    created_at: datetime,
    deepest_stage: str,
    status: str,
    ndc_ids: dict,
) -> dict:
    """
    Build the lifecycle dict stage by stage.
    Each stage carries the relevant IDs used/returned at that stage.
    """
    stage_index = NDC_STAGES.index(deepest_stage)
    offset = 0  # minutes after created_at

    def ts(extra_mins: int) -> str:
        nonlocal offset
        offset += extra_mins
        return (created_at + timedelta(minutes=offset)).isoformat()

    def stage_status(idx: int) -> str:
        if idx < stage_index:
            return "completed"
        elif idx == stage_index:
            return "failed" if status == "Failed" else ("completed" if status in ("Completed", "Refunded") else "in_progress")
        else:
            return "not_reached"

    lifecycle = {}

    # --- Shopping ---
    lifecycle["shopping"] = {
        "status": stage_status(0),
        "timestamp": ts(rng.randint(1, 5)),
        "search_results": ndc_ids.get("shopping_offer_count", 0),
        "offer_ids": ndc_ids.get("shopping_offer_ids", []),
        "filters_applied": rng.choice([True, False]),
        "device": rng.choice(["web", "mobile", "api"]),
    }

    # --- OfferPrice ---
    ofp_status = stage_status(1)
    ofp_data = {
        "status": ofp_status,
        "timestamp": ts(rng.randint(1, 3)) if stage_index >= 1 else None,
    }
    if stage_index >= 1:
        ofp_data["input_offer_id"] = ndc_ids.get("selected_shopping_offer_id")
        ofp_data["priced_offer_id"] = ndc_ids.get("priced_offer_id")
    lifecycle["offer_price"] = ofp_data

    # --- SeatAvailability ---
    seat_status = stage_status(2)
    seat_data = {
        "status": seat_status,
        "timestamp": ts(rng.randint(1, 3)) if stage_index >= 2 else None,
    }
    if stage_index >= 2:
        seat_data["seat_offer_ids"] = ndc_ids.get("seat_offer_ids", [])
    lifecycle["seat_availability"] = seat_data

    # --- ServiceAvailability ---
    svc_status = stage_status(3)
    svc_data = {
        "status": svc_status,
        "timestamp": ts(rng.randint(1, 3)) if stage_index >= 3 else None,
    }
    if stage_index >= 3:
        svc_data["service_offer_ids"] = ndc_ids.get("service_offer_ids", [])
    lifecycle["service_availability"] = svc_data

    # --- OrderCreate ---
    ord_status = stage_status(4)
    ord_data = {
        "status": ord_status,
        "timestamp": ts(rng.randint(1, 5)) if stage_index >= 4 else None,
    }
    if stage_index >= 4:
        ord_data["input_priced_offer_id"] = ndc_ids.get("priced_offer_id")
        ord_data["input_seat_offer_ids"] = ndc_ids.get("seat_offer_ids", [])
        ord_data["input_service_offer_ids"] = ndc_ids.get("service_offer_ids", [])
        ord_data["order_id"] = ndc_ids.get("order_id")
        if ord_status == "completed":
            ord_data["pnr"] = generate_pnr(rng)
            ord_data["e_ticket"] = generate_eticket(rng)
            ord_data["confirmation_sent"] = True
    lifecycle["order_create"] = ord_data

    return lifecycle


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@staticmethod
def get_demo_data(count: int = 200, seed: int = 42) -> list[dict]:
    gen = DemoDataGenerator(seed=seed)
    return gen.generate_many(count)


# Make get_demo_data importable at module level
def get_demo_data(count: int = 200, seed: int = 42) -> list[dict]:
    gen = DemoDataGenerator(seed=seed)
    return gen.generate_many(count)