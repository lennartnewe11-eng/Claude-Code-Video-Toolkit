import {AbsoluteFill, Img, staticFile} from 'remotion';

// 16:9 thumbnail — US flag bg + rail map overlay + Metroliner (right) + Amtrak logo (left),
// dark retro-cyber / synthwave grade.
export const ThumbEv: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f'}}>
      {/* 1 — US flag, full bleed (fills the whole background), darkened */}
      <Img src={staticFile('photos/usflag_full.svg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'saturate(1.1) contrast(1.05) brightness(0.5)'}} />

      {/* 2 — rail map over the flag, glowing cyan lines */}
      <AbsoluteFill>
        <Img src={staticFile('maps/railmap1871.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', mixBlendMode: 'screen', opacity: 0.4, filter: 'grayscale(1) brightness(1.4) contrast(1.3) sepia(1) hue-rotate(150deg) saturate(3)'}} />
      </AbsoluteFill>

      {/* 3 — synthwave duotone + bloom (v2 colors) */}
      <AbsoluteFill style={{background: 'linear-gradient(120deg, rgba(255,28,170,0.55) 0%, rgba(90,20,180,0.4) 50%, rgba(0,180,255,0.5) 100%)', mixBlendMode: 'overlay', opacity: 0.6}} />
      <AbsoluteFill style={{background: 'radial-gradient(130% 90% at 50% 55%, transparent 28%, rgba(120,0,190,0.7) 100%)', mixBlendMode: 'screen', opacity: 0.6}} />

      {/* bottom neon horizon grid */}
      <AbsoluteFill style={{top: 'auto', bottom: 0, height: 380, backgroundImage: 'repeating-linear-gradient(90deg, rgba(0,235,255,0.7) 0px, rgba(0,235,255,0.7) 2px, transparent 2px, transparent 72px)', maskImage: 'linear-gradient(to top, black, transparent)', WebkitMaskImage: 'linear-gradient(to top, black, transparent)', mixBlendMode: 'screen', opacity: 0.34}} />

      {/* 4 — Metroliner entering from the right, fills the right side, tall */}
      <Img
        src={staticFile('cutouts/metroliner_crop.png')}
        style={{position: 'absolute', right: -150, bottom: 36, width: 1360, filter: 'saturate(1.3) contrast(1.12) brightness(0.95) drop-shadow(0 0 28px rgba(0,225,255,0.55)) drop-shadow(0 18px 34px rgba(0,0,0,0.85))'}}
      />

      {/* 5 — Amtrak logo, large on the left, neon glow */}
      <Img
        src={staticFile('logo/amtrak.svg')}
        style={{position: 'absolute', left: 80, top: 420, width: 640, filter: 'drop-shadow(0 0 22px rgba(255,40,170,0.85)) drop-shadow(0 0 10px rgba(0,220,255,0.8))'}}
      />

      {/* scanlines (strong) + vignette */}
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.42) 0px, rgba(0,0,0,0.42) 1px, transparent 1px, transparent 3px)', mixBlendMode: 'multiply', opacity: 0.7}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 420px rgba(3,0,10,0.98)'}} />
    </AbsoluteFill>
  );
};
