import './App.css'
import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import IDEPage from "./pages/IDEPage/IDEPage.tsx";
// import Header from "./components/Header/Header.tsx";
import {useState} from "react";

function App() {
    const [language, setLanguage] = useState("python");

    return (
        <Router>
            <div className="app">
                <main className="content">
                    <Routes>
                        <Route
                            path="/"
                            element={
                                <IDEPage
                                    language={language}
                                    setLanguage={setLanguage}
                                />
                            }
                        />
                        <Route path="*" element={<div style={{ color: "#fff" }}>404 Not Found</div>} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App