from flask import Flask, render_template, jsonify, request, abort
import os
import json
from pathlib import Path
import uuid

app = Flask(__name__, static_folder="static", template_folder="templates")

# Directory where dashboard files are stored
DASHBOARD_DIR = Path("dashboards")

@app.route('/')
def index():
    """List all available dashboards"""
    dashboards = []
    if DASHBOARD_DIR.exists():
        for file in DASHBOARD_DIR.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    dashboards.append({
                        "id": file.stem,
                        "name": data.get("name", "Unnamed Dashboard"),
                        "url": f"/view/{file.stem}"
                    })
            except Exception as e:
                print(f"Error reading dashboard {file}: {e}")
    
    return render_template("dashboard_list.html", dashboards=dashboards)

@app.route('/view/<dashboard_id>')
def view_dashboard(dashboard_id):
    """View a specific dashboard"""
    # Sanitize input to prevent directory traversal
    dashboard_id = os.path.basename(dashboard_id)
    dashboard_path = DASHBOARD_DIR / f"{dashboard_id}.json"
    
    if not dashboard_path.exists():
        return render_template("error.html", error="Dashboard not found", message="The requested dashboard could not be found."), 404
    
    try:
        with open(dashboard_path, 'r') as f:
            dashboard_data = json.load(f)
        
        # Sanitize dashboard data to prevent JSON parsing errors
        def sanitize_json_value(value):
            if isinstance(value, str):
                # Remove control characters that could break JSON parsing
                return ''.join(c for c in value if ord(c) >= 32 or c in '\n\r\t')
            elif isinstance(value, dict):
                return {k: sanitize_json_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_json_value(item) for item in value]
            else:
                return value
        
        dashboard_data = sanitize_json_value(dashboard_data)
        
        # Validate dashboard data
        if not isinstance(dashboard_data, dict):
            raise ValueError("Invalid dashboard data format")
        
        # Ensure required fields exist
        if "name" not in dashboard_data:
            dashboard_data["name"] = "Unnamed Dashboard"
        
        if "widgets" not in dashboard_data or not isinstance(dashboard_data["widgets"], list):
            dashboard_data["widgets"] = []
        
        # Ensure dataset exists
        if "dataset" not in dashboard_data:
            dashboard_data["dataset"] = {"headers": [], "rows": []}
            
        # Check each widget for proper configuration
        for widget in dashboard_data["widgets"]:
            if "type" not in widget:
                widget["type"] = "unknown"
            if "config" not in widget:
                widget["config"] = {}
            if "id" not in widget:
                widget["id"] = f"widget-{str(uuid.uuid4())[:8]}"
        
        return render_template("dashboard_viewer.html", 
                               dashboard=dashboard_data,
                               dashboard_id=dashboard_id)
    except json.JSONDecodeError:
        return render_template("error.html", error="Invalid dashboard data", message="The dashboard file contains invalid data."), 500
    except Exception as e:
        print(f"Error loading dashboard {dashboard_id}: {e}")
        return render_template("error.html", error="Error loading dashboard", message=str(e)), 500

@app.route('/api/dashboard/<dashboard_id>')
def get_dashboard_data(dashboard_id):
    """API endpoint to get dashboard data"""
    dashboard_id = os.path.basename(dashboard_id)
    dashboard_path = DASHBOARD_DIR / f"{dashboard_id}.json"
    
    if not dashboard_path.exists():
        abort(404)
    
    try:
        with open(dashboard_path, 'r') as f:
            dashboard_data = json.load(f)
        
        # Sanitize dashboard data to prevent JSON parsing errors
        def sanitize_json_value(value):
            if isinstance(value, str):
                # Remove control characters that could break JSON parsing
                return ''.join(c for c in value if ord(c) >= 32 or c in '\n\r\t')
            elif isinstance(value, dict):
                return {k: sanitize_json_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_json_value(item) for item in value]
            else:
                return value
        
        dashboard_data = sanitize_json_value(dashboard_data)
        
        return jsonify(dashboard_data)
    except Exception as e:
        print(f"Error loading dashboard {dashboard_id}: {e}")
        abort(500)

if __name__ == "__main__":
    # Create dashboards directory if it doesn't exist
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    app.run(host="0.0.0.0", port=8050, debug=True) 