import React from 'react';

interface ProcessButtonProps {
  onClick: () => void;
  disabled: boolean;
  processing: boolean;
}

const ProcessButton: React.FC<ProcessButtonProps> = ({ onClick, disabled, processing }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || processing}
      className={`w-full px-6 py-3.5 rounded-lg font-semibold text-base transition-all duration-200 ${
        disabled || processing
          ? 'bg-gray-300 cursor-not-allowed text-gray-500'
          : 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg active:scale-[0.98]'
      } flex items-center justify-center gap-2`}
    >
      {processing ? (
        <>
          <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Traitement en cours...</span>
        </>
      ) : (
        <>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>Traiter les PDF</span>
        </>
      )}
    </button>
  );
};

export default ProcessButton;

