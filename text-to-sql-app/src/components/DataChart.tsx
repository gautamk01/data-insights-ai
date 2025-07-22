"use client";

import { useEffect, useRef } from "react";
import { Chart, ChartConfiguration, registerables } from "chart.js";
Chart.register(...registerables);

interface DataChartProps {
  type: string;
  data: any;
}

const DataChart = ({ type, data }: DataChartProps) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstanceRef = useRef<Chart | null>(null);

  useEffect(() => {
    // Destroy the previous chart instance before creating a new one
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
    }

    if (chartRef.current && data) {
      const ctx = chartRef.current.getContext("2d");
      if (!ctx) return;

      const actualChartType = data.type || type;

      const chartConfig: ChartConfiguration = {
        type: actualChartType,
        data: {
          labels: data.labels || [],
          datasets: data.datasets || [],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: `${
                actualChartType.charAt(0).toUpperCase() +
                actualChartType.slice(1)
              } Chart`,
            },
            legend: {
              display: true,
              position: "top",
            },
          },
        },
      };

      const chartsWithoutScales = ["pie", "doughnut", "polarArea"];
      if (!chartsWithoutScales.includes(actualChartType.toLowerCase())) {
        if (chartConfig.options) {
          chartConfig.options.scales = data.options?.scales || {
            y: { beginAtZero: true },
          };
        }
      } else {
        if (chartConfig.options?.plugins) {
          chartConfig.options.plugins.tooltip = {
            callbacks: {
              label: (context: any) => {
                const label = context.label || "";
                const value = context.raw || 0;
                const total = context.dataset.data.reduce(
                  (sum: number, val: number) => sum + val,
                  0
                );
                const percentage =
                  total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                return `${label}: ${value} (${percentage}%)`;
              },
            },
          };
        }
      }

      chartInstanceRef.current = new Chart(ctx, chartConfig);
    }

    // Cleanup: destroy chart on component unmount
    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
    };
  }, [data, type]); // Re-run effect if data or type changes

  return (
    <div className="chart-container">
      <h3>📈 Visualization</h3>
      <div className="chart-wrapper">
        <canvas ref={chartRef}></canvas>
      </div>
    </div>
  );
};

export default DataChart;
