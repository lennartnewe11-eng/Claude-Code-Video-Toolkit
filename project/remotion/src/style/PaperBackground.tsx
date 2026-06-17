import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {COLORS} from './theme';

/** Cream paper texture with a very slow drift + soft vignette. */
export const PaperBackground: React.FC = () => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 300], [1.04, 1.09], {
    extrapolateRight: 'extend',
  });
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.paper}}>
      <Img
        src={staticFile('bg/paper.jpg')}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${scale})`,
        }}
      />
      <AbsoluteFill
        style={{
          boxShadow: 'inset 0 0 320px rgba(120,108,86,0.35)',
        }}
      />
    </AbsoluteFill>
  );
};
