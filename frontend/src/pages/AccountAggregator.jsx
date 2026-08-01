export default function AccountAggregator() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">
          Account Aggregator Intelligence Layer
        </h1>
        <p className="text-slate-400 mt-1">
          Multi-bank behavioral data ingestion and feature engineering pipeline
        </p>
      </div>

      <div className="grid grid-cols-5 gap-3 items-center text-center">
        <Node title="Customer" />
        <Arrow />
        <Node title="AA Consent Layer" />
        <Arrow />
        <Node title="Multi-Bank Data Pull" />
      </div>

      <div className="grid grid-cols-5 gap-3 items-center text-center">
        <Node title="Feature Engineering" />
        <Arrow />
        <Node title="Behavioral Signals" />
        <Arrow />
        <Node title="Risk Engine" />
      </div>

      <div className="app-surface p-4">
        <h2 className="text-xl font-semibold mb-4">
          Extracted Behavioral Signals
        </h2>

        <ul className="space-y-2 text-slate-300 text-sm">
          <li>- Salary credit delay patterns</li>
          <li>- Savings balance trend slope</li>
          <li>- EMI auto-debit failure frequency</li>
          <li>- UPI lending transaction spikes</li>
          <li>- Discretionary spend volatility</li>
          <li>- ATM liquidity stress withdrawals</li>
        </ul>
      </div>

      <div className="app-surface border-l-4 border-l-indigo-500 p-4">
        <p className="text-slate-300 text-sm leading-6">
          Unlike traditional CIBIL bureau scoring, this system analyzes
          real-time behavioral liquidity stress across multiple banks
          using RBI-compliant Account Aggregator framework.
        </p>
      </div>
    </div>
  );
}

function Node({ title }) {
  return (
    <div className="app-surface p-4">
      <h3 className="text-sm font-semibold text-slate-300">
        {title}
      </h3>
    </div>
  );
}

function Arrow() {
  return (
    <div className="text-slate-500 text-sm font-mono">
      -&gt;
    </div>
  );
}
