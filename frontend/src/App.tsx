import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

import LandingPage from './pages/LandingPage/LandingPage.tsx'
import IDEPage from './pages/IDEPage/IDEPage.tsx'
import TestPage from './pages/TestPage/TestPage.tsx'
import NotFoundPage from './pages/NotFoundPage/NotFoundPage.tsx'
import ForbiddenPage from './pages/ForbiddenPage/ForbiddenPage.tsx'

import ProtectedAdminRoute from './components/ProtectedAdminRoute/ProtectedAdminRoute.tsx'
import AdminLayout from './components/AdminLayout/AdminLayout.tsx'
import AdminModulesPage from './pages/AdminModulesPage/AdminModulesPage.tsx'
import AdminModuleTasksPage from './pages/AdminModuleTasksPage/AdminModuleTasksPage.tsx'
import AdminTasksPage from "./pages/AdminTasksPage/AdminTasksPage.tsx"
import AdminTaskEditPage from "./pages/AdminTaskEditPage/AdminTaskEditPage.tsx"
import AdminLoginPage from './pages/AdminLoginPage/AdminLoginPage.tsx'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/task" element={<IDEPage />} />
        <Route path="/test" element={<TestPage />} />
        <Route path="/403" element={<ForbiddenPage />} />
        
        <Route path="/admin" element={<AdminLoginPage />} />
        
        <Route path="/admin/modules" element={<ProtectedAdminRoute />}>
          <Route element={<AdminLayout />}>
            <Route index element={<AdminModulesPage />} />
            <Route path=":moduleId" element={<AdminModuleTasksPage />} />
          </Route>
        </Route>
        
        <Route path="/admin/tasks" element={<ProtectedAdminRoute />}>
          <Route element={<AdminLayout />}>
            <Route index element={<AdminTasksPage />} />
            <Route path=":taskId" element={<AdminTaskEditPage />} />
            <Route path="new" element={<AdminTaskEditPage />} />
          </Route>
        </Route>
        
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  )
}

export default App