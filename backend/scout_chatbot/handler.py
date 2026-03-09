"""
Scout Chatbot Lambda Handler
"""
import json
import boto3
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.errors import ChatbotError
from common.json_encoder import dumps_decimal
from scout_chatbot.query_processor import QueryProcessor
from scout_chatbot.conversation_manager import ConversationManager

logger = get_logger(__name__)


class ScoutChatbotHandler:
    """Handler for Scout chatbot operations."""
    
    def __init__(self):
        """Initialize handler."""
        self.dynamodb = boto3.resource('dynamodb')
        self.conversation_table = self.dynamodb.Table(Config.CONVERSATION_TABLE)
        
        self.query_processor = QueryProcessor()
        self.conversation_manager = ConversationManager(self.conversation_table)
    
    def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response.
        
        Args:
            user_id: User identifier
            message: User message
            conversation_id: Optional conversation ID
        
        Returns:
            Response with answer and metadata
        """
        logger.info(f"Processing message for user: {user_id}")
        
        try:
            # Get or create conversation
            if conversation_id:
                conversation = self.conversation_manager.get_conversation(conversation_id)
            else:
                conversation = self.conversation_manager.create_conversation(user_id)
                conversation_id = conversation['conversation_id']
            
            # Add user message to conversation
            self.conversation_manager.add_message(
                conversation_id=conversation_id,
                role='user',
                content=message
            )
            
            # Process query
            response = self.query_processor.process_query(
                query=message,
                user_id=user_id,
                conversation_history=conversation.get('messages', [])
            )
            
            # Add assistant response to conversation
            self.conversation_manager.add_message(
                conversation_id=conversation_id,
                role='assistant',
                content=response['answer']
            )
            
            logger.info(
                f"Message processed successfully",
                extra={
                    'conversation_id': conversation_id,
                    'intent': response.get('intent')
                }
            )
            
            return {
                'conversation_id': conversation_id,
                'answer': response['answer'],
                'intent': response.get('intent'),
                'data': response.get('data'),
                'charts': response.get('charts', []),
                'confidence': response.get('confidence', 0.8)
            }
        
        except Exception as e:
            logger.error(f"Message processing failed: {str(e)}", exc_info=True)
            raise ChatbotError(f"Failed to process message: {str(e)}")


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for Scout chatbot.
    
    Args:
        event: Lambda event
        context: Lambda context
    
    Returns:
        Response dictionary
    """
    logger.info('Scout chatbot handler started', extra={'event': event})
    
    try:
        handler = ScoutChatbotHandler()
        
        # Parse request
        http_method = event.get('httpMethod', 'POST')
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body) if body else {}
        
        # Get user ID from authorizer context
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', 'demo-user')
        
        # Handle POST - send message
        if http_method == 'POST':
            message = body.get('message')
            conversation_id = body.get('conversation_id')
            
            if not message:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Message is required'
                    })
                }
            
            response = handler.process_message(
                user_id=user_id,
                message=message,
                conversation_id=conversation_id
            )
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': dumps_decimal(response)
            }
        
        # Handle GET - retrieve conversation
        elif http_method == 'GET':
            query_params = event.get('queryStringParameters') or {}
            conversation_id = query_params.get('conversation_id')
            
            if conversation_id:
                conversation = handler.conversation_manager.get_conversation(conversation_id)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': dumps_decimal(conversation)
                }
            else:
                # List conversations for user
                conversations = handler.conversation_manager.list_conversations(user_id)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': dumps_decimal({
                        'conversations': conversations
                    })
                }
        
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Method not allowed'
                })
            }
    
    except Exception as e:
        logger.error(f"Scout chatbot handler failed: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
