# SQL-Agent

SQL Agent using A2A architecture for natural language to SQL queries and Excel exports.

## Overview

This project implements a modular Agent-to-Agent (A2A) architecture for processing natural language queries against databases:

1. **SQL Agent** - Converts natural language to SQL queries and executes them against a database
2. **Excel Agent** - Formats SQL results into professional Excel spreadsheets
3. **Workflow Integration** - Connects these agents for end-to-end processing

## Features

- Natural language to SQL conversion
- Database schema exploration
- Query execution and result retrieval
- Automated Excel report generation with various styling options
- A2A standard protocol for agent communication
- Command-line and API interfaces

## Quick Start

### Prerequisites

- Python 3.8+
- Google API key (for Gemini model)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/SQL-Agent.git
   cd SQL-Agent
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```
   cp .env.example .env
   # Edit .env to add your Google API key
   ```

   Your `.env` file should contain:
   ```
   # API Keys
   GOOGLE_API_KEY=your_google_api_key_here

   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password

   # Agent Settings
   SQL_AGENT_PORT=10000
   EXCEL_AGENT_PORT=10001

   # Output Settings
   OUTPUT_DIR=./outputs
   ```

### Running the SQL-to-Excel Workflow

For the complete workflow (SQL query → Excel export):

```bash
python sql_to_excel.py --query "Show me all users who joined after 2020" --style professional
```

Options:
- `--query` - Natural language query (required)
- `--output-dir` - Directory to save output files (default: ./outputs)
- `--output-file` - Specific output filename (optional)
- `--style` - Excel style template (default: professional, options: default, professional, minimal, colorful)
- `--include-metadata` - Include a metadata sheet with query details

### Running Individual Agents

#### SQL Agent

```bash
python -m api.agents.sql_agent --port 10000
```

#### Excel Agent

```bash
python -m api.agents.excel_agent --port 10001
```

## Architecture

The system uses the Agent-to-Agent (A2A) architecture, where:

1. Each agent publishes its capabilities in a standardized agent card
2. Agents communicate using JSON-RPC over HTTP
3. Tasks are processed asynchronously and can be streamed or pushed via notifications
4. Artifacts (results) can include text, structured data, or files

### Data Flow

```
User Query → Host Agent → SQL Agent → Excel Agent → Excel File
```

### Output

The primary output is an Excel file with:
- Formatted SQL query results
- Optional metadata sheet with query information
- Configurable styling and formatting

## Extending

New agents can be added by:
1. Creating a new agent directory in `api/agents/`
2. Implementing the A2A protocol handlers
3. Publishing an agent card with capabilities
4. Registering with the host agent or workflow
