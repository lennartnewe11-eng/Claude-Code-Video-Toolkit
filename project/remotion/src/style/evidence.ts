import {loadFont as loadMono} from '@remotion/google-fonts/CourierPrime';
import {loadFont as loadCond} from '@remotion/google-fonts/Oswald';

export const EV = {
  paper: '#e9e4d6',
  ink: '#17140f',
  inkSoft: '#5d574c',
  red: '#b3271c', // marker red
  yellow: '#ffd83a', // highlighter
  tape: 'rgba(214,201,160,0.72)',
};

export const mono = loadMono('normal', {
  weights: ['400', '700'],
  subsets: ['latin'],
  ignoreTooManyRequestsWarning: true,
}).fontFamily;

export const cond = loadCond('normal', {
  weights: ['500', '700'],
  subsets: ['latin'],
  ignoreTooManyRequestsWarning: true,
}).fontFamily;

export const PHOTO_SHADOW = '6px 10px 14px rgba(20,16,10,0.32)';
