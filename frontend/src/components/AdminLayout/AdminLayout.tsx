import { NavLink, Outlet } from 'react-router-dom';
import styles from './AdminLayout.module.scss';
import {useAuth} from "../../hooks/queries/useAuth.ts";

const navItems = [
    { to: '/admin/students', label: 'Студенты', icon: 'groups', roles: ['admin', 'teacher'] },
    { to: '/admin/modules', label: 'Модули', icon: 'stars', roles: ['admin', 'teacher'] },
    { to: '/admin/tasks', label: 'Задачи', icon: 'grade', roles: ['admin', 'teacher'] },
    { to: '/admin/roles', label: 'Роли', icon: 'admin_panel_settings', roles: ['admin'] },
];

const AdminLayout = () => {
    const { user, logout } = useAuth();

    const visibleItems = navItems.filter(item =>
        item.roles.includes(user?.role ?? '')
    );

    return (
        <div className={styles.shell}>
            <aside className={styles.sidebar}>
                <nav className={styles.nav} aria-label="Админ-панель">
                    {visibleItems.map(item => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            className={({ isActive }) =>
                                isActive ? `${styles.navItem} ${styles.active}` : styles.navItem
                            }
                        >
                            <span className={styles.navPill}>
                                <md-icon>{item.icon}</md-icon>
                            </span>
                            <span className={styles.navLabel}>{item.label}</span>
                        </NavLink>
                    ))}

                    <button className={styles.navItem} onClick={logout}>
                        <span className={styles.navPill}>
                            <md-icon>logout</md-icon>
                        </span>
                        <span className={styles.navLabel}>Выйти</span>
                    </button>
                </nav>
            </aside>

            <main className={styles.pagePanel}>
                <Outlet />
            </main>
        </div>
    );
};

export default AdminLayout;
