import os
import re
import json
import logging
import httpx
from fastapi import HTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "gemma3:4b")

async def generate_with_ollama(prompt, temperature=0.5):
    """Generate response using Ollama with the specified model."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.95,
            # "top_k": 40,
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    except Exception as e:
        logger.error(f"Error generating response with Ollama: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response with Ollama: {str(e)}")

async def analyze_prompt_intent(prompt: str) -> dict:
    """Determine whether the prompt is requesting data transformation, visualization, or statistical analysis."""
    response_format = {
        "intent": "statistical",
        "reason": "Prompt requests statistical analysis",
        "visualization_type": None,
        "transformation_type": None,
        "statistical_type": "correlation"
    }

    input_text = f"""Analyze the following prompt and determine if it's requesting data transformation, visualization, or statistical analysis:

Prompt: {prompt}

Provide a JSON response with:
1. intent: Either 'visualization', 'transformation', or 'statistical'
2. reason: Brief explanation of why this classification was chosen
3. visualization_type: If intent is 'visualization', specify the chart type ('bar', 'line', 'pie', 'scatter', 'area'),
4. transformation_type: If intent is 'transformation', specify the operation type ('aggregate', 'filter', 'join', 'compute'),
5. statistical_type: If intent is 'statistical', specify the test type ('correlation', 'ttest', 'ztest', 'chi_square'), 

Example response format:
{json.dumps(response_format)}"""

    try:
        json_text = await generate_with_ollama(input_text, temperature=0.4)
        
        # Try to extract JSON from markdown code blocks if present
        json_match = re.search(r"```(?:json)?\n(.*?)\n```", json_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        
        # Clean any potential leading/trailing whitespace
        json_text = json_text.strip()
        print(json_text)
        # Handle potential issues with the JSON format
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract just the JSON object
            json_obj_match = re.search(r"(\{.*\})", json_text, re.DOTALL)
            if json_obj_match:
                return json.loads(json_obj_match.group(1))
            raise
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing prompt intent: {str(e)}")

async def get_chart_config(prompt: str, columns: list) -> dict:
    """Generate chart configuration based on natural language prompt."""
    response_format = {
        "chart_type": "bar",
        "x_axis": "date",
        "y_axis": "sales",
        "aggregation": "sum",
        "title": "Total Sales by Date"
    }
    
    input_text = f"""Based on the following prompt, determine the appropriate chart configuration:

Prompt: {prompt}

Available columns: {', '.join(columns)}

Generate a JSON configuration with:
1. chart_type: 'bar', 'line', 'pie', 'scatter', or 'area'
2. x_axis: column name for x-axis
3. y_axis: column name for y-axis
4. aggregation: 'sum', 'average', 'count', or 'none'
5. title: chart title

Example response format:
{json.dumps(response_format)}

Provide only the JSON configuration, no explanations."""

    try:
        json_text = await generate_with_ollama(input_text, temperature=0.5)
        
        # Try to extract JSON from markdown code blocks if present
        json_match = re.search(r"```(?:json)?\n(.*?)\n```", json_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        
        # Clean any potential leading/trailing whitespace
        json_text = json_text.strip()
        
        # Handle potential issues with the JSON format
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract just the JSON object
            json_obj_match = re.search(r"(\{.*\})", json_text, re.DOTALL)
            if json_obj_match:
                return json.loads(json_obj_match.group(1))
            raise
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart configuration: {str(e)}")

async def get_transformation_code(prompt: str, columns: list) -> str:
    """Generate PySpark transformation code based on prompt."""
    columns_context = "Available columns: " + ", ".join(columns)
    input_text = f"""Write Python code to perform the following PySpark DataFrame transformation:

{prompt}

Available columns: {columns_context}

PySpark Knowledge Base:
1. DataFrame Operations:
   - select(): Select columns
   - filter()/where(): Filter rows
   - groupBy(): Group data
   - orderBy(): Sort data
   - withColumn(): Add/modify columns
   - drop(): Remove columns
   - distinct(): Remove duplicates
   - union(): Combine DataFrames
   - join(): Join DataFrames

2. Common Functions:
   - F.col(): Reference column
   - F.lit(): Create literal value
   - F.when().otherwise(): Conditional logic
   - F.concat(): Concatenate strings
   - F.split(): Split strings
   - F.regexp_replace(): Replace using regex
   - F.to_date(): Convert to date
   - F.date_format(): Format date
   - F.round(): Round numbers
   - F.sum(), F.avg(), F.count(): Aggregations

3. Window Functions:
   - Window.partitionBy(): Partition data
   - F.row_number(): Row numbering
   - F.rank(): Rank values
   - F.lag(): Access previous row
   - F.lead(): Access next row

4. Data Quality:
   - na.fill(): Fill null values
   - na.drop(): Drop null values
   - na.replace(): Replace values
   - dropDuplicates(): Remove duplicates

Requirements:
1. Use PySpark DataFrame operations (pyspark.sql.functions as F)
2. Handle missing values appropriately
3. Store result in 'transformed_df'
4. DO NOT define functions
5. Return a Spark DataFrame
6. Use proper type conversions if needed

allowed_globals = '''
    'spark': spark,
    'F': F,
    'df': df,
    'datetime': datetime
'''

Available imports:
- from pyspark.sql import functions as F
- from pyspark.sql.types import *
- from pyspark.sql.window import Window
- datetime

Example format:
python
transformed_df = df.withColumn('new_column', F.col('column1') * F.col('column2'))
transformed_df = transformed_df.na.fill(0)  # Handle nulls

Provide only the code, no explanations. DO NOT DEFINE functions, directly perform the operations on the df as it is the dataframe"""

    try:
        code = await generate_with_ollama(input_text, temperature=0.4)
        print(code)
        logger.debug(f"Generated transformation code response: {code}")
        code_match = re.search(r"```python\n(.*?)\n```", code, re.DOTALL)
        code = code_match.group(1) if code_match else code
        return code
    except Exception as e:
        logger.error(f"Error generating transformation code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating transformation code: {str(e)}")

async def get_statistical_code(prompt: str, columns: list) -> str:
    """Generate PySpark code for statistical analysis based on prompt."""
    input_text = f"""Write PySpark code to perform the following statistical analysis:

{prompt}

Available columns: {', '.join(columns)}

PySpark Statistical Knowledge Base:
1. Basic Statistics:
   - F.mean(): Calculate mean
   - F.stddev(): Calculate standard deviation
   - F.variance(): Calculate variance
   - F.min(), F.max(): Min/max values
   - F.sum(): Sum values
   - F.count(): Count values
   - F.percentile_approx(): Approximate percentiles

2. Correlation Analysis:
   - Correlation.corr(): Calculate correlation matrix
   - VectorAssembler: Create feature vectors
   - Correlation.corr(): Pearson correlation

3. Hypothesis Testing:
   - ChiSquareTest: Chi-square test
   - KolmogorovSmirnovTest: KS test
   - TTest: T-test for means

4. Feature Engineering:
   - StandardScaler: Standardize features
   - MinMaxScaler: Scale to range
   - Normalizer: Normalize vectors
   - Binarizer: Convert to binary

5. Window Functions for Stats:
   - Window.partitionBy(): Group for rolling stats
   - F.avg().over(): Rolling average
   - F.stddev().over(): Rolling std dev
   - F.sum().over(): Rolling sum

Requirements:
1. Use PySpark SQL functions (pyspark.sql.functions as F)
2. Include proper statistical computations
3. Store result in 'stat_df'
4. DO NOT define functions
5. Return both the statistical results and any relevant metrics
6. Handle null values appropriately
7. Include interpretation of results

allowed_globals = '''
    'spark': spark,
    'F': F,
    'df': df,
    'datetime': datetime,
    'VectorAssembler': VectorAssembler,
    'Correlation': Correlation
'''

Available imports:
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.ml.stat import Correlation, ChiSquareTest, KolmogorovSmirnovTest
from pyspark.ml.feature import VectorAssembler, StandardScaler, MinMaxScaler
from pyspark.sql.window import Window
import numpy as np
from scipy import stats

Example formats:

For correlation:
python
# Create vector of features
assembler = VectorAssembler(inputCols=['col1', 'col2'], outputCol='features')
df_vector = assembler.transform(df)
# Calculate correlation
correlation = Correlation.corr(df_vector, 'features').collect()[0][0]
stat_df = spark.createDataFrame([(correlation.toArray().tolist())], ['correlation_matrix'])

For rolling statistics:
python
# Define window
window_spec = Window.partitionBy('group').orderBy('date').rowsBetween(-30, 0)
# Calculate rolling average
df = df.withColumn('rolling_avg', F.avg('value').over(window_spec))
# Calculate rolling standard deviation
df = df.withColumn('rolling_std', F.stddev('value').over(window_spec))

For hypothesis testing:
python
# Chi-square test
chi_sq_test = ChiSquareTest.test(df, 'features', 'label').collect()[0]
stat_df = spark.createDataFrame([(chi_sq_test.pValues, chi_sq_test.statistics)], ['p_values', 'statistics'])

Provide only the code, no explanations. DO NOT DEFINE functions, directly perform the operations on the df as it is the dataframe"""

    try:
        code = await generate_with_ollama(input_text, temperature=0.3)
        
        code_match = re.search(r"```python\n(.*?)\n```", code, re.DOTALL)
        code = code_match.group(1) if code_match else code
        print(code)
        logger.debug(f"Generated statistical code response: {code}")
        return code
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating statistical code: {str(e)}")

async def test_analyze_prompt_intent():
    prompt = "plot a bar chart for the revenue per item"
    result = await analyze_prompt_intent(prompt)
    print("Test analyze_prompt_intent result:", result)

# Run the test
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_analyze_prompt_intent())