// src/types.ts
export interface Cidade {
  id: number;
  nome: string;
}

export interface MetricaDiaria {
  data: string;
  cidade_id: number;
  variacao_media_preco: number;
  num_produtos_disponiveis: number;
  preco_medio_geral: number;
}

export const METRIC_OPTIONS = [
  { key: "variacao_media_preco", label: "Variação acumulada de preço" },
  { key: "num_produtos_disponiveis", label: "Nº produtos disponíveis" },
  { key: "preco_medio_geral", label: "Preço médio geral" },
] as const;

export type MetricKey = (typeof METRIC_OPTIONS)[number]["key"];

export const DATE_FILTER_OPTIONS = [
  { key: "3m", label: "Últimos 3 meses", months: 3 },
  { key: "6m", label: "Últimos 6 meses", months: 6 },
  { key: "9m", label: "Últimos 9 meses", months: 9 },
  { key: "12m", label: "Últimos 12 meses", months: 12 },
  { key: "24m", label: "Últimos 24 meses", months: 24 },
  { key: "custom", label: "Período personalizado" },
] as const;

export type DateFilterKey = (typeof DATE_FILTER_OPTIONS)[number]["key"];
