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
    <div className="mb-6">
      <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <span className="text-lg">📄</span>
        Fichiers PDF (Plusieurs autorisés)
      </label>
      <div className="mt-1">
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
          className="w-full px-6 py-4 border-2 border-dashed border-blue-300 rounded-xl text-gray-600 hover:border-blue-500 hover:bg-blue-50 transition-all duration-200 font-medium flex items-center justify-center gap-2 group"
        >
          <span className="text-xl group-hover:scale-110 transition-transform">📎</span>
          Cliquez pour sélectionner des fichiers PDF
        </button>
      </div>
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-xs text-gray-500 mb-2">{files.length} fichier(s) sélectionné(s)</p>
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <span className="text-xl">📄</span>
                <span className="text-sm text-gray-700 truncate font-medium">{file.name}</span>
              </div>
              <button
                type="button"
                onClick={() => handleRemoveFile(index)}
                className="ml-3 px-3 py-1 text-red-600 hover:text-white hover:bg-red-500 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-1"
              >
                <span>✕</span>
                <span className="hidden sm:inline">Supprimer</span>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PDFUploader;

