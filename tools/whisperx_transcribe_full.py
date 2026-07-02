#!/usr/bin/env python3
"""Gap-free millisecond transcription for speech-over-music.

WhisperX's pyannote VAD gates transcription and drops speech that sits under
loud background music, leaving timeline gaps. This variant bypasses the VAD:
faster-whisper transcribes the audio continuously (no gaps possible), then
WhisperX forced alignment adds word-level millisecond timestamps.

Anti-hallucination: no_repeat_ngram_size + repetition_penalty stop the
'prop prop prop' / repeated-token loops; temperature fallback +
compression/logprob thresholds suppress music-only garbage.

Usage:
  python whisperx_transcribe_full.py AUDIO --out PREFIX --language de \
         --model large-v2 --compute-type float32
"""
import argparse
import gc
import json
import os

import whisperx
from faster_whisper import WhisperModel


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
    ap.add_argument("audio")
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default="large-v2")
    ap.add_argument("--language", default="de")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--compute-type", default="float32")
    # Lower catches narration buried under music swells; too low invites music-only hallucination
    ap.add_argument("--no-speech-threshold", type=float, default=0.6)
    args = ap.parse_args()

    out = args.out or os.path.splitext(args.audio)[0]

    print("loading audio...", flush=True)
    audio = whisperx.load_audio(args.audio)

    print(f"loading faster-whisper {args.model} ({args.compute_type})...", flush=True)
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type,
                         cpu_threads=os.cpu_count() or 4)

    print("transcribing (continuous, no VAD gating)...", flush=True)
    fw_segments, info = model.transcribe(
        args.audio,
        language=args.language,
        beam_size=5,
        temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        condition_on_previous_text=False,     # stops error propagation between windows
        no_repeat_ngram_size=3,               # kills 'prop prop prop' loops
        repetition_penalty=1.1,
        compression_ratio_threshold=2.4,      # triggers fallback on gibberish
        log_prob_threshold=-1.0,
        no_speech_threshold=args.no_speech_threshold,  # drops true music-only windows
        vad_filter=False,                     # <-- process the whole file, no gaps
    )
    segs = [{"start": s.start, "end": s.end, "text": s.text} for s in fw_segments]
    for s in segs:
        print(f"  [{ts(s['start'], '.')} - {ts(s['end'], '.')}] {s['text'].strip()}", flush=True)
    del model
    gc.collect()

    print("loading alignment model...", flush=True)
    align_model, metadata = whisperx.load_align_model(language_code=args.language, device=args.device)

    print("aligning (word-level)...", flush=True)
    result = whisperx.align(segs, align_model, metadata, audio, args.device,
                            return_char_alignments=False)
    segments = result["segments"]

    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump({"language": args.language, "segments": segments}, f, ensure_ascii=False, indent=2)
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
