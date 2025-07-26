import os
import re
import json
import logging
import httpx
from typing import Optional, List, Union, Dict, Any
from enum import Enum
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# Pydantic Models for Validation
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

class PromptIntentResponse(BaseModel):
    intent: IntentType
    reason: str
    visualization_type: Optional[VisualizationType] = None
    transformation_type: Optional[TransformationType] = None
    statistical_type: Optional[StatisticalType] = None
    
    @validator('visualization_type')
    def validate_visualization_type(cls, v, values):
        if values.get('intent') == IntentType.VISUALIZATION and v is None:
            raise ValueError('visualization_type is required when intent is visualization')
        return v
    
    @validator('transformation_type')
    def validate_transformation_type(cls, v, values):
        if values.get('intent') == IntentType.TRANSFORMATION and v is None:
            raise ValueError('transformation_type is required when intent is transformation')
        return v
    
    @validator('statistical_type')
    def validate_statistical_type(cls, v, values):
        if values.get('intent') == IntentType.STATISTICAL and v is None:
            raise ValueError('statistical_type is required when intent is statistical')
        return v

class ChartConfig(BaseModel):
    chart_type: VisualizationType
    x_axis: str
    y_axis: str
    aggregation: AggregationType
    title: str
    
    @validator('x_axis', 'y_axis')
    def validate_axis_columns(cls, v):
        if not v or not v.strip():
            raise ValueError('Axis column names cannot be empty')
        return v.strip()

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

async def generate_with_ollama(prompt: str, temperature: float = 0.5) -> str:
    """Generate response using Ollama with the specified model."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.95,
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    except httpx.TimeoutException:
        logger.error("Timeout when connecting to Ollama")
        raise HTTPException(status_code=504, detail="Timeout when connecting to Ollama service")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from Ollama: {e.response.status_code}")
        raise HTTPException(status_code=502, detail=f"Ollama service error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Error generating response with Ollama: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response with Ollama: {str(e)}")

def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """Extract and parse JSON from Ollama response."""
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

async def analyze_prompt_intent(request: GenerationRequest) -> PromptIntentResponse:
    """Determine whether the prompt is requesting data transformation, visualization, or statistical analysis."""
    response_format = {
        "intent": "statistical",
        "reason": "Prompt requests statistical analysis",
        "visualization_type": None,
        "transformation_type": None,
        "statistical_type": "correlation"
    }

    input_text = f"""Analyze the following prompt and determine if it's requesting data transformation, visualization, or statistical analysis:

Prompt: {request.prompt}
Available columns: {', '.join(request.columns)}

Provide a JSON response with:
1. intent: Either 'visualization', 'transformation', or 'statistical'
2. reason: Brief explanation of why this classification was chosen
3. visualization_type: If intent is 'visualization', specify the chart type ('bar', 'line', 'pie', 'scatter', 'area')
4. transformation_type: If intent is 'transformation', specify the operation type ('aggregate', 'filter', 'join', 'compute', 'group', 'pivot')
5. statistical_type: If intent is 'statistical', specify the test type ('correlation', 'ttest', 'ztest', 'chi_square', 'anova', 'regression')

Keywords for classification:
- Visualization: plot, chart, graph, visualize, show, display, bar, line, pie, scatter
- Transformation: group, aggregate, filter, join, merge, pivot, transform, calculate, compute
- Statistical: correlation, test, significance, hypothesis, regression, anova, chi-square, p-value

Example response format:
{json.dumps(response_format)}

Provide only the JSON response, no explanations."""

    try:
        response_text = await generate_with_ollama(input_text, temperature=request.temperature)
        json_data = extract_json_from_response(response_text)
        
        # Validate and return structured response
        return PromptIntentResponse(**json_data)
        
    except Exception as e:
        logger.error(f"Error analyzing prompt intent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing prompt intent: {str(e)}")

async def get_chart_config(request: GenerationRequest) -> ChartConfig:
    """Generate chart configuration based on natural language prompt."""
    response_format = {
        "chart_type": "bar",
        "x_axis": "date",
        "y_axis": "sales", 
        "aggregation": "sum",
        "title": "Total Sales by Date"
    }
    
    input_text = f"""Based on the following prompt, determine the appropriate chart configuration:

Prompt: {request.prompt}
Available columns: {', '.join(request.columns)}

Generate a JSON configuration with:
1. chart_type: 'bar', 'line', 'pie', 'scatter', or 'area'
2. x_axis: column name for x-axis (must be from available columns)
3. y_axis: column name for y-axis (must be from available columns)
4. aggregation: 'sum', 'average', 'count', 'min', 'max', 'std', or 'none'
5. title: descriptive chart title

Guidelines:
- For categorical data: use 'bar' or 'pie' charts
- For time series: use 'line' or 'area' charts
- For relationships: use 'scatter' charts
- Choose appropriate aggregation based on data type
- Ensure column names exist in the available columns list

Example response format:
{json.dumps(response_format)}

Provide only the JSON configuration, no explanations."""

    try:
        response_text = await generate_with_ollama(input_text, temperature=request.temperature)
        json_data = extract_json_from_response(response_text)
        
        # Validate column names exist in available columns
        config = ChartConfig(**json_data)
        if config.x_axis not in request.columns:
            raise ValueError(f"X-axis column '{config.x_axis}' not found in available columns")
        if config.y_axis not in request.columns:
            raise ValueError(f"Y-axis column '{config.y_axis}' not found in available columns")
            
        return config
        
    except Exception as e:
        logger.error(f"Error generating chart configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating chart configuration: {str(e)}")

async def get_transformation_code(request: GenerationRequest) -> str:
    """Generate pandas transformation code based on prompt."""
    input_text = f"""Write Python code to perform the following pandas DataFrame transformation:

Prompt: {request.prompt}
Available columns: {', '.join(request.columns)}

# Pandas Knowledge Base:
# 1. DataFrame Operations:
#    - df[['col1', 'col2']]: Select columns (USE LIST, NOT TUPLE!)
#    - df.query() or df[df.column > value]: Filter rows
#    - df.groupby('col').agg({{'col2': 'sum', 'col3': 'mean'}}): Group and aggregate
#    - df.sort_values('col'): Sort data
#    - df.rename(columns={{'old': 'new'}}): Rename columns
#    - df.assign(new_col=lambda x: x.col1 + x.col2): Add/modify columns
#    - df.drop(columns=['col']): Remove columns
#    - df.drop_duplicates(): Remove duplicates
#    - pd.concat([df1, df2]): Combine DataFrames
#    - pd.merge(df1, df2, on='key'): Join/merge DataFrames

# 2. Aggregation Examples:
#    - df.groupby('category')['sales'].sum(): Single column aggregation
#    - df.groupby('category').agg({{'sales': 'sum', 'quantity': 'mean'}}): Multiple aggregations
#    - df.groupby(['cat1', 'cat2'])['value'].sum().reset_index(): Multiple grouping columns

# 3. IMPORTANT SYNTAX RULES:
#    - Always use LISTS for column selection: df[['col1', 'col2']] NOT df[('col1', 'col2')]
#    - Use .reset_index() after groupby operations to flatten the result
#    - Handle missing values with df.fillna() or df.dropna()
#    - Use proper column references: df['column_name'] or df.column_name

Requirements:
1. Use pandas (pd) and numpy (np) for all operations
2. Handle missing values appropriately
3. Store result in 'transformed_df'
4. DO NOT define functions or classes
5. Return a pandas DataFrame
6. Use proper type conversions if needed
7. Handle potential errors gracefully
8. ALWAYS use lists for column selection, never tuples
9. Use .reset_index() after groupby operations
10. No imports

Allowed globals:
- pd: pandas library
- np: numpy library  
- df: input DataFrame (work with df.copy() to avoid modifying original)

Example of CORRECT code:
# Calculate total sales by category (CORRECT - using list)
transformed_df = (df.copy()
                   .query('sales > 0')
                   .groupby('category')
                   .agg({{'sales': 'sum', 'quantity': 'mean'}})
                   .reset_index())

Example of INCORRECT code:
# This will cause error - using tuple instead of list
transformed_df = df.groupby('category')['sales', 'quantity'].sum()  # WRONG!

Provide only the code, no explanations. Work directly with 'df' as the input DataFrame."""

    try:
        response_text = await generate_with_ollama(input_text, temperature=request.temperature)
        
        # Extract code from markdown blocks
        code_match = re.search(r"```python\n(.*?)\n```", response_text, re.DOTALL)
        code = code_match.group(1) if code_match else response_text
        
        # Clean the code
        code = code.strip()
        
        # Validate that the code assigns to transformed_df
        if 'transformed_df' not in code:
            code += '\ntransformed_df = df.copy()'
            
        logger.info(f"Generated transformation code: {code}")
        return code
        
    except Exception as e:
        logger.error(f"Error generating transformation code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating transformation code: {str(e)}")

async def get_statistical_code(request: GenerationRequest) -> str:
    """Generate pandas/scipy code for statistical analysis based on prompt."""
    input_text = f"""Write Python code to perform the following statistical analysis using pandas and scipy:

Prompt: {request.prompt}
Available columns: {', '.join(request.columns)}

Statistical Analysis Guide:
1. Descriptive Statistics:
   - df.describe(): Basic stats (count, mean, std, min, 25%, 50%, 75%, max)
   - df[['col1', 'col2']].mean(), .median(), .std()
   - df.skew(), df.kurtosis()
   - df.quantile([0.25, 0.5, 0.75]): Percentiles

2. Correlation & Covariance:
   - df[['col1', 'col2']].corr(): Correlation matrix
   - df['col1'].corr(df['col2']): Single correlation
   - scipy.stats.pearsonr(df['col1'], df['col2'])
   - scipy.stats.spearmanr(df['col1'], df['col2'])

3. Statistical Tests:
   - scipy.stats.ttest_1samp(df['col'], expected_mean)
   - scipy.stats.ttest_ind(group1, group2)
   - scipy.stats.f_oneway(group1, group2, group3): One-way ANOVA
   - scipy.stats.chi2_contingency(pd.crosstab(df['col1'], df['col2']))
   - scipy.stats.shapiro(df['col']): Normality test

4. Regression Analysis:
   - scipy.stats.linregress(df['x'], df['y'])
   - np.polyfit(df['x'], df['y'], degree=1)

Requirements:
1. Use pandas (pd), numpy (np), and scipy.stats for operations
2. Handle missing values with dropna() before statistical tests
3. Store result in 'stat_result' (can be DataFrame, dict, or statistical result)
4. DO NOT define functions
5. Include proper error handling for missing data
6. Use lists for column selection, never tuples

Allowed globals:
- pd: pandas library
- np: numpy library
- df: input DataFrame
- stats: scipy.stats module

Example formats:

For correlation analysis:
# Calculate correlation matrix
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
correlation_matrix = df[numeric_cols].corr()
stat_result = correlation_matrix

For t-test:
# Perform t-test between two groups
group1 = df[df['category'] == 'A']['value'].dropna()
group2 = df[df['category'] == 'B']['value'].dropna()
t_stat, p_value = stats.ttest_ind(group1, group2)
stat_result = {{'t_statistic': t_stat, 'p_value': p_value}}

For descriptive statistics:
# Generate descriptive statistics
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
stat_result = df[numeric_cols].describe()

Provide only the code, no explanations. Work directly with 'df' as the input DataFrame."""

    try:
        response_text = await generate_with_ollama(input_text, temperature=request.temperature)
        
        # Extract code from markdown blocks
        code_match = re.search(r"```python\n(.*?)\n```", response_text, re.DOTALL)
        code = code_match.group(1) if code_match else response_text
        
        # Clean the code
        code = code.strip()
        
        # Validate that the code assigns to stat_result
        if 'stat_result' not in code:
            code += '\nstat_result = df.describe()'
            
        logger.info(f"Generated statistical code: {code}")
        return code
        
    except Exception as e:
        logger.error(f"Error generating statistical code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating statistical code: {str(e)}")

# Utility function for safe code execution
def execute_code_safely(code: str, df, allowed_modules: Dict[str, Any]) -> Any:
    """Safely execute generated code with restricted globals."""
    import pandas as pd
    import numpy as np
    from scipy import stats
    
    # Create safe execution environment
    safe_globals = {
        '__builtins__': {},
        'pd': pd,
        'np': np,
        'stats': stats,
        'df': df.copy(),  # Work with copy to avoid modifying original
        **allowed_modules
    }
    
    local_vars = {}
    
    try:
        exec(code, safe_globals, local_vars)
        
        # Return the appropriate result based on what was generated
        if 'transformed_df' in local_vars:
            return local_vars['transformed_df']
        elif 'stat_result' in local_vars:
            return local_vars['stat_result']
        else:
            raise ValueError("Generated code did not produce expected result variable")
            
    except Exception as e:
        logger.error(f"Error executing generated code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing generated code: {str(e)}")

# Test function
async def test_analyze_prompt_intent():
    """Test function for prompt intent analysis."""
    test_request = GenerationRequest(
        prompt="plot a bar chart for the revenue per item",
        columns=["item", "quantity", "unit_price_inr", "total_price_inr", "revenue"]
    )
    
    try:
        result = await analyze_prompt_intent(test_request)
        print("Test analyze_prompt_intent result:", result.dict())
        
        if result.intent == IntentType.VISUALIZATION:
            chart_config = await get_chart_config(test_request)
            print("Chart configuration:", chart_config.dict())
            
    except Exception as e:
        print(f"Test failed: {str(e)}")

# Run the test
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_analyze_prompt_intent())