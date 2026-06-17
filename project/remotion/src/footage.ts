/**
 * Footage registry: segment id -> filename inside public/footage.
 * Wired in as clips are downloaded (fetch_footage.sh). Missing entries fall
 * back to themed animated placeholders, so the hook always renders.
 */
export const FOOTAGE: Record<string, string | undefined> = {
  japan: undefined,
  france: undefined,
  china: undefined,
  'usa-break': undefined,
  richest: undefined,
  economy: undefined,
  'best-network': undefined,
  squandered: undefined,
};

/** Themed gradient colours per segment (used by placeholders). */
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
