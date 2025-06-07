import gradio as gr
import pandas as pd
import json
from agents import analyze_data_with_agent
import io
import base64
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_data_and_prompt(file, prompt):
    """Process uploaded file and prompt using the data analysis agent."""
    try:
        if not file:
            return "Please upload a data file.", None, None
            
        if not prompt or prompt.strip() == "":
            return "Please enter an analysis prompt.", None, None

        # Read the uploaded file
        if file.name.endswith('.csv'):
            df = pd.read_csv(file.name)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file.name)
        elif file.name.endswith('.json'):
            df = pd.read_json(file.name)
        else:
            return "Error: Unsupported file format. Please upload CSV, Excel, or JSON files.", None, None

        # Clean column names
        df.columns = [str(col).strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # Show data preview
        data_preview = f"""
        <div style="margin-bottom: 20px;">
            <h3>Data Preview</h3>
            <p><strong>Shape:</strong> {df.shape[0]} rows × {df.shape[1]} columns</p>
            <p><strong>Columns:</strong> {', '.join(df.columns.tolist())}</p>
            {df.head().to_html(classes='table table-striped', table_id='data-preview')}
        </div>
        """

        # Process with agent
        logger.info(f"Processing prompt: {prompt}")
        result = await analyze_data_with_agent(prompt, df)
        logger.info(f"Agent result type: {result.get('type')}")

        # Handle different result types
        if result["type"] == "error":
            error_html = f"""
            <div style="background-color: #fee; border: 1px solid #fcc; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <h3 style="color: #c00;">Error</h3>
                <p><strong>Message:</strong> {result['message']}</p>
                {f"<p><strong>Suggestions:</strong></p><ul>{''.join([f'<li>{s}</li>' for s in result.get('suggestions', [])])}</ul>" if result.get('suggestions') else ""}
            </div>
            """
            return data_preview + error_html, None, None
        
        elif result["type"] == "visualization":
            # Display the chart
            image_base64 = result.get("image")
            if image_base64:
                chart_html = f"""
                <div style="margin-top: 20px;">
                    <h3>Visualization Result</h3>
                    <p><strong>Chart Type:</strong> {result.get('chart_type', 'Unknown').title()}</p>
                    <div style="text-align: center; margin: 20px 0;">
                        <img src="data:image/png;base64,{image_base64}" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px;">
                    </div>
                    <p><em>{result.get('message', 'Visualization created successfully')}</em></p>
                </div>
                """
                return data_preview + chart_html, None, None
            else:
                return data_preview + "<p>Error: Could not generate visualization</p>", None, None
        
        elif result["type"] == "statistical":
            # Format statistical results
            stat_html = f"""
            <div style="margin-top: 20px;">
                <h3>Statistical Analysis Results</h3>
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    {result.get('data', 'No statistical results available')}
                </div>
                <p><em>{result.get('message', 'Statistical analysis completed')}</em></p>
            </div>
            """
            return data_preview + stat_html, None, None
        
        elif result["type"] == "transformation":
            # Return transformed data
            transformed_df = result.get("dataframe")
            if transformed_df is not None:
                # Create CSV for download
                csv_buffer = io.StringIO()
                transformed_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                # Create temporary file for download
                temp_file = "transformed_data.csv"
                with open(temp_file, 'w') as f:
                    f.write(csv_data)
                
                transform_html = f"""
                <div style="margin-top: 20px;">
                    <h3>Data Transformation Results</h3>
                    <p><strong>Original Shape:</strong> {df.shape[0]} rows × {df.shape[1]} columns</p>
                    <p><strong>New Shape:</strong> {result.get('shape', 'Unknown')}</p>
                    <p><strong>New Columns:</strong> {', '.join(result.get('columns', []))}</p>
                    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 10px 0;">
                        <h4>Preview of Transformed Data:</h4>
                        {result.get('preview', 'No preview available')}
                    </div>
                    <p><em>{result.get('message', 'Data transformation completed')}</em></p>
                    <p><strong>Download the transformed data using the button below.</strong></p>
                </div>
                """
                return data_preview + transform_html, temp_file, None
            else:
                return data_preview + "<p>Error: Could not retrieve transformed data</p>", None, None
        
        else:
            return data_preview + f"<p>Unknown result type: {result.get('type')}</p>", None, None

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        error_html = f"""
        <div style="background-color: #fee; border: 1px solid #fcc; padding: 15px; border-radius: 5px;">
            <h3 style="color: #c00;">Processing Error</h3>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><strong>Please check:</strong></p>
            <ul>
                <li>File format is supported (CSV, Excel, JSON)</li>
                <li>File is not corrupted</li>
                <li>Prompt is clear and specific</li>
                <li>Ollama server is running</li>
            </ul>
        </div>
        """
        return error_html, None, None

def process_sync(file, prompt):
    """Synchronous wrapper for the async processing function."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(process_data_and_prompt(file, prompt))
    except Exception as e:
        logger.error(f"Error in sync wrapper: {str(e)}")
        return f"Error: {str(e)}", None, None
    finally:
        loop.close()

def generate_preview(file):
    """Generate a preview of the uploaded file."""
    try:
        if not file:
            return "Please upload a data file."
            
        # Read the uploaded file
        if file.name.endswith('.csv'):
            df = pd.read_csv(file.name)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file.name)
        elif file.name.endswith('.json'):
            df = pd.read_json(file.name)
        else:
            return "Error: Unsupported file format. Please upload CSV, Excel, or JSON files."

        # Clean column names
        df.columns = [str(col).strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # Show data preview
        data_preview = f"""
        <div style="margin-bottom: 20px;">
            <h3>Data Preview</h3>
            <p><strong>Shape:</strong> {df.shape[0]} rows × {df.shape[1]} columns</p>
            <p><strong>Columns:</strong> {', '.join(df.columns.tolist())}</p>
            {df.head().to_html(classes='table table-striped', table_id='data-preview')}
        </div>
        """
        return data_preview
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return f"Error generating preview: {str(e)}"

# Sample prompts for different analysis types
sample_prompts = {
    "Visualization": [
        "Create a bar chart showing the distribution of categories",
        "Generate a line plot of sales over time",
        "Make a scatter plot of price vs quantity",
        "Show a histogram of customer ages",
        "Create a pie chart of market share by region"
    ],
    "Statistical Analysis": [
        "Calculate correlation matrix for all numeric columns",
        "Perform descriptive statistics analysis",
        "Compare means between different groups",
        "Find outliers in the dataset",
        "Calculate summary statistics by category"
    ],
    "Data Transformation": [
        "Filter data where sales > 1000 and add a profit column",
        "Group by category and calculate average values",
        "Remove duplicates and sort by date",
        "Create new columns based on existing ones",
        "Aggregate data by month and calculate totals"
    ]
}

# Create the Gradio interface
with gr.Blocks(
    title="Data Analysis Agent",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1200px;
        margin: auto;
    }
    .table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    .table th, .table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .table-striped tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    """
) as demo:
    
    gr.Markdown("""
    # 🤖 Data Analysis Agent
    
    Upload your data file and describe what analysis you want to perform. The AI agent will:
    - 📊 Create visualizations (charts, plots, graphs)
    - 🔢 Perform statistical analysis (correlations, tests, summaries)
    - 🔧 Transform your data (filter, aggregate, compute new columns)
    
    **Supported formats:** CSV, Excel (.xlsx, .xls), JSON
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📁 Upload Data")
            file_input = gr.File(
                label="Choose your data file",
                file_types=[".csv", ".xlsx", ".xls", ".json"],
                type="filepath"
            )
            
            gr.Markdown("### 📋 Data Preview")
            preview_output = gr.HTML(label="File Preview")
            
            gr.Markdown("### 💬 Analysis Request")
            prompt_input = gr.Textbox(
                label="Describe what you want to analyze",
                placeholder="e.g., 'Create a bar chart showing sales by category' or 'Calculate correlation between price and quantity'",
                lines=3
            )
            
            # Sample prompts
            gr.Markdown("### 💡 Example Prompts")
            
            with gr.Accordion("Visualization Examples", open=False):
                for prompt in sample_prompts["Visualization"]:
                    gr.Button(prompt, size="sm").click(
                        lambda p=prompt: p, outputs=prompt_input
                    )
            
            with gr.Accordion("Statistical Analysis Examples", open=False):
                for prompt in sample_prompts["Statistical Analysis"]:
                    gr.Button(prompt, size="sm").click(
                        lambda p=prompt: p, outputs=prompt_input
                    )
            
            with gr.Accordion("Data Transformation Examples", open=False):
                for prompt in sample_prompts["Data Transformation"]:
                    gr.Button(prompt, size="sm").click(
                        lambda p=prompt: p, outputs=prompt_input
                    )
            
            submit_btn = gr.Button("🚀 Analyze Data", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            gr.Markdown("### 📋 Results")
            output = gr.HTML(label="Analysis Results")
            
            gr.Markdown("### 📥 Downloads")
            download_output = gr.File(label="Download Transformed Data", visible=True)
            
            gr.Markdown("### ℹ️ Status")
            status_output = gr.Textbox(label="Status", visible=False)
    
    # Event handlers
    file_input.change(
        fn=generate_preview,
        inputs=[file_input],
        outputs=[preview_output]
    )
    
    submit_btn.click(
        fn=process_sync,
        inputs=[file_input, prompt_input],
        outputs=[output, download_output, status_output],
        show_progress=True
    )
    
    # Example section
    with gr.Row():
        gr.Markdown("""
        ### 🎯 How to Use
        
        1. **Upload** your data file (CSV, Excel, or JSON)
        2. **Describe** what analysis you want in plain English
        3. **Click** "Analyze Data" to get results
        
        ### 📊 What You Can Do
        
        **Visualizations:**
        - Bar charts, line plots, scatter plots
        - Histograms, box plots, pie charts
        - Automatic chart type selection based on your data
        
        **Statistical Analysis:**
        - Descriptive statistics and summaries
        - Correlation analysis
        - Hypothesis testing
        - Data quality checks
        
        **Data Transformation:**
        - Filter and sort data
        - Create new calculated columns
        - Group and aggregate data
        - Clean and prepare data
        
        ### ⚙️ Requirements
        - Ollama server running locally
        - Model configured in environment variables
        """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )