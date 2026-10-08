// "Mitthu" - our own original orange tabby cat mascot ("mitthu" is a sweet pet name in Hindi and Punjabi).
// Three moods: happy (default), cheer (lesson complete) and sad (mistakes / quitting).
type Mood = "happy" | "sad" | "cheer";

export default function Mascot({ size = 120, mood = "happy", className = "" }: { size?: number; mood?: Mood; className?: string }) {
  const orange = "#ff9600", orangeD = "#e68600", cream = "#fff1d6", pink = "#ff7b9c", ink = "#1f2937";
  const fur = { fill: orange, stroke: orangeD, strokeWidth: 4, strokeLinejoin: "round" as const };
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" className={className} role="img" aria-label="Mitthu the cat">
      {/* tail */}
      <path d="M88 104 Q116 104 110 70" stroke={orangeD} strokeWidth="15" strokeLinecap="round" fill="none" />
      <path d="M88 104 Q116 104 110 70" stroke={orange} strokeWidth="8" strokeLinecap="round" fill="none" />
      <path d="M110 70 q-1 -4 0 -6" stroke={cream} strokeWidth="8" strokeLinecap="round" fill="none" />

      {/* body, belly and arms */}
      <ellipse cx="60" cy="88" rx="29" ry="26" {...fur} />
      <ellipse cx="60" cy="92" rx="16" ry="18" fill={cream} />
      {mood === "cheer" ? (
        <g {...fur}>
          <ellipse cx="29" cy="70" rx="8" ry="17" transform="rotate(-25 29 70)" />
          <ellipse cx="91" cy="70" rx="8" ry="17" transform="rotate(25 91 70)" />
        </g>
      ) : (
        <g {...fur}>
          <ellipse cx="33" cy="90" rx="8" ry="17" transform="rotate(8 33 90)" />
          <ellipse cx="87" cy="90" rx="8" ry="17" transform="rotate(-8 87 90)" />
        </g>
      )}
      {/* paws */}
      <ellipse cx="48" cy="112" rx="11" ry="6" fill={cream} stroke={orangeD} strokeWidth="3" />
      <ellipse cx="72" cy="112" rx="11" ry="6" fill={cream} stroke={orangeD} strokeWidth="3" />

      {/* ears */}
      <path d="M30 40 L27 9 L52 25z" {...fur} />
      <path d="M90 40 L93 9 L68 25z" {...fur} />
      <path d="M33 31 L32 17 L44 25z" fill={pink} />
      <path d="M87 31 L88 17 L76 25z" fill={pink} />

      {/* head */}
      <ellipse cx="60" cy="50" rx="35" ry="29" {...fur} />
      {/* tabby stripes */}
      <g stroke={orangeD} strokeWidth="3.500" strokeLinecap="round">
        <path d="M60 24 v9" /><path d="M50 26 l1 8" /><path d="M70 26 l-1 8" />
      </g>
      {/* muzzle + nose */}
      <ellipse cx="60" cy="60" rx="15" ry="11" fill={cream} />
      <path d="M55.500 54 h9 l-4.500 5.500z" fill={pink} stroke={pink} strokeWidth="1.500" strokeLinejoin="round" />

      {/* eyes */}
      {mood === "cheer" ? (
        <g stroke={ink} strokeWidth="3.500" strokeLinecap="round" fill="none">
          <path d="M38 50 q7 -9 14 0" /><path d="M68 50 q7 -9 14 0" />
        </g>
      ) : (
        <g>
          <ellipse cx="45" cy={mood === "sad" ? 50 : 48} rx="6" ry="7.500" fill={ink} />
          <ellipse cx="75" cy={mood === "sad" ? 50 : 48} rx="6" ry="7.500" fill={ink} />
          <circle cx="47" cy={mood === "sad" ? 47.500 : 45.500} r="2.400" fill="#fff" />
          <circle cx="77" cy={mood === "sad" ? 47.500 : 45.500} r="2.400" fill="#fff" />
        </g>
      )}
      {mood === "sad" && <path d="M36 44 L52 39 M84 44 L68 39" stroke={orangeD} strokeWidth="3.500" strokeLinecap="round" />}
      {mood === "sad" && <path d="M85 57 q4 8 0 12 q-4 -4 0 -12z" fill="#84d8ff" />}

      {/* mouth */}
      {mood === "happy" && <path d="M60 59.500 q-4 6 -9 2 M60 59.500 q4 6 9 2" stroke={ink} strokeWidth="2.500" strokeLinecap="round" fill="none" />}
      {mood === "cheer" && (
        <g>
          <path d="M52 62 Q60 78 68 62z" fill="#9b2c2c" stroke={ink} strokeWidth="2.500" strokeLinejoin="round" />
          <ellipse cx="60" cy="68" rx="4.500" ry="3" fill={pink} />
        </g>
      )}
      {mood === "sad" && <path d="M52 68 q8 -7 16 0" stroke={ink} strokeWidth="2.500" strokeLinecap="round" fill="none" />}

      {/* blush + whiskers */}
      <circle cx="32" cy="60" r="5" fill={pink} opacity=".45" /><circle cx="88" cy="60" r="5" fill={pink} opacity=".45" />
      <g stroke={orangeD} strokeWidth="2" strokeLinecap="round">
        <path d="M22 56 l-10 -3" /><path d="M22 62 l-11 1" /><path d="M98 56 l10 -3" /><path d="M98 62 l11 1" />
      </g>
    </svg>
  );
}
