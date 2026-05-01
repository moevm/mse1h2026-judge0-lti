import { NavLink, Outlet } from 'react-router-dom'
import styles from './AdminLayout.module.scss'

const navItems = [
    { to: '/admin/students', label: 'Студенты', icon: 'groups' },
    { to: '/admin/modules', label: 'Модули', icon: 'stars' },
    { to: '/admin/tasks', label: 'Задачи', icon: 'grade' },
    { to: '/admin/roles', label: 'Роли', icon: 'admin_panel_settings' },
]

const AdminLayout = () => {
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
    )
}

export default AdminLayout
