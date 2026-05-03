from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import openai
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.1,
                openai_api_key=api_key
            )
        else:
            self.llm = None
            print(f"Warning: OPENAI_API_KEY not found. {self.name} will not be able to use LLM features.")
        self.logger = logging.getLogger(f"agent.{name}")
        
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results"""
        pass
    
    def log_processing(self, input_data: Dict[str, Any], output_data: Dict[str, Any], processing_time: float):
        """Log processing information"""
        self.logger.info(f"Agent {self.name} processed data in {processing_time:.2f}s")
        self.logger.debug(f"Input: {input_data}")
        self.logger.debug(f"Output: {output_data}")
    
    async def call_llm(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Call the LLM with messages"""
        if not self.llm:
            raise ValueError(f"LLM not available for {self.name}. Please set OPENAI_API_KEY environment variable.")
        
        try:
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                else:
                    langchain_messages.append(HumanMessage(content=msg["content"]))
            
            response = await self.llm.ainvoke(langchain_messages)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}")
            raise
    
    def validate_output(self, output: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that output contains required fields"""
        for field in required_fields:
            if field not in output:
                self.logger.error(f"Missing required field: {field}")
                return False
        return True
    
    def calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data quality"""
        confidence = 0.5  # Base confidence
        
        # Add confidence based on data completeness
        if data.get("title"):
            confidence += 0.1
        if data.get("content") and len(data["content"]) > 100:
            confidence += 0.1
        if data.get("source_count", 0) > 1:
            confidence += 0.1
        if data.get("published_at"):
            confidence += 0.1
            
        return min(confidence, 1.0)
