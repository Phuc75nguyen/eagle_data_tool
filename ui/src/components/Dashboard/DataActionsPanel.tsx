import React, { useState } from 'react';
import { FaDownload, FaFilter, FaSearch, FaChartBar, FaTable } from 'react-icons/fa';

const MOCK_DATA = [
  { id: '1', date: '2026-04-01', product: 'Cotton Yarn 40s', company: 'Apex Textile', qty: '15,000 kg', status: 'Completed' },
  { id: '2', date: '2026-04-02', product: 'Polyester Fabric', company: 'Global Weavers', qty: '25,000 m', status: 'Pending' },
  { id: '3', date: '2026-04-03', product: 'Denim Raw', company: 'BlueJeans Co.', qty: '5,000 m', status: 'Processing' },
  { id: '4', date: '2026-04-04', product: 'Linen Blend', company: 'EcoFabrics Ltd', qty: '12,500 kg', status: 'Completed' },
  { id: '5', date: '2026-04-05', product: 'Silk Thread', company: 'Apex Textile', qty: '800 kg', status: 'Pending' },
];

const DataActionsPanel: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = () => {
    setIsExporting(true);
    // Mock API Call for exporting
    setTimeout(() => {
      setIsExporting(false);
      alert('Đã tải xuống báo cáo thành công!');
    }, 1500);
  };

  const filteredData = MOCK_DATA.filter((row) =>
    Object.values(row).some((val) => val.toLowerCase().includes(searchTerm.toLowerCase()))
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
              placeholder="Tìm kiếm báo cáo, mặt hàng, công ty..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-50 transition-colors shadow-sm">
            <FaFilter size={12} />
            Lọc Dữ Liệu
          </button>
        </div>
        
        <button
          onClick={handleExport}
          disabled={isExporting}
          className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-bold shadow-md shadow-emerald-600/20 hover:bg-emerald-500 hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
        >
          <FaDownload size={14} />
          {isExporting ? 'Đang xuất...' : 'Xuất Báo Cáo'}
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* Chart Placeholder Box */}
        <div className="w-full h-64 bg-white border border-gray-200 rounded-xl shadow-sm p-5 flex flex-col relative overflow-hidden group hover:border-blue-300 transition-colors">
            <div className="flex items-center gap-2 mb-4 text-slate-800 font-bold">
                <FaChartBar className="text-blue-600" />
                <h3>Tổng Quan Giao Dịch</h3>
            </div>
            <div className="flex-1 flex items-center justify-center border-2 border-dashed border-gray-200 rounded-lg bg-gray-50">
               <div className="text-center">
                  <div className="w-16 h-16 bg-blue-100 text-blue-500 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                      <FaChartBar size={28} />
                  </div>
                  <p className="text-sm font-semibold text-gray-500">Khu vực biểu đồ dữ liệu</p>
                  <p className="text-xs text-gray-400 mt-1">Biểu đồ sẽ được AI generate tự động tại đây</p>
               </div>
            </div>
        </div>

        {/* Data Grid Table */}
        <div className="w-full bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
           <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2 text-slate-800 font-bold bg-slate-50/50">
                <FaTable className="text-emerald-600" />
                <h3>Chi tiết Dữ Liệu crawl gần nhất</h3>
            </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider font-semibold border-b border-gray-200">
                  <th className="px-6 py-4">Mã tham chiếu</th>
                  <th className="px-6 py-4">Ngày</th>
                  <th className="px-6 py-4">Hàng hóa</th>
                  <th className="px-6 py-4">Công ty đối tác</th>
                  <th className="px-6 py-4">Số lượng</th>
                  <th className="px-6 py-4">Trạng thái</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredData.length > 0 ? (
                  filteredData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/80 transition-colors text-sm text-gray-700">
                      <td className="px-6 py-4 font-mono font-medium text-slate-500">#{row.id}</td>
                      <td className="px-6 py-4">{row.date}</td>
                      <td className="px-6 py-4 font-semibold text-slate-800">{row.product}</td>
                      <td className="px-6 py-4">{row.company}</td>
                      <td className="px-6 py-4">{row.qty}</td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-3 py-1 text-[11px] font-bold uppercase rounded-full tracking-wide ${
                            row.status === 'Completed'
                              ? 'bg-emerald-100 text-emerald-700'
                              : row.status === 'Pending'
                              ? 'bg-amber-100 text-amber-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}
                        >
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500 text-sm">
                      Không tìm thấy dữ liệu phù hợp.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {/* Simple Pagination Footer Placeholder */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-sm text-gray-600">
             <span>Hiển thị 1 đến {filteredData.length} của {MOCK_DATA.length} kết quả</span>
             <div className="flex gap-1">
                 <button className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50">Trước</button>
                 <button className="px-3 py-1 bg-blue-600 text-white rounded shadow-sm">1</button>
                 <button className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50">Sau</button>
             </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default DataActionsPanel;
