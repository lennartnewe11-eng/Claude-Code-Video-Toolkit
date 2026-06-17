/**
 * Footage registry: segment id -> filename inside public/footage.
 * All real CC media (Wikimedia Commons). Race phase = trimmed video clips,
 * break + paradox = real photos with Ken-Burns motion. The question phase
 * (how / how-nation) is intentionally typographic over a gradient.
 *
 * Sources & licences are documented in project/CREDITS.md.
 */
export const FOOTAGE: Record<string, string | undefined> = {
  japan: 'japan.mp4', // Shinkansen N700 (CC BY 4.0)
  france: 'tgv.mp4', // TGV countryside pass (CC BY 3.0)
  china: 'china.mp4', // CRH entering Yuyao Station (CC BY-SA 4.0)
  'usa-break': 'usa-break.jpg', // Union Pacific, Grand Junction CO (CC0)
  richest: 'richest.jpg', // Lower Manhattan skyline (CC BY-SA 3.0)
  economy: 'economy.jpg', // Lower Manhattan panorama (CC BY-SA 3.0)
  'best-network': 'best-network.jpg', // Golden Spike 1869 (Public domain)
  squandered: 'squandered.jpg', // abandoned overgrown track (CC BY-SA 2.0)
};

/** Themed gradient colours per segment (placeholder fallback only). */
export const COLORS: Record<string, [string, string]> = {
  japan: ['#bc002d', '#1a0008'],
  france: ['#0055a4', '#04122b'],
  china: ['#de2910', '#3a1500'],
  'usa-break': ['#0a0a12', '#16161f'],
  richest: ['#b8860b', '#1a1206'],
  economy: ['#37475a', '#0c1014'],
  'best-network': ['#6b4f2a', '#241a0c'],
  squandered: ['#5a3a1a', '#140d06'],
  how: ['#0a0a12', '#16161f'],
  'how-nation': ['#0a0a12', '#16161f'],
};
