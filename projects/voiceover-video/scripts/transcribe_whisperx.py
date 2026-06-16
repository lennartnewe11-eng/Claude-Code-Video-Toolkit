#!/usr/bin/env python3
"""High-precision German transcript: faster-whisper ASR + WhisperX forced alignment.

Why this exists alongside transcribe.py:
  transcribe.py gives Whisper's own segment timing (mechanical ~6s chunks that cut
  mid-sentence). This script keeps the same large-v3 ASR but runs a wav2vec2 forced
  alignment on top, yielding frame-accurate word- and sentence-level timestamps -
  what you want for tight editing / kinetic typography sync.

Pipeline:
  1. ASR with faster-whisper large-v3 (beam_size=5, bundled Silero VAD, no download).
  2. Forced alignment with WhisperX using a wav2vec2 model.

Network notes (matter in sandboxed / restricted-egress runs):
  - WhisperX's DEFAULT German align model is a torchaudio bundle hosted on
    download.pytorch.org. If that host is blocked you get HTTP 403. We therefore
    pin a public Hugging Face model (override via WX_ALIGN_MODEL).
  - WhisperX's VAD (silero via github / pyannote gated on HF) is bypassed entirely
    by doing the ASR pass through faster-whisper directly.

Outputs into transcript/:
  transcript_whisperx.json        - segments {start,end,text, words:[{word,start,end,score}]}
  transcript_whisperx.srt         - segment-level subtitles
  transcript_whisperx_words.srt   - word-level subtitles (frame accurate)
  transcript_whisperx_raw.txt     - human-readable [start - end] text

Run from the project root: python3 scripts/transcribe_whisperx.py
Requires: faster-whisper, whisperx, ffmpeg on PATH, huggingface.co egress.
"""
import json, os, sys, gc

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAV = os.path.join(HERE, "assets", "voiceover.wav")
OUT = os.path.join(HERE, "transcript")
os.makedirs(OUT, exist_ok=True)

DEVICE = "cpu"
COMPUTE = os.environ.get("WX_COMPUTE", "int8")     # "float32" for max ASR quality (slow on CPU)
MODEL = os.environ.get("WX_MODEL", "large-v3")
LANG = "de"
THREADS = int(os.environ.get("WX_THREADS", os.cpu_count() or 4))
# Public HF wav2vec2; the whisperx default for "de" lives on download.pytorch.org.
ALIGN_MODEL = os.environ.get("WX_ALIGN_MODEL", "jonatasgrosman/wav2vec2-large-xlsr-53-german")


def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def ensure_wav():
    if os.path.exists(WAV):
        return
    master = os.path.join(HERE, "assets", "voiceover_master.m4a")
    if os.path.exists(master):
        print("voiceover.wav missing - regenerating from voiceover_master.m4a")
        os.system(f'ffmpeg -y -i "{master}" -ac 1 -ar 16000 "{WAV}" -loglevel error')
    else:
        sys.exit(f"missing {WAV} and master - run scripts/extract_audio.sh first")


def main():
    ensure_wav()
    import whisperx

    # --- 1) ASR with faster-whisper (bundled VAD, beam search) ---
    from faster_whisper import WhisperModel
    print(f"ASR: faster-whisper {MODEL} compute={COMPUTE} threads={THREADS}")
    model = WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE, cpu_threads=THREADS)
    fw_segments, info = model.transcribe(
        WAV, language=LANG, beam_size=5, vad_filter=True,
        condition_on_previous_text=True,
    )
    segments = []
    for seg in fw_segments:
        t = seg.text.strip()
        if t:
            segments.append({"start": float(seg.start), "end": float(seg.end), "text": t})
            print(f"[{seg.start:7.2f}-{seg.end:7.2f}] {t}")
    print(f"ASR done: {len(segments)} segments, duration={info.duration:.1f}s")
    del model; gc.collect()

    # --- 2) Forced alignment for frame-accurate word/segment timestamps ---
    audio = whisperx.load_audio(WAV)
    print(f"alignment model: {ALIGN_MODEL}")
    model_a, metadata = whisperx.load_align_model(language_code=LANG, device=DEVICE,
                                                  model_name=ALIGN_MODEL)
    aligned = whisperx.align(segments, model_a, metadata, audio, DEVICE,
                             return_char_alignments=False)
    segs = aligned["segments"]
    words_all = aligned.get("word_segments", [])
    print(f"alignment done: {len(segs)} segments, {len(words_all)} words")
    del model_a; gc.collect()

    # --- 3) Write outputs ---
    data, srt, raw = [], [], []
    for i, s in enumerate(segs, 1):
        st, en = s.get("start"), s.get("end")
        text = s.get("text", "").strip()
        words = [{"word": w.get("word"), "start": w.get("start"),
                  "end": w.get("end"), "score": round(w.get("score", 0), 3)}
                 for w in s.get("words", []) if w.get("start") is not None]
        data.append({"start": round(st, 3) if st is not None else None,
                     "end": round(en, 3) if en is not None else None,
                     "text": text, "words": words})
        if st is not None and en is not None:
            srt.append(f"{i}\n{fmt(st)} --> {fmt(en)}\n{text}\n")
            raw.append(f"[{st:7.2f}s - {en:7.2f}s]  {text}")

    wsrt = []
    for i, w in enumerate(words_all, 1):
        if w.get("start") is None:
            continue
        wsrt.append(f"{i}\n{fmt(w['start'])} --> {fmt(w['end'])}\n{w['word']}\n")

    json.dump(data, open(os.path.join(OUT, "transcript_whisperx.json"), "w"),
              ensure_ascii=False, indent=2)
    open(os.path.join(OUT, "transcript_whisperx.srt"), "w").write("\n".join(srt))
    open(os.path.join(OUT, "transcript_whisperx_words.srt"), "w").write("\n".join(wsrt))
    open(os.path.join(OUT, "transcript_whisperx_raw.txt"), "w").write("\n".join(raw) + "\n")
    print(f"\nWrote {len(data)} segments / {len(wsrt)} word entries to {OUT}")


if __name__ == "__main__":
    main()
