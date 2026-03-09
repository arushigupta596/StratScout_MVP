"""
Amazon Bedrock Client for AI Analysis
"""
import boto3
import json
from typing import Dict, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.errors import BedrockError
from common.utils import retry_with_backoff

logger = get_logger(__name__)


class BedrockClient:
    """Client for Amazon Bedrock API."""
    
    def __init__(self):
        """Initialize Bedrock client."""
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=Config.BEDROCK_REGION
        )
        self.model_id = Config.BEDROCK_MODEL_ID
    
    @retry_with_backoff(max_attempts=3, base_delay=2.0)
    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke Claude 3 Sonnet model via Bedrock.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            system_prompt: Optional system prompt
        
        Returns:
            Model response dictionary
        
        Raises:
            BedrockError: If API call fails
        """
        max_tokens = max_tokens or Config.MAX_TOKENS
        temperature = temperature or Config.TEMPERATURE
        
        # Construct request body for Claude 3
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Add system prompt if provided
        if system_prompt:
            request_body["system"] = system_prompt
        
        try:
            logger.info(f"Invoking Bedrock model: {self.model_id}")
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract content from Claude 3 response
            content = response_body.get('content', [])
            if content and len(content) > 0:
                text = content[0].get('text', '')
            else:
                text = ''
            
            result = {
                'text': text,
                'stop_reason': response_body.get('stop_reason'),
                'usage': response_body.get('usage', {}),
                'model_id': self.model_id
            }
            
            logger.info(
                f"Bedrock invocation successful",
                extra={
                    'input_tokens': result['usage'].get('input_tokens', 0),
                    'output_tokens': result['usage'].get('output_tokens', 0)
                }
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Bedrock invocation failed: {str(e)}", exc_info=True)
            raise BedrockError(f"Failed to invoke Bedrock: {str(e)}")
    
    def analyze_with_structured_output(
        self,
        prompt: str,
        expected_fields: list,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke model and parse structured JSON output.
        
        Args:
            prompt: User prompt requesting JSON output
            expected_fields: List of expected field names
            system_prompt: Optional system prompt
        
        Returns:
            Parsed JSON response
        """
        # Add JSON formatting instruction to prompt
        json_prompt = f"{prompt}\n\nProvide your response as a valid JSON object with these fields: {', '.join(expected_fields)}"
        
        response = self.invoke_model(json_prompt, system_prompt=system_prompt)
        text = response['text']
        
        # Try to extract JSON from response
        try:
            # Look for JSON in code blocks
            if '```json' in text:
                json_start = text.find('```json') + 7
                json_end = text.find('```', json_start)
                json_text = text[json_start:json_end].strip()
            elif '```' in text:
                json_start = text.find('```') + 3
                json_end = text.find('```', json_start)
                json_text = text[json_start:json_end].strip()
            else:
                # Try to find JSON object
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                json_text = text[json_start:json_end]
            
            parsed = json.loads(json_text)
            
            # Add metadata
            parsed['_metadata'] = {
                'model_id': response['model_id'],
                'usage': response['usage']
            }
            
            return parsed
        
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON from Bedrock response: {str(e)}")
            logger.debug(f"Response text: {text}")
            
            # Return raw text with error indicator
            return {
                'error': 'Failed to parse JSON',
                'raw_text': text,
                '_metadata': {
                    'model_id': response['model_id'],
                    'usage': response['usage']
                }
            }
    
    def batch_analyze(
        self,
        prompts: list,
        system_prompt: Optional[str] = None
    ) -> list:
        """
        Analyze multiple prompts in sequence.
        
        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt
        
        Returns:
            List of responses
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"Processing batch item {i+1}/{len(prompts)}")
                result = self.invoke_model(prompt, system_prompt=system_prompt)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch item {i+1} failed: {str(e)}")
                results.append({
                    'error': str(e),
                    'text': ''
                })
        
        return results
