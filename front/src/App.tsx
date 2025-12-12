// src/App.tsx
import { useState } from "react";
import { Container, Typography, Alert, Box } from "@mui/material";
import { CidadeSelector } from "./components/CidadeSelector";
import { MetricSelector } from "./components/MetricSelector";
import { MetricChart } from "./components/MetricChart";
import { DateFilter } from "./components/DateFilter";
import { useCidades } from "./hooks/useCidades";
import { useMetricas } from "./hooks/useMetricas";
import type { Cidade, MetricKey, DateFilterKey } from "./types";
import {
  filterMetricasByDate,
  getAvailableDateOptions,
} from "./utils/dataProcessing";

function App() {
  const [cidadeSelecionada, setCidadeSelecionada] = useState<Cidade | null>(
    null
  );
  const [metricaSelecionada, setMetricaSelecionada] =
    useState<MetricKey | null>("preco_medio_geral");

  const [dateFilterKey, setDateFilterKey] = useState<DateFilterKey>("3m");
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

  const dateOptions = getAvailableDateOptions(dataMinima);

  const metricasFiltradas = filterMetricasByDate(
    metricas,
    dateFilterKey,
    customStartDate,
    customEndDate,
    dataMinima
  );

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
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
