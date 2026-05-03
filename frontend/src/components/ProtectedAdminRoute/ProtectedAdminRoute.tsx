import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

interface JwtPayload {
    role: string;
    type: string;
    exp: number;
}

const ProtectedAdminRoute = () => {
    const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setIsAuthorized(false);
            return;
        }

        try {
            const decoded = jwtDecode<JwtPayload>(token);
            const isValid = decoded.type === 'access' && decoded.exp * 1000 > Date.now() && decoded.role === 'admin';
            setIsAuthorized(isValid);
            if (!isValid) {
                localStorage.removeItem('access_token');
            }
        } catch {
            localStorage.removeItem('access_token');
            setIsAuthorized(false);
        }
    }, []);

    if (isAuthorized === null) {
        return <div>Загрузка...</div>;
    }

    return isAuthorized ? <Outlet /> : <Navigate to="/admin" replace />;
};

export default ProtectedAdminRoute;
