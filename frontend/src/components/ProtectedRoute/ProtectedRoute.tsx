import { useState, useEffect } from 'react';
import { Navigate, Outlet, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/queries/useAuth';
import api from '../../lib/api';

const ProtectedRoute = () => {
    const { isAuthenticated, isLoading, refreshUser, getAccessToken } = useAuth();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const hasLti = searchParams.has('lti');
    const needsRefresh = hasLti || !getAccessToken();

    const [isRefreshing, setIsRefreshing] = useState(() => needsRefresh);

    useEffect(() => {
        if (!needsRefresh) return;

        api.post('/auth/refresh', {}, { withCredentials: true, silent: true })
            .then(async res => {
                localStorage.setItem('access_token', res.data.access_token);
                await refreshUser();
                if (hasLti) {
                    searchParams.delete('lti');
                    const rest = searchParams.toString();
                    navigate(rest ? `/?${rest}` : '/', { replace: true });
                }
            })
            .catch(() => {
                navigate('/403', { replace: true });
            })
            .finally(() => {
                setIsRefreshing(false);
            });
    }, []);

    if (isLoading || isRefreshing) return <div>Загрузка...</div>;

    return isAuthenticated ? <Outlet /> : <Navigate to="/403" replace />;
};

export default ProtectedRoute;