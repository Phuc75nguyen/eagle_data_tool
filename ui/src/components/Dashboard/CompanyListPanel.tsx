import React, { useCallback, useEffect, useRef, useState } from 'react';
import { FaBuilding, FaTimes, FaUpload, FaSpinner, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';
import { fetchWithAuth } from '../../utils/api';

interface Company {
  company_name: string;
  hs_code: string;
}

interface CompanyListPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const CompanyListPanel: React.FC<CompanyListPanelProps> = ({ isOpen, onClose }) => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';

  const loadCompanies = useCallback(async () => {
    setIsLoading(true);
    setErrorMsg('');
    try {
      const res = await fetchWithAuth(`${baseUrl}/api/config/companies`);
      if (!res.ok) throw new Error('Không thể tải danh sách công ty.');
      const data = await res.json();
      setCompanies(data.companies || []);
    } catch (err: any) {
      setErrorMsg(err.message || 'Lỗi không xác định.');
    } finally {
      setIsLoading(false);
    }
  }, [baseUrl]);

  useEffect(() => {
    if (isOpen) loadCompanies();
  }, [isOpen, loadCompanies]);

  const handleFileSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetchWithAuth(`${baseUrl}/api/config/companies/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload thất bại.');

      setCompanies(data.companies || []);
      setSuccessMsg(`Đã cập nhật ${data.total} công ty mục tiêu.`);
    } catch (err: any) {
      setErrorMsg(err.message || 'Đã xảy ra lỗi khi upload file.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl max-h-[85vh] bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-800/80 border-b border-slate-700 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
              <FaBuilding size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Danh sách công ty mục tiêu</h2>
              <p className="text-xs text-slate-400">Upload file Excel (vd "TEXTILE COMPANY.xlsx") để Robot tìm kiếm theo đúng danh sách này</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-700 transition-colors">
            <FaTimes size={16} />
          </button>
        </div>

        {/* Upload area */}
        <div className="p-6 border-b border-slate-700 shrink-0">
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls"
            onChange={handleFileSelected}
            className="hidden"
            id="company-file-input"
            disabled={isUploading}
          />
          <label
            htmlFor="company-file-input"
            className={`flex items-center justify-center gap-2 w-full py-3 border-2 border-dashed rounded-xl cursor-pointer transition-colors text-sm font-semibold ${
              isUploading
                ? 'border-slate-600 text-slate-500 cursor-wait'
                : 'border-blue-500/50 text-blue-400 hover:border-blue-400 hover:bg-blue-500/5'
            }`}
          >
            {isUploading ? <FaSpinner className="animate-spin" size={14} /> : <FaUpload size={14} />}
            {isUploading ? 'Đang xử lý file...' : 'Chọn file Excel danh sách công ty (.xlsx/.xls)'}
          </label>

          {errorMsg && (
            <div className="mt-3 flex items-center gap-2 text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">
              <FaExclamationTriangle size={12} className="shrink-0" />
              {errorMsg}
            </div>
          )}
          {successMsg && (
            <div className="mt-3 flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 rounded-lg px-3 py-2">
              <FaCheckCircle size={12} className="shrink-0" />
              {successMsg}
            </div>
          )}
        </div>

        {/* Company list */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex items-center justify-between mb-3 px-2">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Đang cấu hình: {companies.length} công ty
            </span>
            {isLoading && <FaSpinner className="animate-spin text-slate-500" size={12} />}
          </div>

          {companies.length === 0 && !isLoading ? (
            <div className="text-center py-10 text-slate-500 text-sm">
              Chưa có danh sách công ty nào. Hãy upload file Excel ở trên.
            </div>
          ) : (
            <div className="space-y-1">
              {companies.map((c, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-800 text-sm"
                >
                  <span className="text-slate-200 truncate pr-3">{c.company_name}</span>
                  {c.hs_code && (
                    <span className="shrink-0 font-mono text-[11px] px-2 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded">
                      {c.hs_code}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompanyListPanel;
