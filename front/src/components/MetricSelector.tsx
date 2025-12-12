// src/components/MetricSelector.tsx
import { Autocomplete, TextField, Chip } from "@mui/material";
import { METRIC_OPTIONS, type MetricKey } from "../types";

interface MetricSelectorProps {
  metricaSelecionada: MetricKey | null;
  onMetricaChange: (metrica: MetricKey | null) => void;
}

export const MetricSelector = ({
  metricaSelecionada,
  onMetricaChange,
}: MetricSelectorProps) => {
  const selectedOption =
    METRIC_OPTIONS.find((m) => m.key === metricaSelecionada) || null;

  return (
    <Autocomplete
      options={METRIC_OPTIONS}
      getOptionLabel={(option) => option.label}
      value={selectedOption}
      onChange={(_, newValue) =>
        onMetricaChange((newValue?.key as MetricKey) || null)
      }
      renderInput={(params) => (
        <TextField
          {...params}
          label="Selecione a métrica para exibir no gráfico"
          variant="outlined"
        />
      )}
      renderOption={(props, option) => {
        const { key, ...other } = props;
        return (
          <li key={key} {...other}>
            <Chip label={option.label} size="small" sx={{ mr: 1 }} />
            {option.label}
          </li>
        );
      }}
    />
  );
};
