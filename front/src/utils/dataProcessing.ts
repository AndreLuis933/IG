// src/utils/dataProcessing.ts
import type { MetricaDiaria, DateFilterKey } from "../types";

export const processMetricas = (metricas: MetricaDiaria[]): MetricaDiaria[] => {
  let variacaoAcumulada = 0;

  return metricas.map((metrica) => {
    variacaoAcumulada += metrica.variacao_media_preco || 0;

    return {
      ...metrica,
      variacao_media_preco: variacaoAcumulada,
    };
  });
};

export const formatCidadeNome = (nome: string, id: number): string => {
  if (id === 1 || nome.toLowerCase() === "sem cidade") {
    return "Todas as Cidades (Agregado)";
  }
  return nome;
};

const addMonths = (date: Date, months: number) => {
  const d = new Date(date);
  d.setMonth(d.getMonth() + months);
  return d;
};

export const filterMetricasByDate = (
  metricas: MetricaDiaria[],
  filterKey: DateFilterKey,
  customStart?: string | null,
  customEnd?: string | null,
  dataMinima?: string | null
): MetricaDiaria[] => {
  if (!metricas.length) return metricas;

  // intervalo customizado
  if (filterKey === "custom") {
    if (!customStart || !customEnd) return metricas;

    const start = new Date(customStart);
    const end = new Date(customEnd);
    start.setHours(0, 0, 0, 0);
    end.setHours(23, 59, 59, 999);

    return metricas.filter((m) => {
      const d = new Date(m.data);
      return d >= start && d <= end;
    });
  }

  // presets em meses
  const now = new Date();
  now.setHours(23, 59, 59, 999);

  const monthsMap: Record<string, number> = {
    "3m": -3,
    "6m": -6,
    "9m": -9,
    "12m": -12,
    "24m": -24,
  };

  const months = monthsMap[filterKey] ?? -12;
  let start = addMonths(now, months);
  start.setHours(0, 0, 0, 0);

  // limitar pela data mínima do banco
  if (dataMinima) {
    const minDate = new Date(dataMinima);
    minDate.setHours(0, 0, 0, 0);
    if (start < minDate) {
      start = minDate;
    }
  }

  return metricas.filter((m) => {
    const d = new Date(m.data);
    return d >= start && d <= now;
  });
};

export const getAvailableDateOptions = (dataMinima: string | null) => {
  if (!dataMinima) return [];

  const now = new Date();
  const minDate = new Date(dataMinima);
  const diffMonths =
    (now.getFullYear() - minDate.getFullYear()) * 12 +
    (now.getMonth() - minDate.getMonth());

  const options = [
    { key: "3m" as const, label: "Últimos 3 meses", months: 3 },
    { key: "6m" as const, label: "Últimos 6 meses", months: 6 },
    { key: "9m" as const, label: "Últimos 9 meses", months: 9 },
    { key: "12m" as const, label: "Últimos 12 meses", months: 12 },
    { key: "24m" as const, label: "Últimos 24 meses", months: 24 },
  ];

  // filtra apenas opções que cabem no intervalo disponível
  const available = options.filter((opt) => opt.months <= diffMonths);

  // sempre adiciona a opção custom
  available.push({
    key: "custom" as const,
    label: "Período personalizado",
    months: 0,
  });

  return available;
};
