const outputs = [
  { label: "LinkedIn Post", y: 40 },
  { label: "Sarcastic Caption", y: 110 },
  { label: "Blog Article", y: 180 },
  { label: "X Thread", y: 250 },
  { label: "Press Release", y: 320 },
  { label: "Meeting Notes", y: 390 },
];

/**
 * The signature visual: one source node (the video) branches, via a DNA-like
 * strand, into every downstream content form — visualizing "Understand Once,
 * Transform Everywhere".
 */
export function DnaBranchHero() {
  return (
    <svg
      viewBox="0 0 640 430"
      className="w-full h-auto max-w-xl mx-auto"
      role="img"
      aria-label="A single video branching into many pieces of generated content"
    >
      <defs>
        <linearGradient id="strandGradient" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#7C5CFC" />
          <stop offset="100%" stopColor="#22D3C8" />
        </linearGradient>
      </defs>

      {/* source node */}
      <g>
        <circle cx="60" cy="215" r="34" fill="#12161F" stroke="#7C5CFC" strokeWidth="2" />
        <circle cx="60" cy="215" r="6" fill="#7C5CFC" className="animate-pulseGlow" />
        <text x="60" y="270" textAnchor="middle" className="fill-muted text-[11px] font-mono">
          your video
        </text>
      </g>

      {/* branch strands */}
      {outputs.map((o, i) => (
        <path
          key={o.label}
          d={`M 94 215 C 220 215, 220 ${o.y}, 340 ${o.y}`}
          fill="none"
          stroke="url(#strandGradient)"
          strokeWidth="1.5"
          strokeOpacity="0.55"
          className="dna-strand-line"
          style={{ animationDelay: `${i * 90}ms` }}
        />
      ))}

      {/* output pills */}
      {outputs.map((o, i) => (
        <g key={o.label} style={{ opacity: 0.95 }}>
          <rect
            x="344"
            y={o.y - 16}
            rx="16"
            ry="16"
            width="200"
            height="32"
            fill="#181D29"
            stroke="#232938"
          />
          <circle cx="364" cy={o.y} r="4" fill={i % 2 === 0 ? "#7C5CFC" : "#22D3C8"} />
          <text x="380" y={o.y + 4} className="fill-foreground text-[12px] font-mono">
            {o.label}
          </text>
        </g>
      ))}
    </svg>
  );
}
