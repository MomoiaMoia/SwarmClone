import socket
import torch

from typing import List, Optional

from pathlib import Path
from cosyvoice.cli.cosyvoice import CosyVoice   # type: ignore
from cosyvoice.utils.file_utils import load_wav   # type: ignore

emotion_to_prompt = {
    "like": "happily, shamefully",
    "disgust": "hugely, disgustedly",
    "anger": "strongly, angrily",
    "happy": "slightly, happily",
    "sad": "sadly, tearfully",
}

adj_to_adv = {
    "like": "happily",
    "disgust": "disgustedly",
    "anger": "angrily",
    "happy": "happily",
    "sad": "sadly",
}


def get_emotion_prompt(emotions):
    emotions_top2 = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
    if emotions_top2[0][0] == "neutral":
        return "neutral"
    elif emotions_top2[0][1] > 0.5 and emotions_top2[1][0] != "neutral":
        return emotion_to_prompt[emotions_top2[0][0]]
    else:
        return f"{adj_to_adv[emotions_top2[0][0]]}, {adj_to_adv[emotions_top2[1][0]]}"

@torch.no_grad()
def tts_generate(tts: List[CosyVoice], s: str, tune: str, emotions, is_linux: bool):
    """tts生成

    Args:
        tts (List[CosyVoice]):  对于 Windows 传入 [cosyvoice_ins], linux 传入 [cosyvoice_sft, cosyvoice_ins]
        s (str):                需要生成的文本
        tune (str):             使用的音色
        emotions (EmotionType): 感情
        platform (_type_):      平台
    """
    prompt = get_emotion_prompt(emotions)
    if prompt == "neutral":
        if not is_linux:
            prompt_speech_16k = load_wav(Path(__file__).parent / "asset" / "知络_1.2_ENHANCE.mp3", 16000)
            return list(tts[0].inference_zero_shot(s.strip(), 
                                                "这是一段测试的语音，用来体验这个音色在speaker finetune下的表现效果，你喜欢吗？",
                                                prompt_speech_16k, stream=False))[0]["tts_speech"]
        else:
            return list(tts[0].inference_sft(s.strip(), tune, stream=False))[0]["tts_speech"]
    if not is_linux:
        return list(tts[0].inference_instruct(s.strip(), tune, prompt, stream=False))[0]["tts_speech"]
    else:
        return list(tts[1].inference_instruct(s.strip(), tune, prompt, stream=False))[0]["tts_speech"]
