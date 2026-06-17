import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, body, display} from './theme';

export interface Token {
  t: string;
  w?: 'reg' | 'bold' | 'italic' | 'boldItalic';
  display?: boolean; // huge Didone caps word
  size?: number; // override font size (px)
  accent?: boolean; // oxblood colour
  br?: boolean; // line break AFTER this token
}

/**
 * Word-by-word editorial reveal. Each token springs up with a stagger and
 * carries its own weight/style/size — mirroring the reference (mixed
 * regular / bold / italic / huge display caps within one sentence).
 */
export const EditorialText: React.FC<{
  tokens: Token[];
  cx: number; // centre x in 1920x1080
  cy: number; // centre y
  width?: number;
  baseSize?: number;
  align?: 'left' | 'center';
  delay?: number;
  stagger?: number;
}> = ({tokens, cx, cy, width = 900, baseSize = 52, align = 'center', delay = 0, stagger = 4}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <div
      style={{
        position: 'absolute',
        left: cx,
        top: cy,
        width,
        transform: 'translate(-50%, -50%)',
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.14em 0.36em',
        alignItems: 'baseline',
        justifyContent: align === 'center' ? 'center' : 'flex-start',
        fontFamily: body,
        color: COLORS.ink,
        lineHeight: 1.05,
      }}
    >
      {tokens.map((tok, i) => {
        const s = spring({
          frame: frame - delay - i * stagger,
          fps,
          config: {damping: 16, stiffness: 150},
        });
        const y = interpolate(s, [0, 1], [28, 0]);
        const italic = tok.w === 'italic' || tok.w === 'boldItalic';
        const bold = tok.w === 'bold' || tok.w === 'boldItalic';
        const size = tok.size ?? (tok.display ? baseSize * 2.6 : baseSize);
        return (
          <span key={i} style={{display: 'contents'}}>
            <span
              style={{
                display: 'inline-block',
                transform: `translateY(${y}px)`,
                opacity: s,
                fontFamily: tok.display ? display : body,
                fontWeight: tok.display ? 800 : bold ? 700 : 400,
                fontStyle: italic ? 'italic' : 'normal',
                fontSize: size,
                lineHeight: tok.display ? 0.92 : 1.05,
                letterSpacing: tok.display ? '0.01em' : 0,
                color: tok.accent ? COLORS.accent : COLORS.ink,
                textTransform: tok.display ? 'uppercase' : 'none',
              }}
            >
              {tok.t}
            </span>
            {tok.br ? <span style={{flexBasis: '100%', height: 0}} /> : null}
          </span>
        );
      })}
    </div>
  );
};
