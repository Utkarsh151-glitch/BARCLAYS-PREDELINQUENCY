import Chart from "react-apexcharts";

const RANGE_OPTIONS = [
  { label: "7 Days", value: "7D" },
  { label: "30 Days", value: "30D" },
  { label: "90 Days", value: "90D" },
];

export default function SavingsTrendChart({
  seriesData,
  selectedRange,
  onRangeChange,
  currencySymbol = "₹",
}) {
  const chartSeries = [
    {
      name: "Net Savings",
      data: seriesData.map((point) => ({
        x: point.date,
        y: point.net_savings,
      })),
    },
  ];

  const options = {
    chart: {
      id: "savings-trend",
      toolbar: { show: false },
      zoom: { enabled: false },
      foreColor: "#94a3b8",
    },
    stroke: {
      curve: "smooth",
      width: 3,
    },
    colors: ["#34d399"],
    grid: {
      borderColor: "#1e293b",
      strokeDashArray: 4,
    },
    xaxis: {
      type: "datetime",
      labels: { datetimeUTC: false },
      axisBorder: { color: "#334155" },
      axisTicks: { color: "#334155" },
    },
    yaxis: {
      labels: {
        formatter: (value) => `${currencySymbol}${Math.round(value).toLocaleString()}`,
      },
    },
    tooltip: {
      theme: "dark",
      x: { format: "dd MMM yyyy" },
      y: {
        formatter: (value) => `${currencySymbol}${Math.round(value).toLocaleString()}`,
      },
    },
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
      <div className="flex items-center justify-between gap-3 mb-5">
        <h3 className="text-lg font-semibold">Savings Trend</h3>
        <div className="flex gap-2">
          {RANGE_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => onRangeChange(option.value)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                selectedRange === option.value
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-400/40"
                  : "bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {seriesData.length === 0 ? (
        <div className="text-slate-400 text-sm">No savings trend data available</div>
      ) : (
        <Chart options={options} series={chartSeries} type="line" height={320} />
      )}
    </div>
  );
}
