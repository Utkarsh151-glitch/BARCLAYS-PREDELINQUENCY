export default function AccountAggregator() {

  return (
    <div className="space-y-12">

      <div>
        <h1 className="text-4xl font-semibold">
          Account Aggregator Intelligence Layer
        </h1>
        <p className="text-slate-400 mt-2">
          Multi-bank behavioral data ingestion & feature engineering pipeline
        </p>
      </div>

      {/* Flow Architecture */}
      <div className="grid grid-cols-5 gap-6 items-center text-center">

        <Node title="Customer" />
        <Arrow />
        <Node title="AA Consent Layer" />
        <Arrow />
        <Node title="Multi-Bank Data Pull" />

      </div>

      <div className="grid grid-cols-5 gap-6 items-center text-center mt-8">

        <Node title="Feature Engineering" />
        <Arrow />
        <Node title="Behavioral Signals" />
        <Arrow />
        <Node title="AI Risk Engine" />

      </div>

      {/* Feature Explanation */}
      <div className="bg-slate-900/60 border border-slate-800 p-8 rounded-2xl">

        <h2 className="text-xl font-semibold mb-6">
          Extracted Behavioral Signals
        </h2>

        <ul className="space-y-3 text-slate-300">
          <li>• Salary credit delay patterns</li>
          <li>• Savings balance trend slope</li>
          <li>• EMI auto-debit failure frequency</li>
          <li>• UPI lending transaction spikes</li>
          <li>• Discretionary spend volatility</li>
          <li>• ATM liquidity stress withdrawals</li>
        </ul>

      </div>

      <div className="bg-indigo-500/10 border border-indigo-500/20 p-6 rounded-2xl">
        <p className="text-slate-300">
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
    <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
      <h3 className="text-sm font-semibold text-slate-300">
        {title}
      </h3>
    </div>
  );
}

function Arrow() {
  return (
    <div className="text-slate-500 text-xl">
      →
    </div>
  );
}
