#!/usr/bin/env python
"""
SQL to Excel Workflow Runner

This script provides a command-line interface for running the SQL to Excel workflow.
It automates the process of:
1. Starting the SQL Agent server
2. Starting the Excel Agent server
3. Processing a query through both agents
4. Saving the resulting Excel file

Usage:
  python sql_to_excel.py --query "Show me all users who joined after 2020"
"""

import os
import sys
import json
import argparse
import asyncio
import subprocess
import time
import signal
import atexit
from pathlib import Path
import shutil

# Add the project root to Python path
sys.path.append(os.path.abspath("."))

from api.hosts.multiagent.sql_excel_workflow import SQLExcelWorkflow

# Global process references for cleanup
sql_agent_process = None
excel_agent_process = None

def cleanup_processes():
    """Kill any running agent processes on exit"""
    if sql_agent_process:
        print("Stopping SQL Agent...")
        sql_agent_process.terminate()
        
    if excel_agent_process:
        print("Stopping Excel Agent...")
        excel_agent_process.terminate()

# Register cleanup function
atexit.register(cleanup_processes)

def start_agent_servers(args):
    """Start the SQL and Excel agent servers as background processes"""
    global sql_agent_process, excel_agent_process
    
    # Start SQL Agent
    print(f"Starting SQL Agent on port {args.sql_port}...")
    sql_agent_process = subprocess.Popen(
        [sys.executable, "-m", "api.agents.sql_agent", "--port", str(args.sql_port)],
        stdout=subprocess.PIPE if not args.verbose else None,
        stderr=subprocess.PIPE if not args.verbose else None
    )
    
    # Start Excel Agent
    print(f"Starting Excel Agent on port {args.excel_port}...")
    excel_agent_process = subprocess.Popen(
        [sys.executable, "-m", "api.agents.excel_agent", "--port", str(args.excel_port)],
        stdout=subprocess.PIPE if not args.verbose else None,
        stderr=subprocess.PIPE if not args.verbose else None
    )
    
    # Give the servers time to start up
    print("Waiting for agents to start...")
    time.sleep(5)
    
    return (
        f"http://localhost:{args.sql_port}",
        f"http://localhost:{args.excel_port}"
    )

async def run_workflow(args, sql_url, excel_url):
    """Run the SQL to Excel workflow"""
    print(f"Processing query: {args.query}")
    
    # Create workflow instance
    workflow = SQLExcelWorkflow(
        sql_agent_url=sql_url,
        excel_agent_url=excel_url,
        output_dir=args.output_dir
    )
    
    # Process the query
    result = await workflow.process_query(
        query=args.query,
        format_options={
            "style_template": args.style,
            "include_metadata": args.include_metadata
        }
    )
    
    return result

def save_result_file(result, args):
    """Save the resulting file and return its path"""
    if not result.get("success", False):
        print("Workflow failed!")
        print(json.dumps(result, indent=2))
        return None
    
    excel_file = result.get("excel_file", {})
    if not excel_file or not excel_file.get("name"):
        print("No Excel file found in result!")
        return None
    
    # The file is already saved by the Excel agent
    # We just need to copy it to the final destination if needed
    source_path = None
    if "file_path" in excel_file:
        source_path = excel_file["file_path"]
    else:
        # Search in outputs directory 
        for root, _, files in os.walk(os.path.join(os.getcwd(), "outputs")):
            if excel_file["name"] in files:
                source_path = os.path.join(root, excel_file["name"])
                break
    
    if not source_path or not os.path.exists(source_path):
        print(f"Could not find source file: {excel_file['name']}")
        return None
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Determine destination path
    if args.output_file:
        dest_path = args.output_file
    else:
        dest_path = os.path.join(args.output_dir, excel_file["name"])
    
    # Copy file
    print(f"Saving Excel file to: {dest_path}")
    shutil.copy2(source_path, dest_path)
    
    return dest_path

async def main():
    parser = argparse.ArgumentParser(description="SQL to Excel Workflow Runner")
    parser.add_argument("--query", required=True, help="Natural language query to process")
    parser.add_argument("--output-dir", default="./outputs", help="Output directory")
    parser.add_argument("--output-file", help="Output file path (if not specified, uses generated name)")
    parser.add_argument("--sql-port", type=int, default=10000, help="Port for SQL Agent server")
    parser.add_argument("--excel-port", type=int, default=10001, help="Port for Excel Agent server")
    parser.add_argument("--style", choices=["default", "professional", "minimal", "colorful"], 
                        default="professional", help="Excel styling template")
    parser.add_argument("--include-metadata", action="store_true", help="Include metadata sheet in Excel file")
    parser.add_argument("--skip-server-start", action="store_true", 
                        help="Skip starting servers (assumes they're already running)")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output from agent servers")
    
    args = parser.parse_args()
    
    try:
        sql_url = f"http://localhost:{args.sql_port}"
        excel_url = f"http://localhost:{args.excel_port}"
        
        if not args.skip_server_start:
            sql_url, excel_url = start_agent_servers(args)
        
        # Run the workflow
        result = await run_workflow(args, sql_url, excel_url)
        
        # Save the resulting file
        output_path = save_result_file(result, args)
        
        if output_path:
            print("\nWorkflow completed successfully!")
            print(f"Excel file saved at: {output_path}")
            return 0
        else:
            print("\nWorkflow completed but no output file was saved.")
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1
    finally:
        # Cleanup happens via atexit handler
        pass

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 