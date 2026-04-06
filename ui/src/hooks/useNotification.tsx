import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

// Declare the data structure to show notification
export interface IShowNotification {
    id: string;
    type: 'success' | 'warning' | 'information' | 'error';
    title: string;
    message: string;
    additionalInfo?: { actions?: any[] };
}

interface NotificationContextType {
    notifications: IShowNotification[];
    showNotification: (noti: Omit<IShowNotification, 'id'>) => void;
    clearNotification: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// Provider bọc ngoài ứng dụng
export const NotificationProvider = ({ children }: { children: ReactNode }) => {
    const [notifications, setNotifications] = useState<IShowNotification[]>([]);

    const showNotification = useCallback((noti: Omit<IShowNotification, 'id'>) => {
        const id = Math.random().toString(36).substring(2, 9); // Tạo ID ngẫu nhiên
        setNotifications((prev) => [...prev, { ...noti, id }]);
    }, []);

    const clearNotification = useCallback((id: string) => {
        setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, []);

    return (
        <NotificationContext.Provider value={{ notifications, showNotification, clearNotification }}>
            {children}
        </NotificationContext.Provider>
    );
};

// Hook để các Component khác gọi ra xài
export const useNotification = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error("useNotification must be used within a NotificationProvider");
    }
    return context;
};