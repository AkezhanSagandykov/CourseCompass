import { Route, Routes } from "react-router-dom";
import Header from "./components/Header.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import ProfessorPage from "./pages/ProfessorPage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import SearchPage from "./pages/SearchPage.jsx";
import VerifyPage from "./pages/VerifyPage.jsx";

export default function App() {
  return (
    <>
      <Header />
      <main className="page">
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/professors/:id" element={<ProfessorPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify" element={<VerifyPage />} />
          <Route path="*" element={<p className="notice">This page does not exist. Go back to the search.</p>} />
        </Routes>
      </main>
    </>
  );
}
