import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCustomers } from "../services/api";
import exportCSV  from "../utils/exportCSV";


export default function Customers() {
    const [customers, setCustomers] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        async function loadCustomers() {
            try {
                const data = await getCustomers();
                setCustomers(data);
            } catch (error) {
                console.error("Failed to load customers:", error);
            }
        }

        loadCustomers();
    }, []);

    return (
        <div className="space-y-10">

            <div>
                <h1 className="text-4xl font-semibold tracking-tight">
                    Customer Portfolio
                </h1>
                <p className="text-slate-400 mt-2">
                    Click on a customer to view detailed risk intelligence
                </p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
                <table className="w-full text-sm">
                    <thead className="bg-slate-800 text-slate-400 uppercase text-xs tracking-wider">
                        <tr>
                            <th className="p-4 text-left">Customer ID</th>
                            <th className="p-4 text-left">Risk Score</th>
                            <th className="p-4 text-left">Risk Level</th>
                            <th className="p-4 text-left">Timestamp</th>
                        </tr>
                    </thead>

                    <tbody>
                        {customers.map((customer) => (
                            <tr
                                key={customer.customer_id}
                                onClick={() => navigate(`/customers/${customer.customer_id}`)}
                                className="cursor-pointer hover:bg-slate-800 transition-all"
                            >
                                <td className="p-4 font-medium">
                                    {customer.customer_id}
                                </td>
                                <td className="p-4">
                                    {customer.risk_score?.toFixed(2)}
                                </td>
                                <td className={`p-4 font-semibold ${customer.risk_level === "HIGH"
                                        ? "text-red-400"
                                        : customer.risk_level === "MEDIUM"
                                            ? "text-amber-400"
                                            : "text-emerald-400"
                                    }`}>
                                    {customer.risk_level}
                                </td>
                                <td className="p-4 text-slate-400">
                                    {customer.timestamp}
                                </td>
                            </tr>
                        ))}
                    </tbody>

                </table>
            </div>
            <button
                onClick={() => exportCSV(customers)}
                className="px-6 py-3 bg-indigo-600 rounded-xl"
            >
                Export CSV
            </button>


        </div>
    );
}
