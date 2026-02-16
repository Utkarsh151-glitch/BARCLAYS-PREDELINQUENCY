import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getCustomerById, getAggregator } from "../services/api";

export default function CustomerDetail() {
  const { id } = useParams();

  const [customer, setCustomer] = useState(null);
  const [aggregator, setAggregator] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const customerData = await getCustomerById(id);
        setCustomer(customerData);

        const aggData = await getAggregator(id);
        setAggregator(aggData);
      } catch (err) {
        console.error("Failed to load customer:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [id]);

  if (loading) {
    return (
      <div className="text-slate-400 text-lg">
        Loading customer intelligence...
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="text-red-400">
        Customer not found.
      </div>
    );
  }

  return (
    <div className="space-y-10">

      {/* HEADER */}
      <div>
        <h1 className="text-3xl font-semibold">
          Customer Intelligence: {customer.customer_id}
        </h1>
        <p className="text-slate-400 mt-1">
          Behavioral risk analysis & financial intelligence
        </p>
      </div>

      {/* RISK PROFILE */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-lg font-semibold mb-4">Risk Profile</h3>

        <div className="grid grid-cols-3 gap-6 text-slate-300">
          <InfoCard
            label="Risk Score"
            value={
              customer.risk_score
                ? Number(customer.risk_score).toFixed(4)
                : "-"
            }
          />

          <InfoCard
            label="Risk Level"
            value={customer.risk_level || "-"}
          />

          <InfoCard
            label="Recommended Action"
            value={customer.recommended_action || "-"}
          />
        </div>
      </div>

      {/* EARLY WARNING SIGNALS */}
      {customer.early_signals && customer.early_signals.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-lg font-semibold mb-4">
            Early Warning Signals
          </h3>

          <div className="space-y-2 text-slate-300">
            {customer.early_signals.map((signal, index) => (
              <div key={index}>
                {signal.factor} → {signal.raw_value}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ACCOUNT AGGREGATOR INTELLIGENCE */}
      {aggregator && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 space-y-6">

          <h3 className="text-xl font-semibold">
            Financial Intelligence Layer (Account Aggregator)
          </h3>

          <div className="grid grid-cols-3 gap-6 text-slate-300">

            <InfoCard label="Linked Banks" value={aggregator.linked_banks ?? "-"} />
            <InfoCard label="Monthly Inflow" value={`₹${aggregator.monthly_inflow ?? "-"}`} />
            <InfoCard label="EMI Commitments" value={aggregator.emi_commitments ?? "-"} />
            <InfoCard label="Auto Debit Failures" value={aggregator.auto_debit_failures ?? "-"} />
            <InfoCard label="Salary Stability" value={aggregator.salary_stability ?? "-"} />
            <InfoCard label="Liquidity Stress" value={aggregator.liquidity_index ?? "-"} />
            <InfoCard label="Savings Trend" value={aggregator.savings_trend ?? "-"} />
            <InfoCard label="Spend Volatility" value={aggregator.spend_volatility ?? "-"} />

          </div>

          {/* Composite Score */}
          {aggregator.composite_risk_score && (
            <div className="mt-8 p-6 bg-slate-800 rounded-xl border border-indigo-500/20">

              <h4 className="text-lg font-semibold mb-2">
                Composite Intelligence Score
              </h4>

              <div className="text-3xl font-bold text-indigo-400">
                {aggregator.composite_risk_score}
              </div>

              <p className="text-sm text-slate-400 mt-2">
                Blended behavioral delinquency risk with multi-bank liquidity signals.
              </p>

            </div>
          )}

        </div>
      )}

    </div>
  );
}


/* -----------------------
   Info Card Component
------------------------*/
function InfoCard({ label, value }) {
  return (
    <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700">
      <p className="text-xs uppercase text-slate-400">{label}</p>
      <p className="text-lg font-semibold mt-1">
        {value !== undefined && value !== null ? value : "-"}
      </p>
    </div>
  );
}
