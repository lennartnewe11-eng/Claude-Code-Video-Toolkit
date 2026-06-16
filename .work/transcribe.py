from faster_whisper import WhisperModel
import json
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = m.transcribe("voiceover.wav", language="de", vad_filter=True)
print("LANG", info.language, "DUR", round(info.duration,1))
out=[]
for s in segs:
    out.append({"start":round(s.start,2),"end":round(s.end,2),"text":s.text.strip()})
    print(f"[{s.start:7.2f} - {s.end:7.2f}] {s.text.strip()}")
json.dump(out, open("transcript.json","w"), ensure_ascii=False, indent=2)
