import {
  AbsoluteFill,
  Img,
  interpolate,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {PlaceholderBG} from './PlaceholderBG';

const isImage = (src: string) => /\.(jpg|jpeg|png|webp)$/i.test(src);

/**
 * One cut. Renders real footage from public/footage:
 *  - video  -> OffthreadVideo, with an optional `punch` speed-ramp on entry
 *  - image  -> Img with a continuous Ken-Burns push (so stills still move)
 * Falls back to an animated themed placeholder if `src` is missing.
 */
export const Clip: React.FC<{
  src?: string;
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

  // Video entry scale (speed ramp) vs. continuous Ken-Burns for stills.
  const videoScale = punch
    ? interpolate(frame, [0, 8], [1.25, 1.08], {extrapolateRight: 'clamp'})
    : 1.08;
  const kenBurns = interpolate(frame, [0, 150], [1.06, 1.2], {
    extrapolateRight: 'extend',
  });
  const panX = slowZoom
    ? interpolate(frame, [0, 150], [0, -40], {extrapolateRight: 'extend'})
    : 0;

  const filter = `${sepia ? 'sepia(0.8) contrast(1.05) brightness(0.95) ' : ''}blur(${blur}px)`;

  if (!src) {
    return (
      <AbsoluteFill style={{filter}}>
        <PlaceholderBG colors={colors} label={placeholderLabel} drift={punch ? 200 : 80} />
      </AbsoluteFill>
    );
  }

  if (isImage(src)) {
    return (
      <AbsoluteFill style={{overflow: 'hidden', backgroundColor: '#000'}}>
        <Img
          src={staticFile(`footage/${src}`)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${kenBurns}) translateX(${panX}px)`,
            filter,
          }}
        />
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill
      style={{
        overflow: 'hidden',
        filter,
        transform: `scale(${slowZoom ? kenBurns : videoScale})`,
      }}
    >
      <OffthreadVideo
        src={staticFile(`footage/${src}`)}
        muted
        style={{width: '100%', height: '100%', objectFit: 'cover'}}
      />
    </AbsoluteFill>
  );
};
