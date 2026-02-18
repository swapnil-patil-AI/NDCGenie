# ✈️ NDC Genie - Enterprise Airline Transaction Lifecycle Tracker

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)
![Claude AI](https://img.shields.io/badge/Claude%20AI-Powered-purple.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**A production-ready, AI-powered application for airline customer service teams to track transactions, investigate failures, and manage refunds across the complete customer journey.**

[Features](#-features) • [Installation](#-installation) • [Deployment](#-deployment) • [Usage](#-usage) • [API Reference](#-api-reference) • [Architecture](#-architecture)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Usage Guide](#-usage-guide)
- [API Reference](#-api-reference)
- [Architecture](#-architecture)
- [Data Models](#-data-models)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

### Problem Statement

Airlines face significant challenges in tracking customer transactions across multiple stages:

```
Search → Selection → Booking → Payment → Ticketing → Confirmation → Refund
```

When failures occur at any stage, customer service teams struggle to:
- Quickly identify what went wrong
- Track refund status across multiple systems
- Understand the complete customer journey
- Identify patterns in failures
- Meet SLA requirements

### Solution

**NDC Genie** provides a unified, AI-powered platform that enables customer service teams to:

1. **Natural Language Queries**: Ask questions about transactions in plain English
2. **Complete Visibility**: View the entire transaction lifecycle at a glance
3. **Intelligent Analysis**: AI-powered pattern recognition and failure analysis
4. **Priority Management**: Automatic prioritization with SLA tracking
5. **Refund Tracking**: End-to-end refund status monitoring

---

## ✨ Features

### 💬 AI-Powered Chat Assistant
- Natural language transaction queries
- Intelligent failure investigation
- Pattern analysis and insights
- Contextual recommendations
- Powered by Claude AI (Anthropic)

### 📋 Transaction Browser
- Real-time transaction search
- Multi-field filtering (status, priority, date range)
- Detailed transaction views
- Export to CSV/JSON
- Pagination and sorting

### 📈 Analytics Dashboard
- Key performance indicators
- Success rate tracking
- Failure breakdown analysis
- Priority distribution
- Refund statistics

### 🔔 SLA Management
- Automatic SLA breach detection
- Priority-based routing
- Escalation tracking
- Response time monitoring

### 🔐 Enterprise Features
- Secure API key management
- Role-based access (future)
- Audit logging (future)
- Integration-ready architecture

---

## 💻 System Requirements

### Minimum Requirements
- Python 3.9 or higher
- 2 GB RAM
- 1 GB disk space
- Internet connection (for Claude AI)

### Recommended
- Python 3.11+
- 4 GB RAM
- SSD storage
- Stable broadband connection

### Dependencies
```
streamlit>=1.31.0
anthropic>=0.18.0
pandas>=2.1.0
python-dateutil>=2.8.2
```

---

## 🚀 Installation

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/your-org/ndc-genie.git
cd ndc-genie

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Option 2: Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build and run
docker build -t ndc-genie .
docker run -p 8501:8501 ndc-genie
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude AI | Yes* |

*Can also be entered via the UI

### Streamlit Configuration

The `.streamlit/config.toml` file contains UI and server settings:

```toml
[theme]
primaryColor = "#2b6cb0"
backgroundColor = "#f8fafc"

[server]
headless = true
enableCORS = false

[client]
showErrorDetails = false
```

### Application Configuration

Edit `utils/config.py` for application-level settings:

```python
@dataclass
class AppConfig:
    APP_NAME: str = "NDC Genie"
    APP_VERSION: str = "2.0.0"
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    DEMO_TRANSACTION_COUNT: int = 200
    SLA_RESPONSE_TIME: int = 4  # hours
    SLA_RESOLUTION_TIME: int = 24  # hours
```

---

## ☁️ Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-org/ndc-genie.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets**
   - Go to App Settings → Secrets
   - Add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```

### AWS Deployment

```bash
# Using AWS Elastic Beanstalk
eb init ndc-genie --platform python-3.11
eb create production
eb deploy
```

### Heroku Deployment

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Deploy
heroku create ndc-genie
heroku config:set ANTHROPIC_API_KEY=sk-ant-xxx
git push heroku main
```

---

## 📖 Usage Guide

### Getting Started

1. **Enter API Key**: In the sidebar, enter your Anthropic API key
2. **Explore Transactions**: Browse the demo data or connect your own
3. **Ask Questions**: Use the AI chat to query transactions
4. **Analyze Patterns**: Check the Analytics dashboard

### Sample AI Queries

| Category | Example Query |
|----------|--------------|
| **Lookup** | "Find transaction TXN-202501-ABC12345" |
| **Search** | "Show all bookings for john.smith@email.com" |
| **Failures** | "Why did transaction TXN-XXX fail?" |
| **Patterns** | "What are the most common payment errors?" |
| **Refunds** | "List all pending refunds over $500" |
| **Analytics** | "What is our success rate this week?" |

### Filtering Transactions

Use the sidebar filters to narrow down results:
- **Status**: Completed, Failed, Refunded, etc.
- **Priority**: Critical, High, Medium, Low
- **Date Range**: Today, Last 7 Days, Last 30 Days

### Exporting Data

Click "Export to CSV" or "Export to JSON" in the sidebar to download filtered transactions.

---

## 🔌 API Reference

### ClaudeAssistant

```python
from utils.ai_assistant import ClaudeAssistant

# Initialize
assistant = ClaudeAssistant(api_key="sk-ant-xxx")

# Get response
response = assistant.get_response(
    messages=[{"role": "user", "content": "Show failed transactions"}],
    transactions=transaction_data
)

# Quick analysis
analysis = assistant.get_quick_analysis(transactions, "payment_failures")
```

### DemoDataGenerator

```python
from data.demo_data import get_demo_data, DemoDataGenerator

# Quick generation
transactions = get_demo_data(count=200, seed=42)

# Custom generation
generator = DemoDataGenerator(seed=42)
transaction = generator.generate_transaction()
```

### UI Components

```python
from components.ui_components import (
    get_status_badge,
    get_priority_badge,
    render_lifecycle_visual,
    render_metric_card
)

# Status badge
html = get_status_badge("Completed")

# Priority badge  
html = get_priority_badge("Critical")

# Lifecycle visual
html = render_lifecycle_visual(transaction['lifecycle'])
```

---

## 🏗️ Architecture

```
ndc_genie/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
│
├── .streamlit/
│   ├── config.toml        # Streamlit configuration
│   └── secrets.toml       # Secrets (not in repo)
│
├── components/
│   ├── __init__.py
│   └── ui_components.py   # UI rendering functions
│
├── data/
│   ├── __init__.py
│   └── demo_data.py       # Demo data generation
│
└── utils/
    ├── __init__.py
    ├── config.py          # Application configuration
    └── ai_assistant.py    # Claude AI integration
```

### Design Patterns

- **Modular Architecture**: Separated concerns for maintainability
- **Configuration as Code**: Centralized settings in `config.py`
- **Dependency Injection**: API keys passed as parameters
- **Caching**: Streamlit caching for demo data
- **State Management**: Session state for chat history

---

## 📊 Data Models

### Transaction

```python
{
    "transaction_id": "TXN-202501-ABCD1234",
    "customer": {
        "customer_id": "CUST-12345",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-123-4567",
        "loyalty_tier": "Gold",
        "loyalty_points": 45000,
        "member_since": "2020-01-15",
        "lifetime_value": 15000.00
    },
    "flight": {
        "flight_number": "SW1234",
        "airline_name": "SkyWings Airlines",
        "origin": "JFK",
        "destination": "LAX",
        "departure_date": "2025-02-15",
        "cabin_class": "Business",
        "passengers": 2
    },
    "pricing": {
        "base_fare": 1200.00,
        "taxes": 180.00,
        "total": 1450.00,
        "currency": "USD"
    },
    "lifecycle": {
        "search": {"status": "completed", "timestamp": "..."},
        "selection": {"status": "completed", "timestamp": "..."},
        "booking": {"status": "completed", "booking_ref": "ABCDEF"},
        "payment": {"status": "failed", "details": "Card declined"},
        "ticketing": {"status": "not_reached"},
        "refund": {"status": "not_applicable"}
    },
    "status": "Failed",
    "priority": "High",
    "sla_breach": false,
    "error_info": {
        "error_stage": "Payment",
        "error_code": "ERR-PAY-1234",
        "error_message": "Card declined - Insufficient funds",
        "suggested_resolution": "Advise customer to use different payment method"
    }
}
```

### Lifecycle Stages

| Stage | Description | Key Fields |
|-------|-------------|------------|
| Search | Customer searches for flights | results_count, filters, device |
| Selection | Customer selects a flight | alternatives_viewed, fare_rules |
| Booking | Passenger details entered | booking_ref, validation_status |
| Payment | Payment processed | payment_method, auth_code, fraud_score |
| Ticketing | E-ticket generated | pnr, e_ticket_number, itinerary_sent |
| Confirmation | Confirmations sent | email_sent, sms_sent |
| Refund | Refund processed (if applicable) | refund_amount, refund_reason |

---

## 🔧 Troubleshooting

### Common Issues

#### API Key Not Working
```
Error: Authentication Error
```
**Solution**: Verify your API key at [console.anthropic.com](https://console.anthropic.com)

#### Slow Response Times
**Solution**: 
- Reduce `DEMO_TRANSACTION_COUNT` in config
- Check internet connection
- Consider API rate limits

#### UI Not Loading
**Solution**:
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart application
streamlit run app.py
```

### Getting Help

1. Check the **Help** tab in the application
2. Review the [Anthropic Documentation](https://docs.anthropic.com)
3. Check [Streamlit Documentation](https://docs.streamlit.io)

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Add unit tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for Claude AI
- [Streamlit](https://streamlit.io) for the amazing framework
- The airline industry professionals who inspired this solution

---

<div align="center">

**Built with ❤️ for Customer Service Excellence**

[⬆ Back to Top](#️-ndc-genie---enterprise-airline-transaction-lifecycle-tracker)

</div>
