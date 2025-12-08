# Agent Performance & Commission Tracking System

A comprehensive insurance agent management system with automated commission calculation and performance tracking.

## Features

- **Login System**: Separate access for administrators and agents
- **Admin Dashboard**:
  - View all agents and their profiles
  - Add new agents with region and targets
  - Export data for audits
  - Monitor agent performance across regions

- **Employee Dashboard**:
  - View personal profile and targets
  - Real-time performance metrics (KPIs)
  - Commission tracking
  - Policy sales history
  - Productivity metrics

- **Automated Commission Calculation**: AI-powered rule engine calculates commissions based on policy type, premium amount, and tenure

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the application at: `http://localhost:8080`

## Login Credentials

### Admin Access
- Username: `admin`
- Password: `admin123`

### Agent Access
- Username: Any agent ID (e.g., `AGT-10238`, `AGT-10239`, etc.)
- Password: `agent123`

## Available Agent IDs
- AGT-10234, AGT-10238, AGT-10239, AGT-10240, AGT-10241
- AGT-10242, AGT-10243, AGT-10244, AGT-10245, AGT-10246
- AGT-10247, AGT-10248

## System Architecture

- **Frontend**: NiceGUI (Python-based web framework)
- **Backend**: LangChain with OpenAI for AI-powered calculations
- **Data Storage**: JSON file-based storage
- **Commission Engine**: AI agent with predefined rules

## Key Metrics Calculated

1. **Total Premium Amount**: Sum of all premiums by policy type
2. **Average Tenure**: Average policy duration in months
3. **Agent Commission**: 10% of total premium amount
4. **Count of Premiums**: Policies sold in last 6 months
5. **Agent Productivity**: Percentage of target achieved (last 6 months)
6. **Average Policy Value**: Average premium of policies sold in last 3 months

## Data Export

Administrators can export agent data to JSON format for audit purposes from the Reports tab.
