import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import PDFUploader from './components/PDFUploader';
import ExcelUploader from './components/ExcelUploader';
import ProcessButton from './components/ProcessButton';
import StatusDisplay from './components/StatusDisplay';
import axios from 'axios';

type Status = 'idle' | 'processing' | 'success' | 'error';

function App() {
  const [machineType, setMachineType] = useState('IOL700');
  const [pdfFiles, setPdfFiles] = useState<File[]>([]);
  const [excelFile, setExcelFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState('');
  const [downloadUrl, setDownloadUrl] = useState<string | undefined>();

  const handleProcess = async () => {
    if (pdfFiles.length === 0) {
      setStatus('error');
      setMessage('Veuillez sélectionner au moins un fichier PDF.');
      return;
    }

    setStatus('processing');
    setMessage('Traitement des PDF en cours...');
    setDownloadUrl(undefined);

    try {
      const formData = new FormData();
      formData.append('machine_type', machineType);
      
      pdfFiles.forEach((file) => {
        formData.append('pdf_files', file);
      });
      
      if (excelFile) {
        formData.append('excel_file', excelFile);
      }

      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${apiUrl}/extract`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      // Create download URL from blob
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);

      setStatus('success');
      setMessage(`${pdfFiles.length} fichier(s) PDF traité(s) avec succès. Cliquez sur télécharger pour obtenir le fichier Excel.`);
    } catch (error: any) {
      setStatus('error');
      if (error.response) {
        setMessage(`Erreur : ${error.response.data?.detail || error.response.statusText}`);
      } else if (error.request) {
        setMessage('Erreur : Aucune réponse du serveur. Assurez-vous que le backend est en cours d\'exécution.');
      } else {
        setMessage(`Erreur : ${error.message}`);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Sidebar selectedMachine={machineType} onMachineChange={setMachineType} />
      
      {/* Main Content */}
      <div className="ml-64 min-h-screen">
        <div className="max-w-5xl mx-auto px-8 py-12">
          {/* Header */}
          <div className="mb-10">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Extraction de Données
            </h1>
            <p className="text-gray-600 text-lg">
              Téléversez vos fichiers PDF et Excel pour extraire et fusionner les données ophtalmologiques
            </p>
          </div>

          {/* Content Card */}
          <div className="bg-white/70 backdrop-blur-sm shadow-xl rounded-2xl p-8 border border-white/50">
            <div className="space-y-6">
              <PDFUploader files={pdfFiles} onChange={setPdfFiles} />
              
              <ExcelUploader file={excelFile} onChange={setExcelFile} />
              
              <ProcessButton
                onClick={handleProcess}
                disabled={pdfFiles.length === 0}
                processing={status === 'processing'}
              />
              
              <StatusDisplay
                status={status}
                message={message}
                downloadUrl={downloadUrl}
              />
            </div>

            {/* Instructions */}
            <div className="mt-10 pt-8 border-t border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <span className="text-xl">📋</span>
                Instructions
              </h2>
              <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600 leading-relaxed">
                <li>Sélectionnez le type de machine dans le menu de gauche</li>
                <li>Téléversez un ou plusieurs fichiers PDF contenant des données ophtalmologiques</li>
                <li>Optionnellement, téléversez un fichier Excel existant pour fusionner les données</li>
                <li>Cliquez sur "Traiter les PDF" pour extraire les données</li>
                <li>Téléchargez le fichier Excel résultant</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

