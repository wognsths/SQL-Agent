"""
Main entry point for the SQL Agent Web Interface
"""
import os
from dotenv import load_dotenv
import click
from api.web.app import app

# Load environment variables
load_dotenv()

@click.command()
@click.option("--host", default=None, help="Host to bind the server to")
@click.option("--port", default=None, type=int, help="Port to bind the server to")
@click.option("--sql-agent-url", default=None, help="URL of the SQL Agent")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def main(host, port, sql_agent_url, debug):
    """Run the SQL Agent Web Interface"""
    # Set the environment variables if provided via command line
    if sql_agent_url:
        os.environ['SQL_AGENT_URL'] = sql_agent_url
    
    if host:
        os.environ['HOST'] = host
    
    if port:
        os.environ['PORT'] = str(port)
    
    if debug:
        os.environ['FLASK_DEBUG'] = 'True'
    
    # Get the environment variables (possibly set by command line args)
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    sql_agent_url = os.environ.get('SQL_AGENT_URL')
    
    # Check if SQL Agent URL is set
    if not sql_agent_url:
        print("Warning: SQL_AGENT_URL not set. Using default: http://localhost:10000")
        os.environ['SQL_AGENT_URL'] = 'http://localhost:10000'
    
    # Run the Flask app
    print(f"Starting SQL Agent Web Interface on http://{host}:{port}")
    print(f"SQL Agent URL: {os.environ.get('SQL_AGENT_URL')}")
    print(f"Debug mode: {'enabled' if debug else 'disabled'}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main() 