import './App.css'

import { BrowserRouter as Router, Routes, Route, Outlet } from "react-router-dom"
import {useState} from "react"

import IDEPage from "./pages/IDEPage/IDEPage.tsx"
import TestPage from "./pages/TestPage/TestPage.tsx" // временная страница
import NotFoundPage from "./pages/NotFoundPage/NotFoundPage.tsx";
import ForbiddenPage from "./pages/ForbiddenPage/ForbiddenPage.tsx";

import Header from "./components/Header/Header.tsx"

function App() {
  const [language, setLanguage] = useState("python");
  return (
      <Router>
        <Routes>
          {/* Маршруты с хедером */}
          <Route element={
            <div className="app">
              <Header language={language} setLanguage={setLanguage} />
              <main className="content">
                <Outlet />
              </main>
            </div>
          }>
            <Route path="/" element={<IDEPage language={language} />} />
          </Route>

          {/* 404 — без хедера */}
          <Route path="/test" element={<TestPage />} />
          <Route path="/403" element={<ForbiddenPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
  )
}

export default App