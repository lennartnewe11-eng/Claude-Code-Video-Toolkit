/**
 * Hook timeline — frame-accurate, derived from the WhisperX transcript
 * (project/script_timed.txt). All times in SECONDS, absolute from clip start.
 * The voiceover (0615_2.mov) is dropped in at 0:00 later; every visual cut is
 * anchored to a spoken phrase so picture and voice stay locked.
 */
export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

// Hook runs from the first word (1.38s) to just before chapter 1 ("Das
// goldene Zeitalter" @ 36.22s). We start the comp at 0 to keep a short
// breath of lead-in and end on the title card.
export const HOOK_END = 36.5;
export const DURATION_IN_FRAMES = Math.round(HOOK_END * FPS);

export const sec = (s: number) => Math.round(s * FPS);

export type Phase = 'race' | 'break' | 'paradox' | 'question';

export interface Segment {
  id: string;
  from: number; // seconds
  to: number; // seconds
  phase: Phase;
  text: string; // the spoken line (for kinetic typo / reference)
  label?: string; // on-screen country / context label
  overlay?: string; // speed / counter overlay
  footage?: string; // filename in public/footage (wired as downloaded)
  search: string; // footage search term (sourcing reference)
}

export const SEGMENTS: Segment[] = [
  {
    id: 'japan',
    from: 1.38,
    to: 4.98,
    phase: 'race',
    text: 'In Japan kommst du mit dem Zug in unter drei Stunden von Tokio nach Osaka.',
    label: 'JAPAN',
    overlay: 'Tokio → Osaka  <3 h',
    search: 'shinkansen passing, bullet train japan',
  },
  {
    id: 'france',
    from: 5.32,
    to: 8.95,
    phase: 'race',
    text: 'In Frankreich rast der TGV mit über 300 km/h durchs Land.',
    label: 'FRANKREICH',
    overlay: '300+ km/h',
    search: 'TGV high speed, france train fast',
  },
  {
    id: 'china',
    from: 9.33,
    to: 14.03,
    phase: 'race',
    text: 'China hat in nur 15 Jahren das größte Hochgeschwindigkeitsnetz der Welt aus dem Boden gestampft.',
    label: 'CHINA',
    overlay: '0 → 42.000 km · 15 Jahre',
    search: 'CRH china high speed rail',
  },
  {
    id: 'usa-break',
    from: 14.65,
    to: 16.17,
    phase: 'break',
    text: 'Und dann gibt es die USA.',
    label: 'USA',
    search: 'empty us train station, amtrak slow',
  },
  {
    id: 'richest',
    from: 16.55,
    to: 17.77,
    phase: 'paradox',
    text: 'Das reichste Land der Erde.',
    search: 'new york skyline, wall street',
  },
  {
    id: 'economy',
    from: 18.05,
    to: 20.14,
    phase: 'paradox',
    text: 'Die größte Wirtschaftsmacht der Geschichte.',
    search: 'usa economy montage',
  },
  {
    id: 'best-network',
    from: 20.59,
    to: 23.98,
    phase: 'paradox',
    text: 'Ein Land, das einmal mit Abstand das beste Eisenbahnnetz der Welt hatte.',
    search: '1900s american railroad, transcontinental railroad (sepia)',
  },
  {
    id: 'squandered',
    from: 24.46,
    to: 27.16,
    phase: 'paradox',
    text: 'Und das diesen Vorsprung heute komplett verspielt hat.',
    search: 'abandoned railroad tracks usa, rusty rails',
  },
  {
    id: 'how',
    from: 27.72,
    to: 30.37,
    phase: 'question',
    text: 'Die große Frage ist, wie kann das sein?',
    search: '—',
  },
  {
    id: 'how-nation',
    from: 30.49,
    to: 35.6,
    phase: 'question',
    text: 'Wie verliert eine Nation, die das Reisen mit der Bahn praktisch erfunden hat, ausgerechnet die Bahn?',
    search: 'recap montage of hook shots',
  },
];

/** Title card at the very end of the hook. */
export const TITLE_FROM = 33.6;
