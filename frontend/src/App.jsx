import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout";

import Dashboard from "./pages/Dashboard";
import PortfolioRisk from "./pages/PortfolioRisk";
import Customers from "./pages/Customers";
import CustomerDetail from "./pages/CustomerDetail";
import Alerts from "./pages/Alerts";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>

          <Route index element={<Dashboard />} />
          <Route path="portfolio-risk" element={<PortfolioRisk />} />
          <Route path="customers" element={<Customers />} />
          <Route path="customers/:id" element={<CustomerDetail />} />
          <Route path="alerts" element={<Alerts />} />

        </Route>
      </Routes>
    </Router>
  );
}
