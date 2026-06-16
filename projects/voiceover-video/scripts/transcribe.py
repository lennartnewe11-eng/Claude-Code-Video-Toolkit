#!/usr/bin/env python3
"""Transcribe the German voiceover with word-level timestamps.

Requires huggingface.co egress (model download). Outputs:
  transcript/transcript.json  - segments with start/end/text
  transcript/transcript.srt   - subtitle file for review / burn-in
Run from the project root: python3 scripts/transcribe.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAV = os.path.join(HERE, "assets", "voiceover.wav")
OUT = os.path.join(HERE, "transcript")
os.makedirs(OUT, exist_ok=True)

MODEL = os.environ.get("WHISPER_MODEL", "large-v3")  # use "small" for a quick pass

def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

def main():
    if not os.path.exists(WAV):
        master = os.path.join(HERE, "assets", "voiceover_master.m4a")
        if os.path.exists(master):
            print("voiceover.wav missing - regenerating from voiceover_master.m4a")
            os.system(f'ffmpeg -y -i "{master}" -ac 1 -ar 16000 "{WAV}" -loglevel error')
        else:
            sys.exit(f"missing {WAV} and master - run scripts/extract_audio.sh first")
    from faster_whisper import WhisperModel
    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    segments, info = model.transcribe(WAV, language="de", vad_filter=True,
                                      word_timestamps=True)
    print(f"language={info.language} duration={info.duration:.1f}s model={MODEL}")
    data, srt = [], []
    for i, seg in enumerate(segments, 1):
        data.append({"start": round(seg.start, 2), "end": round(seg.end, 2),
                     "text": seg.text.strip()})
        srt.append(f"{i}\n{fmt(seg.start)} --> {fmt(seg.end)}\n{seg.text.strip()}\n")
        print(f"[{seg.start:7.2f}-{seg.end:7.2f}] {seg.text.strip()}")
    json.dump(data, open(os.path.join(OUT, "transcript.json"), "w"),
              ensure_ascii=False, indent=2)
    open(os.path.join(OUT, "transcript.srt"), "w").write("\n".join(srt))
    print(f"\nWrote {OUT}/transcript.json and transcript.srt ({len(data)} segments)")

if __name__ == "__main__":
    main()
