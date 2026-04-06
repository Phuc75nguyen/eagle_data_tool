import { useCallback, useEffect, useRef, useState } from "react";
import { useNotification } from "../../hooks/useNotification"; // Trỏ đúng đường dẫn hook
import { ASNotificationComponent } from "./notification.component";
import { FaTimes } from "react-icons/fa"; // Tận dụng react-icons sếp đang có

export function NotificationDisplay() {
    const { notifications, clearNotification } = useNotification();
    const [_isHovered, setIsHovered] = useState(false);
    const timersRef = useRef<{ [key: string]: ReturnType<typeof setTimeout> }>({});

    const handleClearNotification = useCallback((id: string) => {
        clearNotification(id);
        if (timersRef.current[id]) clearTimeout(timersRef.current[id]);
    }, [clearNotification]);

    useEffect(() => {
        return () => Object.values(timersRef.current).forEach(clearTimeout);
    }, []);

    return (
        <div
            className="fixed top-10 right-4 z-[9999] flex flex-col gap-2"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {notifications.map((item, _index) => {
                if (!timersRef.current[item.id]) {
                    timersRef.current[item.id] = setTimeout(() => handleClearNotification(item.id), 3000); // Tự ẩn sau 3s
                }
                return (
                    <div key={item.id} className="relative transition-all duration-300 animate-fade-in-up">
                        {/* Gọi cái ruột UI của Mr Khánh */}
                        <ASNotificationComponent type={item.type} title={item.title} message={item.message} />

                        {/* Nút X để tắt */}
                        <button
                            className="absolute top-3 right-3 text-gray-400 hover:text-gray-700"
                            onClick={() => handleClearNotification(item.id)}
                        >
                            <FaTimes />
                        </button>
                    </div>
                );
            })}
        </div>
    );
}