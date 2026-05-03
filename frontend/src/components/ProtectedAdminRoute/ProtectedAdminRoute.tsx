import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/queries/useAuth';

const ProtectedAdminRoute = () => {
    const { isAdmin, isLoading } = useAuth();

    if (isLoading) {
        return <div>Загрузка...</div>;
    }

    return isAdmin ? <Outlet /> : <Navigate to="/admin" replace />;
};

export default ProtectedAdminRoute;