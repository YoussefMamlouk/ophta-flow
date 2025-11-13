import React from 'react';

interface StatusDisplayProps {
  status: 'idle' | 'processing' | 'success' | 'error';
  message: string;
  downloadUrl?: string;
}

const StatusDisplay: React.FC<StatusDisplayProps> = ({ status, message, downloadUrl }) => {
  if (status === 'idle') {
    return null;
  }

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-300 text-blue-800';
      case 'success':
        return 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300 text-green-800';
      case 'error':
        return 'bg-gradient-to-r from-red-50 to-rose-50 border-red-300 text-red-800';
      default:
        return 'bg-gray-50 border-gray-300 text-gray-700';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return '⏳';
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className={`mt-4 p-5 border-2 rounded-xl shadow-lg ${getStatusColor()} animate-in fade-in slide-in-from-bottom-2`}>
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <span className="text-2xl">{getStatusIcon()}</span>
          <p className="text-sm font-semibold flex-1">{message}</p>
        </div>
        {status === 'success' && downloadUrl && (
          <a
            href={downloadUrl}
            download="extracted_data.xlsx"
            className="px-5 py-2.5 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white text-sm font-semibold rounded-xl transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105 active:scale-95 flex items-center gap-2 whitespace-nowrap"
          >
            <span>⬇️</span>
            <span>Télécharger Excel</span>
          </a>
        )}
      </div>
    </div>
  );
};

export default StatusDisplay;

