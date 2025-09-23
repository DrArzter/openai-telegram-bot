# services/openai_client.py
import base64
from os import getenv
import openai
from typing import Optional, List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """
    OpenAI API client for ChatGPT integration.
    """

    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")

        self.client = openai.OpenAI(api_key=api_key)
        logger.info("OpenAI client initialized successfully")

    async def get_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Get response from ChatGPT.

        Args:
            user_message: User's message/question
            system_prompt: System prompt to set context/personality
            model: OpenAI model to use
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)

        Returns:
            ChatGPT response text or None if error occurred
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": user_message})

            logger.info(
                f"Sending request to OpenAI: model={model}, tokens={max_tokens}"
            )

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            content = response.choices[0].message.content
            usage = response.usage

            if usage:
                logger.info(
                    f"OpenAI response received: tokens_used={usage.total_tokens}"
                )
            else:
                logger.info(
                    "OpenAI response received: token usage not available in response."
                )

            return content

        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            return "Rate limit exceeded. Please try again later."

        except openai.AuthenticationError:
            logger.error("OpenAI authentication failed")
            return "Authentication error. Please check API key."

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "API error occurred. Please try again."

        except Exception as e:
            logger.error(f"Unexpected error in OpenAI request: {e}")
            return "An unexpected error occurred. Please try again."

    async def get_conversation_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Get response for a conversation with message history.

        Args:
            messages: List of messages in OpenAI format [{"role": "...", "content": "..."}]
            model: OpenAI model to use
            max_tokens: Maximum tokens in response
            temperature: Response creativity

        Returns:
            ChatGPT response text or None if error occurred
        """
        try:
            logger.info(f"Sending conversation to OpenAI: {len(messages)} messages")

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            content = response.choices[0].message.content
            usage = response.usage

            if usage:
                logger.info(
                    f"OpenAI response received: tokens_used={usage.total_tokens}"
                )
            else:
                logger.info(
                    "OpenAI response received: token usage not available in response."
                )

            return content

        except Exception as e:
            logger.error(f"Error in conversation request: {e}")
            return "Error occurred during conversation. Please try again."

    async def describe_image(
        self,
        image_bytes: bytes,
        prompt: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Describe an image using ChatGPT with vision capabilities.
        """
        try:
            logger.info("Sending image to OpenAI for description")

            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            content = response.choices[0].message.content
            usage = response.usage

            if usage:
                logger.info(
                    f"Image description received: tokens_used={usage.total_tokens}"
                )
            else:
                logger.info(
                    "Image description received: token usage not available in response."
                )

            return content

        except Exception as e:
            logger.error(f"Error in image description request: {e}")
            return "Error occurred during image description. Please try again."


# Global client instance
openai_client = OpenAIClient()
