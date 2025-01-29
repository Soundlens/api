interface InfoTooltipProps {
  title: string;
  description: string;
}

export default function InfoTooltip({ title, description }: InfoTooltipProps) {
  return (
    <div className="group relative inline-block">
      <div className="cursor-help ml-1 text-gray-400 hover:text-gray-300">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.94 6.94a.75.75 0 11-1.061-1.061 3 3 0 112.871 5.026v.345a.75.75 0 01-1.5 0v-.5c0-.72.57-1.172 1.081-1.287A1.5 1.5 0 108.94 6.94zM10 15a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
        </svg>
      </div>
      <div className="opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 absolute z-10 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-gray-900 rounded-lg shadow-xl">
        <div className="text-sm font-medium text-white mb-1">{title}</div>
        <div className="text-xs text-gray-300">{description}</div>
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>
      </div>
    </div>
  );
} 