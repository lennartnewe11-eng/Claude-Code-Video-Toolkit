#!/usr/bin/env python3
"""Millisecond-accurate transcription with WhisperX (word-level forced alignment).

Produces, for a given audio/video file:
  - <out>.json        full result incl. per-word timings + confidence
  - <out>.srt         segment-level subtitles
  - <out>.words.txt   start_ms<TAB>end_ms<TAB>word   (one row per word)
  - <out>.txt         readable transcript with segment timestamps

Usage:
  python whisperx_transcribe.py AUDIO [--out PREFIX] [--model medium]
                                      [--language de] [--device cpu]

On CPU use a small/medium model with compute_type int8. For best accuracy
use --model large-v3 (slower). Requires: whisperx, ffmpeg, nltk 'punkt_tab'.
"""
import argparse
import gc
import json
import os

import whisperx


def ts(sec, sep=","):
    if sec is None:
        sec = 0.0
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="path to audio or video file")
    ap.add_argument("--out", default=None, help="output prefix (default: alongside input)")
    ap.add_argument("--model", default="medium", help="whisper model (medium, large-v3, ...)")
    ap.add_argument("--language", default=None, help="force language code, e.g. de (default: auto-detect)")
    ap.add_argument("--device", default="cpu", help="cpu or cuda")
    ap.add_argument("--compute-type", default="int8", help="int8 (cpu) / float16 (gpu)")
    ap.add_argument("--batch-size", type=int, default=8)
    args = ap.parse_args()

    out = args.out or os.path.splitext(args.audio)[0]

    print("loading audio...", flush=True)
    audio = whisperx.load_audio(args.audio)

    print(f"loading model {args.model}...", flush=True)
    model = whisperx.load_model(args.model, args.device, compute_type=args.compute_type,
                                language=args.language)

    print("transcribing...", flush=True)
    result = model.transcribe(audio, batch_size=args.batch_size, language=args.language)
    lang = result["language"]
    print("language:", lang, flush=True)
    del model
    gc.collect()

    print("loading alignment model...", flush=True)
    align_model, metadata = whisperx.load_align_model(language_code=lang, device=args.device)

    print("aligning (word-level)...", flush=True)
    result = whisperx.align(result["segments"], align_model, metadata, audio, args.device,
                            return_char_alignments=False)

    segments = result["segments"]

    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump({"language": lang, "segments": segments}, f, ensure_ascii=False, indent=2)

    with open(out + ".srt", "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n{ts(seg.get('start'))} --> {ts(seg.get('end'))}\n{seg['text'].strip()}\n\n")

    with open(out + ".words.txt", "w", encoding="utf-8") as f:
        f.write("start_ms\tend_ms\tword\n")
        for seg in segments:
            for w in seg.get("words", []):
                st, en = w.get("start"), w.get("end")
                sm = "" if st is None else int(round(st * 1000))
                em = "" if en is None else int(round(en * 1000))
                f.write(f"{sm}\t{em}\t{w['word']}\n")

    with open(out + ".txt", "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"[{ts(seg.get('start'), '.')} - {ts(seg.get('end'), '.')}] {seg['text'].strip()}\n")

    print("DONE ->", out + ".{json,srt,words.txt,txt}")


if __name__ == "__main__":
    main()
