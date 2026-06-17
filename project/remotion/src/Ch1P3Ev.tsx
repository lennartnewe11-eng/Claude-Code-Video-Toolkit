import {AbsoluteFill, Audio, staticFile} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, TapedPhoto, BodyBlock, MapPlate, RouteLine, XMark, MapDot, RedNote, Stamp, Crosshair, Highlight} from './style/Evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 63.08;
export const P3EV_DURATION = Math.round(11.4 * FPS);
const f = (s: number) => Math.round(s * FPS);

// quieter SFX for this part
const PAPER = 0.3, DRAW = 0.3, STAMP = 0.5, TYPE = 0.22, DOT = 0.22, DRONE = 0.06;

/**
 * Chapter 1 · Part 3 (63.08–74.48) — the railroad opens the West.
 * Towns spring up along the line (dots pop on the 1871 rail map, Deadwood
 * boomtown), while a town with no connection is struck off (Bodie ghost town).
 */
export const Ch1P3Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />

      <TypeHeading text="Akte 01 — Das goldene Zeitalter" x={110} y={78} size={26} at={f(0.2)} />
      <TypeHeading text="Der Westen erwacht" x={110} y={132} size={22} at={f(0.8)} highlight />
      <Crosshair x={1850} y={70} at={f(1.6)} />

      {/* the 1871 railroad map */}
      <MapPlate src="railmap1871.jpg" cx={1300} cy={500} w={900} at={f(0.5)} rot={-1} />

      {/* drawn route pushing west + label */}
      <RouteLine points={[[1520, 470], [1330, 452], [1090, 480], [940, 500]]} at={f(1.5)} drawFrames={38} />
      <RedNote text="→ Der Westen" x={840} y={400} size={44} at={f(2.4)} rot={-4} />

      {/* towns spring up along the line */}
      <MapDot x={1520} y={470} label="Omaha" at={f(5.3)} />
      <MapDot x={1330} y={452} label="Cheyenne '67" at={f(5.7)} />
      <MapDot x={1090} y={480} label="Reno '68" at={f(6.1)} below />
      <MapDot x={940} y={500} label="Sacramento" at={f(6.5)} below />

      {/* boomtown photo, upper-left, connected to a town dot */}
      <TapedPhoto src="boomtown.jpg" cx={350} cy={430} w={430} rot={-3} at={f(5.3)} caption="Deadwood, 1876" />
      <RedNote text="Boomtown" x={350} y={210} size={46} at={f(5.9)} rot={-3} />
      <RouteLine points={[[565, 440], [950, 450], [1310, 452]]} at={f(6.6)} drawFrames={22} width={3} />

      {/* no connection -> wiped off the map */}
      <MapDot x={1200} y={660} label="ohne Bahn" at={f(8.6)} struck below />
      <XMark x={1200} y={660} at={f(8.9)} size={30} />
      <TapedPhoto src="ghosttown.jpg" cx={360} cy={800} w={400} rot={3} at={f(8.3)} caption="Bodie — verlassen" />
      <Stamp text="von der Landkarte" x={760} y={690} size={40} at={f(9.0)} rot={-7} />

      {/* case note */}
      <BodyBlock
        x={700} y={250} w={470} at={f(3.6)} size={19}
        lines={[
          'Ganze Städte entstehen aus dem Nichts —',
          'einzig, weil dort eine Bahnlinie verläuft.',
        ]}
      />

      <Highlight x={600} y={920} w={760} at={f(9.2)} h={26} />
      <Headline text="Anschluss — oder vergessen" x={600} y={907} size={74} at={f(9.3)} />

      {/* ── sound (quieter) ── */}
      <DroneBed durationInFrames={P3EV_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(0.5)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(1.5)} volume={DRAW} />
      <Sfx src="sfx_draw.mp3" at={f(5.3)} volume={DOT} />
      <Sfx src="sfx_draw.mp3" at={f(5.7)} volume={DOT} />
      <Sfx src="sfx_draw.mp3" at={f(6.1)} volume={DOT} />
      <Sfx src="sfx_draw.mp3" at={f(6.5)} volume={DOT} />
      <Sfx src="sfx_paper.mp3" at={f(5.3)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(6.6)} volume={DRAW} />
      <TypeClicks at={f(3.6)} n={4} gap={5} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(8.3)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(8.9)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(9.0)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(9.3)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
