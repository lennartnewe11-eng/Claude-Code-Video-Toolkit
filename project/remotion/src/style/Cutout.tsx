import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {CUTOUT_SHADOW} from './theme';

type Entrance = 'drive' | 'drop' | 'pop' | 'slideR';

/**
 * A collage cut-out object. Positioned by its CENTRE at (cx, cy) in the
 * 1920x1080 canvas, sized by width in px. Enters with a chosen animation and
 * then gently floats (idle) so the collage feels alive.
 */
export const Cutout: React.FC<{
  src: string; // filename in public/cutouts
  cx: number;
  cy: number;
  width: number;
  entrance?: Entrance;
  delay?: number; // frames
  rotate?: number; // resting rotation (deg)
  flip?: boolean;
}> = ({src, cx, cy, width, entrance = 'pop', delay = 0, rotate = 0, flip}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const f = frame - delay;

  const s = spring({frame: f, fps, config: {damping: 14, stiffness: 130}});

  let tx = 0;
  let ty = 0;
  let rot = rotate;
  let scale = 1;
  let opacity = interpolate(f, [0, 6], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  if (entrance === 'drive') {
    tx = interpolate(s, [0, 1], [-width * 1.4, 0]);
  } else if (entrance === 'slideR') {
    tx = interpolate(s, [0, 1], [width * 1.4, 0]);
  } else if (entrance === 'drop') {
    ty = interpolate(s, [0, 1], [-700, 0]);
    rot = interpolate(s, [0, 1], [rotate - 18, rotate]);
  } else {
    scale = interpolate(s, [0, 1], [0.6, 1]);
  }

  // gentle idle float after settling
  const idle = Math.sin((frame + delay) / 26) * 4;

  return (
    <Img
      src={staticFile(`cutouts/${src}`)}
      style={{
        position: 'absolute',
        left: cx,
        top: cy,
        width,
        transform: `translate(-50%, -50%) translate(${tx}px, ${ty + idle}px) rotate(${rot}deg) scale(${scale}) ${flip ? 'scaleX(-1)' : ''}`,
        filter: CUTOUT_SHADOW,
        opacity,
      }}
    />
  );
};
