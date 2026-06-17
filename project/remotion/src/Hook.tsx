import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import {SEGMENTS, sec, TITLE_FROM, HOOK_END, Segment, FPS} from './timeline';
import {FOOTAGE, COLORS} from './footage';
import {Clip} from './components/Clip';
import {CountryLabel, SpeedOverlay, GrowthCounter} from './components/Overlays';
import {KineticText} from './components/KineticText';
import {BreakReveal, TitleCard} from './components/Extras';
import {AudioLayer} from './audio/AudioLayer';

// Cross-dissolve length between clips. The break is a deliberate hard cut.
const OVERLAP = Math.round(0.3 * FPS); // ~9 frames

const SegmentBody: React.FC<{seg: Segment}> = ({seg}) => {
  const colors = COLORS[seg.id] ?? ['#0a0a12', '#16161f'];
  const src = FOOTAGE[seg.id];

  switch (seg.phase) {
    case 'race':
      return (
        <AbsoluteFill>
          <Clip src={src} colors={colors} placeholderLabel={seg.label} punch />
          {seg.label ? <CountryLabel text={seg.label} /> : null}
          {seg.id === 'china' ? (
            <GrowthCounter target={42000} suffix="km" />
          ) : seg.overlay ? (
            <SpeedOverlay text={seg.overlay} />
          ) : null}
        </AbsoluteFill>
      );

    case 'break':
      return (
        <AbsoluteFill style={{backgroundColor: '#000'}}>
          <Clip src={src} colors={colors} slowZoom />
          <AbsoluteFill style={{backgroundColor: '#000', opacity: 0.45}} />
          <BreakReveal />
        </AbsoluteFill>
      );

    case 'paradox': {
      const sepia = seg.id === 'best-network' || seg.id === 'squandered';
      const accent =
        seg.id === 'richest'
          ? 'reichste'
          : seg.id === 'squandered'
            ? 'verspielt'
            : undefined;
      return (
        <AbsoluteFill style={{backgroundColor: '#000'}}>
          <Clip src={src} colors={colors} sepia={sepia} slowZoom />
          <AbsoluteFill style={{backgroundColor: '#000', opacity: 0.4}} />
          <KineticText text={seg.text} accentWord={accent} fontSize={84} />
        </AbsoluteFill>
      );
    }

    case 'question':
      return (
        <AbsoluteFill
          style={{
            background:
              'radial-gradient(circle at 50% 45%, #16161f 0%, #050507 75%)',
          }}
        >
          <KineticText
            text={seg.text}
            accentWord={seg.id === 'how' ? 'sein?' : 'Bahn?'}
            fontSize={seg.id === 'how' ? 100 : 72}
          />
        </AbsoluteFill>
      );
  }
};

/** Wraps a segment with its cross-dissolve fade-in (0 = hard cut). */
const FadeIn: React.FC<{frames: number; children: React.ReactNode}> = ({
  frames,
  children,
}) => {
  const frame = useCurrentFrame();
  const opacity =
    frames <= 0 ? 1 : interpolate(frame, [0, frames], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  return <AbsoluteFill style={{opacity}}>{children}</AbsoluteFill>;
};

export const Hook: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {SEGMENTS.map((seg, i) => {
        const anchor = sec(seg.from);
        const nextAnchor =
          i + 1 < SEGMENTS.length ? sec(SEGMENTS[i + 1].from) : sec(HOOK_END);
        // The break slams in on a hard cut; everything else cross-dissolves.
        const fadeIn = i === 0 || seg.id === 'usa-break' ? 0 : OVERLAP;
        const from = anchor - fadeIn;
        // Extend past the next anchor so the incoming clip's dissolve always
        // has this one underneath — no black ever shows between cuts.
        const duration = nextAnchor - from + OVERLAP;
        return (
          <Sequence key={seg.id} from={from} durationInFrames={duration} name={seg.id}>
            <FadeIn frames={fadeIn}>
              <SegmentBody seg={seg} />
            </FadeIn>
          </Sequence>
        );
      })}

      {/* Title card overlaps the tail of the last question line */}
      <Sequence
        from={sec(TITLE_FROM)}
        durationInFrames={sec(HOOK_END) - sec(TITLE_FROM)}
        name="title"
      >
        <TitleCard />
      </Sequence>

      <AudioLayer />
    </AbsoluteFill>
  );
};
