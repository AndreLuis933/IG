// src/App.tsx
import { useState } from "react";
import { Container, Typography, Alert, Box } from "@mui/material";
import { CidadeSelector } from "./components/CidadeSelector";
import { MetricSelector } from "./components/MetricSelector";
import { MetricChart } from "./components/MetricChart";
import { DateFilter } from "./components/DateFilter";
import { useCidades } from "./hooks/useCidades";
import { useMetricas } from "./hooks/useMetricas";
import type {
  Cidade,
  MetricKey,
  DateFilterKey,
  DateFilterOption,
} from "./types";
import {
  filterMetricasByDate,
  getAvailableDateOptions,
} from "./utils/dataProcessing";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/react";

const formatDate = (iso: string) => new Date(iso).toLocaleDateString("pt-BR");

function App() {
  const isProd = process.env.NODE_ENV === "production";
  const [cidadeSelecionada, setCidadeSelecionada] = useState<Cidade | null>(
    null
  );
  const [metricaSelecionada, setMetricaSelecionada] =
    useState<MetricKey | null>("variacao_media_preco");

  const [dateFilterKey, setDateFilterKey] = useState<DateFilterKey>("all");
  const [customStartDate, setCustomStartDate] = useState<string | null>(null);
  const [customEndDate, setCustomEndDate] = useState<string | null>(null);

  const {
    cidades,
    loading: loadingCidades,
    error: errorCidades,
  } = useCidades();
  const {
    metricas,
    dataMinima,
    loading: loadingMetricas,
    error: errorMetricas,
  } = useMetricas(cidadeSelecionada);

  const error = errorCidades || errorMetricas;

  const baseOptions = getAvailableDateOptions(dataMinima);

  const todayIso = new Date().toISOString().split("T")[0];

  const dateOptions: DateFilterOption[] = baseOptions.map((opt) => {
    if (opt.key === "all" && dataMinima) {
      return {
        ...opt,
        label: `Tudo (${formatDate(dataMinima)} - ${formatDate(todayIso)})`,
      };
    }

    if (opt.key === "custom" && customStartDate && customEndDate) {
      return {
        ...opt,
        label: `Personalizado (${formatDate(customStartDate)} - ${formatDate(
          customEndDate
        )})`,
      };
    }

    return opt;
  });

  const metricasFiltradas = filterMetricasByDate(
    metricas,
    dateFilterKey,
    customStartDate,
    customEndDate,
    dataMinima
  );

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {isProd && <Analytics />}
      {isProd && <SpeedInsights />}
      <Typography variant="h4" gutterBottom>
        Métricas Diárias por Cidade
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 3 }}>
        <CidadeSelector
          cidades={cidades}
          cidadeSelecionada={cidadeSelecionada}
          onCidadeChange={setCidadeSelecionada}
          loading={loadingCidades}
        />
      </Box>

      <Box sx={{ mb: 3 }}>
        <MetricSelector
          metricaSelecionada={metricaSelecionada}
          onMetricaChange={setMetricaSelecionada}
        />
      </Box>

      {cidadeSelecionada && dateOptions.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <DateFilter
            options={dateOptions}
            dateFilterKey={dateFilterKey}
            onDateFilterKeyChange={setDateFilterKey}
            customStartDate={customStartDate}
            customEndDate={customEndDate}
            onCustomStartChange={setCustomStartDate}
            onCustomEndChange={setCustomEndDate}
            dataMinima={dataMinima}
          />
        </Box>
      )}

      <MetricChart
        cidadeSelecionada={cidadeSelecionada}
        metricas={metricasFiltradas}
        metricaSelecionada={metricaSelecionada}
        loading={loadingMetricas}
      />
    </Container>
  );
}

export default App;
