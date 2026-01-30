import json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from config import Config

class BookGenerator:
    def __init__(self):
        # Initialize the Agno Agent with vLLM configuration
        self.model = OpenAIChat(
            id=Config.MODEL_NAME,
            base_url=Config.VLLM_API_BASE,
            api_key=Config.VLLM_API_KEY,
        )
        
        # We use a single capable agent for the different steps
        self.agent = Agent(
            model=self.model,
            description="You are an expert author and editor.",
            markdown=False # We want raw text for processing
        )

    def generate_outline(self, topic):
        """Step 1: Generate a list of chapters."""
        prompt = (
            f"Create a detailed book outline for the topic: '{topic}'. "
            "Return ONLY a valid JSON list of strings, where each string is a chapter title. "
            "Do not add markdown formatting or extra text. "
            "Example format: [\"Chapter 1: Introduction\", \"Chapter 2: History\"]"
        )
        response = self.agent.run(prompt)
        
        # Clean and parse JSON
        content = response.content
        try:
            # Attempt to find JSON array in text if model chats too much
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
            return json.loads(content)
        except Exception as e:
            # Fallback if JSON fails
            return [f"Chapter 1: {topic} Overview", f"Chapter 2: Deep Dive into {topic}"]

    def write_chapter(self, chapter_title, topic):
        """Step 2: Write paragraphs for a specific chapter."""
        prompt = (
            f"Write a detailed set of paragraphs for the chapter: '{chapter_title}' "
            f"based on the main book topic: '{topic}'. "
            "Provide rich, informative content. Do not include the chapter title in the output, just the body text."
        )
        response = self.agent.run(prompt)
        return response.content

    def proofread_and_format_rtf(self, full_text):
        """Step 3: Proofread and convert to RTF format."""
        # Note: We ask the LLM to generate the raw RTF syntax.
        # Ideally, we would use a Python library for RTF to be safe, 
        # but the prompt requires the model to do the conversion.
        prompt = (
            "Act as a professional editor and formatter. "
            "1. Proofread the text below for grammar and flow. "
            "2. Convert the entire text into valid RTF (Rich Text Format) code. "
            "Ensure it has a header, appropriate font settings, and formatting for Chapters and Paragraphs. "
            "Return ONLY the raw RTF code starting with {\\rtf and ending with }."
            f"\n\nTEXT TO PROCESS:\n{full_text}"
        )
        response = self.agent.run(prompt)
        return response.content
    