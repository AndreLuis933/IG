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

const formatDate = (iso: string) => new Date(iso).toLocaleDateString("pt-BR");

function App() {
  const [cidadeSelecionada, setCidadeSelecionada] = useState<Cidade | null>(
    null
  );
  const [metricaSelecionada, setMetricaSelecionada] =
    useState<MetricKey | null>("preco_medio_geral");

  // agora default é "all"
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

  // opções base limitadas pela data mínima
  const baseOptions = getAvailableDateOptions(dataMinima);

  // agora ajustamos os labels de "all" e "custom" para mostrar o intervalo
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
