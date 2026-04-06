import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleCheck, faCircleInfo, faTriangleExclamation } from "@fortawesome/free-solid-svg-icons";

const notiComponent = (decoratorClass: string, icon: any, iconClass: string, title: string, message: string) => (
    <div className="notiWrap">
        <div className="notiFlex">
            <div className={`decorNoti ${decoratorClass}`}></div>
            <div className="iconWrap">
                <FontAwesomeIcon icon={icon} className={`${iconClass} text-lg`} />
            </div>
            <div>
                <p className="notiTitle">{title}</p>
                <p className="notiMessage">{message}</p>
            </div>
        </div>
    </div>
);

const notificationComponents: Record<string, any> = {
    success: (title: string, message: string) => notiComponent("bg-green-500", faCircleCheck, "text-green-500", title, message),
    warning: (title: string, message: string) => notiComponent("bg-orange-500", faTriangleExclamation, "text-orange-500", title, message),
    information: (title: string, message: string) => notiComponent("bg-blue-500", faCircleInfo, "text-blue-500", title, message),
    error: (title: string, message: string) => notiComponent("bg-red-500", faTriangleExclamation, "text-red-500", title, message),
};

export function ASNotificationComponent({ type, title, message }: any) {
    const NotificationComponent = notificationComponents[type];
    return <>{NotificationComponent && NotificationComponent(title, message)}</>;
}