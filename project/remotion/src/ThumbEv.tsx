import {AbsoluteFill, Img, staticFile} from 'remotion';

// 16:9 thumbnail — US flag bg + rail map overlay + Metroliner (right) + Amtrak logo (left),
// dark retro-cyber / synthwave grade.
export const ThumbEv: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f'}}>
      {/* 1 — US flag, full bleed, darkened */}
      <Img src={staticFile('photos/usflag.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'saturate(1.15) contrast(1.1) brightness(0.42)'}} />

      {/* 2 — rail map over the flag, glowing cyan lines */}
      <AbsoluteFill>
        <Img src={staticFile('maps/railmap1871.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', mixBlendMode: 'screen', opacity: 0.4, filter: 'grayscale(1) brightness(1.4) contrast(1.3) sepia(1) hue-rotate(150deg) saturate(3)'}} />
      </AbsoluteFill>

      {/* 3 — synthwave duotone + bloom */}
      <AbsoluteFill style={{background: 'linear-gradient(120deg, rgba(255,28,170,0.55) 0%, rgba(90,20,180,0.4) 50%, rgba(0,180,255,0.5) 100%)', mixBlendMode: 'overlay', opacity: 0.6}} />
      <AbsoluteFill style={{background: 'radial-gradient(130% 90% at 50% 55%, transparent 28%, rgba(120,0,190,0.7) 100%)', mixBlendMode: 'screen', opacity: 0.6}} />

      {/* bottom neon horizon grid */}
      <AbsoluteFill style={{top: 'auto', bottom: 0, height: 340, backgroundImage: 'repeating-linear-gradient(90deg, rgba(0,235,255,0.6) 0px, rgba(0,235,255,0.6) 2px, transparent 2px, transparent 78px)', maskImage: 'linear-gradient(to top, black, transparent)', WebkitMaskImage: 'linear-gradient(to top, black, transparent)', mixBlendMode: 'screen', opacity: 0.22}} />

      {/* 4 — Metroliner entering from the right, ~right half */}
      <Img
        src={staticFile('cutouts/metroliner_crop.png')}
        style={{position: 'absolute', right: -60, bottom: 150, width: 1180, filter: 'saturate(1.3) contrast(1.12) brightness(0.92) drop-shadow(0 0 26px rgba(0,225,255,0.55)) drop-shadow(0 18px 30px rgba(0,0,0,0.8))'}}
      />

      {/* 5 — Amtrak logo, large on the left, neon glow */}
      <Img
        src={staticFile('logo/amtrak.svg')}
        style={{position: 'absolute', left: 80, top: 420, width: 640, filter: 'drop-shadow(0 0 22px rgba(255,40,170,0.85)) drop-shadow(0 0 10px rgba(0,220,255,0.8))'}}
      />

      {/* scanlines + vignette */}
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.26) 0px, rgba(0,0,0,0.26) 1px, transparent 1px, transparent 3px)', mixBlendMode: 'multiply', opacity: 0.5}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 420px rgba(3,0,10,0.98)'}} />
    </AbsoluteFill>
  );
};
