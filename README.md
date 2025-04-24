# SQL Agent Web Application

SQL Agent Web Application provides a web interface for converting natural language queries to SQL and retrieving results from databases using the A2A (Agent-to-Agent) protocol.

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
- Web interface and API endpoints
- Docker support for easy deployment

## Installation and Setup

### Environment Configuration

1. Create a `.env` file for environment variables:
   ```
   # SQL Agent Web Interface Environment Variables
   SQL_AGENT_URL=http://localhost:10000
   PORT=8000
   HOST=0.0.0.0
   GOOGLE_API_KEY=your_google_api_key_here
   FLASK_DEBUG=True
   
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```
   
2. Add your Google API Key to the `.env` file
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Local Development Environment

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the SQL Agent server:
   ```
   python -m api.agents.sql_agent
   ```

3. Run the web interface:
   ```
   python -m api.web
   ```

4. Access the web interface at http://localhost:8000

### Docker Deployment

1. Install Docker and Docker Compose

2. Build and run using Docker Compose:
   ```
   docker-compose up -d
   ```

3. Access the web interface at http://localhost:8000

## Project Structure

- `api/agents/`: SQL Agent implementing the A2A protocol
- `api/common/`: Common modules for A2A protocol implementation
- `api/web/`: Web interface module
- `api/core/`: Database schema and connection management
- `Dockerfile`: Docker configuration for web interface
- `Dockerfile.sql_agent`: Docker configuration for SQL Agent
- `docker-compose.yml`: Docker Compose configuration

## Environment Variables

Main environment variables:

- `SQL_AGENT_URL`: SQL Agent server URL
- `PORT`: Web server port
- `HOST`: Web server host
- `GOOGLE_API_KEY`: Google API key
- `FLASK_DEBUG`: Debug mode setting

### Database Environment Variables

- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password

## Usage

1. Enter a natural language question or SQL query in the input box
   Example: "Show me all users" or "SELECT * FROM users"

2. Click the "Submit Query" button

3. View the results in the table

4. Click the "Download Excel" button to download the results as an Excel file

## Troubleshooting

- SQL Agent connection error: Verify that the SQL Agent server is running
- Database connection error: Check database configuration
- Docker execution error: Check logs with `docker-compose logs`
