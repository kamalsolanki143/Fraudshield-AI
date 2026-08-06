import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, Image as ImageIcon, CheckCircle, X, Sparkles } from 'lucide-react';

interface UploadBoxProps {
  onFileSelect: (file: File) => void;
  isScanning?: boolean;
}

export const UploadBox: React.FC<UploadBoxProps> = ({ onFileSelect, isScanning = false }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
        onFileSelect(file);
      }
    },
  });

  const clearSelection = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  return (
    <div className="relative">
      <div
        {...getRootProps()}
        className={`relative flex flex-col items-center justify-center p-8 rounded-3xl cursor-pointer border-2 border-dashed transition-all overflow-hidden ${
          isDragActive
            ? 'border-cyan-400 bg-cyan-950/30 shadow-glow-md scale-[1.01]'
            : 'border-slate-700/80 hover:border-brand-500/60 bg-slate-900/40 hover:bg-slate-900/60'
        }`}
      >
        <input {...getInputProps()} />

        {/* Laser Scanner animation during scanning */}
        <AnimatePresence>
          {isScanning && (
            <motion.div
              initial={{ y: '0%' }}
              animate={{ y: ['0%', '100%', '0%'] }}
              transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
              className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-glow-lg z-20 pointer-events-none"
            />
          )}
        </AnimatePresence>

        {previewUrl ? (
          <div className="relative w-full max-w-sm flex flex-col items-center space-y-3">
            <div className="relative group rounded-2xl overflow-hidden border border-slate-700 shadow-xl max-h-56">
              <img src={previewUrl} alt="Upload preview" className="w-full object-cover" />
              {!isScanning && (
                <button
                  onClick={clearSelection}
                  className="absolute top-2 right-2 p-1.5 rounded-full bg-slate-900/90 text-white hover:bg-danger transition-colors shadow-lg"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-300 bg-cyan-950/50 px-3 py-1.5 rounded-full border border-cyan-800/40">
              <CheckCircle className="w-3.5 h-3.5 text-cyan-400" />
              <span className="truncate max-w-[200px]">{selectedFile?.name}</span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center text-center space-y-3">
            <div className="p-4 rounded-2xl bg-brand-600/10 border border-brand-500/30 text-brand-400 shadow-glow-sm">
              <UploadCloud className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">
                Drag & Drop Screenshot / Document
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Supports PNG, JPG, WEBP screenshots of WhatsApp, SMS, or Fake Websites
              </p>
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono text-cyan-400 bg-slate-800 border border-slate-700">
              <Sparkles className="w-3 h-3 text-cyan-300" />
              Gemini OCR Laser Scanning Ready
            </div>
          </div>
        )}
      </div>

      {/* Preset Demo Image Buttons */}
      <div className="mt-3 flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Need a demo sample?</span>
        <button
          type="button"
          onClick={() => {
            const fakeFile = new File(['mock'], 'SBI_Phishing_SMS_Screenshot.png', { type: 'image/png' });
            setSelectedFile(fakeFile);
            setPreviewUrl('https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&q=80&w=400');
            onFileSelect(fakeFile);
          }}
          className="text-cyan-400 hover:underline font-medium flex items-center gap-1"
        >
          <ImageIcon className="w-3.5 h-3.5" />
          Load Sample Banking Scam Screenshot
        </button>
      </div>
    </div>
  );
};
