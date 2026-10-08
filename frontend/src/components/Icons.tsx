// Small hand-drawn SVG icons for the top-bar stats (flame, gem, heart, bolt).
type P = { size?: number; grey?: boolean };

export const Flame = ({ size = 26, grey }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-label="streak">
    <path d="M12.5 1.5c.6 3.2 5.5 5.6 5.5 11a6 6 0 0 1-12 0c0-2.4 1.1-3.9 2.3-5 .1 1.8.9 2.9 2 3.3C9.4 7.4 10 4 12.5 1.5z" fill={grey ? "#afafaf" : "#ff9600"} />
    <path d="M12 12c.4 1.5 2.8 2.4 2.8 4.8a2.8 2.8 0 0 1-5.6 0c0-1.5.8-2.3 1.6-3 .2 1 .6 1.4 1.1 1.5-.1-1.100 0-2.300.1-3.300z" fill={grey ? "#cfcfcf" : "#ffc800"} />
  </svg>
);

export const Gem = ({ size = 26 }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-label="gems">
    <path d="M6 3h12l4 6-10 13L2 9z" fill="#1cb0f6" />
    <path d="M6 3l-4 6h20l-4-6z" fill="#84d8ff" />
    <path d="M9 9l3 13 3-13z" fill="#1899d6" />
  </svg>
);

export const Heart = ({ size = 26, grey }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-label="hearts">
    <path d="M12 21.5C5 16.300 2 12.800 2 8.800 2 6 4.200 4 6.800 4c2 0 3.600 1.100 5.200 3.100C13.600 5.100 15.200 4 17.200 4 19.800 4 22 6 22 8.800c0 4-3 7.500-10 12.700z" fill={grey ? "#afafaf" : "#ff4b4b"} />
    <path d="M6.500 7.200c-1 .3-1.700 1.200-1.700 2.300" stroke="#fff" strokeOpacity=".5" strokeWidth="1.600" strokeLinecap="round" fill="none" />
  </svg>
);

export const Bolt = ({ size = 26 }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-label="xp">
    <path d="M13.500 1 4 14h6.500L9.500 23 20 9.500h-6.500z" fill="#ffc800" stroke="#e5a800" strokeWidth="1" strokeLinejoin="round" />
  </svg>
);

export const Chest = ({ size = 40 }: P) => <span style={{ fontSize: size }}>🎁</span>;
