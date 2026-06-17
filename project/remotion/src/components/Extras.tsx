import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const FONT = '"Inter", "Helvetica Neue", Arial, sans-serif';

/** Quick white flash at a cut to sell the whoosh. */
export const FlashCut: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 4], [0.6, 0], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{backgroundColor: '#fff', opacity: o}} />;
};

/** The hard-break reveal: black slams in, then a huge "USA" eases up. */
export const BreakReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - 6, fps, config: {damping: 18, stiffness: 90}});
  const y = interpolate(s, [0, 1], [40, 0]);
  const scale = interpolate(s, [0, 1], [1.3, 1]);
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <div
        style={{
          transform: `translateY(${y}px) scale(${scale})`,
          opacity: s,
          fontFamily: FONT,
          fontWeight: 900,
          fontSize: 320,
          letterSpacing: 16,
          color: '#fff',
        }}
      >
        USA
      </div>
    </AbsoluteFill>
  );
};

/** Final title card. */
export const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame, fps, config: {damping: 20, stiffness: 110}});
  const line2 = spring({frame: frame - 8, fps, config: {damping: 20}});
  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
        gap: 20,
        background:
          'radial-gradient(circle at 50% 40%, #16161f 0%, #050507 70%)',
      }}
    >
      <div
        style={{
          opacity: s,
          transform: `translateY(${interpolate(s, [0, 1], [40, 0])}px)`,
          fontFamily: FONT,
          fontWeight: 900,
          fontSize: 110,
          color: '#fff',
          textAlign: 'center',
          lineHeight: 1.05,
        }}
      >
        Wie Amerika
        <br />
        die Bahn verlor
      </div>
      <div
        style={{
          opacity: line2,
          fontFamily: FONT,
          fontWeight: 600,
          fontSize: 40,
          color: '#ff3b30',
          letterSpacing: 6,
        }}
      >
        EINE GESCHICHTE DES NIEDERGANGS
      </div>
    </AbsoluteFill>
  );
};
