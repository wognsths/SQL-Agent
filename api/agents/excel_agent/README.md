# Excel Agent for A2A Architecture

Excel Agent is a specialized service that converts SQL query results into formatted Excel files with various styling options.

## Features

- Convert SQL query results to Excel spreadsheets
- Multiple styling templates (default, professional, minimal, colorful)
- Automatic column width adjustment
- Optional metadata sheet with query details
- Auto-filtering and freezing panes
- Clean API interface following A2A protocol

## Usage

The Excel Agent accepts input in the form of an `ExcelRequestMessage` with the following structure:

```json
{
  "query": "Natural language query that was processed",
  "sql_query": "SELECT * FROM users WHERE joined_date > '2020-01-01'",
  "result": [
    {"id": 1, "name": "John", "joined_date": "2021-03-15"},
    {"id": 2, "name": "Jane", "joined_date": "2022-01-20"}
  ],
  "format_options": {
    "style_template": "professional",
    "include_metadata": true
  }
}
```

### Format Options

- `sheet_name`: Name of the data sheet (default: "Data")
- `include_headers`: Whether to include column headers (default: true)
- `auto_filter`: Add filtering capability to columns (default: true)
- `freeze_panes`: Freeze the header row (default: true)
- `column_width_auto`: Automatically adjust column widths (default: true)
- `include_timestamp`: Include generation timestamp (default: true)
- `include_query`: Include original query in metadata (default: true)
- `include_metadata`: Add a metadata sheet (default: true)
- `style_template`: Styling template to use (default: "default")
  - Options: "default", "professional", "minimal", "colorful"

## Running the Agent

Start the Excel Agent server:

```bash
python -m api.agents.excel_agent --port 10001
```

The agent will be available at http://localhost:10001/ and will expose the standard A2A endpoints.

## Integration with SQL Agent

This agent is designed to work seamlessly with the SQL Agent to form a complete natural language to Excel workflow:

1. SQL Agent converts natural language to SQL and executes queries
2. Excel Agent formats the results into professional Excel files
3. The final Excel file is returned to the user

Use the integrated workflow script for the complete pipeline:

```bash
python sql_to_excel.py --query "Show me all users who joined after 2020" --style professional
``` 