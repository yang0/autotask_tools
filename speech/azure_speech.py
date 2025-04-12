try:
    from autotask.nodes import Node, register_node
    from autotask.api_keys import get_api_key
except ImportError:
    from ..stub import Node, register_node, get_api_key

from typing import Dict, Any
from .azureText2Speech import AzureTextToSpeech
from .azurevoice import VOICE_NAME, STYLE_LIST
import os
from datetime import datetime


AZURE_SPEECH_API_KEY = get_api_key(provider="api.cognitive.microsoft.com", key_name="AZURE_SPEECH_API_KEY")


def generate_unique_path(base_path: str) -> str:
    """
    生成唯一的文件路径，如果文件已存在则添加流水号
    """
    if not os.path.exists(base_path):
        return base_path
        
    directory = os.path.dirname(base_path)
    filename = os.path.basename(base_path)
    name, ext = os.path.splitext(filename)
    
    counter = 1
    while True:
        new_path = os.path.join(directory, f"{name}_{counter:03d}{ext}")
        if not os.path.exists(new_path):
            return new_path
        counter += 1

@register_node
class AzureSpeechNode(Node):
    NAME = "Azure Speech Node"
    DESCRIPTION = "Convert text to speech using Azure/Azure Speech Service。（https://portal.azure.com/）"

    INPUTS = {
        "text": {
            "label": "Input Text",
            "description": "The text content to be converted to speech",
            "type": "STRING",
            "required": True,
        },
        "voice": {
            "label": "Voice Name",
            "description": "The voice to use for speech synthesis",
            "type": "COMBO",
            "default": "晓涵",
            "required": False,
            "options": list(VOICE_NAME.keys()),
        },
        "style": {
            "label": "Speaking Style",
            "description": "The style of speech (e.g., 'chat', 'newscast', etc.)",
            "type": "COMBO",
            "default": "default",
            "required": False,
            "options": STYLE_LIST
        },
        "rate": {
            "label": "Speech Rate",
            "description": "The speed of speech (default is 1.0)",
            "type": "FLOAT",
            "default": 1.0,
            "required": False,
        },
        "output_dir": {
            "label": "Output Directory",
            "description": "Directory where the audio file will be saved",
            "type": "STRING",
            "required": True,
        }
    }

    OUTPUTS = {
        "audio_path": {
            "label": "Audio File Path",
            "description": "Path to the generated audio file",
            "type": "STRING",
        }
    }

    async def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        try:
            # Extract inputs
            text = node_inputs["text"]
            voice = node_inputs.get("voice", "晓涵")
            style = node_inputs.get("style", "default")
            rate = node_inputs.get("rate", 1.0)
            output_dir = node_inputs["output_dir"]

            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"speech_{timestamp}.wav"
            temp_output_path = os.path.join(output_dir, output_filename)
            
            # 检查文件是否存在，如果存在则添加流水号
            final_output_path = generate_unique_path(temp_output_path)

            workflow_logger.info(f"Starting text-to-speech conversion with voice: {voice}")
            workflow_logger.debug(f"Text content: {text[:100]}...")

            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)

            # Initialize Azure TTS
            azure_tts = AzureTextToSpeech(
                key=AZURE_SPEECH_API_KEY,
                voice=voice,
                style=style,
                rate=rate
            )

            # Convert text to speech
            azure_tts.txt2audio(text, final_output_path)
            
            workflow_logger.info(f"Successfully generated audio file at: {final_output_path}")
            
            return {
                "success": True,
                "audio_path": final_output_path
            }

        except Exception as e:
            error_msg = f"Text-to-speech conversion failed: {str(e)}"
            workflow_logger.error(error_msg)
            return {
                "success": False,
                "error_message": error_msg
            }

def text_to_speech(text: str, output_dir: str, voice: str = "晓涵", style: str = "default", rate: float = 1.0) -> str:
    """
    Convenience function to convert text to speech
    Returns the path to the generated audio file
    """
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"speech_{timestamp}.wav"
    temp_output_path = os.path.join(output_dir, output_filename)
    
    # 检查文件是否存在，如果存在则添加流水号
    final_output_path = generate_unique_path(temp_output_path)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    azure_tts = AzureTextToSpeech(key=AZURE_SPEECH_API_KEY, voice=voice, style=style, rate=rate)
    azure_tts.txt2audio(text, final_output_path)
    return final_output_path
