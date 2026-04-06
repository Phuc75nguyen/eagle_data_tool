import React, { useState, useRef, useEffect } from 'react';
import { FaPaperPlane, FaRobot, FaUser } from 'react-icons/fa';

interface Message {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  timestamp: Date;
}

const AIChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: 'Xin chào! Tôi là AI Assistant của Eagle Pacific. Bạn cần tôi phân tích hay xuất báo cáo dữ liệu gì hôm nay?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: input.trim(),
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    // Mock API Call to AI Backend
    setTimeout(() => {
      const aiReply: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: `Tôi đã nhận được yêu cầu: **${userMsg.text}**. \nTiến trình đang được phân tích xử lý...`,
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, aiReply]);
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-700 text-slate-100 shadow-xl overflow-hidden rounded-l-xl">
      {/* Header */}
      <div className="px-6 py-4 bg-slate-800/80 backdrop-blur-md border-b border-slate-700 flex items-center justify-between z-10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
            <FaRobot size={20} />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-wide">Data Assistant AI</h2>
            <p className="text-xs text-slate-400 font-medium">Eagle Pacific Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-xs font-semibold text-slate-300">Online</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-4 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            <div
              className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${
                msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-200'
              }`}
            >
              {msg.sender === 'user' ? <FaUser size={14} /> : <FaRobot size={14} />}
            </div>
            <div
              className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none shadow-blue-900/20 shadow-xl'
                  : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-none shadow-md'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>
              <div className={`text-[10px] mt-2 opacity-60 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex items-start gap-4">
             <div className="shrink-0 w-8 h-8 rounded-full bg-slate-700 text-slate-200 flex items-center justify-center shadow-lg">
                <FaRobot size={14} />
             </div>
             <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-none p-4 flex gap-1 items-center">
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
             </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-slate-800 border-t border-slate-700 shrink-0">
        <div className="relative flex items-end bg-slate-900 border border-slate-600 rounded-xl focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all shadow-inner">
          <textarea
            className="w-full bg-transparent text-slate-200 min-h-[52px] max-h-32 p-4 outline-none resize-none text-sm scrollbar-thin rounded-xl placeholder:text-slate-500"
            placeholder="Nhập yêu cầu phân tích dữ liệu... (Enter để gửi, Shift+Enter xuống dòng)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
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
