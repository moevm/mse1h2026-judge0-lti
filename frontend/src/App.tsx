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

import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute.tsx";
import AdminStudentsPage from './pages/AdminStudentsPage/AdminStudentsPage.tsx'
import AdminStudentPage from './pages/AdminStudentPage/AdminStudentPage.tsx'
import AdminStudentModulePage from './pages/AdminStudentModulePage/AdminStudentModulePage.tsx'
import AdminStudentTaskPage from './pages/AdminStudentTaskPage/AdminStudentTaskPage.tsx'
import AdminStudentAttemptPage from './pages/AdminStudentAttemptPage/AdminStudentAttemptPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/task" element={<IDEPage />} />
        </Route>
        <Route path="/test" element={<TestPage />} />
        <Route path="/403" element={<ForbiddenPage />} />

        <Route path="/admin" element={<AdminLoginPage />} />

        {/* СТУДЕНТЫ */}
        <Route path="/admin/students" element={<ProtectedAdminRoute />}>
          <Route element={<AdminLayout />}>
            <Route index element={<AdminStudentsPage />} />
            <Route path=":userId" element={<AdminStudentPage />} />
            {/* НОВЫЙ РОУТ: модули студента */}
            <Route path=":userId/modules/:moduleId" element={<AdminStudentModulePage />} />
            {/* НОВЫЙ РОУТ: задачи студента в модуле */}
            <Route path=":userId/modules/:moduleId/tasks/:taskId" element={<AdminStudentTaskPage />} />
            <Route path=":userId/attempts/:attemptId" element={<AdminStudentAttemptPage />} />
          </Route>
        </Route>

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
