from .baseText2Speech import Text2SpeechBase
from .azurevoice import VOICE_NAME


class AzureTextToSpeech(Text2SpeechBase):
    def __init__(self, key, region="eastasia", voice="晓涵", style="default", rate=1):
        self.voice = voice
        self.style = style
        self.rate = rate
        self.key = key
        self.region = region
        self.endpoint = f"https://{self.region}.api.cognitive.microsoft.com/sts/v10/issuetoken"
        self.speech_config = None
        self.synthesizer = None
        self._initialize_azure()

    def _initialize_azure(self):
        import azure.cognitiveservices.speech as speechsdk
        self.speech_config = speechsdk.SpeechConfig(subscription=self.key, region=self.region)
        self.speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
        self.synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)

    def txt2audio(self, txt, output_file):
        ssml = self._generate_ssml(txt)
        # print(ssml)

        result = self.synthesizer.speak_ssml_async(ssml).get()
        with open(output_file, "wb") as audio_file:
            audio_file.write(result.audio_data)

    def _generate_ssml(self, txt):
        voice_name = self._get_voice_name()
        print(f"{voice_name}/{self.style}/{self.rate}/{txt}")
        return f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
        <voice name="{voice_name}">
            <mstts:express-as style="{self.style}">
                <prosody rate="{self.rate}">
                {txt}
                </prosody>
            </mstts:express-as>
        </voice>
        </speak>
        """

    def _get_voice_name(self):
        return VOICE_NAME[self.voice]
    

def read_english(text: str, audio_path: str, rate=0.7) -> str:
    azure_text2speech = AzureTextToSpeech(voice="ava", rate=rate)
    azure_text2speech.txt2audio(text, output_file=audio_path)

    return audio_path