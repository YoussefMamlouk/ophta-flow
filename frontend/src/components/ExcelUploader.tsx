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
    <div className="mb-6">
      <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <span className="text-lg">📊</span>
        Fichier Excel Existant (Optionnel)
      </label>
      <div className="mt-1">
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
          className="w-full px-6 py-4 border-2 border-dashed border-green-300 rounded-xl text-gray-600 hover:border-green-500 hover:bg-green-50 transition-all duration-200 font-medium flex items-center justify-center gap-2 group"
        >
          <span className="text-xl group-hover:scale-110 transition-transform">📊</span>
          {file ? 'Changer le fichier Excel' : 'Cliquez pour sélectionner un fichier Excel'}
        </button>
      </div>
      {file && (
        <div className="mt-4 flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <span className="text-xl">📊</span>
            <span className="text-sm text-gray-700 truncate font-medium">{file.name}</span>
          </div>
          <button
            type="button"
            onClick={handleRemove}
            className="ml-3 px-3 py-1 text-red-600 hover:text-white hover:bg-red-500 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-1"
          >
            <span>✕</span>
            <span className="hidden sm:inline">Supprimer</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default ExcelUploader;

