export default function AIInsightPanel({ summary }) {

  const riskRatio =
    (summary.high_risk / summary.total_customers) * 100;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
      <h3 className="text-lg font-semibold mb-4">
        AI Risk Intelligence Summary
      </h3>

      <p className="text-slate-400 text-sm leading-6">
        Currently {riskRatio.toFixed(1)}% of the portfolio is classified
        as high-risk. Behavioral stress indicators show salary delay
        acceleration and balance erosion patterns consistent with
        pre-delinquency stages.
      </p>
    </div>
  );
}
