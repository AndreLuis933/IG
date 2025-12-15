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

// agora inclui "all" e "custom"
export type DateFilterKey =
  | "all"
  | "3m"
  | "6m"
  | "9m"
  | "12m"
  | "24m"
  | "custom";

// tipo comum para opções de filtro de data
export interface DateFilterOption {
  key: DateFilterKey;
  label: string;
  months?: number; // usado só para os presets em meses
}
