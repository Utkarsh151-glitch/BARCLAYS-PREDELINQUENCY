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
  currencySymbol = "Rs.",
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
      foreColor: "#5B6472",
      animations: {
        speed: 180,
      },
    },
    stroke: {
      curve: "straight",
      width: 2,
    },
    colors: ["#2F7D5C"],
    grid: {
      borderColor: "#E3E7ED",
      strokeDashArray: 0,
    },
    xaxis: {
      type: "datetime",
      labels: { datetimeUTC: false },
      axisBorder: { color: "#E3E7ED" },
      axisTicks: { color: "#E3E7ED" },
    },
    yaxis: {
      labels: {
        formatter: (value) => `${currencySymbol}${Math.round(value).toLocaleString()}`,
      },
    },
    tooltip: {
      theme: "light",
      x: { format: "dd MMM yyyy" },
      y: {
        formatter: (value) => `${currencySymbol}${Math.round(value).toLocaleString()}`,
      },
    },
  };

  return (
    <div className="app-surface p-4">
      <div className="flex items-center justify-between gap-3 mb-4">
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
