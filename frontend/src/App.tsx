import './App.css'

import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import {useState} from "react"

import IDEPage from "./pages/IDEPage/IDEPage.tsx"
import TestPage from "./pages/TestPage/TestPage.tsx" // временная страница
import NotFoundPage from "./pages/NotFoundPage/NotFoundPage.tsx";
import ForbiddenPage from "./pages/ForbiddenPage/ForbiddenPage.tsx";

function App() {
  const [language, setLanguage] = useState("python");

  return (
      <Router>
        <Routes>
          <Route path="/" element={<IDEPage language={language} setLanguage={setLanguage} />} />
          <Route path="/test" element={<TestPage />} />
          <Route path="/403" element={<ForbiddenPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
  )
}

export default App