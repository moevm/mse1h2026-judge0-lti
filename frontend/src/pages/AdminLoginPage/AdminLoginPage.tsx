import { type FormEvent, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { jwtDecode } from 'jwt-decode';
import { authApi } from '../../api/auth.api';
import styles from './AdminLoginPage.module.scss';

interface JwtPayload {
    role: string;
    type: string;
    exp: number;
}

const AdminLoginPage = () => {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const decoded = jwtDecode<JwtPayload>(token);
                if (decoded.type === 'access' && decoded.exp * 1000 > Date.now() && decoded.role === 'admin') {
                    navigate('/admin/modules', { replace: true });
                } else {
                    localStorage.removeItem('access_token');
                }
            } catch {
                localStorage.removeItem('access_token');
            }
        }
    }, [navigate]);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!username.trim() || !password.trim()) {
            toast.error('Заполните все поля');
            return;
        }

        setIsLoading(true);
        try {
            const { access_token } = await authApi.login({ username, password });
            localStorage.setItem('access_token', access_token);
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