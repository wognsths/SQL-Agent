from flask import Flask, render_template, request, jsonify, send_file
import os
import asyncio
import json
import pandas as pd
from io import BytesIO
from datetime import datetime
from common.client import A2AClient
from common.types import Message, TextPart, FilePart, FileContent
from uuid import uuid4

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration from environment variables
SQL_AGENT_URL = os.environ.get('SQL_AGENT_URL', 'http://localhost:10000')
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 8000))

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    """Handle SQL query requests"""
    data = request.json
    query_text = data.get('query', '')
    session_id = data.get('session_id', uuid4().hex)
    
    try:
        # Run the async query in a synchronous context
        response = asyncio.run(send_query(query_text, session_id))
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_excel():
    """Download query results as Excel file"""
    data = request.json
    results = data.get('results', [])
    
    if not results:
        return jsonify({'error': 'No results to download'}), 400
    
    try:
        # Convert the results to a pandas DataFrame
        df = pd.DataFrame(results)
        
        # Create an Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Results', index=False)
        
        output.seek(0)
        
        # Generate a filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'sql_results_{timestamp}.xlsx'
        
        # Return the Excel file as a downloadable attachment
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def send_query(query_text, session_id):
    """Send a query to the SQL agent and get the response"""
    client = A2AClient(url=SQL_AGENT_URL)
    
    # Create a message with the query
    message = Message(
        role="user",
        parts=[TextPart(text=query_text)]
    )
    
    # Prepare the request parameters
    payload = {
        "id": uuid4().hex,
        "sessionId": session_id,
        "message": message,
    }
    
    # Send the task to the agent
    try:
        response = await client.send_task(payload)
        
        if response.result and response.result.artifacts:
            # Process the artifacts and extract the results
            artifact = response.result.artifacts[0]
            content = artifact.parts[0].text if hasattr(artifact.parts[0], 'text') else str(artifact.parts[0])
            
            # Try to parse the content as JSON if it's a string
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    pass
            
            return {
                'success': True,
                'task_id': response.result.id,
                'session_id': response.result.sessionId,
                'state': response.result.status.state,
                'content': content
            }
        else:
            # Return the task status if no artifacts
            return {
                'success': True,
                'task_id': response.result.id,
                'session_id': response.result.sessionId,
                'state': response.result.status.state,
                'content': 'No results available'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT) 