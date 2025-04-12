
import os

# 基类
class Text2SpeechBase:
    def txt2audio(self, txt, output_file):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def txt2audio_break_lines(self, txt_file, output_dir=None):
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if not line.strip():
                continue

            line = line[:5000]  # Truncate line if it exceeds the character limit

            audio_file = self._generate_filename(txt_file, output_dir, i)
            self.txt2audio(line, audio_file)

    def _generate_filename(self, txt_file, output_dir, index):
        if output_dir:
            filename = os.path.split(txt_file)[-1]
            file_only = filename.split(".")[0]
            return os.path.join(output_dir, f"{file_only}_{index}.wav")
        else:
            return f"{os.path.splitext(txt_file)[0]}_{index}.wav"