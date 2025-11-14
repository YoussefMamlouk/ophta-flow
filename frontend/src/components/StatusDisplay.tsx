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

  const getStatusStyles = () => {
    switch (status) {
      case 'processing':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          text: 'text-blue-800',
          icon: (
            <svg className="w-5 h-5 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )
        };
      case 'success':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          text: 'text-green-800',
          icon: (
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          )
        };
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-800',
          icon: (
            <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          text: 'text-gray-700',
          icon: null
        };
    }
  };

  const styles = getStatusStyles();

  return (
    <div className={`p-4 rounded-lg border ${styles.bg} ${styles.border} ${styles.text} animate-in fade-in slide-in-from-bottom-2`}>
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {styles.icon}
          <p className="text-sm font-medium flex-1">{message}</p>
        </div>
        {status === 'success' && downloadUrl && (
          <a
            href={downloadUrl}
            download="extracted_data.xlsx"
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-all duration-200 flex items-center gap-2 whitespace-nowrap shadow-sm hover:shadow"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            <span>Télécharger</span>
          </a>
        )}
      </div>
    </div>
  );
};

export default StatusDisplay;

