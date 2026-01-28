"""
Acadza WebSocket Assignment - Backend Server
FastAPI + WebSocket + Google Gemini AI Integration
Professional implementation with error handling and logging
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Acadza WebSocket AI Assignment",
    description="Real-time AI-powered follow-up questions via WebSocket",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY is required")

genai.configure(api_key=GEMINI_API_KEY)

# Use gemini-pro model (most stable and widely available)
model = genai.GenerativeModel('gemini-2.5-flash')


class ConversationManager:
    """Manages conversation state and AI interactions"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.follow_up_count = 0
        self.max_follow_ups = 3
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from user input
        Filters out common stop words and returns important words
        """
        # Remove special characters and convert to lowercase
        cleaned_text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Common stop words to filter out
        stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
            'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
            'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
            'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
            'against', 'between', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
            'out', 'on', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'just'
        }
        
        # Extract words and filter
        words = cleaned_text.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return top keywords (prioritize longer words)
        keywords.sort(key=len, reverse=True)
        return keywords[:3] if keywords else words[:2]
    
    def generate_follow_up_question(self, user_input: str) -> str:
        """
        Generate AI-powered follow-up question using Gemini
        Ensures the question contains at least one exact word from user input
        """
        try:
            # Extract keywords from user input
            keywords = self.extract_keywords(user_input)
            
            if not keywords:
                # Fallback: use the entire user input
                keywords = user_input.split()[:2]
            
            # Select the most relevant keyword
            keyword_to_use = keywords[0] if keywords else "that"
            
            # Build conversation context
            context = "\n".join([
                f"User: {msg['user']}\nAI: {msg['ai']}" 
                for msg in self.conversation_history
            ])
            
            # Craft a sophisticated prompt for Gemini
            prompt = f"""You are an empathetic conversational AI assistant conducting a follow-up interview.

Previous conversation:
{context if context else "This is the first question."}

User's latest response: "{user_input}"

CRITICAL REQUIREMENTS:
1. Generate exactly ONE follow-up question
2. The question MUST include the exact word "{keyword_to_use}" from the user's response
3. The question should feel natural and empathetic
4. Dig deeper into what the user said
5. Keep the question concise (1-2 sentences max)
6. Make it conversational and human-like
7. DO NOT ask about feelings or emotions, ask about specific details

This is follow-up question #{self.follow_up_count + 1} of {self.max_follow_ups}.

Generate the follow-up question now (MUST contain the word "{keyword_to_use}"):"""

            # Call Gemini AI
            response = model.generate_content(prompt)
            follow_up_question = response.text.strip()
            
            # Remove any quotes around the question
            follow_up_question = follow_up_question.strip('"').strip("'")
            
            # Validation: Ensure keyword is present (case-insensitive)
            if keyword_to_use.lower() not in follow_up_question.lower():
                # Force inject the keyword naturally
                follow_up_question = f"You mentioned '{keyword_to_use}'. Can you tell me more about that?"
            
            logger.info(f"✅ Generated follow-up #{self.follow_up_count + 1}: {follow_up_question}")
            return follow_up_question
            
        except Exception as e:
            logger.error(f"❌ Error generating follow-up question: {str(e)}")
            # Graceful fallback
            keyword = keywords[0] if keywords else "that"
            return f"Can you tell me more about '{keyword}'?"
    
    def add_to_history(self, user_message: str, ai_response: str):
        """Add interaction to conversation history"""
        self.conversation_history.append({
            "user": user_message,
            "ai": ai_response
        })
    
    def increment_follow_up(self):
        """Increment follow-up counter"""
        self.follow_up_count += 1
    
    def is_complete(self) -> bool:
        """Check if conversation is complete"""
        return self.follow_up_count >= self.max_follow_ups
    
    def reset(self):
        """Reset conversation state"""
        self.conversation_history.clear()
        self.follow_up_count = 0


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "message": "Acadza WebSocket AI Server is running",
        "version": "1.0.0",
        "model": "gemini-2.5-flash"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time AI conversation
    Handles bidirectional communication with frontend
    """
    await websocket.accept()
    logger.info("🔌 New WebSocket connection established")
    
    # Create a new conversation manager for this session
    conversation = ConversationManager()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            user_message = message_data.get("message", "").strip()
            
            logger.info(f"📥 Received: {message_type} - {user_message}")
            
            if message_type == "initial":
                # Handle initial user sentence
                if not user_message:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Please provide a valid sentence."
                    })
                    continue
                
                # Generate first follow-up question
                follow_up = conversation.generate_follow_up_question(user_message)
                conversation.add_to_history(user_message, follow_up)
                conversation.increment_follow_up()
                
                # Send follow-up to client
                await websocket.send_json({
                    "type": "follow_up",
                    "question": follow_up,
                    "number": conversation.follow_up_count,
                    "total": conversation.max_follow_ups
                })
            
            elif message_type == "answer":
                # Handle user's answer to follow-up question
                if conversation.is_complete():
                    # All follow-ups done
                    await websocket.send_json({
                        "type": "complete",
                        "message": "Thanks, we have got your data."
                    })
                    logger.info("✅ Conversation completed successfully")
                    break
                
                # Generate next follow-up
                follow_up = conversation.generate_follow_up_question(user_message)
                conversation.add_to_history(user_message, follow_up)
                conversation.increment_follow_up()
                
                if conversation.is_complete():
                    # This was the last question
                    await websocket.send_json({
                        "type": "follow_up",
                        "question": follow_up,
                        "number": conversation.follow_up_count,
                        "total": conversation.max_follow_ups
                    })
                else:
                    await websocket.send_json({
                        "type": "follow_up",
                        "question": follow_up,
                        "number": conversation.follow_up_count,
                        "total": conversation.max_follow_ups
                    })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid message type"
                })
    
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket connection closed by client")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "An error occurred. Please try again."
            })
        except:
            pass
    finally:
        logger.info("🔌 WebSocket connection terminated")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
