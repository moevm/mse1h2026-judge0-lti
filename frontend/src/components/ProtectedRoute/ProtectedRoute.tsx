import { useState, useEffect } from 'react';
import { Navigate, Outlet, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/queries/useAuth';
import {authApi} from '../../lib/api';

interface Props {
    roles?: string[];
    redirectTo?: string;
}
const ProtectedRoute = ({ roles, redirectTo = '/403' }: Props) => {
    const { isAuthenticated, isLoading, refreshUser, getAccessToken, user } = useAuth();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const hasLti = searchParams.has('lti');
    const needsRefresh = hasLti || !getAccessToken();
    const [isRefreshing, setIsRefreshing] = useState(() => needsRefresh);

    useEffect(() => {
        if (!needsRefresh) return;

        authApi.post('/auth/refresh', {}, { withCredentials: true, silent: true })
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
                navigate(redirectTo, { replace: true });
            })
            .finally(() => {
                setIsRefreshing(false);
            });
    }, []);

    if (isLoading || isRefreshing) return <div>Загрузка...</div>;

    if (!isAuthenticated) return <Navigate to={redirectTo} replace />;

    if (roles && roles.length > 0 && !roles.includes(user?.role ?? '')) {
        return <Navigate to={redirectTo} replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;