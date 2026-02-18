"""
Operations Dashboard UI for NDC Genie
Flight Status, EU261 Compensation, Fraud Detection, Corporate Travel

Version: 1.0.0
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random

# Import new services
try:
    from data.pnr_generator import generate_booking, generate_bookings, get_generator, AIRLINES, AIRPORTS
    from services.flight_status import (
        get_simulator, simulate_daily_operations, 
        FlightStatus, DelayReason
    )
    from services.compensation import (
        calculate_eu261, assess_fraud, get_flight_distance,
        EU261Calculator, FraudDetector
    )
    from services.corporate import (
        get_corporate_manager, get_travel_analytics,
        CorporateTravelManager
    )
    SERVICES_AVAILABLE = True
except ImportError as e:
    SERVICES_AVAILABLE = False
    IMPORT_ERROR = str(e)


def render_operations_tab():
    """Render the Operations dashboard with all new features"""
    
    if not SERVICES_AVAILABLE:
        st.error(f"⚠️ Services not available: {IMPORT_ERROR}")
        st.info("Please ensure all service modules are installed correctly.")
        return
    
    st.markdown("## ✈️ Operations Center")
    st.markdown("Real-time flight operations, compensation calculator, fraud detection, and corporate travel management.")
    
    # Sub-tabs for different operations
    ops_tabs = st.tabs([
        "🛫 Flight Status",
        "🎫 PNR Lookup",
        "💶 EU261 Calculator",
        "🛡️ Fraud Detection",
        "🏢 Corporate Travel"
    ])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1: FLIGHT STATUS
    # ═══════════════════════════════════════════════════════════════════════════
    with ops_tabs[0]:
        render_flight_status_section()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2: PNR LOOKUP
    # ═══════════════════════════════════════════════════════════════════════════
    with ops_tabs[1]:
        render_pnr_section()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3: EU261 CALCULATOR
    # ═══════════════════════════════════════════════════════════════════════════
    with ops_tabs[2]:
        render_eu261_section()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 4: FRAUD DETECTION
    # ═══════════════════════════════════════════════════════════════════════════
    with ops_tabs[3]:
        render_fraud_section()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 5: CORPORATE TRAVEL
    # ═══════════════════════════════════════════════════════════════════════════
    with ops_tabs[4]:
        render_corporate_section()


def render_flight_status_section():
    """Render flight status and operations dashboard"""
    
    st.markdown("### 🛫 Flight Operations Dashboard")
    
    # Initialize or refresh operations data
    if 'ops_summary' not in st.session_state:
        st.session_state.ops_summary = simulate_daily_operations(50)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🔄 Refresh Operations", use_container_width=True):
            st.session_state.ops_summary = simulate_daily_operations(50)
            st.rerun()
    
    summary = st.session_state.ops_summary
    
    # Key Metrics
    st.markdown("#### Today's Operations")
    
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric(
            "Total Flights",
            summary['total_flights'],
            delta=None
        )
    
    with m2:
        otp = summary['on_time_performance']
        delta_color = "normal" if otp >= 80 else "inverse"
        st.metric(
            "On-Time %",
            f"{otp}%",
            delta=f"{otp - 85:.1f}%" if otp != 85 else None,
            delta_color=delta_color
        )
    
    with m3:
        st.metric(
            "Delayed",
            summary['delayed'],
            delta=None
        )
    
    with m4:
        st.metric(
            "Cancelled",
            summary['cancelled'],
            delta=None
        )
    
    # Second row
    m5, m6, m7, m8 = st.columns(4)
    
    with m5:
        st.metric(
            "✅ On Time",
            summary['on_time']
        )
    
    with m6:
        st.metric(
            "⏱️ Avg Delay",
            f"{summary['average_delay_minutes']:.0f} min"
        )
    
    with m7:
        st.metric(
            "🔴 Disruptions",
            summary['disruptions']
        )
    
    with m8:
        liability = summary['total_compensation_liability']
        st.metric(
            "💶 EU261 Liability",
            f"€{liability:,.0f}"
        )
    
    # Delay Reasons Chart
    if summary['delay_reasons']:
        st.markdown("#### Delay Reasons")
        
        import pandas as pd
        delay_df = pd.DataFrame([
            {"Reason": k, "Count": v}
            for k, v in summary['delay_reasons'].items()
        ])
        
        if not delay_df.empty:
            st.bar_chart(delay_df.set_index("Reason"))
    
    # Flight Status Table
    st.markdown("#### Flight Status Board")
    
    simulator = get_simulator()
    flights = list(simulator.flight_statuses.values())[:20]
    
    if flights:
        flight_data = []
        for f in flights:
            status_emoji = {
                "Scheduled": "🕐",
                "On Time": "✅",
                "Delayed": "⚠️",
                "Cancelled": "❌",
                "Boarding": "🚶",
                "Departed": "🛫",
                "In Flight": "✈️",
                "Landed": "🛬",
                "Arrived": "🏁"
            }.get(f.status, "❓")
            
            flight_data.append({
                "Flight": f.flight_number,
                "Route": f"{f.origin} → {f.destination}",
                "Scheduled": f.scheduled_departure,
                "Status": f"{status_emoji} {f.status}",
                "Delay": f"+{f.delay_minutes}min" if f.delay_minutes > 0 else "-",
                "Gate": f.departure_gate or "-"
            })
        
        st.dataframe(
            flight_data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No flight data available. Click 'Refresh Operations' to generate.")


def render_pnr_section():
    """Render PNR lookup and booking generator"""
    
    st.markdown("### 🎫 PNR & Booking Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Generate Demo Booking")
        
        num_pax = st.selectbox("Passengers", [1, 2, 3, 4], index=1)
        trip_type = st.selectbox("Trip Type", ["Round-Trip", "One-Way"])
        cabin = st.selectbox("Cabin Class", ["Economy", "Premium Economy", "Business Class", "First Class"])
        with_conn = st.checkbox("Include Connections", value=True)
        
        if st.button("🎫 Generate Booking", use_container_width=True):
            booking = generate_booking(
                num_passengers=num_pax,
                trip_type=trip_type,
                cabin=cabin,
                with_connections=with_conn
            )
            st.session_state.current_booking = booking
            st.success(f"✅ Booking generated: **{booking['pnr']}**")
    
    with col2:
        st.markdown("#### Quick Stats")
        
        if 'current_booking' in st.session_state:
            booking = st.session_state.current_booking
            
            st.info(f"**PNR:** {booking['pnr']}")
            st.info(f"**Status:** {booking['booking_status']}")
            st.info(f"**Cabin:** {booking['cabin_class']}")
            st.info(f"**Total:** ${booking['fare']['total']:,.2f}")
        else:
            st.info("Generate a booking to see details")
    
    # Display booking details if available
    if 'current_booking' in st.session_state:
        booking = st.session_state.current_booking
        
        st.markdown("---")
        st.markdown(f"### 📋 Booking Details: {booking['pnr']}")
        
        # Passengers
        st.markdown("#### 👥 Passengers")
        pax_data = []
        for pax in booking['passengers']:
            pax_data.append({
                "Name": pax['full_name'],
                "Type": pax['passenger_type'],
                "Loyalty": pax.get('loyalty_tier') or '-',
                "Seat Pref": pax['seat_preference'],
                "Meal": pax['meal_preference']
            })
        st.dataframe(pax_data, use_container_width=True, hide_index=True)
        
        # E-Tickets
        st.markdown("#### 🎫 E-Tickets")
        ticket_data = []
        for tkt in booking['etickets']:
            ticket_data.append({
                "Ticket Number": tkt['ticket_number'],
                "Passenger": tkt['passenger_name'],
                "Airline": tkt['airline_name'],
                "Status": tkt['ticket_status'],
                "Fare": f"${tkt['total_fare']:,.2f}"
            })
        st.dataframe(ticket_data, use_container_width=True, hide_index=True)
        
        # Itinerary
        st.markdown("#### ✈️ Itinerary")
        itin = booking['itinerary']
        
        for seg in itin['segments']:
            conn_info = f" (Connection: {seg['connection_time_minutes']}min)" if seg['connection_time_minutes'] else ""
            
            with st.container():
                c1, c2, c3 = st.columns([2, 3, 2])
                with c1:
                    st.markdown(f"**{seg['flight_number']}**")
                    st.caption(f"{seg['marketing_carrier_name']}")
                with c2:
                    st.markdown(f"**{seg['origin']}** ({seg['origin_city']}) → **{seg['destination']}** ({seg['destination_city']})")
                    st.caption(f"{seg['departure_date']} {seg['departure_time']} - {seg['arrival_time']} ({seg['duration_minutes']}min){conn_info}")
                with c3:
                    st.markdown(f"**{seg['cabin_class_name']}**")
                    st.caption(f"Seat: {seg['seat_assignment']} | {seg['aircraft_type']}")
        
        # Fare breakdown
        st.markdown("#### 💰 Fare Breakdown")
        fare = booking['fare']
        
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.metric("Base Fare", f"${fare['base_fare']:,.2f}")
        with fc2:
            st.metric("Taxes & Fees", f"${fare['taxes'] + fare['fuel_surcharge'] + fare['security_fee']:,.2f}")
        with fc3:
            st.metric("Total", f"${fare['total']:,.2f}")


def render_eu261_section():
    """Render EU261 compensation calculator"""
    
    st.markdown("### 💶 EU261 Compensation Calculator")
    st.markdown("Calculate passenger compensation under EU Regulation 261/2004")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Flight Details")
        
        # Airport selection
        airports = list(AIRPORTS.keys())
        origin = st.selectbox("Origin Airport", airports, index=airports.index("LHR") if "LHR" in airports else 0)
        destination = st.selectbox("Destination Airport", airports, index=airports.index("JFK") if "JFK" in airports else 1)
        
        # Airline
        airlines = list(AIRLINES.keys())
        airline = st.selectbox("Operating Airline", airlines, index=airlines.index("BA") if "BA" in airlines else 0)
        
        # Disruption type
        disruption = st.radio("Disruption Type", ["Delay", "Cancellation", "Denied Boarding"])
        
        if disruption == "Delay":
            delay_mins = st.slider("Delay (minutes)", 0, 600, 180, step=15)
            is_cancelled = False
            is_denied = False
        elif disruption == "Cancellation":
            delay_mins = 0
            is_cancelled = True
            is_denied = False
            advance_notice = st.slider("Advance Notice (days)", 0, 21, 0)
        else:
            delay_mins = 0
            is_cancelled = False
            is_denied = True
        
        # Extraordinary circumstances
        extraordinary = st.checkbox("Extraordinary Circumstances (weather, strike, etc.)")
    
    with col2:
        st.markdown("#### Calculation Result")
        
        if st.button("🧮 Calculate Compensation", use_container_width=True):
            kwargs = {
                "is_cancelled": is_cancelled,
                "is_denied_boarding": is_denied,
                "extraordinary_circumstances": extraordinary
            }
            if disruption == "Cancellation":
                kwargs["advance_notice_days"] = advance_notice
            
            result = calculate_eu261(origin, destination, airline, delay_mins, **kwargs)
            
            # Store result
            st.session_state.eu261_result = result
        
        if 'eu261_result' in st.session_state:
            result = st.session_state.eu261_result
            
            # Eligibility badge
            if result.eligible:
                st.success(f"✅ **ELIGIBLE** for compensation")
                st.markdown(f"### €{result.compensation_amount:,.0f}")
            else:
                st.error(f"❌ **NOT ELIGIBLE** for compensation")
            
            # Details
            st.markdown(f"**Regulation:** {result.regulation}")
            st.markdown(f"**Distance:** {result.distance_km:,.0f} km")
            st.markdown(f"**Reason:** {result.reason}")
            
            # Additional rights
            if result.additional_rights:
                st.markdown("#### Additional Rights")
                for right in result.additional_rights:
                    st.markdown(f"• {right}")
            
            # Exceptions
            if result.exceptions:
                st.warning("**Exceptions:**")
                for exc in result.exceptions:
                    st.markdown(f"• {exc}")
    
    # Reference table
    st.markdown("---")
    st.markdown("#### EU261 Compensation Rates")
    
    rate_data = [
        {"Distance": "< 1,500 km", "Delay Threshold": "3+ hours", "Compensation": "€250"},
        {"Distance": "1,500 - 3,500 km", "Delay Threshold": "3+ hours", "Compensation": "€400"},
        {"Distance": "> 3,500 km", "Delay Threshold": "4+ hours", "Compensation": "€600"},
    ]
    st.dataframe(rate_data, use_container_width=True, hide_index=True)


def render_fraud_section():
    """Render fraud detection dashboard"""
    
    st.markdown("### 🛡️ Fraud Detection & Risk Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Simulate Transaction")
        
        amount = st.number_input("Transaction Amount ($)", min_value=100, max_value=10000, value=1500)
        
        # Risk factors
        st.markdown("**Risk Factors (for simulation):**")
        ip_mismatch = st.checkbox("IP/Billing Country Mismatch")
        new_device = st.checkbox("New Device")
        vpn_used = st.checkbox("VPN/Proxy Detected")
        one_way = st.checkbox("One-Way International Ticket")
        last_minute = st.checkbox("Last Minute Booking (<24h)")
        
        if st.button("🔍 Assess Risk", use_container_width=True):
            # Generate assessment
            from services.compensation import get_fraud_detector
            detector = get_fraud_detector()
            
            # Custom assessment based on checkboxes
            assessment = detector.assess_transaction(
                transaction_id=f"TXN-{random.randint(10000, 99999)}",
                amount=amount,
                currency="USD",
                card_bin="411111",
                card_country="US" if not ip_mismatch else "UK",
                billing_country="US",
                ip_address="192.168.1.1",
                ip_country="US" if not ip_mismatch else "RU",
                email="customer@gmail.com",
                passenger_names=["John Smith"],
                cardholder_name="John Smith",
                is_one_way=one_way,
                destination_country="NG" if one_way else "UK",
                hours_to_departure=12 if last_minute else 168,
                device_fingerprint="abc123",
                is_new_device=new_device,
                is_vpn=vpn_used,
                previous_chargebacks=0,
                failed_attempts=0,
                bookings_last_hour=1
            )
            
            st.session_state.fraud_assessment = assessment
    
    with col2:
        st.markdown("#### Risk Assessment Result")
        
        if 'fraud_assessment' in st.session_state:
            assessment = st.session_state.fraud_assessment
            
            # Risk score gauge
            score = assessment.risk_score
            level = assessment.risk_level
            
            color = {
                "Low": "🟢",
                "Medium": "🟡",
                "High": "🟠",
                "Critical": "🔴"
            }.get(level, "⚪")
            
            st.markdown(f"### {color} Risk Score: {score}/100")
            st.progress(score / 100)
            
            st.markdown(f"**Level:** {level}")
            st.markdown(f"**Action:** {assessment.recommended_action}")
            
            # Indicators
            if assessment.indicators:
                st.markdown("#### Risk Indicators Found")
                for ind in assessment.indicators:
                    st.markdown(f"• **{ind['name']}** (+{ind['score']} points)")
                    st.caption(f"  {ind['description']}")
            
            # Recommendations
            st.markdown("---")
            if assessment.auto_decline:
                st.error("⛔ **AUTO-DECLINE** - High fraud risk")
            elif assessment.requires_manual_review:
                st.warning("👤 **MANUAL REVIEW** required")
            elif assessment.requires_3ds:
                st.info("🔐 **3D Secure** verification required")
            else:
                st.success("✅ **AUTO-APPROVE** - Low risk")
            
            st.metric("Chargeback Probability", f"{assessment.chargeback_probability*100:.1f}%")
        else:
            st.info("Configure risk factors and click 'Assess Risk'")


def render_corporate_section():
    """Render corporate travel management"""
    
    st.markdown("### 🏢 Corporate Travel Management")
    
    manager = get_corporate_manager()
    
    # Company selector
    companies = list(manager.companies.values())
    company_names = ["All Companies"] + [c.company_name for c in companies]
    selected_company = st.selectbox("Select Company", company_names)
    
    company_id = None
    if selected_company != "All Companies":
        for c in companies:
            if c.company_name == selected_company:
                company_id = c.company_id
                break
    
    # Analytics
    st.markdown("---")
    st.markdown("#### 📊 Travel Analytics")
    
    if st.button("📈 Generate Analytics Report", use_container_width=True):
        analytics = get_travel_analytics("2024-Q4", company_id)
        st.session_state.corporate_analytics = analytics
    
    if 'corporate_analytics' in st.session_state:
        analytics = st.session_state.corporate_analytics
        
        # Key metrics
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.metric("Total Bookings", analytics.total_bookings)
        with m2:
            st.metric("Total Spend", f"${analytics.total_spend:,.0f}")
        with m3:
            st.metric("In-Policy Rate", f"{analytics.in_policy_rate}%")
        with m4:
            st.metric("Total Savings", f"${analytics.total_savings:,.0f}")
        
        # Spend breakdown
        st.markdown("#### Spend Breakdown")
        
        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("✈️ Flights", f"${analytics.flight_spend:,.0f}")
        with s2:
            st.metric("🏨 Hotels", f"${analytics.hotel_spend:,.0f}")
        with s3:
            st.metric("📦 Other", f"${analytics.other_spend:,.0f}")
        
        # Violations
        if analytics.top_violations:
            st.markdown("#### ⚠️ Top Policy Violations")
            for v in analytics.top_violations[:5]:
                st.markdown(f"• **{v['type']}**: {v['count']} occurrences")
        
        # Spend by department
        if analytics.spend_by_department:
            st.markdown("#### Spend by Department")
            import pandas as pd
            dept_df = pd.DataFrame([
                {"Department": k, "Spend": v}
                for k, v in sorted(analytics.spend_by_department.items(), key=lambda x: x[1], reverse=True)[:10]
            ])
            st.bar_chart(dept_df.set_index("Department"))
    
    # Pending approvals
    st.markdown("---")
    st.markdown("#### ⏳ Pending Approvals")
    
    pending = manager.get_pending_approvals(company_id)
    
    if pending:
        for b in pending[:5]:
            with st.expander(f"📋 {b.booking_id} - {b.employee_name} (${b.total_cost:,.2f})"):
                st.markdown(f"**Company:** {b.company_name}")
                st.markdown(f"**Department:** {b.department}")
                st.markdown(f"**Purpose:** {b.trip_purpose}")
                st.markdown(f"**Dates:** {b.trip_start_date} to {b.trip_end_date}")
                
                if b.violations:
                    st.warning("**Policy Violations:**")
                    for v in b.violations:
                        st.markdown(f"• {v['type']}: {v['description']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.button("✅ Approve", key=f"approve_{b.booking_id}")
                with c2:
                    st.button("❌ Reject", key=f"reject_{b.booking_id}")
    else:
        st.info("No pending approvals")
    
    # Policy violations summary
    st.markdown("---")
    st.markdown("#### 📋 Policy Violations Summary")
    
    violations = manager.get_policy_violations_summary(company_id)
    
    v1, v2 = st.columns(2)
    with v1:
        st.metric("Total Violations", violations['total_violations'])
    with v2:
        st.metric("Bookings with Violations", violations['total_bookings_with_violations'])
    
    if violations['violation_breakdown']:
        for v in violations['violation_breakdown'][:5]:
            st.markdown(f"• **{v['type']}**: {v['count']} occurrences (${v['total_cost']:,.0f})")
