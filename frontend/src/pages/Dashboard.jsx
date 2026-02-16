import { useEffect, useState } from "react";
import RiskSummaryCard from "../components/RiskSummaryCard";
import RiskDonutChart from "../components/RiskDonutChart";
import { getPortfolioSummary } from "../services/api";

export default function Dashboard() {
    const [summary, setSummary] = useState(null);

    useEffect(() => {
        async function loadData() {
            const data = await getPortfolioSummary();
            setSummary(data);
        }

        loadData();
    }, []);

    if (!summary) {
        return <div className="text-slate-400">Loading portfolio data...</div>;
    }

    return (
        <div className="space-y-14">

            <div>
                <h1 className="text-4xl font-semibold tracking-tight">
                    Enterprise Risk Portfolio
                </h1>
                <p className="text-slate-400 mt-2">
                    Real-time behavioral credit risk intelligence
                </p>
            </div>
            <div className="flex gap-4">
                <button className="px-4 py-2 bg-slate-800 rounded-xl">7 Days</button>
                <button className="px-4 py-2 bg-slate-800 rounded-xl">30 Days</button>
                <button className="px-4 py-2 bg-slate-800 rounded-xl">90 Days</button>
            </div>


            {/* SUMMARY CARDS ONLY */}
            <div className="grid grid-cols-4 gap-8">
                <RiskSummaryCard
                    title="Total Customers"
                    value={summary.total_customers}
                    type="neutral"
                />
                <RiskSummaryCard
                    title="High Risk"
                    value={summary.high_risk}
                    type="high"
                />
                <RiskSummaryCard
                    title="Medium Risk"
                    value={summary.medium_risk}
                    type="medium"
                />
                <RiskSummaryCard
                    title="Low Risk"
                    value={summary.low_risk}
                    type="low"
                />
            </div>

            {/* SMALL SNAPSHOT DONUT */}
            <div className="w-80">
                <RiskDonutChart summary={summary} />
            </div>

        </div>
    );
}
