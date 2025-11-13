import React, { useState } from 'react';
import MachineSelector from './components/MachineSelector';
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

      const response = await axios.post('http://localhost:8000/extract', formData, {
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white/80 backdrop-blur-lg shadow-2xl rounded-2xl p-8 md:p-12 border border-white/20">
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mb-4 shadow-lg">
              <span className="text-4xl">👁️</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-3">
              Extracteur de Données PDF Ophtalmologie
            </h1>
            <p className="text-gray-600 text-lg">
              Extrayez des données structurées à partir de rapports PDF et fusionnez-les avec des fichiers Excel existants
            </p>
          </div>

          <div className="space-y-6">
            <MachineSelector value={machineType} onChange={setMachineType} />
            
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

          <div className="mt-10 pt-8 border-t border-gray-200/50">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">📋</span>
              Instructions
            </h2>
            <ol className="list-decimal list-inside space-y-3 text-sm text-gray-700">
              <li>Sélectionnez le type de machine (actuellement seul IOL700 est disponible)</li>
              <li>Téléversez un ou plusieurs fichiers PDF contenant des données ophtalmologiques</li>
              <li>Optionnellement, téléversez un fichier Excel existant pour fusion</li>
              <li>Cliquez sur "Traiter les PDF" pour extraire les données</li>
              <li>Téléchargez le fichier Excel résultant</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

