import React from "react";
import { useNavigate } from "react-router-dom";
import {
    FaArrowLeft, FaRocket, FaDatabase, FaUserCircle,
    FaSignOutAlt, FaRobot
} from "react-icons/fa";
import DataActionsPanel from "../Dashboard/DataActionsPanel";

const DataViewerPage: React.FC = () => {
    const navigate = useNavigate();
    const userName = sessionStorage.getItem("userName") || "User";

    const handleLogout = () => {
        sessionStorage.clear();
        navigate("/login");
    };

    return (
        <div className="h-screen w-screen flex bg-slate-950 font-sans overflow-hidden">

            {/* ── LEFT SIDEBAR ── */}
            <aside className="w-16 md:w-64 bg-slate-900 border-r border-slate-800 flex flex-col flex-shrink-0 h-full">
                {/* Logo */}
                <div className="h-16 flex items-center justify-center md:justify-start md:px-6 border-b border-slate-800 shrink-0">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white shrink-0 shadow-lg shadow-blue-600/30">
                        <FaRocket />
                    </div>
                    <span className="hidden md:block ml-3 font-bold text-white text-lg tracking-wide whitespace-nowrap">
                        EaglePax
                    </span>
                </div>

                {/* Menu */}
                <nav className="flex-1 overflow-y-auto p-3 space-y-2">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="flex items-center gap-4 w-full p-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl font-medium transition-colors"
                    >
                        <FaRobot size={18} className="shrink-0" />
                        <span className="hidden md:block text-sm whitespace-nowrap">AI Assistant</span>
                    </button>
                    <button
                        onClick={() => navigate('/data-viewer')}
                        className="flex items-center gap-4 w-full p-3 bg-emerald-600/10 text-emerald-400 rounded-xl font-bold border border-emerald-500/20"
                    >
                        <FaDatabase size={18} className="shrink-0" />
                        <span className="hidden md:block text-sm whitespace-nowrap">Data Viewer</span>
                    </button>
                </nav>

                {/* User profile */}
                <div className="mt-auto p-4 border-t border-slate-800 shrink-0">
                    <div className="relative group cursor-pointer">
                        <div className="flex flex-col md:flex-row items-center gap-3 p-3 bg-slate-800/40 rounded-xl border border-slate-700/50 hover:bg-slate-800 transition-colors">
                            <div className="w-9 h-9 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                                <FaUserCircle size={22} />
                            </div>
                            <div className="hidden md:flex flex-col flex-1 min-w-0">
                                <p className="text-sm font-bold text-slate-100 truncate">{userName}</p>
                            </div>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="hidden md:flex absolute inset-0 bg-red-600/90 rounded-xl items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity gap-2 font-bold text-sm"
                        >
                            <FaSignOutAlt /> Đăng xuất
                        </button>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="md:hidden mt-3 w-full flex justify-center text-slate-400 hover:text-red-400 transition-colors p-2"
                        title="Đăng xuất"
                    >
                        <FaSignOutAlt size={20} />
                    </button>
                </div>
            </aside>

            {/* ── MAIN CONTENT ── */}
            <main className="flex-1 flex flex-col min-w-0 h-full bg-[#0B1120] relative overflow-hidden">
                {/* Ambient glows */}
                <div className="absolute top-0 right-0 w-[40%] h-[40%] bg-emerald-600/10 rounded-full blur-[120px] pointer-events-none z-0" />
                <div className="absolute bottom-0 left-0 w-[30%] h-[30%] bg-blue-600/10 rounded-full blur-[100px] pointer-events-none z-0" />

                {/* Header */}
                <header className="h-16 border-b border-white/5 bg-slate-900/40 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm font-semibold"
                        >
                            <FaArrowLeft size={14} />
                            <span className="hidden sm:inline">Quay lại AI Chat</span>
                        </button>
                        <div className="w-px h-6 bg-slate-700" />
                        <h1 className="text-xl font-bold text-slate-100">Data Viewer</h1>
                        <span className="hidden sm:inline-block px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20">
                            11 Columns · Live
                        </span>
                    </div>
                </header>

                {/* DataActionsPanel fills the rest */}
                <div className="flex-1 overflow-hidden p-3 lg:p-5 z-10">
                    <div className="h-full rounded-xl overflow-hidden border border-slate-700/30 shadow-2xl">
                        <DataActionsPanel />
                    </div>
                </div>
            </main>
        </div>
    );
};

export default DataViewerPage;
