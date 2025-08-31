import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import os
import re
import google.generativeai as genai
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agents import (
    GenerationRequest, IntentType, analyze_with_agents
)
import uuid
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from the Backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Local filesystem base path for storing files
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter()



def process_chart_data(data: List[Dict], config: Dict) -> Dict:
    """Process data according to chart configuration, handling large numbers."""
    logger.info(f"Processing chart data with config: {config}")
    df = pd.DataFrame(data)

    # Validate that we have data
    if df.empty:
        logger.warning("Empty DataFrame provided to process_chart_data")
        return {
            'type': 'bar',
            'data': {'labels': [], 'datasets': [{'label': 'No Data', 'data': []}]},
            'options': {'plugins': {'title': {'text': 'No Data Available'}}}
        }

    # Map agent config keys to expected keys
    chart_type = config.get('chart_type', 'bar')
    x_axis = config.get('x_axis', df.columns[0] if len(df.columns) > 0 else 'x')
    y_axis = config.get('y_axis', df.columns[1] if len(df.columns) > 1 else df.columns[0])
    aggregation = config.get('aggregation', 'none')
    title = config.get('chart_title', config.get('title', 'Chart'))  # Handle both chart_title and title

    # Validate that the specified columns exist
    if x_axis not in df.columns:
        logger.warning(f"X-axis column '{x_axis}' not found, using first column")
        x_axis = df.columns[0] if len(df.columns) > 0 else 'x'
    
    if y_axis not in df.columns:
        logger.warning(f"Y-axis column '{y_axis}' not found, using second column")
        y_axis = df.columns[1] if len(df.columns) > 1 else df.columns[0] if len(df.columns) > 0 else 'y'

    # Apply aggregation if specified
    if aggregation != 'none':
        try:
            if aggregation == 'sum':
                df = df.groupby(x_axis)[y_axis].sum().reset_index()
            elif aggregation == 'average':
                df = df.groupby(x_axis)[y_axis].mean().reset_index()
            elif aggregation == 'count':
                df = df.groupby(x_axis).size().reset_index(name=y_axis)
            elif aggregation == 'min':
                df = df.groupby(x_axis)[y_axis].min().reset_index()
            elif aggregation == 'max':
                df = df.groupby(x_axis)[y_axis].max().reset_index()
            elif aggregation == 'std':
                df = df.groupby(x_axis)[y_axis].std().reset_index()
        except Exception as e:
            logger.warning(f"Aggregation failed: {str(e)}, using original data")
            # If aggregation fails, use the original data
            pass

    logger.debug(f"Aggregated data: {df}")

    # Convert categorical values to string (Avoid converting numeric y-axis to string)
    df[x_axis] = df[x_axis].astype(str)

    # Ensure y-axis data is numeric for proper chart rendering
    try:
        df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
        # Remove rows with NaN values in y-axis
        df = df.dropna(subset=[y_axis])
    except Exception as e:
        logger.warning(f"Could not convert y-axis to numeric: {str(e)}")

    # Prepare data for chart
    labels = df[x_axis].tolist()
    data_values = df[y_axis].tolist()

    chart_config = {
        'type': chart_type,
        'data': {
            'labels': labels,
            'datasets': [{
                'label': y_axis,
                'data': data_values,
                'backgroundColor': [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                    '#FF9F40', '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'
                ],
                'borderColor': '#36A2EB',
                'fill': True
            }]
        },
        'options': {
            'responsive': True,
            'plugins': {
                'title': {
                    'display': True,
                    'text': title
                },
                'legend': {
                    'display': True
                }
            },
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'title': {
                        'display': True,
                        'text': y_axis
                    }
                },
                'x': {
                    'title': {
                        'display': True,
                        'text': x_axis
                    }
                }
            }
        }
    }

    logger.info(f"Chart configuration generated: {chart_config}")
    return chart_config

def save_user_data(user_id: str, file_name: str, data: pd.DataFrame) -> str:
    """Save user data locally with user ID for future cloud migration.
    
    Args:
        user_id: Unique identifier for the user
        file_name: Original file name
        data: DataFrame containing the data to save
        
    Returns:
        str: Path where the data was saved
    """
    # Create user directory if it doesn't exist
    user_dir = os.path.join(UPLOAD_FOLDER, user_id)
    os.makedirs(user_dir, exist_ok=True)
    
    # Create a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_base = os.path.splitext(file_name)[0]
    save_path = os.path.join(user_dir, f"{file_base}_{timestamp}.parquet")
    
    # Save as parquet for efficient storage
    data.to_parquet(save_path, index=False)
    logger.info(f"Saved user data to: {save_path}")
    return save_path

@router.post("/process")
async def process_data(
    files: List[UploadFile] = File(...),
    prompt: str = Form(...),
    user_id: str = Form("anonymous")  # Default to 'anonymous' if not provided
) -> Dict[str, Any]:
    """
    Process multiple files and a prompt, storing files locally.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        df_list = []
        # Process each uploaded file
        for file in files:
            extension = os.path.splitext(file.filename)[-1].lower()
            logger.info(f"Processing file: {file.filename} with extension: {extension}")

            # Read file content
            file_content = await file.read()
            
            # Save file locally temporarily
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            try:
                # Read file into pandas DataFrame based on extension
                if extension == '.csv':
                    part_df = pd.read_csv(file_path)
                elif extension in ['.xlsx', '.xls']:
                    part_df = pd.read_excel(file_path)
                elif extension == '.json':
                    part_df = pd.read_json(file_path)
                else:
                    raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")
                
                logger.info(f"Loaded DataFrame from {file.filename} with columns: {part_df.columns.tolist()}")

                # Clean column names
                clean_columns = {}
                for col in part_df.columns:
                    clean_col = re.sub(r'[^\w\s]', '', str(col)).strip().lower().replace(' ', '_')
                    clean_columns[col] = clean_col
                
                part_df = part_df.rename(columns=clean_columns)
                logger.info(f"Cleaned columns for {file.filename}: {part_df.columns.tolist()}")
                
                df_list.append(part_df)
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error processing file {file.filename}: {str(e)}")
            
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)

        # Combine all DataFrames
        if not df_list:
            raise HTTPException(status_code=400, detail="No valid data found in any file")
            
        # Combine DataFrames with different columns
        combined_df = pd.concat(df_list, ignore_index=True)
        logger.info(f"Combined DataFrame shape: {combined_df.shape}, columns: {combined_df.columns.tolist()}")

        if len(files) > 1:
            prompt = f"(Combined multiple files) {prompt}"

        # Use the new agent workflow
        generation_request = GenerationRequest(prompt=prompt, columns=combined_df.columns.tolist())
        agent_result = await analyze_with_agents(generation_request, combined_df)

        logger.info(f"Agent result: {agent_result}")

        # Parse the result and return appropriate response
        intent = agent_result.get("intent")
        if intent == IntentType.VISUALIZATION or intent == "visualization":
            chart_config = agent_result.get("chart_config")
            processed_chart_data = process_chart_data(combined_df.to_dict('records'), chart_config)
            return {
                "type": "chart",
                "config": processed_chart_data,
                "data": combined_df.to_dict('records')
            }
        elif intent == IntentType.TRANSFORMATION or intent == "transformation":
            result = agent_result.get("result")
            # result is expected to be a DataFrame or list of dicts
            if isinstance(result, pd.DataFrame):
                data = result.to_dict('records')
            else:
                data = result
            return {
                "type": "table",
                "data": data,
                "message": "Data transformed successfully."
            }
        elif intent == IntentType.STATISTICAL or intent == "statistical":
            result = agent_result.get("result")
            # Convert result to a JSON-serializable format
            if isinstance(result, pd.DataFrame):
                result_data = result.to_dict('records')
            elif isinstance(result, dict):
                result_data = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in result.items()}
            elif isinstance(result, (np.ndarray, list)):
                result_data = result.tolist() if isinstance(result, np.ndarray) else result
            else:
                result_data = str(result)
            return {
                "type": "statistical_result",
                "result": result_data,
                "message": "Statistical analysis completed."
            }
        else:
            logger.error(f"Unknown or unsupported intent: {intent}")
            raise HTTPException(status_code=400, detail="Could not determine the intent of the prompt.")

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup any temporary files if needed
        pass

@router.post("/generate-dashboard")
async def generate_dashboard(prompt: str, columns: List[str], data: List[Dict[str, Any]]):
    """Generate dashboard widgets based on natural language prompt."""
    logger.info(f"Generating dashboard with prompt: {prompt}")
    try:
        # Convert data to DataFrame for agent processing
        df = pd.DataFrame(data)
        
        # Use the new agent workflow
        generation_request = GenerationRequest(prompt=prompt, columns=columns)
        agent_result = await analyze_with_agents(generation_request, df)
        
        logger.info(f"Agent result for dashboard: {agent_result}")
        
        # Generate widget configurations based on agent result
        widgets = []
        intent = agent_result.get("intent", "visualization")
        
        # Process based on intent
        if intent == "visualization" or "chart" in prompt.lower() or "plot" in prompt.lower() or "visualize" in prompt.lower():
            # Generate visualization widget(s)
            chart_config = agent_result.get("chart_config", {})
            if chart_config:
                widgets.append({
                    "type": "chart",
                    "id": f"chart_{len(widgets)+1}",
                    "config": {
                        "title": chart_config.get("chart_title", chart_config.get("title", "Chart")),
                        "chartType": chart_config.get("chart_type", "bar"),
                        "xColumn": columns.index(chart_config.get("x_axis", columns[0])) if chart_config.get("x_axis") in columns else 0,
                        "yColumns": [columns.index(chart_config.get("y_axis", columns[1] if len(columns) > 1 else columns[0]))] if chart_config.get("y_axis") in columns else [1 if len(columns) > 1 else 0],
                        "size": 2  # Medium size as default
                    }
                })
        
        if "table" in prompt.lower():
            # Generate table widget
            widgets.append({
                "type": "table",
                "id": f"table_{len(widgets)+1}",
                "config": {
                    "title": "Data Table",
                    "columns": list(range(min(5, len(columns)))),  # First 5 columns by default
                    "showPagination": True,
                    "size": 2  # Medium size as default
                }
            })
        
        if intent == "statistical" or "stat" in prompt.lower() or "statistic" in prompt.lower():
            # Generate stat widget(s)
            # Attempt to find a numeric column for statistics
            numeric_columns = []
            for i, col in enumerate(columns):
                if any(isinstance(row.get(col), (int, float)) for row in data if row.get(col) is not None):
                    numeric_columns.append(i)
            
            if numeric_columns:
                widgets.append({
                    "type": "stat",
                    "id": f"stat_{len(widgets)+1}",
                    "config": {
                        "title": "Key Statistics",
                        "column": numeric_columns[0],
                        "metrics": ["avg", "min", "max"],
                        "size": 1  # Small size as default
                    }
                })
        
        if "insight" in prompt.lower() or "analyze" in prompt.lower():
            # Generate insight widget - use agent result if available
            insight_text = "Data analysis completed."
            if agent_result.get("result"):
                insight_text = str(agent_result["result"])
            
            widgets.append({
                "type": "insight",
                "id": f"insight_{len(widgets)+1}",
                "config": {
                    "title": "Data Insight",
                    "text": insight_text,
                    "size": 2  # Medium size as default
                }
            })
        
        # If no specific widgets were requested, generate a default dashboard
        if not widgets:
            # Create default dashboard with chart, table and stat
            # Choose first column as x-axis and second as y-axis
            x_col = 0
            y_col = 1 if len(columns) > 1 else 0
            
            widgets = [
                {
                    "type": "chart",
                    "id": "chart_1",
                    "config": {
                        "title": "Data Visualization",
                        "chartType": "bar",
                        "xColumn": x_col,
                        "yColumns": [y_col],
                        "size": 2
                    }
                },
                {
                    "type": "table",
                    "id": "table_1",
                    "config": {
                        "title": "Data Table",
                        "columns": list(range(min(5, len(columns)))),
                        "showPagination": True,
                        "size": 2
                    }
                }
            ]
            
            # Add stat widget if we have numeric columns
            numeric_columns = []
            for i, col in enumerate(columns):
                if any(isinstance(row.get(col), (int, float)) for row in data if row.get(col) is not None):
                    numeric_columns.append(i)
            
            if numeric_columns:
                widgets.append({
                    "type": "stat",
                    "id": "stat_1",
                    "config": {
                        "title": "Key Statistics",
                        "column": numeric_columns[0],
                        "metrics": ["avg", "min", "max"],
                        "size": 1
                    }
                })
        
        # Arrange widgets in a layout (side by side where appropriate)
        layout = []
        current_row = []
        total_size = 0
        
        for widget in widgets:
            widget_size = widget["config"]["size"]
            
            # If adding this widget exceeds row width, start a new row
            if total_size + widget_size > 4:
                layout.append(current_row)
                current_row = [widget]
                total_size = widget_size
            else:
                current_row.append(widget)
                total_size += widget_size
        
        # Add the last row if not empty
        if current_row:
            layout.append(current_row)
        
        return {
            "widgets": widgets,
            "layout": layout
        }
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")

@router.post("/deploy-dashboard")
async def deploy_dashboard(dashboard_data: dict):
    """
    Deploy a dashboard using Cloudflare Tunnels for public sharing.
    
    This is a prototype implementation that saves the dashboard data to a file
    and creates a public URL using Cloudflare Tunnels.
    """
    try:
        # Create a unique ID for the dashboard
        dashboard_id = str(uuid.uuid4())
        
        # Sanitize dashboard name for filename
        safe_name = "".join(c for c in dashboard_data["name"] if c.isalnum() or c in [' ', '_', '-']).strip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        # Create dashboards directory if it doesn't exist
        os.makedirs("dashboards", exist_ok=True)
        
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
        
        # Sanitize dashboard data to prevent JSON parsing errors when viewing
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
        dashboard_path = f"Dashboard_Viewer/dashboards/{safe_name}_{dashboard_id}.json"
        with open(dashboard_path, "w") as f:
            json.dump(dashboard_data, f)
            
        # In a production environment, you would use the Cloudflare API to create a tunnel
        # For this prototype, we'll assume the Cloudflare tunnel is already running
        # and serving the /dashboards directory
        
        # Generate a URL for the dashboard
        tunnel_hostname = os.getenv("CLOUDFLARE_TUNNEL_HOSTNAME", "ai.edventuretech.in")
        # Remove https:// if present
        if tunnel_hostname.startswith("https://"):
            tunnel_hostname = tunnel_hostname[8:]
        elif tunnel_hostname.startswith("http://"):
            tunnel_hostname = tunnel_hostname[7:]
        
        deploy_url = f"https://{tunnel_hostname}/view/{safe_name}_{dashboard_id}"
        
        return {"deployUrl": deploy_url, "dashboardId": dashboard_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deploying dashboard: {str(e)}")