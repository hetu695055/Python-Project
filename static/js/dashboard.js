// dashboard.js - Plotly rendering and interactive controls

function renderPlotlyChart(containerId, chartJson) {
  const container = document.getElementById(containerId);
  if (!container || !chartJson) return;

  try {
    const figure = (typeof chartJson === "string") ? JSON.parse(chartJson) : chartJson;
    const config = {
      responsive: true,
      displayModeBar: false
    };

    Plotly.newPlot(containerId, figure.data, figure.layout, config);
  } catch (err) {
    console.error(`Error rendering chart ${containerId}:`, err);
  }
}

// Window resize listener to keep charts perfectly fitted
window.addEventListener("resize", () => {
  const charts = document.querySelectorAll(".chart-container, .chart-container-lg");
  charts.forEach((chart) => {
    if (chart.id && chart.children.length > 0) {
      Plotly.Plots.resize(chart.id);
    }
  });
});

// Setup dynamic trend period buttons (7 Days / 30 Days / 3 Months)
document.addEventListener("DOMContentLoaded", () => {
  const trendButtons = document.querySelectorAll("[data-trend-days]");
  const trendChartEl = document.getElementById("trendChart");

  trendButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      trendButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const days = btn.getAttribute("data-trend-days");
      if (trendChartEl) {
        trendChartEl.style.opacity = "0.5";
      }

      try {
        const response = await fetch(`/api/trends?days=${days}`);
        const data = await response.json();
        if (data.success && data.chart) {
          renderPlotlyChart("trendChart", data.chart);
        }
      } catch (e) {
        console.error("Failed to load trends:", e);
      } finally {
        if (trendChartEl) {
          trendChartEl.style.opacity = "1";
        }
      }
    });
  });
});
