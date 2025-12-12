// src/components/MetricChart.tsx
import { Box, Typography, Alert, CircularProgress } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import type { Cidade, MetricaDiaria, MetricKey } from "../types";
import { METRIC_OPTIONS } from "../types";

interface MetricChartProps {
  cidadeSelecionada: Cidade | null;
  metricas: MetricaDiaria[];
  metricaSelecionada: MetricKey | null;
  loading: boolean;
}

export const MetricChart = ({
  cidadeSelecionada,
  metricas,
  metricaSelecionada,
  loading,
}: MetricChartProps) => {
  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!cidadeSelecionada) {
    return null;
  }

  if (!metricaSelecionada) {
    return (
      <Alert severity="info">
        Selecione uma métrica para visualizar o gráfico.
      </Alert>
    );
  }

  if (metricas.length === 0) {
    return (
      <Alert severity="warning">
        Não há métricas para os filtros selecionados nesta cidade.
      </Alert>
    );
  }

  const metricLabel =
    METRIC_OPTIONS.find((m) => m.key === metricaSelecionada)?.label || "";
  const xAxisData = metricas.map((m) => new Date(m.data));
  const yAxisData = metricas.map((m) => m[metricaSelecionada]);

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        {metricLabel} - {cidadeSelecionada.nome}
      </Typography>
      <Box sx={{ width: "100%", height: 400 }}>
        <LineChart
          xAxis={[
            {
              data: xAxisData,
              scaleType: "time",
              valueFormatter: (date) =>
                new Date(date).toLocaleDateString("pt-BR"),
            },
          ]}
          series={[
            {
              data: yAxisData,
              label: metricLabel,
              showMark: false,
            },
          ]}
          height={400}
        />
      </Box>
    </Box>
  );
};
