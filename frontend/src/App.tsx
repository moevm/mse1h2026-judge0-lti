import './App.css'
import { BrowserRouter as Router, Routes, Route, Outlet } from "react-router-dom";
import IDEPage from "./pages/IDEPage/IDEPage.tsx";
import NotFoundPage from "./pages/NotFoundPage/NotFoundPage.tsx";
import TestPage from "./pages/TestPage/TestPage.tsx"; // временная страница
import Header from "./components/Header/Header.tsx";
import {useState} from "react";

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
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
  )
}

export default App