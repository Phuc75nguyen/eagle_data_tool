import React, { useState, useEffect, useCallback } from 'react';
import { FaDownload, FaFilter, FaSearch, FaSync, FaTable } from 'react-icons/fa';

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

interface InteractiveDataViewerProps {
  initialStart?: string;
  initialEnd?: string;
  initialKeyword?: string;
  refreshTrigger?: number;
}

const InteractiveDataViewer: React.FC<InteractiveDataViewerProps> = ({ 
  initialStart, 
  initialEnd, 
  initialKeyword,
  refreshTrigger = 0
}) => {
  const [tradeData, setTradeData] = useState<TradeRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState(initialKeyword || '');

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      let url = `${baseUrl}/api/data/?limit=100`;
      if (initialStart) url += `&start=${initialStart}`;
      if (initialEnd) url += `&end=${initialEnd}`;
      if (initialKeyword) url += `&keyword=${initialKeyword}`;

      const res = await fetch(url, { credentials: 'include' });
      if (!res.ok) throw new Error('Không thể tải dữ liệu.');
      const data = await res.json();
      
      const mapped = (data.data || []).map((item: any) => ({
        id: item.id,
        date: item.date || '---',
        origin_country: item.origin_country || '---',
        exporter: item.exporter || '---',
        importer: item.importer || '---',
        hs_code: item.hs_code || '---',
        product: item.product || '---',
        quantity: item.quantity || 0,
        quantity_unit: item.quantity_unit || 'KG',
        value: item.value || 0,
        value_unit: item.value_unit || 'USD',
        unit_price: item.unit_price || 0
      }));
      
      setTradeData(mapped);
    } catch (err: any) {
      console.error(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [initialStart, initialEnd, initialKeyword]);

  useEffect(() => {
    fetchData();
  }, [fetchData, refreshTrigger]);

  const filteredData = tradeData.filter(row => 
    Object.values(row).some(val => String(val).toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="flex flex-col h-full bg-white overflow-hidden w-full">
      {/* Toolbar */}
      <div className="p-4 border-b flex flex-wrap items-center justify-between bg-gray-50/50 shrink-0 gap-4">
        <div className="relative flex-1 max-w-md">
          <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input 
            type="text" 
            placeholder="Lọc trong kết quả..." 
            className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-inner bg-white"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button onClick={fetchData} className="p-2 hover:bg-gray-200 rounded-lg transition-colors text-gray-600 shadow-sm border border-transparent hover:border-gray-300" title="Làm mới">
            <FaSync className={isLoading ? 'animate-spin' : ''} />
          </button>
          <button className="hidden sm:flex items-center gap-2 px-4 py-2 bg-white border rounded-xl text-sm font-bold hover:bg-gray-50 transition-colors shadow-sm">
            <FaFilter size={12} />
            Lọc
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-xl text-sm font-bold hover:bg-emerald-500 transition-colors shadow-sm shadow-emerald-200">
            <FaDownload size={12} />
            Xuất Excel
          </button>
        </div>
      </div>

      {/* Table Area (overflow-hidden parent, overflow-auto inner) */}
      <div className="flex-1 overflow-hidden flex flex-col p-2 bg-white">
        <div className="flex-1 overflow-auto scrollbar-thin scrollbar-thumb-gray-300 border border-gray-200 rounded-lg relative">
          <table className="w-full border-collapse text-[13px] min-w-max text-left">
            <thead className="sticky top-0 bg-gray-100 shadow-sm z-10 border-b border-gray-200">
              <tr className="text-gray-500 font-bold uppercase tracking-wider text-xs">
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
                filteredData.map((row) => (
                  <tr key={row.id} className="hover:bg-blue-50/50 transition-colors">
                      <td className="px-4 py-2 font-mono text-gray-400">#{row.id}</td>
                      <td className="px-4 py-2 font-medium">{row.date}</td>
                      <td className="px-4 py-2"><div className="truncate w-16 whitespace-nowrap" title={row.origin_country}>{row.origin_country}</div></td>
                      <td className="px-4 py-2"><div className="truncate max-w-[150px] whitespace-nowrap" title={row.exporter}>{row.exporter || '-'}</div></td>
                      <td className="px-4 py-2"><div className="truncate max-w-[150px] whitespace-nowrap" title={row.importer}>{row.importer || '-'}</div></td>
                      
                      <td className="px-4 py-2 font-mono font-bold text-blue-600 text-center bg-blue-50/20">{row.hs_code}</td>
                      <td className="px-4 py-2"><div className="truncate max-w-[200px]" title={row.product}>{row.product}</div></td>
                      
                      <td className="px-4 py-2 text-right font-semibold text-slate-800 whitespace-nowrap">{row.quantity ? row.quantity.toLocaleString() : '-'}</td>
                      <td className="px-4 py-2 text-left text-xs text-slate-500">{row.quantity_unit}</td>
                      
                      <td className="px-4 py-2 text-right font-bold text-emerald-600 bg-emerald-50/10 whitespace-nowrap">{row.value ? row.value.toLocaleString() : '-'}</td>
                      <td className="px-4 py-2 text-left text-xs text-emerald-800">{row.value_unit}</td>
                      <td className="px-4 py-2 text-right font-mono text-slate-500 whitespace-nowrap">{row.unit_price ? row.unit_price.toLocaleString() : '-'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={12} className="py-20 text-center">
                    {isLoading ? (
                      <div className="flex flex-col items-center gap-2">
                        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                        <p className="text-gray-500 font-medium tracking-wide">Đang truy xuất dữ liệu 11 cột...</p>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center gap-2 text-gray-400">
                        <FaTable size={40} className="mb-2 opacity-20" />
                        <p>Không tìm thấy bản ghi nào phù hợp.</p>
                      </div>
                    )}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer info */}
      <div className="px-6 py-3 border-t bg-gray-50/50 flex justify-between items-center text-xs text-gray-500 font-medium shrink-0">
        <div>Đang hiển thị {filteredData.length} kết quả</div>
        <div className="flex gap-4">
           <span className="flex items-center gap-1 font-bold text-blue-600">Sync Active</span>
        </div>
      </div>
    </div>
  );
};

export default InteractiveDataViewer;
