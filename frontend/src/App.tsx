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
import AdminRolesPage from './pages/AdminRolesPage/AdminRolesPage.tsx'

import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute.tsx";
import AdminStudentsPage from './pages/AdminStudentsPage/AdminStudentsPage.tsx'
import AdminStudentPage from './pages/AdminStudentPage/AdminStudentPage.tsx'
import AdminStudentModulePage from './pages/AdminStudentModulePage/AdminStudentModulePage.tsx'
import AdminStudentTaskPage from './pages/AdminStudentTaskPage/AdminStudentTaskPage.tsx'
import AdminStudentAttemptPage from './pages/AdminStudentAttemptPage/AdminStudentAttemptPage.tsx'
import LtiKeyPage from './pages/LtiKeyPage/LtiKeyPage.tsx'

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/task" element={<IDEPage />} />
        </Route>
        <Route path="/lti-key" element={<LtiKeyPage />} />
        <Route path="/test" element={<TestPage />} />
        <Route path="/403" element={<ForbiddenPage />} />

        <Route path="/admin" element={<AdminLoginPage />} />

        <Route element={<ProtectedAdminRoute />}>
          <Route element={<AdminLayout />}>

            {/* Студенты */}
            <Route path="/admin/students" element={<AdminStudentsPage />} />
            <Route path="/admin/students/:userId" element={<AdminStudentPage />} />
            <Route path="/admin/students/:userId/modules/:moduleId" element={<AdminStudentModulePage />} />
            <Route path="/admin/students/:userId/modules/:moduleId/tasks/:taskId" element={<AdminStudentTaskPage />} />
            <Route path="/admin/students/:userId/attempts/:attemptId" element={<AdminStudentAttemptPage />} />

            {/* Модули */}
            <Route path="/admin/modules" element={<AdminModulesPage />} />
            <Route path="/admin/modules/:moduleId" element={<AdminModuleTasksPage />} />

            {/* Задачи */}
            <Route path="/admin/tasks" element={<AdminTasksPage />} />
            <Route path="/admin/tasks/:taskId" element={<AdminTaskEditPage />} />
            <Route path="/admin/tasks/new" element={<AdminTaskEditPage />} />

            {/* Роли */}
            <Route path="/admin/roles" element={<AdminRolesPage />} />
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  )
}

export default App
