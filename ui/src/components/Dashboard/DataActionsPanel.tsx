import React, { useState, useEffect } from 'react';
import { FaDownload, FaFilter, FaSearch, FaTable, FaSync, FaExclamationTriangle, FaRobot, FaSpinner } from 'react-icons/fa';

interface TradeRecord {
  id: number;
  date: string;
  origin_country: string;
  exporter: string;
  importer: string;
  hs_code: string;
  product: string;
  quantity: number;
  quantity_unit: string;
  value: number;
  value_unit: string;
  unit_price: number;
}

interface DataActionsPanelProps {
  refreshTrigger?: number;
}

const DataActionsPanel: React.FC<DataActionsPanelProps> = ({ refreshTrigger = 0 }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [tradeData, setTradeData] = useState<TradeRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // ── Cảnh báo tháng mới ──
  const [needsUpdate, setNeedsUpdate] = useState(false);
  const [missingMonth, setMissingMonth] = useState<string | null>(null);
  const [isCheckingMonth, setIsCheckingMonth] = useState(false);
  const [monthCheckMsg, setMonthCheckMsg] = useState('');

  const fetchStatus = async () => {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      const res = await fetch(`${baseUrl}/api/data/status`, { credentials: 'include' });
      if (!res.ok) return;
      const data = await res.json();
      setNeedsUpdate(!!data.needs_update);
      setMissingMonth(data.missing_month ?? null);
    } catch (_) {
      // im lặng — không chặn UI chính vì lỗi kiểm tra trạng thái
    }
  };

  const handleCheckNewMonth = async () => {
    setIsCheckingMonth(true);
    setMonthCheckMsg('');
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      const res = await fetch(`${baseUrl}/api/data/crawl/check-new-month`, {
        method: 'POST',
        credentials: 'include',
      });
      const data = await res.json();
      setMonthCheckMsg(data.message || '');
      if (data.triggered) {
        setNeedsUpdate(false);
      }
    } catch (err: any) {
      setMonthCheckMsg('Không thể kết nối máy chủ để kiểm tra.');
    } finally {
      setIsCheckingMonth(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [refreshTrigger]);

  const fetchTradeData = async () => {
    setIsLoading(true);
    setErrorMsg('');
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      const res = await fetch(`${baseUrl}/api/data/?limit=100`, { 
        method: 'GET',
        credentials: 'include'
      });
      
      if (res.status === 401) {
        throw new Error('Vui lòng đăng nhập lại để xem dữ liệu (Hết phiên làm việc).');
      }

      if (!res.ok) throw new Error('Không thể tải dữ liệu từ máy chủ.');

      const data = await res.json();
      setTradeData(data.data || []);
    } catch (error: any) {
      console.error('Fetch error:', error);
      setErrorMsg(error.message || 'Lỗi không xác định.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTradeData();
  }, [refreshTrigger]);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      const res = await fetch(`${baseUrl}/api/data/export`, {
        method: 'GET',
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Xuất báo cáo thất bại.');
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'exported_data.xlsx');
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (err: any) {
      alert(err.message || "Đã xảy ra lỗi khi tải file");
    } finally {
      setIsExporting(false);
    }
  };

  const filteredData = tradeData.filter((row) =>
    Object.values(row).some((val) => 
      String(val).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className="flex flex-col h-full bg-slate-50 overflow-hidden w-full">
      {/* Cảnh báo tháng mới */}
      {needsUpdate && (
        <div className="px-5 py-3 sm:px-6 bg-amber-50 border-b border-amber-200 flex flex-wrap items-center justify-between gap-3 shrink-0">
          <div className="flex items-center gap-2 text-amber-800 text-sm font-semibold">
            <FaExclamationTriangle className="shrink-0 text-amber-500" size={16} />
            <span>
              Dữ liệu chưa cập nhật tháng {missingMonth ?? ''}
              {monthCheckMsg ? ` — ${monthCheckMsg}` : '. Nhấn nút bên phải để Robot tự động cào dữ liệu tháng này.'}
            </span>
          </div>
          <button
            onClick={handleCheckNewMonth}
            disabled={isCheckingMonth}
            className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-sm font-bold shadow-sm transition-all disabled:opacity-70 disabled:cursor-wait whitespace-nowrap"
          >
            {isCheckingMonth ? <FaSpinner className="animate-spin" size={13} /> : <FaRobot size={13} />}
            {isCheckingMonth ? 'Đang kích hoạt...' : 'Kích hoạt Robot'}
          </button>
        </div>
      )}

      {/* Top Toolbar */}
      <div className="px-5 py-3 sm:px-6 sm:py-4 bg-white border-b border-gray-200 flex flex-wrap gap-4 items-center justify-between shrink-0 shadow-sm z-10 w-full overflow-x-auto">
        <div className="flex gap-4 items-center flex-1 min-w-[300px]">
          <div className="relative w-full max-w-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <FaSearch size={14} />
            </div>
            <input
              type="text"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50 outline-none transition-all shadow-inner"
              placeholder="Gõ từ khóa bộ lọc..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="hidden sm:flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-50 transition-colors shadow-sm whitespace-nowrap">
            <FaFilter size={12} />
            Lọc Nâng Cao
          </button>
        </div>
        
        <div className="flex gap-2 sm:gap-3 shrink-0">
          <button
            onClick={fetchTradeData}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 sm:px-4 py-2 sm:py-2.5 bg-blue-100 text-blue-700 border border-blue-200 rounded-lg text-sm font-bold shadow-sm hover:bg-blue-200 transition-all disabled:opacity-70 disabled:cursor-wait whitespace-nowrap"
          >
            <FaSync size={14} className={isLoading ? 'animate-spin' : ''} />
            <span className="hidden sm:block">Refresh</span>
          </button>
          
          <button
            onClick={handleExport}
            disabled={isExporting}
            className="flex items-center gap-2 px-3 sm:px-5 py-2 sm:py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-bold shadow-md shadow-emerald-600/20 hover:bg-emerald-500 hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed whitespace-nowrap"
          >
            <FaDownload size={14} />
            {isExporting ? 'Đang xuất...' : 'Xuất Excel'}
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden flex flex-col bg-gray-50/50 p-2 sm:p-4">
        
        {/* Error Notification */}
        {errorMsg && (
          <div className="p-4 mb-4 bg-red-100 text-red-700 border border-red-300 rounded-xl text-sm font-medium shadow-sm shrink-0">
            {errorMsg}
          </div>
        )}

        {/* Data Grid Table Container */}
        <div className="w-full bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-full relative">
           <div className="px-5 py-3 border-b border-gray-100 flex items-center justify-between gap-2 text-slate-800 font-bold bg-slate-50 shrink-0">
                <div className="flex items-center gap-2">
                    <FaTable className="text-emerald-600" />
                    <h3 className="hidden sm:block">Database XNK Doanh nghiệp</h3>
                    <h3 className="sm:hidden">Dữ liệu</h3>
                </div>
                {isLoading && <span className="text-[10px] sm:text-xs text-slate-500 italic block">Đang kết nối Backend...</span>}
            </div>
            
          {/* Table Body wrapper with overflow-y-auto */}
          <div className="flex-1 overflow-auto bg-white">
            <table className="w-full text-left border-collapse whitespace-nowrap min-w-max">
              <thead className="sticky top-0 bg-gray-100 z-10 shadow-sm border-b border-gray-200">
                <tr className="text-gray-500 text-[11px] sm:text-xs uppercase tracking-wider font-bold">
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Ngày</th>
                  <th className="px-4 py-3">Origin</th>
                  <th className="px-4 py-3">Xuất khẩu (Exporter)</th>
                  <th className="px-4 py-3">Nhập khẩu (Importer)</th>
                  <th className="px-4 py-3 text-center">HS Code</th>
                  <th className="px-4 py-3">Product</th>
                  <th className="px-4 py-3 text-right">Khối lượng</th>
                  <th className="px-4 py-3 text-left">ĐVT (Qty)</th>
                  <th className="px-4 py-3 text-right">Giá trị ($)</th>
                  <th className="px-4 py-3 text-left">ĐVT (Val)</th>
                  <th className="px-4 py-3 text-right">Đơn giá</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredData.length > 0 ? (
                  filteredData.map((row, idx) => (
                    <tr key={row.id || idx} className="hover:bg-blue-50/50 transition-colors text-[13px] text-gray-700">
                      <td className="px-4 py-2.5 font-mono text-gray-400">#{row.id}</td>
                      <td className="px-4 py-2.5 font-medium">{row.date}</td>
                      <td className="px-4 py-2.5"><div className="truncate w-16" title={row.origin_country}>{row.origin_country}</div></td>
                      <td className="px-4 py-2.5"><div className="truncate max-w-[150px]" title={row.exporter}>{row.exporter || '-'}</div></td>
                      <td className="px-4 py-2.5"><div className="truncate max-w-[150px]" title={row.importer}>{row.importer || '-'}</div></td>
                      
                      <td className="px-4 py-2.5 font-mono font-bold text-blue-600 text-center bg-blue-50/20">{row.hs_code}</td>
                      <td className="px-4 py-2.5"><div className="truncate max-w-[200px]" title={row.product}>{row.product}</div></td>
                      
                      <td className="px-4 py-2.5 text-right font-semibold text-slate-800">{row.quantity ? row.quantity.toLocaleString() : '-'}</td>
                      <td className="px-4 py-2.5 text-left text-xs text-slate-500">{row.quantity_unit}</td>
                      
                      <td className="px-4 py-2.5 text-right font-bold text-emerald-600 bg-emerald-50/10">{row.value ? row.value.toLocaleString() : '-'}</td>
                      <td className="px-4 py-2.5 text-left text-xs text-emerald-800">{row.value_unit}</td>
                      <td className="px-4 py-2.5 text-right font-mono text-slate-500">{row.unit_price ? row.unit_price.toLocaleString() : '-'}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={12} className="px-6 py-20 text-center">
                      <div className="flex flex-col items-center justify-center text-gray-400">
                         <FaTable className="mb-4 opacity-50" size={32} />
                         <span className="text-sm font-medium">{isLoading ? 'Đang truy xuất CSDL...' : 'Không có dữ liệu khớp với 11 cột chuẩn.'}</span>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          {/* Simple Pagination Footer Placeholder */}
          <div className="px-5 py-3 bg-gray-50 border-t border-gray-200 flex flex-wrap items-center justify-between text-xs sm:text-sm text-gray-600 shrink-0">
             <span className="font-medium">Tìm thấy {filteredData.length} kết quả</span>
             <div className="flex gap-2 items-center">
                <span className="hidden sm:inline text-xs text-gray-400 border border-gray-200 rounded px-2 py-1 bg-white shadow-sm">11 Columns Verified</span>
             </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default DataActionsPanel;
