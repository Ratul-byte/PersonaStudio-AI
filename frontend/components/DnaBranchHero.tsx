"use client";

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
    <>
      {/* 
        This local style block overrides the hardcoded CSS limits. 
        It ensures the line draws 100% of the way, regardless of how long the curve is. 
      */}
      <style>{`
        @keyframes drawFullStrand {
          to { stroke-dashoffset: 0; }
        }
      `}</style>

      <svg
        viewBox="0 0 640 430"
        className="w-full h-auto max-w-xl mx-auto overflow-visible"
        role="img"
        aria-label="A single video branching into many pieces of generated content"
      >
        <defs>
          <linearGradient id="strandGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#7C5CFC" />
            <stop offset="100%" stopColor="#22D3C8" />
          </linearGradient>
        </defs>

        {/* Source node with hover scale */}
        <g className="transition-transform duration-500 ease-out hover:scale-105 origin-[60px_215px] cursor-pointer group">
          <circle cx="60" cy="215" r="34" fill="#12161F" stroke="#7C5CFC" strokeWidth="2" className="group-hover:stroke-accent transition-colors duration-300" />
          <circle cx="60" cy="215" r="6" fill="#7C5CFC" className="animate-pulseGlow group-hover:fill-accent transition-colors duration-300" />
          <text x="60" y="270" textAnchor="middle" className="fill-muted text-[11px] font-mono group-hover:fill-foreground transition-colors duration-300">
            your video
          </text>
        </g>

        {/* Branch strands drawing from left to right */}
        {outputs.map((o, i) => (
          <path
            key={`strand-${o.label}`}
            d={`M 94 215 C 220 215, 220 ${o.y}, 340 ${o.y}`}
            fill="none"
            stroke="url(#strandGradient)"
            strokeWidth="1.5"
            strokeOpacity="0.55"
            className="drop-shadow-md"
            pathLength="100" // Normalizes the physical length to exactly 100 units
            style={{
              strokeDasharray: 100,
              strokeDashoffset: 100,
              // The animation draws the line over 1 second, staggered per branch
              animation: `drawFullStrand 1s ease-out forwards ${200 + i * 100}ms`
            }}
          />
        ))}

        {/* Output pills with incoming arrowheads */}
        {outputs.map((o, i) => (
          <g 
            key={`output-${o.label}`} 
            className="animate-in fade-in zoom-in duration-500 fill-mode-both transition-transform hover:-translate-y-1 cursor-pointer origin-[444px_center]"
            // The box (and arrow) appears right as the line finishes drawing
            style={{ animationDelay: `${900 + (i * 100)}ms` }}
          >
            {/* The arrowhead connecting the line perfectly into the box */}
            <path 
              d={`M 335 ${o.y - 4} L 344 ${o.y} L 335 ${o.y + 4} Z`} 
              fill={i % 2 === 0 ? "#7C5CFC" : "#22D3C8"} 
              className="drop-shadow-md"
            />
            
            <rect
              x="344"
              y={o.y - 16}
              rx="16"
              ry="16"
              width="200"
              height="32"
              fill="#181D29"
              stroke="#232938"
              className="hover:stroke-accent transition-colors duration-300 shadow-xl"
            />
            <circle 
              cx="364" 
              cy={o.y} 
              r="4" 
              fill={i % 2 === 0 ? "#7C5CFC" : "#22D3C8"} 
              className="animate-pulseGlow"
            />
            <text x="380" y={o.y + 4} className="fill-foreground text-[12px] font-mono">
              {o.label}
            </text>
          </g>
        ))}
      </svg>
    </>
  );
}