import {AbsoluteFill, Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {Halftone, Stamp, RedNote} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, DroneBed} from './style/Sound';

const START = 620.262;
export const C3P14_DURATION = Math.round(30.9 * FPS);
const f = (s: number) => Math.round(s * FPS);
const DRONE = 0.06, STAMP = 0.5;
const LIGHT = '#f3efe4';
const BLUE = '#1f6fb0';

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 6, show[1] - 7, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Full-screen image. gray=0 → glossy colour (pitch); gray=1 → B/W grime (reality). */
const Shot: React.FC<{src: string; from: number; dur: number; gray?: number; bright?: boolean}> = ({src, from, dur, gray = 1, bright}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <ShotInner src={src} dur={dur} gray={gray} bright={bright} />
  </Sequence>
);
const ShotInner: React.FC<{src: string; dur: number; gray: number; bright?: boolean}> = ({src, dur, gray, bright}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 6, dur - 7, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.05, 1.14]);
  return (
    <AbsoluteFill style={{backgroundColor: bright ? '#dfe7ee' : '#000', opacity: io}}>
      <Img src={staticFile(`photos/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: gray ? 'grayscale(1) contrast(1.16) brightness(0.95)' : 'saturate(1.08) contrast(1.03)'}} />
      {gray ? (
        <>
          <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.35}} />
          <AbsoluteFill style={{boxShadow: 'inset 0 0 300px rgba(0,0,0,0.9)'}} />
        </>
      ) : (
        <AbsoluteFill style={{boxShadow: 'inset 0 0 220px rgba(255,255,255,0.25)'}} />
      )}
    </AbsoluteFill>
  );
};

/** Clean glossy pitch card. */
const PitchCard: React.FC<{label: string; value: string; x: number; y: number; at: number; w?: number}> = ({label, value, x, y, at, w = 420}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ty = interpolate(frame - at, [0, 7], [24, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, opacity: o, transform: `translateY(${ty}px)`, background: '#ffffff', borderRadius: 10, padding: '18px 22px', boxShadow: '0 12px 30px rgba(0,0,0,0.28)', borderTop: `5px solid ${BLUE}`}}>
      <div style={{fontFamily: mono, fontWeight: 700, fontSize: 18, letterSpacing: '0.14em', textTransform: 'uppercase', color: BLUE}}>{label}</div>
      <div style={{fontFamily: cond, fontWeight: 700, fontSize: 58, lineHeight: 1.0, color: '#10243a', marginTop: 4}}>{value}</div>
    </div>
  );
};

/** Reality stat row with a red ✗/figure, builds in. */
const Stat: React.FC<{mark: string; text: string; x: number; y: number; at: number}> = ({mark, text, x, y, at}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o, display: 'flex', alignItems: 'center'}}>
      <span style={{fontFamily: cond, fontWeight: 700, fontSize: 64, color: EV.red, marginRight: 22, minWidth: 90, textShadow: '0 2px 12px rgba(0,0,0,0.8)'}}>{mark}</span>
      <span style={{fontFamily: cond, fontWeight: 700, fontSize: 54, color: LIGHT, textTransform: 'uppercase', textShadow: '0 2px 14px rgba(0,0,0,0.85)'}}>{text}</span>
    </div>
  );
};

export const Ch3P14Ev: React.FC = () => {
  const frame = useCurrentFrame();
  // cost explosion bar (172)
  const costP = interpolate(frame, [f(28.6), f(30.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {/* ===== PITCH (bright, colour) ===== */}
      <Shot src="cahsr_render.jpg" from={0} dur={f(17.1)} gray={0} bright />
      <Group show={[0, f(17.1)]}>
        <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: '#10243a', background: '#ffffffcc', padding: '6px 14px', borderRadius: 6}}>DER PITCH · 2008</div>
        <div style={{position: 'absolute', left: 80, top: 150, opacity: interpolate(frame, [f(0.4), f(1.1)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 96, lineHeight: 0.95, color: '#ffffff', textShadow: '0 3px 20px rgba(0,0,0,0.5)'}}>California</div>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 96, lineHeight: 0.95, color: '#ffffff', textShadow: '0 3px 20px rgba(0,0,0,0.5)'}}>High-Speed Rail</div>
        </div>
        <div style={{position: 'absolute', left: 84, top: 350, fontFamily: mono, fontSize: 26, color: '#ffffff', textShadow: '0 2px 10px rgba(0,0,0,0.6)', opacity: interpolate(frame, [f(3.8), f(4.5)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>2008 — per Volksentscheid bewilligt ✓</div>

        <PitchCard label="Versprochene Kosten" value="$33 Mrd." x={84} y={560} at={f(7.6)} />
        <PitchCard label="Verbindung" value="San Francisco ↔ LA" x={84} y={760} at={f(9.0)} w={560} />
        <PitchCard label="Fertig bis" value="2020" x={540} y={560} at={f(10.4)} w={300} />
      </Group>

      {/* ===== REALITY (B/W grime) ===== */}
      <Shot src="cahsr_cedar.jpg" from={f(16.8)} dur={f(4.2)} gray={1} />
      <Shot src="cahsr_drone.jpg" from={f(20.8)} dur={f(7.0)} gray={1} />
      <Shot src="cahsr_wasco.jpg" from={f(27.6)} dur={C3P14_DURATION - f(27.6)} gray={1} />
      <Halftone opacity={0.08} size={7} />

      {/* 170 — the reality 2026 */}
      <Group show={[f(16.8), f(20.9)]}>
        <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>DIE WIRKLICHKEIT · 2026</div>
        <div style={{position: 'absolute', left: 80, top: 300, opacity: interpolate(frame, [f(17.2), f(17.9)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 92, lineHeight: 0.95, color: LIGHT, textTransform: 'uppercase', textShadow: '0 2px 18px rgba(0,0,0,0.85)'}}>Die Wirklichkeit</div>
          <div style={{position: 'relative', marginTop: 6}}>
            <span style={{position: 'absolute', left: -6, top: '16%', height: '70%', width: 240, background: EV.red, transform: 'skewX(-6deg)'}} />
            <span style={{position: 'relative', fontFamily: cond, fontWeight: 700, fontSize: 92, color: LIGHT, textTransform: 'uppercase', textShadow: '0 2px 18px rgba(0,0,0,0.85)'}}>2026</span>
          </div>
        </div>
        <div style={{position: 'absolute', left: 84, bottom: 60, fontFamily: mono, fontSize: 22, color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>Central Valley — im Bau</div>
      </Group>

      {/* 171 — the damning facts */}
      <Group show={[f(20.7), f(28.0)]}>
        <Stat mark="0 km" text="in Betrieb" x={90} y={300} at={f(21.0)} />
        <Stat mark="0" text="fertige Züge" x={90} y={420} at={f(22.4)} />
        <Stat mark="$18 Mrd" text="bereits ausgegeben" x={90} y={540} at={f(24.0)} />
        <Stamp text="nichts fährt" x={1430} y={760} size={52} at={f(25.8)} rot={-7} />
      </Group>

      {/* 172 — the cost explosion */}
      <Group show={[f(27.6), C3P14_DURATION]}>
        <div style={{position: 'absolute', left: 84, top: 150, fontFamily: cond, fontWeight: 700, fontSize: 64, color: LIGHT, textTransform: 'uppercase', textShadow: '0 2px 16px rgba(0,0,0,0.85)'}}>Kosten heute</div>
        {/* bar from 33 to 120+ */}
        <div style={{position: 'absolute', left: 90, top: 320, width: 1400, height: 70, border: `3px solid ${LIGHT}`, background: 'rgba(0,0,0,0.35)'}}>
          <div style={{height: '100%', width: `${(33 / 120) * 100}%`, background: '#9a8f78', display: 'flex', alignItems: 'center', paddingLeft: 16, fontFamily: cond, fontWeight: 700, fontSize: 36, color: '#10243a'}}>$33 Mrd. (Versprechen)</div>
        </div>
        <div style={{position: 'absolute', left: 90, top: 420, width: 1400 * costP, height: 70, background: EV.red, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', paddingRight: 18, fontFamily: cond, fontWeight: 700, fontSize: 40, color: LIGHT, overflow: 'hidden'}}>{costP > 0.6 ? '> $120 Mrd.' : ''}</div>
        <RedNote text="das Vierfache" x={1300} y={540} size={52} at={f(29.8)} rot={-5} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P14_DURATION} volume={DRONE} />
      <Sfx src="riser.mp3" at={f(0.2)} volume={0.22} />
      <Sfx src="impact.mp3" at={f(16.8)} volume={0.5} />
      <Sfx src="whoosh.mp3" at={f(20.8)} volume={0.35} />
      <Sfx src="sfx_stamp.mp3" at={f(25.8)} volume={STAMP} />
      <Sfx src="whoosh.mp3" at={f(27.6)} volume={0.35} />
      <Sfx src="impact.mp3" at={f(28.6)} volume={0.4} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
