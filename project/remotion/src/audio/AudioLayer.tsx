import {Audio, Sequence, staticFile, interpolate} from 'remotion';
import {AUDIO} from './assets';
import {FPS, SEGMENTS, sec} from '../timeline';

const at = (id: string) => SEGMENTS.find((s) => s.id === id)!;

/**
 * The four-layer sound design, all anchored to the same transcript timecodes
 * as the picture:
 *   1. music bed — loud through the "race", cut to near-silence at the break,
 *      a low presence through the paradox, swelling back under the question.
 *   2. whooshes  — one on each fast cut (Japan/France/China entries).
 *   3. impact    — the hard break on "Und dann gibt es die USA." (14.65s).
 *   4. riser+boom — build under "Wie kann das sein?" and a final hit on title.
 */
export const AudioLayer: React.FC = () => {
  const breakF = sec(at('usa-break').from);
  const questionF = sec(at('how').from);

  return (
    <>
      {AUDIO.musicBed ? (
        <Audio
          src={staticFile(`audio/${AUDIO.musicBed}`)}
          volume={(f) =>
            // loud race → duck hard at the break → low under paradox → swell
            interpolate(
              f,
              [
                0,
                breakF - 4,
                breakF, // hard duck
                breakF + 12,
                questionF, // start swelling
                questionF + 70,
              ],
              [0.9, 0.9, 0.04, 0.18, 0.25, 0.8],
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
            )
          }
        />
      ) : null}

      {/* whooshes on the three race cuts */}
      {AUDIO.whoosh
        ? ['japan', 'france', 'china'].map((id) => (
            <Sequence key={id} from={sec(at(id).from) - 3} durationInFrames={FPS}>
              <Audio src={staticFile(`audio/${AUDIO.whoosh}`)} volume={0.8} />
            </Sequence>
          ))
        : null}

      {/* the break impact */}
      {AUDIO.impact ? (
        <Sequence from={breakF - 2} durationInFrames={2 * FPS}>
          <Audio src={staticFile(`audio/${AUDIO.impact}`)} volume={1} />
        </Sequence>
      ) : null}

      {/* riser under the question */}
      {AUDIO.riser ? (
        <Sequence from={questionF} durationInFrames={3 * FPS}>
          <Audio src={staticFile(`audio/${AUDIO.riser}`)} volume={0.7} />
        </Sequence>
      ) : null}

      {/* final boom on the title card */}
      {AUDIO.boom ? (
        <Sequence from={sec(33.6)} durationInFrames={2 * FPS}>
          <Audio src={staticFile(`audio/${AUDIO.boom}`)} volume={1} />
        </Sequence>
      ) : null}
    </>
  );
};
