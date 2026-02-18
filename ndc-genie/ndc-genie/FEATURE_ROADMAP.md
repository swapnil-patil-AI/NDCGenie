# NDC Genie - Real-World Feature Enhancements

## Executive Summary

This document outlines real-world airline industry scenarios that can be added to NDC Genie to make it truly enterprise-ready. These enhancements are based on actual airline operations, GDS systems, and customer service workflows.

---

## 🎯 Priority 1: Core Booking Enhancements

### 1.1 PNR (Passenger Name Record) Integration
**What it is:** The 6-character booking reference used globally by all airlines.

**Real-world usage:**
- Customer calls: "I have booking ABC123"
- Links all passengers, flights, payments in one record
- Used for check-in, changes, refunds

**Implementation:**
```python
# Example PNR lookup
pnr = "ABC123"
booking = get_booking_by_pnr(pnr)
# Returns: All passengers, flights, payments, history
```

**AI Assistant queries enabled:**
- "Look up PNR ABC123"
- "What's the status of booking XYZW99?"
- "Show me all bookings created yesterday"

---

### 1.2 E-Ticket Numbers
**What it is:** 13-digit electronic ticket number (e.g., 016-1234567890)

**Real-world usage:**
- Required for check-in at airport
- Used for refund processing
- Links to specific fare rules

**AI Assistant queries enabled:**
- "Find ticket number 016-1234567890"
- "Is this ticket refundable?"
- "What's the ticket status?"

---

### 1.3 Multi-Segment Itineraries
**What it is:** Journeys with connections (most real bookings)

**Current limitation:** Single flight segments only

**Enhancement:**
```
Outbound: NYC → LAX → SFO (connection)
Return: SFO → DEN → NYC (connection)
```

**AI Assistant queries enabled:**
- "What's the connection time in Denver?"
- "Show me bookings with tight connections under 60 minutes"
- "Any misconnection risks today?"

---

## 🎯 Priority 2: Operational Intelligence

### 2.1 Real-Time Flight Status
**What it is:** Live operational status of flights

**Statuses:**
| Status | Description |
|--------|-------------|
| On Time | Operating as scheduled |
| Delayed | Departure delayed (with reason) |
| Cancelled | Flight cancelled |
| Diverted | Redirected to different airport |
| Boarding | Currently boarding |
| Departed | Has left gate |
| In Flight | Airborne |
| Landed | Touched down |

**AI Assistant queries enabled:**
- "Is flight AA123 on time today?"
- "Show me all delayed flights"
- "Which customers are affected by the JFK delays?"

---

### 2.2 Disruption Management (IROP)
**What it is:** Irregular Operations handling

**Scenarios:**
- Weather delays
- Mechanical issues
- Crew shortages
- Air traffic control delays
- Security incidents

**Data tracked:**
```python
disruption = {
    "type": "Weather",
    "delay_minutes": 180,
    "affected_passengers": 245,
    "rebooking_options": [...],
    "compensation_eligible": True,
    "eu261_amount": 400.00
}
```

**AI Assistant queries enabled:**
- "How many passengers affected by today's cancellations?"
- "What rebooking options for passenger on cancelled AA456?"
- "Calculate EU261 compensation for 3-hour delay to Paris"

---

### 2.3 Baggage Tracking
**What it is:** Real-time baggage location tracking

**Statuses:**
- Checked In → Security Screened → Loaded → In Transit → Arrived → Collected
- Or: Delayed → Mishandled → Lost → Found → Delivered

**AI Assistant queries enabled:**
- "Where is bag tag 0016123456?"
- "Show all delayed baggage for today's flights"
- "Create PIR (Property Irregularity Report) for lost bag"

---

## 🎯 Priority 3: Financial & Compliance

### 3.1 Fraud Detection
**What it is:** Risk scoring for payment transactions

**Risk Factors:**
- IP geolocation vs billing country mismatch
- Multiple failed payment attempts
- Velocity (many bookings in short time)
- High-risk destination one-way
- Device fingerprint anomalies
- BIN (card) country mismatch

**Risk Levels:**
| Score | Level | Action |
|-------|-------|--------|
| 0-30 | Low | Auto-approve |
| 31-60 | Medium | 3DS verification |
| 61-85 | High | Manual review |
| 86+ | Critical | Auto-decline |

**AI Assistant queries enabled:**
- "Show high-risk transactions from today"
- "Why was this payment flagged?"
- "What's our fraud rate this month?"

---

### 3.2 Regulatory Compensation (EU261/DOT)
**What it is:** Mandatory compensation for delays/cancellations

**EU261 Compensation Table:**
| Distance | Delay | Amount |
|----------|-------|--------|
| < 1500km | 3+ hours | €250 |
| 1500-3500km | 3+ hours | €400 |
| > 3500km | 4+ hours | €600 |

**AI Assistant queries enabled:**
- "Is this passenger eligible for EU261?"
- "Calculate compensation for cancelled Paris flight"
- "Show all pending compensation claims"
- "What's our EU261 liability this month?"

---

### 3.3 Fare Rules Engine
**What it is:** Ticket change/refund policies

**Rule Categories:**
- Changes permitted (Y/N)
- Change fee amount
- Refund type (Full/Partial/Credit/Non-refundable)
- Rebooking validity
- Blackout dates

**AI Assistant queries enabled:**
- "Can this ticket be changed?"
- "What's the change fee for fare basis YLOWUS?"
- "Is this ticket refundable?"

---

## 🎯 Priority 4: Corporate Travel

### 4.1 Business Travel Management
**What it is:** Corporate booking workflow

**Features:**
- Cost center allocation
- Travel policy compliance checking
- Approval workflows
- Budget tracking
- Invoice consolidation

**Data tracked:**
```python
corporate = {
    "company": "Acme Corp",
    "cost_center": "MKTG-2024",
    "within_policy": False,
    "violations": ["Exceeded daily hotel limit"],
    "requires_approval": True,
    "approver": "manager@acme.com"
}
```

**AI Assistant queries enabled:**
- "Show all out-of-policy bookings"
- "What's the travel spend for Marketing department?"
- "Which bookings need manager approval?"

---

## 🎯 Priority 5: Customer Intelligence

### 5.1 Customer Satisfaction (NPS/CSAT)
**What it is:** Post-interaction feedback tracking

**Metrics:**
- NPS (Net Promoter Score): -100 to +100
- CSAT (Customer Satisfaction): 1-5
- CES (Customer Effort Score): 1-7

**AI Assistant queries enabled:**
- "What's our NPS this month?"
- "Show detractors from last week"
- "Which service areas have lowest ratings?"

---

### 5.2 Customer 360 View
**What it is:** Complete customer profile

**Includes:**
- Booking history
- Loyalty status & miles
- Communication history
- Preferences
- Past issues/complaints
- Lifetime value

**AI Assistant queries enabled:**
- "Tell me about customer John Smith"
- "What issues has this customer had before?"
- "Show VIP customers with recent complaints"

---

## 🎯 Priority 6: Channel & Distribution

### 6.1 Booking Channel Analytics
**What it is:** Track where bookings come from

**Channels:**
- Direct (Website, App, Call Center)
- OTAs (Expedia, Booking.com, etc.)
- Travel Agents
- Corporate Portals
- GDS (Amadeus, Sabre, Travelport)
- NDC/API

**AI Assistant queries enabled:**
- "What's our direct booking percentage?"
- "Which OTA has highest cancellation rate?"
- "Compare conversion by channel"

---

## 📊 Dashboard Enhancements

### Real-Time Operations Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  TODAY'S OPERATIONS                         Jan 10, 2026    │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│ ✅ On Time  │ ⚠️ Delayed  │ ❌ Cancelled │ 🔄 Diverted    │
│    847      │    123      │     12      │      3         │
├─────────────┴─────────────┴─────────────┴─────────────────┤
│                                                            │
│  DISRUPTION ALERTS                                         │
│  🌧️ Weather delay affecting JFK departures (+45 min avg)  │
│  🔧 Aircraft swap AA456 - 738 → 321 (capacity reduced)    │
│  👥 156 passengers need rebooking (cancelled UA789)        │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  COMPENSATION LIABILITY (EU261)                            │
│  Today: €24,500  |  This Week: €156,000  |  MTD: €445,000 │
└────────────────────────────────────────────────────────────┘
```

### Customer Service Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  SERVICE METRICS                            Live            │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│ Queue       │ Avg Wait    │ FCR         │ CSAT Today      │
│   23        │  4:32       │   78%       │    4.2/5        │
├─────────────┴─────────────┴─────────────┴─────────────────┤
│                                                            │
│  TOP ISSUES TODAY                                          │
│  1. Flight delays (45%)                                    │
│  2. Baggage inquiries (22%)                                │
│  3. Refund requests (18%)                                  │
│  4. Booking changes (15%)                                  │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  ESCALATIONS REQUIRING ATTENTION                           │
│  🔴 3 Critical  │  🟡 12 High  │  🟢 28 Normal            │
└────────────────────────────────────────────────────────────┘
```

---

## 🔌 Integration Points

### External Systems to Integrate
1. **Flight Data API** (FlightAware, OAG) - Real-time status
2. **GDS Connection** - Booking retrieval
3. **Payment Gateway** - Transaction processing
4. **Baggage System** (WorldTracer) - Bag tracking
5. **CRM System** - Customer data
6. **Loyalty System** - Miles/points

### Sample API Integrations
```python
# Flight status from FlightAware
GET /flights/AA123/2026-01-10
→ {"status": "delayed", "delay_minutes": 45, "reason": "weather"}

# Baggage from WorldTracer  
GET /baggage/0016123456
→ {"status": "in_transit", "location": "ORD", "eta": "2026-01-10T15:30Z"}

# PNR from Amadeus
GET /pnr/ABC123
→ {full booking details}
```

---

## 📈 Implementation Roadmap

### Phase 1 (Week 1-2): Core Booking
- [ ] PNR model and lookup
- [ ] E-ticket numbers
- [ ] Multi-segment itineraries
- [ ] Enhanced demo data generator

### Phase 2 (Week 3-4): Operations
- [ ] Flight status tracking
- [ ] Disruption management
- [ ] Baggage tracking
- [ ] Operations dashboard

### Phase 3 (Week 5-6): Financial
- [ ] Fraud scoring
- [ ] EU261 calculator
- [ ] Fare rules engine
- [ ] Refund workflow

### Phase 4 (Week 7-8): Corporate & Analytics
- [ ] Corporate booking module
- [ ] Customer 360 view
- [ ] Advanced analytics
- [ ] Channel reporting

---

## 🤖 Enhanced AI Assistant Capabilities

With these enhancements, the AI can answer:

**Booking Questions:**
- "What's the status of PNR ABC123?"
- "Show me all bookings for customer John Smith"
- "Find all tickets issued yesterday over $2000"

**Operational Questions:**
- "Which flights are delayed out of JFK right now?"
- "How many passengers need rebooking from cancelled flights?"
- "What's our on-time performance this month?"

**Financial Questions:**
- "Calculate EU261 compensation for this booking"
- "What's our refund liability for today?"
- "Show high-fraud-risk transactions"

**Service Questions:**
- "What's this customer's history with us?"
- "Show me VIP customers with recent complaints"
- "What are the top issues today?"

**Corporate Questions:**
- "Show out-of-policy bookings for Acme Corp"
- "What's the travel spend for Q4?"
- "Which approvals are pending?"

---

## 📁 New Files Structure

```
ndc-genie_ai/
├── data/
│   ├── demo_data.py          # Current
│   ├── enhanced_models.py    # NEW - Enhanced data models
│   └── generators/           # NEW
│       ├── pnr_generator.py
│       ├── flight_generator.py
│       ├── disruption_generator.py
│       └── corporate_generator.py
├── services/                  # NEW
│   ├── flight_status.py      # Real-time flight ops
│   ├── compensation.py       # EU261/DOT calculator
│   ├── fraud_detection.py    # Risk scoring
│   └── baggage_tracking.py   # Bag status
└── dashboards/               # NEW
    ├── operations.py         # Ops dashboard
    ├── service.py            # CS dashboard
    └── corporate.py          # Business travel
```

---

*This enhancement roadmap transforms NDC Genie from a demo into a production-ready enterprise system.*
