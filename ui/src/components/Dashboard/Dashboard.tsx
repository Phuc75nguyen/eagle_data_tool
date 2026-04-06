import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FaSignOutAlt, FaRocket, FaDatabase, FaCog, FaHistory, FaUserCircle } from "react-icons/fa";
import { fetchWithAuth } from "../../utils/api";
import AIChatPanel from "./AIChatPanel";
import DataActionsPanel from "./DataActionsPanel";

const Dashboard: React.FC = () => {
    const navigate = useNavigate();

    const [userName, setUserName] = useState("");
    const [userEmail, setUserEmail] = useState("");
    const [credits, setCredits] = useState<number>(0);

    // Fetch User Profile on mount
    useEffect(() => {
        const email = sessionStorage.getItem("userEmail");
        const name = sessionStorage.getItem("userName");

        if (!email) {
            navigate("/login");
            return;
        }

        setUserEmail(email);
        setUserName(name || "User");

        // Fetch Full Profile if needed
        const loadProfile = async () => {
            try {
                const res = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/profile`);
                if (res.ok) {
                    const data = await res.json();
                    setCredits(data.credits || 0);
                    setUserName(`${data.first_name || ''} ${data.last_name || ''}`.trim());
                }
            } catch (err) {
                console.error("Could not fetch profile:", err);
            }
        };
        loadProfile();
    }, [navigate]);

    const handleLogout = async () => {
        try {
            sessionStorage.clear();
            navigate("/login");
        } catch (error) {
            console.error("Logout failed", error);
        }
    };

    return (
        <div className="flex h-screen w-screen bg-slate-950 font-sans overflow-hidden">
            
            {/* --- SIDEBAR --- */}
            <aside className="w-20 md:w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 transition-all">
                <div>
                   <div className="h-16 flex items-center justify-center md:justify-start md:px-6 border-b border-slate-800">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white shrink-0 shadow-lg shadow-blue-600/30">
                           <FaRocket />
                        </div>
                        <span className="hidden md:block ml-3 font-bold text-white text-lg tracking-wide">
                            Eagle Data
                        </span>
                   </div>

                   <nav className="p-4 space-y-2 mt-4">
                        <button className="flex items-center gap-4 w-full p-3 bg-blue-600/10 text-blue-500 rounded-xl font-bold transition-all border border-blue-500/20 shadow-inner">
                            <FaDatabase size={18} />
                            <span className="hidden md:block text-sm">Data Studio</span>
                        </button>
                        <button className="flex items-center gap-4 w-full p-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl font-medium transition-colors">
                            <FaHistory size={18} />
                            <span className="hidden md:block text-sm">Lịch sử Agent</span>
                        </button>
                        <button className="flex items-center gap-4 w-full p-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl font-medium transition-colors">
                            <FaCog size={18} />
                            <span className="hidden md:block text-sm">Cài đặt</span>
                        </button>
                   </nav>
                </div>

                {/* User Profile Mini */}
                <div className="p-4 border-t border-slate-800">
                    <div className="flex flex-col md:flex-row items-center gap-3 p-3 bg-slate-800/50 rounded-xl cursor-default border border-slate-700">
                        <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                            <FaUserCircle size={24} />
                        </div>
                        <div className="hidden md:block flex-1 min-w-0">
                            <p className="text-sm font-bold text-slate-100 truncate">{userName}</p>
                            <p className="text-[10px] text-slate-400 truncate">{userEmail}</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* --- MAIN CONTENT WRAPPER --- */}
            <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-slate-900 relative">
                
                {/* DYNAMIC BACKGROUND EFFECTS */}
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-emerald-600/10 rounded-full blur-[100px] pointer-events-none"></div>

                {/* --- HEADER --- */}
                <header className="h-16 border-b border-white/5 bg-slate-900/50 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10">
                    <div className="flex items-center gap-2">
                        <h1 className="text-xl font-bold text-slate-100">AI Data Explorer</h1>
                        <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20">
                            Enterprise Edition
                        </span>
                    </div>
                    
                    <div className="flex items-center gap-4">
                        <div className="hidden sm:flex flex-col text-right">
                           <span className="text-xs text-slate-400">Số dư Credit</span>
                           <span className="text-sm font-bold text-amber-400">{credits || '∞'} Credits</span>
                        </div>
                        <div className="w-px h-8 bg-slate-700"></div>
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 text-slate-400 hover:text-red-400 font-semibold text-sm transition-colors"
                        >
                            <FaSignOutAlt /> <span className="hidden sm:inline">Đăng xuất</span>
                        </button>
                    </div>
                </header>

                {/* --- SPLIT SCREEN LAYOUT --- */}
                <div className="flex-1 p-4 lg:p-6 flex flex-col lg:flex-row gap-6 overflow-hidden z-10">
                    
                    {/* LEFT PANEL: AI ASSISTANT CHAT (40%) */}
                    <div className="w-full lg:w-[35%] flex-shrink-0 flex flex-col shadow-2xl rounded-xl">
                        <AIChatPanel />
                    </div>

                    {/* RIGHT PANEL: DATA & ACTIONS GRID (65%) */}
                    <div className="flex-1 flex flex-col min-w-0 shadow-2xl rounded-xl">
                        <DataActionsPanel />
                    </div>

                </div>
            </main>

        </div>
    );
};

export default Dashboard;