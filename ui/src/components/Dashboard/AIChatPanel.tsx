import React, { useState, useRef, useEffect, useCallback } from 'react';
import { FaPaperPlane, FaRobot, FaUser, FaTable, FaExternalLinkAlt, FaSpinner } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

interface Message {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  timestamp: Date;
  suggested_prompts?: string[];
  data_ready?: boolean;        // shows "View Data" button
  is_crawling?: boolean;       // shows crawl progress indicator
}

interface AIChatPanelProps {
  onChatComplete?: () => void;
}

const DATA_VIEWER_PATH = '/data-viewer';

const AIChatPanel: React.FC<AIChatPanelProps> = ({ onChatComplete }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: 'Dạ sếp cần em tải báo cáo hay cào dữ liệu mới về ạ?',
      timestamp: new Date(),
      suggested_prompts: [
        'Cào dữ liệu từ ngày 2026-01-01 đến 2026-01-30',
        'Em làm được những gì?',
        'Lấy dữ liệu áo thun',
      ],
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isCrawling, setIsCrawling] = useState(false);
  const [crawlLog, setCrawlLog] = useState<string>(''); // last SSE log line shown in header
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Cleanup SSE on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []);

  // -----------------------------------------------------------------------
  // Connect EventSource SSE to /api/data/stream
  // Listens for log events and final __DONE__:<count> sentinel.
  // -----------------------------------------------------------------------
  const startSSE = useCallback((prevCount: number) => {
    // Close any existing SSE connection first
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
    // EventSource does not support custom headers; credentials (cookies) are
    // sent automatically when withCredentials = true.
    const es = new EventSource(`${baseUrl}/api/data/stream`, { withCredentials: true });
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const msg: string = payload.message ?? '';

        if (msg.startsWith('__DONE__:')) {
          // Final sentinel: crawl finished
          const newTotal = parseInt(msg.split(':')[1] ?? '0', 10);
          es.close();
          eventSourceRef.current = null;
          setIsCrawling(false);
          setCrawlLog('');

          const added = newTotal - prevCount;
          const readyMsg: Message = {
            id: `ready-${Date.now()}`,
            sender: 'ai',
            text: `✅ Robot đã tải và xử lý xong dữ liệu! Thêm ${added > 0 ? added : newTotal} bản ghi mới (tổng: ${newTotal} bản ghi).`,
            timestamp: new Date(),
            data_ready: true,
            suggested_prompts: ['Tải thêm dữ liệu tháng trước', 'Cào dữ liệu tháng khác'],
          };
          setMessages(prev => [...prev, readyMsg]);
          if (onChatComplete) onChatComplete();
        } else {
          // Progress log — update header ticker
          setCrawlLog(msg);
        }
      } catch (_) {}
    };

    es.onerror = () => {
      // SSE will auto-reconnect; only close if crawl is done
      if (!isCrawling) {
        es.close();
        eventSourceRef.current = null;
      }
    };
  }, [onChatComplete, isCrawling]);

  // -----------------------------------------------------------------------
  // Send message to backend
  // -----------------------------------------------------------------------
  const handleSend = async (textToSend: string = input) => {
    if (!textToSend.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg]);
    if (textToSend === input) setInput('');
    setIsLoading(true);

    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';

      // Snapshot current record count BEFORE triggering the crawl
      let prevCount = 0;
      try {
        const statusRes = await fetch(`${baseUrl}/api/data/status`, { credentials: 'include' });
        if (statusRes.ok) {
          const s = await statusRes.json();
          prevCount = s.total_records ?? 0;
        }
      } catch (_) {}

      const response = await fetch(`${baseUrl}/api/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.text }),
        credentials: 'include',
      });

      if (response.status === 401) {
        throw new Error('Vui lòng đăng nhập lại để sử dụng AI (Session hết hạn).');
      }
      if (!response.ok) throw new Error('Không thể kết nối server AI.');

      const data = await response.json();

      const aiReply: Message = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        text: data.reply,
        timestamp: new Date(),
        suggested_prompts: data.suggested_prompts || [],
        data_ready: data.data_ready ?? false,
        // mark message as crawling placeholder if status === ok (crawl just started)
        is_crawling: data.status === 'ok',
      };
      setMessages(prev => [...prev, aiReply]);

      if (data.status === 'ok') {
        setIsCrawling(true);
        startSSE(prevCount);
      }

      if (data.data_ready && onChatComplete) {
        onChatComplete();
      }
    } catch (error: any) {
      const errorReply: Message = {
        id: `err-${Date.now()}`,
        sender: 'ai',
        text: error.message || 'Xin lỗi sếp, em không thể kết nối tới server AI lúc này.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorReply]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 text-slate-100 shadow-xl overflow-hidden rounded-xl">
      
      {/* ── Header ── */}
      <div className="px-6 py-4 bg-slate-800/80 backdrop-blur-md border-b border-slate-700 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
            <FaRobot size={20} />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-wide">EaglePax Assistant</h2>
            <p className="text-xs text-slate-400">AI Data Agent · Eagle Pacific Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isCrawling ? (
            <>
              <FaSpinner className="text-amber-400 animate-spin" size={12} />
              <span className="text-xs font-semibold text-amber-400 truncate max-w-[180px]" title={crawlLog}>
                {crawlLog || 'Đang cào…'}
              </span>
            </>
          ) : (
            <>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-semibold text-slate-300">Online</span>
            </>
          )}
        </div>
      </div>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            {/* Avatar */}
            <div
              className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-200'
              }`}
            >
              {msg.sender === 'user' ? <FaUser size={13} /> : <FaRobot size={13} />}
            </div>

            {/* Bubble */}
            <div
              className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none shadow-xl shadow-blue-900/20'
                  : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-none shadow-md'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>

              {/* ── "View Data" Card — shown when data_ready = true ── */}
              {msg.data_ready && (
                <div className="mt-4 p-4 bg-emerald-900/40 border border-emerald-600/50 rounded-xl flex flex-col gap-3">
                  <div className="flex items-center gap-2 text-emerald-300 font-bold text-sm">
                    <FaTable />
                    <span>Dữ liệu đã sẵn sàng để xem!</span>
                  </div>
                  <button
                    onClick={() => navigate(DATA_VIEWER_PATH)}
                    className="flex items-center justify-center gap-2 w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg transition-all hover:shadow-lg hover:shadow-emerald-700/30 hover:-translate-y-0.5 text-sm"
                  >
                    <FaExternalLinkAlt size={12} />
                    Mở Bảng Dữ Liệu
                  </button>
                </div>
              )}

              {/* ── Crawl-in-progress indicator ── */}
              {msg.is_crawling && !msg.data_ready && (
                <div className="mt-3 flex items-center gap-2 text-xs text-amber-400">
                  <FaSpinner className="animate-spin" size={11} />
                  <span>Robot đang chạy ngầm… Em sẽ thông báo sếp khi xong.</span>
                </div>
              )}

              {/* ── Suggested prompts ── */}
              {msg.sender === 'ai' && msg.suggested_prompts && msg.suggested_prompts.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {msg.suggested_prompts.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSend(prompt)}
                      className="text-xs bg-slate-700/60 hover:bg-blue-600 border border-slate-600 hover:border-blue-500 text-slate-200 px-3 py-1.5 rounded-full transition-colors cursor-pointer shadow-sm"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              )}

              <div
                className={`text-[10px] mt-2 opacity-50 ${
                  msg.sender === 'user' ? 'text-right' : 'text-left'
                }`}
              >
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {/* ── AI loading animation ── */}
        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="shrink-0 w-8 h-8 rounded-full bg-slate-700 text-slate-200 flex items-center justify-center shadow-lg">
              <FaRobot size={13} />
            </div>
            <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-none p-4 flex gap-1 items-center">
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* ── Input Area ── */}
      <div className="p-4 bg-slate-800 border-t border-slate-700 shrink-0">
        {/* Quick access to data viewer if data exists */}
        <div className="mb-3 flex justify-end">
          <button
            onClick={() => navigate(DATA_VIEWER_PATH)}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-emerald-400 transition-colors font-medium border border-slate-700 hover:border-emerald-600/50 px-3 py-1.5 rounded-full"
          >
            <FaTable size={11} />
            Mở trang dữ liệu
          </button>
        </div>

        <div className="relative flex items-end bg-slate-900 border border-slate-600 rounded-xl focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all shadow-inner">
          <textarea
            className="w-full bg-transparent text-slate-200 min-h-[52px] max-h-32 p-4 outline-none resize-none text-sm rounded-xl placeholder:text-slate-500"
            placeholder="Nhập yêu cầu… (Enter gửi · Shift+Enter xuống dòng)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            onClick={() => handleSend(input)}
            disabled={!input.trim() || isLoading}
            className="shrink-0 m-2 p-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg"
          >
            <FaPaperPlane size={14} />
          </button>
        </div>
        <div className="text-center mt-2">
          <span className="text-[10px] text-slate-500">AI có thể mắc lỗi nhỏ. Vui lòng kiểm tra lại báo cáo xuất ra.</span>
        </div>
      </div>
    </div>
  );
};

export default AIChatPanel;
