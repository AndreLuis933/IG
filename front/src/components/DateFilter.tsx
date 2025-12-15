// src/components/DateFilter.tsx
import { useState } from "react";
import {
  Autocomplete,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
} from "@mui/material";
import type { DateFilterKey, DateFilterOption } from "../types";

interface DateFilterProps {
  options: DateFilterOption[];
  dateFilterKey: DateFilterKey;
  onDateFilterKeyChange: (key: DateFilterKey) => void;
  customStartDate: string | null;
  customEndDate: string | null;
  onCustomStartChange: (value: string | null) => void;
  onCustomEndChange: (value: string | null) => void;
  dataMinima: string | null;
}

export const DateFilter = ({
  options,
  dateFilterKey,
  onDateFilterKeyChange,
  customStartDate,
  customEndDate,
  onCustomStartChange,
  onCustomEndChange,
  dataMinima,
}: DateFilterProps) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tempStart, setTempStart] = useState<string | null>(customStartDate);
  const [tempEnd, setTempEnd] = useState<string | null>(customEndDate);

  const selectedOption =
    options.find((opt) => opt.key === dateFilterKey) || null;

  const handleChange = (newValue: DateFilterOption | null) => {
    if (!newValue) return;

    if (newValue.key === "custom") {
      setDialogOpen(true);
    } else {
      onDateFilterKeyChange(newValue.key);
    }
  };

  const handleDialogConfirm = () => {
    onCustomStartChange(tempStart);
    onCustomEndChange(tempEnd);
    onDateFilterKeyChange("custom");
    setDialogOpen(false);
  };

  const handleDialogCancel = () => {
    setTempStart(customStartDate);
    setTempEnd(customEndDate);
    setDialogOpen(false);
  };

  const today = new Date().toISOString().split("T")[0];

  return (
    <>
      <Autocomplete
        options={options}
        getOptionLabel={(option) => option.label}
        value={selectedOption}
        onChange={(_, newValue) => handleChange(newValue)}
        renderInput={(params) => (
          <TextField {...params} label="Período" variant="outlined" />
        )}
      />

      <Dialog
        open={dialogOpen}
        onClose={handleDialogCancel}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Período personalizado</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
            <TextField
              label="Data início"
              type="date"
              fullWidth
              value={tempStart ?? ""}
              onChange={(e) => setTempStart(e.target.value || null)}
              InputLabelProps={{ shrink: true }}
              inputProps={{
                min: dataMinima ?? undefined,
                max: today,
              }}
            />
            <TextField
              label="Data fim"
              type="date"
              fullWidth
              value={tempEnd ?? ""}
              onChange={(e) => setTempEnd(e.target.value || null)}
              InputLabelProps={{ shrink: true }}
              inputProps={{
                min: tempStart ?? dataMinima ?? undefined,
                max: today,
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogCancel}>Cancelar</Button>
          <Button
            onClick={handleDialogConfirm}
            variant="contained"
            disabled={!tempStart || !tempEnd}
          >
            Aplicar
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
