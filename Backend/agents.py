import os
import re
import json
import logging
import httpx
import pandas as pd
import numpy as np
from typing import Optional, List, Union, Dict, Any, TypedDict
from enum import Enum
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# LangChain imports
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Google Generative AI imports
import google.generativeai as genai

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")

# Pydantic Models for Validation (keeping existing models)
class IntentType(str, Enum):
    VISUALIZATION = "visualization"
    TRANSFORMATION = "transformation" 
    STATISTICAL = "statistical"

class VisualizationType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"

class TransformationType(str, Enum):
    AGGREGATE = "aggregate"
    FILTER = "filter"
    JOIN = "join"
    COMPUTE = "compute"
    GROUP = "group"
    PIVOT = "pivot"

class StatisticalType(str, Enum):
    CORRELATION = "correlation"
    TTEST = "ttest"
    ZTEST = "ztest"
    CHI_SQUARE = "chi_square"
    ANOVA = "anova"
    REGRESSION = "regression"

class AggregationType(str, Enum):
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    NONE = "none"
    MIN = "min"
    MAX = "max"
    STD = "std"

# State for LangGraph
class AgentState(TypedDict):
    messages: List[BaseMessage]
    prompt: str
    columns: List[str]
    data_sample: str
    intent: Optional[str]
    intent_details: Optional[Dict[str, Any]]
    chart_config: Optional[Dict[str, Any]]
    generated_code: Optional[str]
    result: Optional[Any]
    error: Optional[str]

# Custom Gemini LLM for LangChain
class GeminiLLM(LLM):
    temperature: float = 0.5
    
    @property
    def _llm_type(self) -> str:
        return "gemini"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Gemini API synchronously."""
        import asyncio
        return asyncio.run(self._acall(prompt, stop, run_manager, **kwargs))
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Gemini API asynchronously."""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        
        try:
            # Configure the model
            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    top_p=0.95,
                    max_output_tokens=8192,
                )
            )
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Extract the text from the response
            if response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini API")
                return ""
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise

class DataAnalysisAgents:
    """Main class containing all data analysis agents using LangChain and LangGraph."""
    
    def __init__(self, temperature: float = 0.05):
        self.llm = GeminiLLM(temperature=temperature)
        self.setup_tools()
        self.setup_agents()
        self.setup_graph()
    
    def get_data_context(self, df: pd.DataFrame, num_rows: int = 5) -> str:
        """Generate data context from the first few rows of the DataFrame."""
        try:
            # Get basic info about the dataset
            data_info = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict(),
                "sample_data": df.head(num_rows).to_dict('records'),
                "null_counts": df.isnull().sum().to_dict(),
                "memory_usage": df.memory_usage(deep=True).to_dict()
            }
            
            # Analyze data types for better chart recommendations
            numeric_columns = []
            categorical_columns = []
            datetime_columns = []
            
            for col, dtype in data_info['dtypes'].items():
                if pd.api.types.is_numeric_dtype(dtype):
                    numeric_columns.append(col)
                elif pd.api.types.is_datetime64_any_dtype(dtype):
                    datetime_columns.append(col)
                else:
                    categorical_columns.append(col)
            
            # Convert to readable string format
            context = f"""
Dataset Overview:
- Shape: {data_info['shape'][0]} rows × {data_info['shape'][1]} columns
- Columns: {', '.join(data_info['columns'])}

Data Types:
{chr(10).join([f'- {col}: {dtype}' for col, dtype in data_info['dtypes'].items()])}

Column Analysis:
- Numeric columns: {', '.join(numeric_columns) if numeric_columns else 'None'}
- Categorical columns: {', '.join(categorical_columns) if categorical_columns else 'None'}
- Datetime columns: {', '.join(datetime_columns) if datetime_columns else 'None'}

Sample Data (first {num_rows} rows):
{pd.DataFrame(data_info['sample_data']).to_string(index=False)}

Missing Values:
{chr(10).join([f'- {col}: {count} missing' for col, count in data_info['null_counts'].items() if count > 0])}
"""
            return context.strip()
            
        except Exception as e:
            logger.error(f"Error generating data context: {str(e)}")
            return f"Error generating data context: {str(e)}"
    
    def setup_tools(self):
        """Setup tools for the agents."""
        self.tools = []
    
    def setup_agents(self):
        """Setup individual agents using LangChain."""
        
        # Intent Analysis Agent
        self.intent_agent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data analyst specializing in understanding user intentions for data analysis tasks.

Your job is to analyze user prompts and classify them into one of three categories:
1. VISUALIZATION: User wants to create charts, graphs, or visual representations
2. TRANSFORMATION: User wants to modify, filter, aggregate, or transform data
3. STATISTICAL: User wants to perform statistical analysis, tests, or calculations

Consider the data context provided to make informed decisions.

Keywords for classification:
- Visualization: plot, chart, graph, visualize, show, display, bar, line, pie, scatter
- Transformation: group, aggregate, filter, join, merge, pivot, transform, calculate, compute
- Statistical: correlation, test, significance, hypothesis, regression, anova, chi-square, p-value

Always respond with valid JSON containing:
- intent: one of "visualization", "transformation", or "statistical"
- reason: brief explanation of your classification
- specific_type: specific subtype based on the intent
- confidence: confidence score from 0.0 to 1.0"""),
            ("human", """Data Context:
{data_context}

User Prompt: {prompt}

Analyze this prompt and provide your classification as JSON.""")
        ])
        
        # Chart Configuration Agent
        self.chart_config_agent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a data visualization expert. Your job is to create optimal chart configurations based on user requests and data characteristics.

Your output must be compatible with the process_chart_data function in services.py, which expects these specific keys:
- chart_type: one of "bar", "line", "pie", "scatter", "area"
- x_axis: column name for x-axis (must exist in available columns)
- y_axis: column name for y-axis (must exist in available columns)
- aggregation: one of "none", "sum", "average", "count", "min", "max", "std"
- chart_title: descriptive title for the chart

Guidelines for chart type selection:
- Categorical data: use "bar" or "pie" charts
- Time series: use "line" or "area" charts
- Relationships between numeric variables: use "scatter" charts
- Multiple categories: use "bar" charts with aggregation
- Distribution analysis: use "bar" charts with count aggregation

Guidelines for axis selection:
- x_axis: typically categorical or time-based columns (look for categorical or datetime columns)
- y_axis: typically numeric columns for measurements/values (look for numeric columns)
- For pie charts, use the main category as x_axis and values as y_axis
- For scatter plots, both x_axis and y_axis should be numeric columns
- For line charts, x_axis is often time-based and y_axis is numeric

Guidelines for aggregation:
- "none": use raw data
- "sum": for total values
- "average": for mean values
- "count": for frequency analysis
- "min"/"max": for range analysis
- "std": for variability analysis

IMPORTANT: Always ensure the column names you specify exist in the available columns list.

Always respond with valid JSON containing exactly these keys: chart_type, x_axis, y_axis, aggregation, chart_title"""),
            ("human", """Data Context:
{data_context}

User Prompt: {prompt}

Available Columns: {columns}

Generate an optimal chart configuration as JSON that matches the user's request and data characteristics.

Example outputs:
For "show me a bar chart of sales by region":
{{"chart_type": "bar", "x_axis": "region", "y_axis": "sales", "aggregation": "sum", "chart_title": "Sales by Region"}}

For "plot revenue over time":
{{"chart_type": "line", "x_axis": "date", "y_axis": "revenue", "aggregation": "none", "chart_title": "Revenue Over Time"}}

For "create a pie chart of product distribution":
{{"chart_type": "pie", "x_axis": "product", "y_axis": "quantity", "aggregation": "sum", "chart_title": "Product Distribution"}}""")
        ])
        
        # Code Generation Agent
        self.code_generation_agent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Python programmer specializing in pandas, numpy, and data analysis.

Generate clean, efficient, and safe Python code based on user requirements. 

For TRANSFORMATION tasks:
- Use pandas operations efficiently
- Handle missing values appropriately
- Store result in 'transformed_df'
- Use proper column selection with lists, not tuples
- Include error handling

For STATISTICAL tasks:
- Use pandas, numpy, and scipy.stats
- Handle missing values with dropna()
- Store result in 'stat_result'
- Include proper statistical tests and interpretations

For VISUALIZATION tasks:
- Generate code that prepares data for visualization
- Store configuration in 'chart_config'

IMPORTANT RULES:
- Always use lists for column selection: df[['col1', 'col2']]
- you have access to data in the variable 'df'
- Store result in 'transformed_df'
- Handle edge cases and missing data
- No function definitions, work directly with variables

Generate only the code, no explanations."""),
            ("human", """Data Context:
{data_context}

User Prompt: {prompt}
Available Columns: {columns}

Generate the appropriate Python code.""")
        ])
    
    def setup_graph(self):
        """Setup LangGraph workflow."""
        
        # Define the workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_intent", self.analyze_intent_node)
        workflow.add_node("generate_chart_config", self.generate_chart_config_node)
        workflow.add_node("generate_code", self.generate_code_node)
        workflow.add_node("execute_code", self.execute_code_node)
        
        # Define edges
        workflow.set_entry_point("analyze_intent")
        
        workflow.add_conditional_edges(
            "analyze_intent",
            self.route_after_intent,
            {
                "visualization": "generate_chart_config",
                "transformation": "generate_code",
                "statistical": "generate_code"
            }
        )
        
        workflow.add_edge("generate_chart_config", "generate_code")
        workflow.add_edge("generate_code", "execute_code")
        workflow.add_edge("execute_code", END)
        
        # Compile the graph
        self.app = workflow.compile(checkpointer=MemorySaver())
    
    async def analyze_intent_node(self, state: AgentState) -> AgentState:
        """Node to analyze user intent."""
        try:
            prompt = self.intent_agent_prompt.format(
                data_context=state["data_sample"],
                prompt=state["prompt"]
            )
            
            response = await self.llm._acall(prompt)
            intent_data = self.extract_json_from_response(response)
            
            state["intent"] = intent_data.get("intent")
            state["intent_details"] = intent_data
            
            logger.info(f"Intent analyzed: {intent_data}")
            
        except Exception as e:
            logger.error(f"Error in analyze_intent_node: {str(e)}")
            state["error"] = str(e)
        
        return state
    
    async def generate_chart_config_node(self, state: AgentState) -> AgentState:
        """Node to generate chart configuration."""
        try:
            prompt = self.chart_config_agent_prompt.format(
                data_context=state["data_sample"],
                prompt=state["prompt"],
                columns=", ".join(state["columns"])
            )
            
            response = await self.llm._acall(prompt)
            chart_config = self.extract_json_from_response(response)
            
            # Validate and sanitize the chart configuration
            validated_config = self.validate_chart_config(chart_config, state["columns"])
            state["chart_config"] = validated_config
            
            logger.info(f"Chart config generated: {validated_config}")
            
        except Exception as e:
            logger.error(f"Error in generate_chart_config_node: {str(e)}")
            state["error"] = str(e)
        
        return state
    
    async def generate_code_node(self, state: AgentState) -> AgentState:
        """Node to generate Python code."""
        try:
            prompt = self.code_generation_agent_prompt.format(
                data_context=state["data_sample"],
                intent=state["intent"],
                prompt=state["prompt"],
                columns=", ".join(state["columns"])
            )
            
            response = await self.llm._acall(prompt)
            
            # Extract code from response
            code_match = re.search(r"```python\n(.*?)\n```", response, re.DOTALL)
            code = code_match.group(1) if code_match else response
            code = code.strip()
            
            # Ensure proper result variable based on intent
            if state["intent"] == "transformation":
                if "transformed_df" not in code:
                    code += "\n#transformed_df exists\ntransformed_df = df.copy()"

            elif state["intent"] == "statistical":
                if "stat_result" not in code:
                    code += "\n# stat_result exists\nstat_result = df.describe()"
            
            state["generated_code"] = code
            
            logger.info(f"Code generated for {state['intent']}: {code[:200]}...")
            
        except Exception as e:
            logger.error(f"Error in generate_code_node: {str(e)}")
            state["error"] = str(e)
        
        return state
    
    async def execute_code_node(self, state: AgentState) -> AgentState:
        """Node to safely execute generated code."""
        try:
            if not state.get("generated_code"):
                state["error"] = "No code to execute"
                return state
            
            # Create a safe execution environment
            import pandas as pd
            import numpy as np
            from scipy import stats
            
            # Get the DataFrame from state
            df = self.current_df
            if df is None:
                state["error"] = "No DataFrame available for execution"
                return state
            
            # Execute the generated code in a safe environment
            local_vars = {
                'pd': pd,
                'np': np,
                'stats': stats,
                'df': df.copy()  # Use a copy to avoid modifying original
            }
            
            # Execute the code
            exec(state["generated_code"], {}, local_vars)
            
            # Extract the result based on intent
            if state["intent"] == "transformation":
                if "transformed_df" in local_vars:
                    transformed_df = local_vars["transformed_df"]
                    # Ensure it's a DataFrame
                    if isinstance(transformed_df, pd.DataFrame):
                        # Convert DataFrame to dict for serialization
                        state["result"] = transformed_df.to_dict('records')
                    else:
                        # If it's not a DataFrame, try to convert it
                        try:
                            df_result = pd.DataFrame(transformed_df)
                            state["result"] = df_result.to_dict('records')
                        except:
                            state["error"] = "Transformation result is not a valid DataFrame"
                else:
                    # Fallback: create a simple transformation
                    logger.warning("Transformation code did not create 'transformed_df', using fallback")
                    try:
                        # Create a simple transformation as fallback
                        fallback_code = "transformed_df = df.copy()"
                        exec(fallback_code, {}, local_vars)
                        fallback_df = local_vars["transformed_df"]
                        state["result"] = fallback_df.to_dict('records')
                    except Exception as fallback_error:
                        state["error"] = f"Transformation failed and fallback also failed: {str(fallback_error)}"
                        
            elif state["intent"] == "statistical":
                if "stat_result" in local_vars:
                    stat_result = local_vars["stat_result"]
                    # Handle different types of statistical results
                    if isinstance(stat_result, pd.DataFrame):
                        state["result"] = stat_result.to_dict('records')
                    elif isinstance(stat_result, dict):
                        state["result"] = stat_result
                    else:
                        state["result"] = str(stat_result)
                else:
                    # Fallback: create basic statistics
                    logger.warning("Statistical code did not create 'stat_result', using fallback")
                    try:
                        fallback_code = "stat_result = df.describe()"
                        exec(fallback_code, {}, local_vars)
                        fallback_result = local_vars["stat_result"]
                        if isinstance(fallback_result, pd.DataFrame):
                            state["result"] = fallback_result.to_dict('records')
                        else:
                            state["result"] = str(fallback_result)
                    except Exception as fallback_error:
                        state["error"] = f"Statistical analysis failed and fallback also failed: {str(fallback_error)}"
            else:
                # For visualization, store the chart config
                state["result"] = {
                    "intent": state["intent"],
                    "chart_config": state.get("chart_config")
                }
            
            logger.info(f"Code execution completed for {state['intent']}")
            
        except Exception as e:
            logger.error(f"Error in execute_code_node: {str(e)}")
            state["error"] = f"Code execution failed: {str(e)}"
        
        return state
    
    def route_after_intent(self, state: AgentState) -> str:
        """Route to appropriate node based on intent."""
        intent = state.get("intent", "transformation")
        return intent
    
    def validate_chart_config(self, chart_config: Dict[str, Any], available_columns: List[str]) -> Dict[str, Any]:
        """Validate and sanitize chart configuration to ensure compatibility with process_chart_data."""
        try:
            # Ensure all required keys exist
            required_keys = ['chart_type', 'x_axis', 'y_axis', 'aggregation', 'chart_title']
            validated_config = {}
            
            # Set defaults and validate chart_type
            validated_config['chart_type'] = chart_config.get('chart_type', 'bar')
            if validated_config['chart_type'] not in ['bar', 'line', 'pie', 'scatter', 'area']:
                validated_config['chart_type'] = 'bar'
            
            # Validate and set x_axis
            x_axis = chart_config.get('x_axis', '')
            if x_axis in available_columns:
                validated_config['x_axis'] = x_axis
            else:
                # Fallback to first available column
                validated_config['x_axis'] = available_columns[0] if available_columns else 'x'
            
            # Validate and set y_axis
            y_axis = chart_config.get('y_axis', '')
            if y_axis in available_columns:
                validated_config['y_axis'] = y_axis
            else:
                # Fallback to second column if available, otherwise first
                if len(available_columns) > 1:
                    validated_config['y_axis'] = available_columns[1]
                else:
                    validated_config['y_axis'] = available_columns[0] if available_columns else 'y'
            
            # Validate aggregation
            aggregation = chart_config.get('aggregation', 'none')
            valid_aggregations = ['none', 'sum', 'average', 'count', 'min', 'max', 'std']
            validated_config['aggregation'] = aggregation if aggregation in valid_aggregations else 'none'
            
            # Set chart title
            validated_config['chart_title'] = chart_config.get('chart_title', 'Chart')
            
            # Special handling for pie charts - ensure we have appropriate data
            if validated_config['chart_type'] == 'pie':
                # For pie charts, aggregation is often needed to avoid too many slices
                if validated_config['aggregation'] == 'none':
                    validated_config['aggregation'] = 'sum'
            
            # Special handling for scatter plots - ensure both axes are numeric
            if validated_config['chart_type'] == 'scatter':
                # For scatter plots, aggregation should typically be 'none'
                validated_config['aggregation'] = 'none'
            
            logger.info(f"Validated chart config: {validated_config}")
            return validated_config
            
        except Exception as e:
            logger.error(f"Error validating chart config: {str(e)}")
            # Return a safe default configuration
            return {
                'chart_type': 'bar',
                'x_axis': available_columns[0] if available_columns else 'x',
                'y_axis': available_columns[1] if len(available_columns) > 1 else available_columns[0] if available_columns else 'y',
                'aggregation': 'none',
                'chart_title': 'Chart'
            }
    
    def extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response."""
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\n(.*?)\n```", response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        # Clean any potential leading/trailing whitespace
        response_text = response_text.strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract just the JSON object
            json_obj_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
            if json_obj_match:
                return json.loads(json_obj_match.group(1))
            raise ValueError(f"Could not parse JSON from response: {response_text}")
    
    async def process_request(self, prompt: str, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Process a data analysis request through the agent workflow."""
        
        # Generate data context
        data_sample = self.get_data_context(df)
        
        # Store DataFrame in the agent instance for use in execution
        self.current_df = df
        
        # Initial state
        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "prompt": prompt,
            "columns": columns,
            "data_sample": data_sample,
            "intent": None,
            "intent_details": None,
            "chart_config": None,
            "generated_code": None,
            "result": None,
            "error": None
        }
        
        # Run the workflow
        config = {"configurable": {"thread_id": "test"}}
        final_state = await self.app.ainvoke(initial_state, config=config)
        
        return {
            "intent": final_state.get("intent"),
            "intent_details": final_state.get("intent_details"),
            "chart_config": final_state.get("chart_config"),
            "generated_code": final_state.get("generated_code"),
            "result": final_state.get("result"),
            "error": final_state.get("error"),
            "data_context": data_sample
        }

# Main API functions using the new agent system
class GenerationRequest(BaseModel):
    prompt: str
    columns: List[str]
    temperature: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()
    
    @validator('columns')
    def validate_columns(cls, v):
        if not v:
            raise ValueError('At least one column must be provided')
        return [col.strip() for col in v if col.strip()]

# Global agent instance
data_agents = None

def get_data_agents(temperature: float = 0.5) -> DataAnalysisAgents:
    """Get or create the data analysis agents instance."""
    global data_agents
    if data_agents is None:
        data_agents = DataAnalysisAgents(temperature=temperature)
    return data_agents

async def analyze_with_agents(request: GenerationRequest, df: pd.DataFrame) -> Dict[str, Any]:
    """Main function to analyze data using the agent workflow."""
    try:
        agents = get_data_agents(request.temperature)
        result = await agents.process_request(request.prompt, df, request.columns)
        return result
        
    except Exception as e:
        logger.error(f"Error in agent analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in agent analysis: {str(e)}")

# Test function
async def test_agent_workflow():
    """Test function for the agent workflow."""
    # Create sample data
    sample_data = pd.DataFrame({
        "item": ["Apple", "Banana", "Orange", "Apple", "Banana"],
        "quantity": [10, 20, 15, 25, 30],
        "unit_price_inr": [100, 50, 80, 100, 50],
        "total_price_inr": [1000, 1000, 1200, 2500, 1500],
        "revenue": [900, 950, 1100, 2300, 1400]
    })
    
    test_request = GenerationRequest(
        prompt="plot a bar chart for the revenue per item",
        columns=list(sample_data.columns)
    )
    
    try:
        result = await analyze_with_agents(test_request, sample_data)
        print("Agent workflow result:", json.dumps(result, indent=2, default=str))
        
        # Test the chart configuration integration
        if result.get("intent") == "visualization" and result.get("chart_config"):
            print("\nTesting chart configuration integration...")
            from api.services import process_chart_data
            
            chart_result = process_chart_data(sample_data.to_dict('records'), result["chart_config"])
            print("Chart processing result:", json.dumps(chart_result, indent=2, default=str))
        
    except Exception as e:
        print(f"Test failed: {str(e)}")

async def test_chart_config_integration():
    """Test the chart configuration integration specifically."""
    # Create sample data
    sample_data = pd.DataFrame({
        "region": ["North", "South", "East", "West", "North", "South"],
        "sales": [1000, 1500, 800, 1200, 1100, 1600],
        "profit": [200, 300, 150, 250, 220, 320]
    })
    
    test_cases = [
        "show me a bar chart of sales by region",
        "create a pie chart of total sales by region", 
        "plot profit over time",
        "show revenue distribution"
    ]
    
    for prompt in test_cases:
        print(f"\nTesting prompt: {prompt}")
        test_request = GenerationRequest(
            prompt=prompt,
            columns=list(sample_data.columns)
        )
        
        try:
            result = await analyze_with_agents(test_request, sample_data)
            if result.get("chart_config"):
                print(f"Generated chart config: {result['chart_config']}")
                
                # Test integration with process_chart_data
                from api.services import process_chart_data
                chart_result = process_chart_data(sample_data.to_dict('records'), result["chart_config"])
                print(f"Chart type: {chart_result['type']}")
                print(f"Number of data points: {len(chart_result['data']['labels'])}")
            else:
                print("No chart config generated")
                
        except Exception as e:
            print(f"Error: {str(e)}")

# Run the test
if __name__ == "__main__":
    import asyncio
    print("Running basic agent workflow test...")
    asyncio.run(test_agent_workflow())
    
    print("\n" + "="*50)
    print("Running chart configuration integration test...")
    asyncio.run(test_chart_config_integration())