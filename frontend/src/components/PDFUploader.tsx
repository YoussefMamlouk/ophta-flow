import React, { useRef } from 'react';

interface PDFUploaderProps {
  files: File[];
  onChange: (files: File[]) => void;
}

const PDFUploader: React.FC<PDFUploaderProps> = ({ files, onChange }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    const pdfFiles = selectedFiles.filter(file => file.type === 'application/pdf');
    onChange([...files, ...pdfFiles]);
  };

  const handleRemoveFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    onChange(newFiles);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div>
      <label className="block text-sm font-semibold text-gray-800 mb-3">
        Fichiers PDF
        <span className="text-gray-500 font-normal ml-2">(Plusieurs autorisés)</span>
      </label>
      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          onChange={handleFileChange}
          className="hidden"
        />
        <button
          type="button"
          onClick={handleClick}
          className="w-full px-6 py-4 border-2 border-dashed border-gray-300 rounded-xl text-gray-700 hover:border-blue-500 hover:bg-blue-50/50 transition-all duration-200 font-medium flex items-center justify-center gap-3 group"
        >
          <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span>Cliquez pour sélectionner des fichiers PDF</span>
        </button>
      </div>
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-xs text-gray-500 mb-2 font-medium">{files.length} fichier(s) sélectionné(s)</p>
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-all"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-gray-700 truncate font-medium">{file.name}</span>
              </div>
              <button
                type="button"
                onClick={() => handleRemoveFile(index)}
                className="ml-3 p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all duration-200"
                title="Supprimer"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PDFUploader;

