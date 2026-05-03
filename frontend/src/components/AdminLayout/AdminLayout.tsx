import { useEffect, useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import styles from './AdminLayout.module.scss';

interface JwtPayload {
    role: string;
    type: string;
    exp: number;
}

const navItems = [
    { to: '/admin/students', label: 'Студенты', icon: 'groups' },
    { to: '/admin/modules', label: 'Модули', icon: 'stars' },
    { to: '/admin/tasks', label: 'Задачи', icon: 'grade' },
    { to: '/admin/roles', label: 'Роли', icon: 'admin_panel_settings' },
];

const AdminLayout = () => {
    const navigate = useNavigate();
    const [isChecking, setIsChecking] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            navigate('/admin', { replace: true });
            return;
        }

        try {
            const decoded = jwtDecode<JwtPayload>(token);
            const isValid = decoded.type === 'access' && decoded.exp * 1000 > Date.now() && decoded.role === 'admin';
            if (!isValid) {
                localStorage.removeItem('access_token');
                navigate('/admin', { replace: true });
            }
        } catch {
            localStorage.removeItem('access_token');
            navigate('/admin', { replace: true });
        } finally {
            setIsChecking(false);
        }
    }, [navigate]);

    if (isChecking) {
        return <div className={styles.loading}>Загрузка...</div>;
    }

    return (
        <div className={styles.shell}>
            <aside className={styles.sidebar}>
                <nav className={styles.nav} aria-label="Админ-панель">
                    {navItems.map(item => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            className={({ isActive }) => isActive ? `${styles.navItem} ${styles.active}` : styles.navItem}
                        >
                            <span className={styles.navPill}>
                                <md-icon>{item.icon}</md-icon>
                            </span>
                            <span className={styles.navLabel}>{item.label}</span>
                        </NavLink>
                    ))}
                </nav>
            </aside>

            <main className={styles.pagePanel}>
                <Outlet />
            </main>
        </div>
    );
};

export default AdminLayout;