// src/components/CidadeSelector.tsx
import {
  Autocomplete,
  TextField,
  Box,
  CircularProgress,
  Alert,
} from "@mui/material";
import type { Cidade } from "../types";

interface CidadeSelectorProps {
  cidades: Cidade[];
  cidadeSelecionada: Cidade | null;
  onCidadeChange: (cidade: Cidade | null) => void;
  loading: boolean;
}

export const CidadeSelector = ({
  cidades,
  cidadeSelecionada,
  onCidadeChange,
  loading,
}: CidadeSelectorProps) => {
  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (cidades.length === 0) {
    return (
      <Alert severity="warning">
        Nenhuma cidade encontrada na tabela "cidades".
      </Alert>
    );
  }

  return (
    <Autocomplete
      options={cidades}
      getOptionLabel={(option) => option.nome}
      value={cidadeSelecionada}
      onChange={(_, newValue) => onCidadeChange(newValue)}
      renderInput={(params) => (
        <TextField {...params} label="Selecione a cidade" variant="outlined" />
      )}
    />
  );
};
