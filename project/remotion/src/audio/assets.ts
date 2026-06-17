/**
 * Audio asset registry. Files live in public/audio and are downloaded by
 * project/tools/fetch_audio.sh (music from Incompetech CC-BY, SFX from
 * Freesound / archive.org). A value of `null` means "not yet downloaded" —
 * the AudioLayer then simply skips it, so the comp always renders.
 *
 * Fill these in as files land in public/audio.
 */
export const AUDIO = {
  // Driving music bed for the "race" phase (loud) that carries under the
  // whole hook with volume automation handled in AudioLayer.
  musicBed: null as string | null, // e.g. 'music-bed.mp3'

  // One-shot SFX
  whoosh: null as string | null, // cut transitions in race phase
  impact: null as string | null, // the hard break on "Und dann gibt es die USA"
  riser: null as string | null, // build under the closing question
  boom: null as string | null, // final hit on the title card
};
