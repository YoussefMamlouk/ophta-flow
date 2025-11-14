import React, { useRef } from 'react';

interface ExcelUploaderProps {
  file: File | null;
  onChange: (file: File | null) => void;
}

const ExcelUploader: React.FC<ExcelUploaderProps> = ({ file, onChange }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && (
      selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
      selectedFile.type === 'application/vnd.ms-excel' ||
      selectedFile.name.endsWith('.xlsx') ||
      selectedFile.name.endsWith('.xls')
    )) {
      onChange(selectedFile);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemove = () => {
    onChange(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div>
      <label className="block text-sm font-semibold text-gray-800 mb-3">
        Fichier Excel Existant
        <span className="text-gray-500 font-normal ml-2">(Optionnel)</span>
      </label>
      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls"
          onChange={handleFileChange}
          className="hidden"
        />
        <button
          type="button"
          onClick={handleClick}
          className="w-full px-6 py-4 border-2 border-dashed border-gray-300 rounded-xl text-gray-700 hover:border-green-500 hover:bg-green-50/50 transition-all duration-200 font-medium flex items-center justify-center gap-3 group"
        >
          <svg className="w-5 h-5 text-gray-400 group-hover:text-green-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{file ? 'Changer le fichier Excel' : 'Cliquez pour sélectionner un fichier Excel'}</span>
        </button>
      </div>
      {file && (
        <div className="mt-4 flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200 hover:border-green-300 transition-all">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
            <span className="text-sm text-gray-700 truncate font-medium">{file.name}</span>
          </div>
          <button
            type="button"
            onClick={handleRemove}
            className="ml-3 p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all duration-200"
            title="Supprimer"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};

export default ExcelUploader;

