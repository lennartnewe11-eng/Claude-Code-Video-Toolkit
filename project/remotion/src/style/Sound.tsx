import {Audio, Loop, Sequence, staticFile} from 'remotion';

/** One-shot SFX fired at a given frame. */
export const Sfx: React.FC<{src: string; at: number; volume?: number; dur?: number}> = ({
  src, at, volume = 0.6, dur = 90,
}) => (
  <Sequence from={at} durationInFrames={dur} layout="none">
    <Audio src={staticFile(`audio/${src}`)} volume={volume} />
  </Sequence>
);

/** A few quick typewriter clicks (for headings / case notes). */
export const TypeClicks: React.FC<{at: number; n?: number; gap?: number; volume?: number}> = ({
  at, n = 4, gap = 5, volume = 0.4,
}) => (
  <>
    {Array.from({length: n}).map((_, i) => (
      <Sfx key={i} src="sfx_type.mp3" at={at + i * gap} volume={volume} dur={20} />
    ))}
  </>
);

/** Low ambient drone bed, looped across the whole part. */
export const DroneBed: React.FC<{durationInFrames: number; volume?: number}> = ({
  durationInFrames, volume = 0.09,
}) => (
  <Loop durationInFrames={144} layout="none">
    <Audio src={staticFile('audio/sfx_drone.mp3')} volume={volume} />
  </Loop>
);
