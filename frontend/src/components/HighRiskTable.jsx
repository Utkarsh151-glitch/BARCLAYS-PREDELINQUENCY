export default function HighRiskTable() {

  const customers = [
    { id: "C9001", score: 0.81, action: "EMI Restructure" },
    { id: "C9102", score: 0.78, action: "Payment Reminder" },
    { id: "C9203", score: 0.85, action: "Immediate Outreach" },
  ];

  return (
    <div className="app-surface p-4">

      <p className="text-xs uppercase tracking-widest text-slate-400 mb-6">
        High Risk Customers
      </p>

      <table className="w-full text-sm">
        <thead>
          <tr className="text-slate-400 border-b border-slate-800">
            <th className="text-left pb-3">Customer ID</th>
            <th className="text-left pb-3">Risk Score</th>
            <th className="text-left pb-3">Recommended Action</th>
          </tr>
        </thead>

        <tbody>
          {customers.map((c) => (
            <tr key={c.id} className="border-b border-slate-800 hover:bg-slate-800/40">
              <td className="py-4">{c.id}</td>
              <td className="py-4 text-red-400 font-semibold">
                {c.score}
              </td>
              <td className="py-4 text-slate-300">
                {c.action}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

    </div>
  );
}
