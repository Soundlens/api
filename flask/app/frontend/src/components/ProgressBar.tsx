interface ProgressBarProps {
  progress: number;
  status: string;
  currentStep?: string;
  error?: string;
}

export default function ProgressBar({ progress, status, currentStep, error }: ProgressBarProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'processing':
        return 'bg-blue-500';
      case 'pending':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'failed':
        return '✕';
      case 'processing':
        return '⟳';
      case 'pending':
        return '⋯';
      default:
        return '⋯';
    }
  };

  return (
    <div className="w-full space-y-3">
      <div className="flex justify-between items-center text-sm">
        <div className="flex items-center gap-2">
          <span className={`
            ${status === 'processing' ? 'animate-spin' : ''} 
            ${getStatusColor().replace('bg-', 'text-')}
          `}>
            {getStatusIcon()}
          </span>
          <span className="text-gray-300">{currentStep || status}</span>
        </div>
        <span className="text-gray-400 font-mono">{progress}%</span>
      </div>
      
      <div className="relative w-full h-2 bg-gray-700 rounded-full overflow-hidden">
        {/* Background pulse animation for processing state */}
        {status === 'processing' && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-pulse" />
        )}
        
        <div 
          className={`h-full ${getStatusColor()} transition-all duration-300 ease-out`}
          style={{ width: `${progress}%` }}
        >
          {/* Progress bar shine effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-[shine_2s_ease-in-out_infinite]" />
        </div>
      </div>

      {error && (
        <div className="text-sm text-red-500 bg-red-500/10 p-2 rounded-lg">
          {error}
        </div>
      )}
    </div>
  );
} 