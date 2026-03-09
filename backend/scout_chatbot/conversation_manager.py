"""
Conversation Manager for Scout Chatbot
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger

logger = get_logger(__name__)


class ConversationManager:
    """Manage conversation state and history."""
    
    def __init__(self, conversation_table):
        """Initialize conversation manager."""
        self.conversation_table = conversation_table
    
    def create_conversation(self, user_id: str) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            user_id: User identifier
        
        Returns:
            Conversation object
        """
        conversation_id = f"conv-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        conversation = {
            'conversation_id': conversation_id,
            'timestamp': timestamp,  # Required for sort key
            'user_id': user_id,
            'created_at': timestamp,
            'updated_at': timestamp,
            'messages': []
        }
        
        self.conversation_table.put_item(Item=conversation)
        logger.info(f"Created conversation: {conversation_id}")
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: Conversation identifier
        
        Returns:
            Conversation object
        """
        try:
            # Scan to find the conversation (since we don't know the timestamp)
            response = self.conversation_table.query(
                KeyConditionExpression='conversation_id = :cid',
                ExpressionAttributeValues={':cid': conversation_id},
                Limit=1
            )
            items = response.get('Items', [])
            return items[0] if items else {}
        except Exception as e:
            logger.error(f"Failed to get conversation: {str(e)}")
            return {}
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> None:
        """
        Add a message to conversation.
        
        Args:
            conversation_id: Conversation identifier
            role: Message role (user/assistant)
            content: Message content
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        message = {
            'role': role,
            'content': content,
            'timestamp': timestamp
        }
        
        # Get current conversation
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Conversation not found: {conversation_id}")
            return
            
        messages = conversation.get('messages', [])
        messages.append(message)
        
        # Update conversation
        try:
            self.conversation_table.update_item(
                Key={
                    'conversation_id': conversation_id,
                    'timestamp': conversation.get('timestamp')
                },
                UpdateExpression='SET messages = :messages, updated_at = :updated',
                ExpressionAttributeValues={
                    ':messages': messages,
                    ':updated': timestamp
                }
            )
            logger.debug(f"Added {role} message to conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Failed to add message: {str(e)}")
    
    def list_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List conversations for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations
        
        Returns:
            List of conversations
        """
        response = self.conversation_table.query(
            IndexName='UserConversationIndex',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,
            Limit=limit
        )
        
        return response.get('Items', [])
