import { useEffect, useState } from "react";
import { getAlerts } from "../services/api";

export default function Alerts() {

  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    async function loadData() {
      const data = await getAlerts();
      setAlerts(data);
    }

    loadData();
  }, []);

  return (
    <div className="space-y-8">

      <h1 className="text-3xl font-semibold text-red-400">
        High Risk Alerts
      </h1>

      <div className="space-y-6">

        {alerts.map((alert, index) => (
          <div key={index}
            className="p-6 bg-red-500/5 border border-red-500/20 rounded-2xl">

            <div className="flex justify-between">
              <div>
                <h3 className="text-lg font-semibold">
                  {alert.customer_id}
                </h3>

                <p className="text-sm text-slate-400 mt-1">
                  Risk Score: {alert.risk_score?.toFixed(2)}
                </p>
              </div>

              <span className="text-red-400 font-semibold">
                HIGH RISK
              </span>
            </div>

            <p className="mt-4 text-sm text-slate-300">
              {alert.recommended_action}
            </p>

          </div>
        ))}

      </div>

    </div>
  );
}
