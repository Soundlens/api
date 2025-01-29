export default function Logo({ className = "w-12 h-12" }: { className?: string }) {
  return (
    <svg 
      viewBox="0 0 100 100" 
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer Circle (Lens) */}
      <circle 
        cx="50" 
        cy="50" 
        r="45" 
        className="stroke-blue-400" 
        strokeWidth="4"
        strokeDasharray="8 4"
      />
      
      {/* Sound Wave Lines */}
      <path
        d="M30 50 Q 40 30, 50 50 T 70 50"
        className="stroke-violet-400"
        strokeWidth="4"
        strokeLinecap="round"
      />
      <path
        d="M25 50 Q 40 20, 50 50 T 75 50"
        className="stroke-blue-400 opacity-60"
        strokeWidth="3"
        strokeLinecap="round"
      />
      <path
        d="M35 50 Q 40 40, 50 50 T 65 50"
        className="stroke-violet-400 opacity-80"
        strokeWidth="3"
        strokeLinecap="round"
      />

      {/* Center Point */}
      <circle 
        cx="50" 
        cy="50" 
        r="4" 
        className="fill-blue-400"
      />
    </svg>
  );
} 