import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from scipy import stats
import os
import re
import google.generativeai as genai
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.ml.stat import Correlation
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.linalg import Vectors
from dotenv import load_dotenv
from agents import analyze_prompt_intent, get_chart_config, get_transformation_code, get_statistical_code
import uuid
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize Spark with HDFS configuration
spark = SparkSession.builder \
    .appName("DataTransformation") \
    .config("spark.hadoop.fs.defaultFS", os.getenv("HDFS_NAMENODE_URL", "hdfs://0.0.0.0:19000")) \
    .getOrCreate()

# Define HDFS base path for storing files
# HDFS_BASE_PATH = os.getenv("HDFS_BASE_PATH", "/tmp/uploads")

router = APIRouter()

class ChartConfig(BaseModel):
    x_axis: str
    y_axis: str
    aggregation: str
    chart_type: str
    title: str

def process_chart_data(data: List[Dict], config: Dict) -> Dict:
    """Process data according to chart configuration, handling large numbers."""
    logger.info(f"Processing chart data with config: {config}")
    df = pd.DataFrame(data)

    # Apply aggregation if specified
    if config['aggregation'] != 'none':
        if config['aggregation'] == 'sum':
            df = df.groupby(config['x_axis'])[config['y_axis']].sum().reset_index()
        elif config['aggregation'] == 'average':
            df = df.groupby(config['x_axis'])[config['y_axis']].mean().reset_index()
        elif config['aggregation'] == 'count':
            df = df.groupby(config['x_axis']).size().reset_index(name=config['y_axis'])

    logger.debug(f"Aggregated data: {df}")

    # Convert categorical values to string (Avoid converting numeric y-axis to string)
    df[config['x_axis']] = df[config['x_axis']].astype(str)

    chart_config = {
        'type': config['chart_type'],
        'data': {
            'labels': df[config['x_axis']].tolist(),
            'datasets': [{
                'label': config['y_axis'],
                'data': df[config['y_axis']].tolist(),
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
                    'text': config['title']
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
                        'text': config['y_axis']
                    }
                },
                'x': {
                    'title': {
                        'display': True,
                        'text': config['x_axis']
                    }
                }
            }
        }
    }

    logger.info(f"Chart configuration generated: {chart_config}")
    return chart_config

def execute_transformation(code: str, df) -> pd.DataFrame:
    """Execute PySpark transformation code."""
    logger.info(f"Executing transformation code:\n{code}")
    try:
        # Create a restricted global environment
        allowed_globals = {
            'spark': spark,
            'F': F,
            'df': df,
            'datetime': datetime
        }

        # Execute the transformation code
        exec(code, allowed_globals)
        transformed_df = allowed_globals.get('transformed_df')

        if transformed_df is None:
            raise ValueError("Transformation did not produce a result")

        logger.info("Transformation successful, resulting DataFrame:")
        transformed_df.show()
        return transformed_df.toPandas()
    except Exception as e:
        logger.error(f"Error executing transformation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing transformation: {str(e)}")

# def store_file_in_hdfs(local_path, file_name):
#     """Store a file in HDFS and return the HDFS path"""
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')
#     hdfs_dir = f"{HDFS_BASE_PATH}/{timestamp}"
#     hdfs_path = f"{hdfs_dir}/{file_name}"
    
#     # Create directory in HDFS
#     try:
#         # Check if directory exists
#         dir_exists = spark._jvm.org.apache.hadoop.fs.FileSystem.get(
#             spark._jsc.hadoopConfiguration()
#         ).exists(spark._jvm.org.apache.hadoop.fs.Path(hdfs_dir))
        
#         if not dir_exists:
#             # Create directory
#             spark._jvm.org.apache.hadoop.fs.FileSystem.get(
#                 spark._jsc.hadoopConfiguration()
#             ).mkdirs(spark._jvm.org.apache.hadoop.fs.Path(hdfs_dir))
            
#         logger.info(f"Created HDFS directory: {hdfs_dir}")
#     except Exception as e:
#         logger.error(f"Error creating HDFS directory: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error creating HDFS directory: {str(e)}")
    
#     # Copy file to HDFS
#     try:
#         spark._jvm.org.apache.hadoop.fs.FileUtil.copy(
#             spark._jvm.java.io.File(local_path),
#             spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration()),
#             spark._jvm.org.apache.hadoop.fs.Path(hdfs_path),
#             True  # Delete source
#         )
#         logger.info(f"Stored file in HDFS at: {hdfs_path}")
#         return hdfs_path
#     except Exception as e:
#         logger.error(f"Error storing file in HDFS: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error storing file in HDFS: {str(e)}")

@router.post("/process")
async def process_data(files: List[UploadFile] = File(...), prompt: str = Form(...)):
    """
    Process multiple files and a prompt, storing files in Hadoop.
    """
    hadoop_paths = []
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        df_list = []
        # Process each uploaded file
        for file in files:
            extension = os.path.splitext(file.filename)[-1].lower()

            # Create a unique Hadoop path
            hadoop_path = f"{os.getenv('HDFS_BASE_PATH', '/tmp/uploads')}/temp_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}_{file.filename}"
            hadoop_paths.append(hadoop_path)
            logger.info(f"Saving file {file.filename} to Hadoop path: {hadoop_path}")

            # Read the file content and save it to Hadoop
            file_content = await file.read()
            rdd = spark.sparkContext.parallelize([file_content])
            rdd.saveAsTextFile(hadoop_path)

            # Load the file from Hadoop into a Spark DataFrame
            if extension == '.csv':
                part_df = spark.read.csv(hadoop_path, header=True, inferSchema=True)
            elif extension in ['.xlsx', '.xls']:
                # Read from hdfs to local, and then read excel using pandas, and then convert to spark dataframe.
                local_path = f"/tmp/{file.filename}"
                spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration()).copyToLocalFile(
                    spark._jvm.org.apache.hadoop.fs.Path(hadoop_path+"/part-00000"),
                    spark._jvm.org.apache.hadoop.fs.Path(local_path)
                )

                pandas_df = pd.read_excel(local_path)
                part_df = spark.createDataFrame(pandas_df)
                os.remove(local_path)

            elif extension == '.json':
                part_df = spark.read.json(hadoop_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
            logger.info(f"Loaded DataFrame from {file.filename} with columns: {part_df.columns}")

            # Clean column names
            for old_col in part_df.columns:
                new_col = re.sub(r'[^\w\s]', '', old_col).strip().lower().replace(' ', '_')
                part_df = part_df.withColumnRenamed(old_col, new_col)
            logger.info(f"Cleaned columns for {file.filename}: {part_df.columns}")
            df_list.append(part_df)

        # Combine all DataFrames using unionByName (allowing missing columns)
        combined_df = df_list[0]
        for part_df in df_list[1:]:
            combined_df = combined_df.unionByName(part_df, allowMissingColumns=True)

        logger.info(f"Combined DataFrame columns: {combined_df.columns}")

        if len(files) > 1:
            prompt = f"(Combined multiple files) {prompt}"

        # Analyze the prompt intent (visualization, statistical, transformation, etc.)
        intent_analysis = await analyze_prompt_intent(prompt)
        logger.info(f"Intent analysis result: {intent_analysis['intent']}")
        columns = combined_df.columns

        # Process according to the intent
        if intent_analysis['intent'] == 'visualization':
            # Generate visualization configuration
            chart_config = await get_chart_config(prompt, columns)
            pandas_df = combined_df.toPandas()
            visualization = process_chart_data(pandas_df.to_dict('records'), chart_config)

            response = {
                "type": "visualization",
                "visualization": visualization,
                "config": chart_config,
                # "hdfs_paths": hdfs_paths  
            }

            logger.info(f"Visualization response prepared")
        elif intent_analysis['intent'] == 'statistical':
            # Generate and execute statistical analysis code
            statistical_code = await get_statistical_code(prompt, columns)

            allowed_globals = {
                'spark': spark,
                'F': F,
                'df': combined_df,
                'np': np,
                'stats': stats,
                'VectorAssembler': VectorAssembler,
                'Correlation': Correlation
            }

            exec(statistical_code, allowed_globals)
            stat_df = allowed_globals.get('stat_df')

            if stat_df is None:
                raise ValueError("Statistical analysis did not produce a result")

            result_df = stat_df.toPandas()
            response = {
                "type": "statistical",
                "data": result_df.to_dict('records'),
                "statistical_type": intent_analysis.get('statistical_type', None),
                # "hdfs_paths": hdfs_paths  
            }
        else:
            # Default to data transformation
            transformation_code = await get_transformation_code(prompt, columns)
            transformed_df = execute_transformation(transformation_code, combined_df)
            
            # Store the transformed data in HDFS
            transformed_hdfs_path = f"/tmp/transformed_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
            transformed_spark_df = spark.createDataFrame(transformed_df)
            transformed_spark_df.write.parquet(transformed_hdfs_path, mode="overwrite")
            logger.info(f"Transformed data stored in HDFS at: {transformed_hdfs_path}")
            
            response = {
                "type": "transformation",
                "data": transformed_df.to_dict('records'),
                "columns": transformed_df.columns.tolist(),
                "rows": len(transformed_df),
                # "hdfs_paths": hdfs_paths,  
                "transformed_hdfs_path": transformed_hdfs_path  # Path to transformed data
            }

        return response

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Remove all Hadoop files
        for hadoop_path in hadoop_paths:
            try:
                fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
                fs.delete(spark._jvm.org.apache.hadoop.fs.Path(hadoop_path), True) #recursive delete
                logger.info(f"Hadoop file removed: {hadoop_path}")
            except Exception as delete_error:
                logger.error(f"Error deleting Hadoop file {hadoop_path}: {delete_error}")

@router.post("/generate-dashboard")
async def generate_dashboard(prompt: str, columns: List[str], data: List[Dict[str, Any]]):
    """Generate dashboard widgets based on natural language prompt."""
    logger.info(f"Generating dashboard with prompt: {prompt}")
    try:
        # Analyze prompt to understand the user's intent
        intent_analysis = await analyze_prompt_intent(prompt)
        
        # Generate widget configurations
        widgets = []
        
        # Process based on intent
        if "chart" in prompt.lower() or "plot" in prompt.lower() or "visualize" in prompt.lower() or intent_analysis['intent'] == 'visualization':
            # Generate visualization widget(s)
            chart_config = await get_chart_config(prompt, columns)
            widgets.append({
                "type": "chart",
                "id": f"chart_{len(widgets)+1}",
                "config": {
                    "title": chart_config["title"],
                    "chartType": chart_config["chart_type"],
                    "xColumn": columns.index(chart_config["x_axis"]) if chart_config["x_axis"] in columns else 0,
                    "yColumns": [columns.index(chart_config["y_axis"])] if chart_config["y_axis"] in columns else [1],
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
        
        if "stat" in prompt.lower() or "statistic" in prompt.lower() or intent_analysis['intent'] == 'statistical':
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
            # Generate insight widget
            text_prompt = f"Provide a brief data insight about the following columns: {', '.join(columns)}"
            insight_text = await generate_with_ollama(text_prompt)
            
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
        dashboard_path = f"dashboards/{safe_name}_{dashboard_id}.json"
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