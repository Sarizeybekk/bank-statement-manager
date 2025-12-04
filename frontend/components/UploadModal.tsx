"use client";

import { useState } from "react";
import { X, Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";
import { transactionsAPI } from "@/lib/api";

interface UploadModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function UploadModal({ onClose, onSuccess }: UploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Lütfen bir dosya seçin");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await transactionsAPI.upload(file);
      setResult(data);
      
      const importedCount = data.imported_count || data.batch?.imported_rows || 0;
      
      if (importedCount > 0 || data.batch) {
        setTimeout(() => {
          onSuccess();
        }, 1500);
      } else {
        setResult(data);
        setTimeout(() => {
          onSuccess();
        }, 2000);
      }
    } catch (err: any) {
      console.error("Upload error details:", err);
      console.error("Error response:", err.response?.data);
      
      let errorMessage = "Yükleme başarısız";
      
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.error) {
          errorMessage = err.response.data.error;
        } else if (err.response.data.details) {
          errorMessage = Array.isArray(err.response.data.details) 
            ? err.response.data.details.join(', ')
            : err.response.data.details;
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        } else if (err.response.data.non_field_errors) {
          errorMessage = Array.isArray(err.response.data.non_field_errors)
            ? err.response.data.non_field_errors.join(', ')
            : err.response.data.non_field_errors;
        } else {
          const errorKeys = Object.keys(err.response.data);
          if (errorKeys.length > 0) {
            const firstError = err.response.data[errorKeys[0]];
            errorMessage = Array.isArray(firstError) 
              ? `${errorKeys[0]}: ${firstError.join(', ')}`
              : `${errorKeys[0]}: ${firstError}`;
          }
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">CSV Dosyası Yükle</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {!result ? (
          <>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CSV Dosyası Seçin
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-500 transition-colors">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="flex flex-col items-center"
                >
                  <Upload className="w-12 h-12 text-gray-400 mb-4" />
                  {file ? (
                    <div className="flex items-center gap-2 text-primary-600">
                      <FileText className="w-5 h-5" />
                      <span className="font-medium">{file.name}</span>
                    </div>
                  ) : (
                    <>
                      <p className="text-sm text-gray-600 mb-1">
                        Yüklemek için tıklayın veya sürükleyip bırakın
                      </p>
                      <p className="text-xs text-gray-500">Sadece CSV dosyaları</p>
                    </>
                  )}
                </label>
              </div>
            </div>

            {error && (
              <div className="mb-4 bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded-lg text-sm flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                {error}
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                İptal
              </button>
              <button
                onClick={handleUpload}
                disabled={!file || loading}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                {loading ? "Yükleniyor..." : "Yükle"}
              </button>
            </div>
          </>
        ) : (
          <div className="text-center py-4">
            <CheckCircle className="w-16 h-16 text-success-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Yükleme Başarılı!</h3>
            <div className="space-y-2 text-sm text-gray-600 mb-6">
              <p>İçe Aktarılan: <span className="font-semibold text-success-600">{result.imported_count || result.batch?.imported_rows || 0}</span> işlem</p>
              {(result.failed_count > 0 || result.batch?.failed_rows > 0) && (
                <p>Başarısız: <span className="font-semibold text-danger-600">{result.failed_count || result.batch?.failed_rows || 0}</span> işlem</p>
              )}
            </div>
            <button
              onClick={() => {
                onSuccess();
                onClose();
              }}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Kapat ve Yenile
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

