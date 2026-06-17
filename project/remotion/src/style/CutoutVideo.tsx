import {Easing, interpolate, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {CUTOUT_SHADOW} from './theme';

/**
 * An animated cut-out: a transparent (alpha) WebM of real footage, driven
 * across the frame. Meant to be placed inside a <Sequence> so the clip plays
 * from its start; x is animated by the local frame. When scaled large it
 * nearly fills the frame and works as a wipe transition.
 */
export const CutoutVideo: React.FC<{
  src: string; // filename in public/cutvid
  fromX: number;
  toX: number;
  y: number; // centre y
  width: number;
  durationFrames: number;
  rotate?: number;
  easing?: boolean;
}> = ({src, fromX, toX, y, width, durationFrames, rotate = 0, easing = true}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, durationFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: easing ? Easing.inOut(Easing.cubic) : Easing.linear,
  });
  const x = interpolate(p, [0, 1], [fromX, toX]);
  return (
    <OffthreadVideo
      src={staticFile(`cutvid/${src}`)}
      transparent
      muted
      style={{
        position: 'absolute',
        left: '50%',
        top: y,
        width,
        transform: `translate(-50%, -50%) translateX(${x}px) rotate(${rotate}deg)`,
        filter: CUTOUT_SHADOW,
      }}
    />
  );
};
