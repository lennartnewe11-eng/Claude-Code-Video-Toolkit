import {
  AbsoluteFill,
  interpolate,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {PlaceholderBG} from './PlaceholderBG';

/**
 * One cut. Renders real footage from public/footage when `src` is given,
 * otherwise an animated themed placeholder so the comp always renders.
 * `punch` adds a short scale+blur "speed ramp" on entry for the fast phase.
 */
export const Clip: React.FC<{
  src?: string; // filename inside public/footage
  colors: [string, string];
  placeholderLabel?: string;
  punch?: boolean;
  sepia?: boolean;
  slowZoom?: boolean;
}> = ({src, colors, placeholderLabel, punch, sepia, slowZoom}) => {
  const frame = useCurrentFrame();

  const blur = punch
    ? interpolate(frame, [0, 6], [14, 0], {extrapolateRight: 'clamp'})
    : 0;
  const entryScale = punch
    ? interpolate(frame, [0, 8], [1.25, 1.08], {extrapolateRight: 'clamp'})
    : 1.08;
  const zoom = slowZoom
    ? interpolate(frame, [0, 120], [1.05, 1.18], {extrapolateRight: 'extend'})
    : entryScale;

  return (
    <AbsoluteFill
      style={{
        overflow: 'hidden',
        filter: `${sepia ? 'sepia(0.85) contrast(1.05) ' : ''}blur(${blur}px)`,
        transform: `scale(${slowZoom ? zoom : entryScale})`,
      }}
    >
      {src ? (
        <OffthreadVideo
          src={staticFile(`footage/${src}`)}
          muted
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
        />
      ) : (
        <PlaceholderBG colors={colors} label={placeholderLabel} drift={punch ? 200 : 80} />
      )}
    </AbsoluteFill>
  );
};
