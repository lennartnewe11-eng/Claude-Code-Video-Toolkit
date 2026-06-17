import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, body, display} from './theme';

/**
 * Schematic transcontinental rail line: an ink line draws across, station
 * dots pop in along it with small-caps labels. Visualises "crossing the land /
 * towns spring up along the line" without fiddly geography.
 */
export const RailLine: React.FC<{
  cx: number;
  cy: number;
  width: number;
  stations: {x: number; label: string}[]; // x in 0..1
  delay?: number;
  drawFrames?: number;
}> = ({cx, cy, width, stations, delay = 0, drawFrames = 40}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(frame - delay, [0, drawFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div style={{position: 'absolute', left: cx, top: cy, width, transform: 'translate(-50%,-50%)'}}>
      {/* the line */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: width * p,
          height: 5,
          background: COLORS.ink,
          // little cross-ties feel
          boxShadow: '0 0 0 1px rgba(26,23,20,0.15)',
        }}
      />
      {stations.map((st, i) => {
        const reach = st.x <= p; // dot appears once the line passes it
        const s = spring({
          frame: frame - delay - st.x * drawFrames,
          fps,
          config: {damping: 12, stiffness: 200},
        });
        const scale = reach ? s : 0;
        return (
          <div key={i} style={{position: 'absolute', left: width * st.x, top: 2}}>
            <div
              style={{
                position: 'absolute',
                width: 22,
                height: 22,
                borderRadius: '50%',
                background: i === stations.length - 1 ? COLORS.accent : COLORS.ink,
                border: '3px solid ' + COLORS.paper,
                transform: `translate(-50%,-50%) scale(${scale})`,
              }}
            />
            <div
              style={{
                position: 'absolute',
                top: i % 2 ? 22 : -54,
                transform: 'translateX(-50%)',
                opacity: scale,
                fontFamily: body,
                fontWeight: 700,
                fontSize: 26,
                letterSpacing: '0.16em',
                textTransform: 'uppercase',
                color: COLORS.ink,
                whiteSpace: 'nowrap',
              }}
            >
              {st.label}
            </div>
          </div>
        );
      })}
    </div>
  );
};

/** Big editorial count-up with a unit label underneath. */
export const Counter: React.FC<{
  target: number;
  unit: string;
  cx: number;
  cy: number;
  delay?: number;
  countFrames?: number;
}> = ({target, unit, cx, cy, delay = 0, countFrames = 55}) => {
  const frame = useCurrentFrame();
  const v = Math.round(
    interpolate(frame - delay, [0, countFrames], [0, target], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );
  const s = interpolate(frame - delay, [0, 10], [0.8, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%,-50%) scale(${s})`, textAlign: 'center'}}>
      <div style={{fontFamily: display, fontWeight: 900, fontSize: 240, lineHeight: 0.9, color: COLORS.ink}}>
        {v.toLocaleString('de-DE')}
      </div>
      <div style={{fontFamily: body, fontWeight: 700, fontSize: 46, letterSpacing: '0.3em', textTransform: 'uppercase', color: COLORS.accent}}>
        {unit}
      </div>
    </div>
  );
};

/** Two comparison bars that grow (USA dwarfs Europe). */
export const CompareBars: React.FC<{
  cx: number;
  cy: number;
  width: number;
  a: {label: string; frac: number};
  b: {label: string; frac: number};
  delay?: number;
}> = ({cx, cy, width, a, b, delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const g = spring({frame: frame - delay, fps, config: {damping: 18, stiffness: 80}});
  const Bar = (d: {label: string; frac: number}, color: string, i: number) => (
    <div style={{display: 'flex', alignItems: 'center', gap: 24, marginBottom: 28}}>
      <div style={{width: 230, textAlign: 'right', fontFamily: body, fontWeight: 700, fontSize: 34, color: COLORS.ink}}>
        {d.label}
      </div>
      <div style={{height: 56, width: width * d.frac * g, background: color}} />
    </div>
  );
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: 'translate(-50%,-50%)'}}>
      {Bar(a, COLORS.accent, 0)}
      {Bar(b, COLORS.olive, 1)}
    </div>
  );
};
