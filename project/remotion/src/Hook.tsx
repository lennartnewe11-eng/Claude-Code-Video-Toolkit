import {AbsoluteFill, Sequence} from 'remotion';
import {SEGMENTS, sec, TITLE_FROM, HOOK_END, Segment} from './timeline';
import {FOOTAGE, COLORS} from './footage';
import {Clip} from './components/Clip';
import {CountryLabel, SpeedOverlay, GrowthCounter} from './components/Overlays';
import {KineticText} from './components/KineticText';
import {FlashCut, BreakReveal, TitleCard} from './components/Extras';
import {AudioLayer} from './audio/AudioLayer';

const dur = (seg: Segment) => sec(seg.to) - sec(seg.from);

const SegmentView: React.FC<{seg: Segment}> = ({seg}) => {
  const colors = COLORS[seg.id] ?? ['#0a0a12', '#16161f'];
  const src = FOOTAGE[seg.id];

  switch (seg.phase) {
    case 'race':
      return (
        <AbsoluteFill>
          <Clip src={src} colors={colors} placeholderLabel={seg.label} punch />
          <FlashCut />
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
          <Clip src={src} colors={colors} placeholderLabel="" slowZoom />
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

export const Hook: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {SEGMENTS.map((seg) => (
        <Sequence
          key={seg.id}
          from={sec(seg.from)}
          durationInFrames={dur(seg)}
          name={seg.id}
        >
          <SegmentView seg={seg} />
        </Sequence>
      ))}

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
