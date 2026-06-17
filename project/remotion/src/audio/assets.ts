/**
 * Audio asset registry. Files live in public/audio (gitignored, fetched by
 * project/tools/fetch_audio.sh). `null` = not yet downloaded -> AudioLayer
 * skips it, so the comp always renders.
 */
export const AUDIO = {
  // Voiceover — the full narration track extracted from 0615_2.mov.
  // The hook comp starts at 0:00, so the VO sits at its natural timing
  // (first word @ 1.38s) and every cut is locked to it.
  vo: 'vo.m4a' as string | null,

  // Driving music bed ("Crypto" by Kevin MacLeod, Incompetech, CC-BY 4.0).
  musicBed: 'musicBed.mp3' as string | null,

  // One-shot SFX (Freesound, CC0)
  whoosh: 'whoosh.mp3' as string | null,
  impact: 'impact.mp3' as string | null,
  riser: 'riser.mp3' as string | null,
  boom: 'impact.mp3' as string | null, // reuse the impact as the title hit
};
