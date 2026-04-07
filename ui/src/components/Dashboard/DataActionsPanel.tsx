import React, { useState, useEffect } from 'react';
import { FaDownload, FaFilter, FaSearch, FaChartBar, FaTable, FaSync } from 'react-icons/fa';

interface TradeRecord {
  id: number;
  date: string;
  importer: string;
  hs_code: string;
  product: string;
  quantity: number;
  quantity_unit: string;
  value: number;
  value_unit: string;
  unit_price: number;
}

const DataActionsPanel: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [tradeData, setTradeData] = useState<TradeRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const fetchTradeData = async () => {
    setIsLoading(true);
    setErrorMsg('');
    try {
      // Gọi lên Backend (thông qua Vite Proxy /api -> 8000)
      const res = await fetch(`/api/data/?limit=100`, { 
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
  }, []);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const res = await fetch(`/api/data/export`, {
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
    <div className="flex flex-col h-full bg-slate-50 overflow-hidden rounded-r-xl">
      {/* Top Toolbar */}
      <div className="px-6 py-4 bg-white border-b border-gray-200 flex items-center justify-between shrink-0 shadow-sm z-10">
        <div className="flex gap-4 items-center w-2/3">
          <div className="relative w-full max-w-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <FaSearch size={14} />
            </div>
            <input
              type="text"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50 outline-none transition-all shadow-inner"
              placeholder="Gõ từ khóa tìm kiếm..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-50 transition-colors shadow-sm">
            <FaFilter size={12} />
            Lọc Dữ Liệu
          </button>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={fetchTradeData}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2.5 bg-blue-100 text-blue-700 border border-blue-200 rounded-lg text-sm font-bold shadow-sm hover:bg-blue-200 transition-all disabled:opacity-70 disabled:cursor-wait"
          >
            <FaSync size={14} className={isLoading ? 'animate-spin' : ''} />
            Refresh Data
          </button>
          
          <button
            onClick={handleExport}
            disabled={isExporting}
            className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-bold shadow-md shadow-emerald-600/20 hover:bg-emerald-500 hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <FaDownload size={14} />
            {isExporting ? 'Đang xuất...' : 'Xuất Excel'}
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* Error Notification */}
        {errorMsg && (
          <div className="p-4 bg-red-100 text-red-700 border border-red-300 rounded-xl text-sm font-medium shadow-sm">
            {errorMsg}
          </div>
        )}

        {/* Data Grid Table */}
        <div className="w-full bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden flex flex-col min-h-[400px]">
           <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between gap-2 text-slate-800 font-bold bg-slate-50/50 shrink-0">
                <div className="flex items-center gap-2">
                    <FaTable className="text-emerald-600" />
                    <h3>Chi tiết Dữ Liệu XNK (Database)</h3>
                </div>
                {isLoading && <span className="text-xs text-slate-500 italic block">Đang kết nối Backend...</span>}
            </div>
            
          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left border-collapse whitespace-nowrap">
              <thead>
                <tr className="bg-gray-50 text-gray-500 text-[11px] uppercase tracking-wider font-bold border-b border-gray-200">
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Ngày (Date)</th>
                  <th className="px-4 py-3 min-w-[200px]">Đơn vị NK (Importer)</th>
                  <th className="px-4 py-3 font-mono text-center">HS Code</th>
                  <th className="px-4 py-3 min-w-[250px]">Hàng hóa (Product)</th>
                  <th className="px-4 py-3 text-right">Khối lượng</th>
                  <th className="px-4 py-3 text-right">Giá trị</th>
                  <th className="px-4 py-3 text-right">Đơn giá</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredData.length > 0 ? (
                  filteredData.map((row, idx) => (
                    <tr key={row.id || idx} className="hover:bg-slate-50/80 transition-colors text-sm text-gray-700">
                      <td className="px-4 py-3 font-mono font-medium text-slate-400">#{row.id}</td>
                      <td className="px-4 py-3 font-medium">{row.date}</td>
                      <td className="px-4 py-3">
                         <div className="truncate max-w-[200px]" title={row.importer}>{row.importer}</div>
                      </td>
                      <td className="px-4 py-3 font-mono font-semibold text-blue-600 text-center">{row.hs_code}</td>
                      <td className="px-4 py-3">
                         <div className="truncate max-w-[250px] whitespace-normal line-clamp-2 leading-relaxed" title={row.product}>{row.product}</div>
                      </td>
                      <td className="px-4 py-3 text-right font-medium text-slate-800">
                         {row.quantity ? row.quantity.toLocaleString() : '-'} <span className="text-xs text-slate-500">{row.quantity_unit}</span>
                      </td>
                      <td className="px-4 py-3 text-right font-bold text-emerald-600">
                         {row.value ? row.value.toLocaleString() : '-'} <span className="text-xs text-emerald-800">{row.value_unit}</span>
                      </td>
                      <td className="px-4 py-3 text-right text-slate-600 font-mono text-xs">
                         {row.unit_price ? row.unit_price.toLocaleString() : '-'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="px-6 py-20 text-center flex-col items-center flex text-gray-500 text-sm">
                      <FaTable className="text-gray-300 mb-3" size={32} />
                      {isLoading ? 'Đang tải dữ liệu...' : 'Không có dữ liệu trong Database. Thử gọi AI tải dữ liệu nhé!'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {/* Simple Pagination Footer Placeholder */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-sm text-gray-600 shrink-0">
             <span>Hiển thị 1 đến {filteredData.length} của {tradeData.length} kết quả</span>
             <div className="flex gap-1">
                 <button className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50" disabled>Trước</button>
                 <button className="px-3 py-1 bg-blue-600 text-white rounded shadow-sm">1</button>
                 <button className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50" disabled>Sau</button>
             </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default DataActionsPanel;
