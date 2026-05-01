import './App.css'

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

import IDEPage from './pages/IDEPage/IDEPage.tsx'
import TestPage from './pages/TestPage/TestPage.tsx'
import NotFoundPage from './pages/NotFoundPage/NotFoundPage.tsx'
import ForbiddenPage from './pages/ForbiddenPage/ForbiddenPage.tsx'
import AdminLayout from './components/AdminLayout/AdminLayout.tsx'
import AdminModulesPage from './pages/AdminModulesPage/AdminModulesPage.tsx'
import AdminModuleTasksPage from './pages/AdminModuleTasksPage/AdminModuleTasksPage.tsx'

function App() {
  return (
      <Router>
        <Routes>
          <Route path="/" element={<IDEPage />} />
          <Route path="/test" element={<TestPage />} />
          <Route path="/403" element={<ForbiddenPage />} />
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminModulesPage />} />
            <Route path="modules" element={<AdminModulesPage />} />
            <Route path="modules/:moduleId" element={<AdminModuleTasksPage />} />
            <Route path="modules/:moduleId/tasks" element={<AdminModuleTasksPage />} />
            <Route path="tasks" element={<NotFoundPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
  )
}

export default App
