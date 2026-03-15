import './App.css'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import IDEPage from "./pages/IDEPage/IDEPage.tsx";
import Header from "./components/Header/Header.tsx";

function App() {
  return (
    <>
      <Router>
          <Header />
          <Routes>
            <Route path="/" element={<IDEPage />} />
          </Routes>
    </Router>
    </>
  )
}

export default App
