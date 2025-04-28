from flask import Flask, render_template, jsonify, request, abort
import os
import json
from pathlib import Path
import uuid
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
# Enable CORS for specific origins
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://zenith-ed.netlify.app"]}})

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

@app.route('/api/deploy-dashboard', methods=['POST'])
def deploy_dashboard():
    """
    Deploy a dashboard for public sharing.
    """
    try:
        # Get dashboard data from the request
        dashboard_data = request.json
        
        # Create a unique ID for the dashboard
        dashboard_id = str(uuid.uuid4())
        
        # Sanitize dashboard name for filename
        safe_name = "".join(c for c in dashboard_data["name"] if c.isalnum() or c in [' ', '_', '-']).strip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        # Create dashboards directory if it doesn't exist
        os.makedirs(DASHBOARD_DIR, exist_ok=True)
        
        # Ensure dataset structure is valid
        if "dataset" not in dashboard_data:
            dashboard_data["dataset"] = {"headers": [], "rows": []}
        else:
            # Validate dataset format
            if not isinstance(dashboard_data["dataset"], dict):
                dashboard_data["dataset"] = {"headers": [], "rows": []}
            else:
                if "headers" not in dashboard_data["dataset"] or not isinstance(dashboard_data["dataset"]["headers"], list):
                    dashboard_data["dataset"]["headers"] = []
                if "rows" not in dashboard_data["dataset"] or not isinstance(dashboard_data["dataset"]["rows"], list):
                    dashboard_data["dataset"]["rows"] = []
        
        # Validate widgets
        if "widgets" not in dashboard_data or not isinstance(dashboard_data["widgets"], list):
            dashboard_data["widgets"] = []
        
        for widget in dashboard_data["widgets"]:
            if "config" not in widget:
                widget["config"] = {}
            if "type" not in widget:
                widget["type"] = "unknown"
        
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
        
        # Save dashboard data to file
        file_name = f"{safe_name}_{dashboard_id}.json"
        dashboard_path = DASHBOARD_DIR / file_name
        with open(dashboard_path, "w") as f:
            json.dump(dashboard_data, f)
            
        # Generate a URL for the dashboard
        host_url = request.host_url.rstrip('/')
        deploy_url = f"{host_url}/view/{safe_name}_{dashboard_id}"
        
        return jsonify({"deployUrl": deploy_url, "dashboardId": dashboard_id})
    except Exception as e:
        print(f"Error deploying dashboard: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Create dashboards directory if it doesn't exist
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    app.run(host="0.0.0.0", port=8050, debug=True) 