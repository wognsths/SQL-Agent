# SQL Agent Web Interface

A simple web interface for interacting with the SQL Agent using the A2A protocol.

## Features

- Submit queries in natural language or SQL syntax
- View query results in a table format
- Download results as Excel files
- Clean and modern UI with Bootstrap

## Setup

### Local Development

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory (you can copy from `.env.example`):
   ```
   SQL_AGENT_URL=http://localhost:10000
   PORT=8000
   HOST=0.0.0.0
   GOOGLE_API_KEY=your_google_api_key_here
   FLASK_DEBUG=True
   ```

3. Make sure the SQL Agent is running:
   ```
   python -m api.agents.sql_agent
   ```

4. Start the web interface:
   ```
   python -m api.web
   ```

5. Open your browser and navigate to: `http://localhost:8000`

### Docker Deployment

We provide Docker support for easy deployment:

1. Make sure Docker and Docker Compose are installed on your system

2. Create a `.env` file in the root directory with your configuration

3. Build and run using Docker Compose:
   ```
   docker-compose up -d
   ```

4. Access the web interface at: `http://localhost:8000`

#### Docker Environment Variables

You can modify the environment variables in the `.env` file or directly in the `docker-compose.yml` file:

- `SQL_AGENT_URL`: URL of the SQL Agent
- `PORT`: Port to bind the web server to
- `HOST`: Host to bind the server to
- `GOOGLE_API_KEY`: Your Google API key for the SQL Agent
- `FLASK_DEBUG`: Enable debug mode (set to False in production)

## Configuration

You can configure the web interface using environment variables or command-line options:

### Environment Variables:
- `SQL_AGENT_URL`: URL of the SQL Agent (default: `http://localhost:10000`)
- `HOST`: Host to bind the server to (default: `0.0.0.0`)
- `PORT`: Port to bind the server to (default: `8000`)
- `FLASK_DEBUG`: Enable debug mode (default: `False`)

### Command-line Options:
- `--host`: Host to bind the server to
- `--port`: Port to bind the server to
- `--sql-agent-url`: URL of the SQL Agent
- `--debug`: Enable debug mode

Example:
```
python -m api.web --port 9000 --sql-agent-url http://localhost:5000 --debug
```

## Usage

1. Enter your query in the text box. You can use natural language or SQL syntax:
   - "Show me all users who signed up last month"
   - "SELECT * FROM users WHERE created_at > '2023-01-01'"

2. Click "Submit Query" to send the query to the SQL Agent.

3. View the results in the table below.

4. Use the "Download Excel" button to download the results as an Excel file.

## Troubleshooting

- If you see "Error connecting to SQL Agent", make sure the SQL Agent is running.
- Make sure you have installed all required packages from requirements.txt.
- Check if the SQL Agent URL is correct in the configuration.
- When using Docker, ensure both containers are running with `docker-compose ps`.

## License

See the project's main license file. 