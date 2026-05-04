import { type FormEvent, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import styles from './AdminLoginPage.module.scss';
import {useAuth} from "../../hooks/queries/useAuth.ts";


const AdminLoginPage = () => {
    const navigate = useNavigate();
    const { login, isAdmin, isLoading: isAuthLoading } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (!isAuthLoading && isAdmin) {
            navigate('/admin/modules', { replace: true });
        }
    }, [navigate, isAdmin, isAuthLoading]);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!username.trim() || !password.trim()) {
            toast.error('Заполните все поля');
            return;
        }

        setIsLoading(true);
        try {
            await login({ username, password });
            toast.success('Вход выполнен успешно');
            navigate('/admin/modules', { replace: true });
        } catch (error: any) {
            const detail = error.response?.data?.detail;
            toast.error('Ошибка входа', {
                description: detail || 'Неверный логин или пароль',
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.page}>
            <div className={styles.card}>
                <div className={styles.header}>
                    <img src="/logo.png" alt="Logo" className={styles.logo} />
                    <h1>Вход в админ-панель</h1>
                </div>

                <form onSubmit={handleSubmit} className={styles.form}>
                    <label className={styles.field}>
                        <span>Логин</span>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="admin"
                            autoComplete="username"
                            disabled={isLoading}
                        />
                    </label>

                    <label className={styles.field}>
                        <span>Пароль</span>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••"
                            autoComplete="current-password"
                            disabled={isLoading}
                        />
                    </label>

                    <md-filled-button
                        type="submit"
                        disabled={isLoading || undefined}
                        className={styles.button}
                    >
                        {isLoading ? 'Вход...' : 'Войти'}
                    </md-filled-button>
                </form>
            </div>
        </div>
    );
};

export default AdminLoginPage;