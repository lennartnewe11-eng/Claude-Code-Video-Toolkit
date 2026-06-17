import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const FONT = '"Inter", "Helvetica Neue", Arial, sans-serif';

/**
 * Word-by-word kinetic typography. Each word springs up with a stagger.
 * Used in the "paradox" phase (richest country / biggest economy) and the
 * closing question.
 */
export const KineticText: React.FC<{
  text: string;
  color?: string;
  fontSize?: number;
  accentWord?: string; // word to highlight in red
}> = ({text, color = '#fff', fontSize = 96, accentWord}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const words = text.split(' ');
  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: '0 160px',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '0 24px',
          fontFamily: FONT,
          fontWeight: 900,
          fontSize,
          lineHeight: 1.1,
          textAlign: 'center',
        }}
      >
        {words.map((w, i) => {
          const delay = i * 3;
          const s = spring({
            frame: frame - delay,
            fps,
            config: {damping: 16, stiffness: 160},
          });
          const y = interpolate(s, [0, 1], [60, 0]);
          const isAccent =
            accentWord && w.replace(/[.,]/g, '') === accentWord;
          return (
            <span
              key={i}
              style={{
                display: 'inline-block',
                transform: `translateY(${y}px)`,
                opacity: s,
                color: isAccent ? '#ff3b30' : color,
                textShadow: '0 6px 30px rgba(0,0,0,0.55)',
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
