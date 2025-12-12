// src/hooks/useMetricas.ts
import { useEffect, useState } from "react";
import { supabase } from "@/services/supabaseClient";
import type { Cidade, MetricaDiaria } from "../types";
import { processMetricas } from "../utils/dataProcessing";

export const useMetricas = (cidadeSelecionada: Cidade | null) => {
  const [metricas, setMetricas] = useState<MetricaDiaria[]>([]);
  const [dataMinima, setDataMinima] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetricas = async () => {
      if (!cidadeSelecionada) {
        setMetricas([]);
        setDataMinima(null);
        return;
      }

      setLoading(true);
      setError(null);

      const { data, error } = await supabase
        .from("metricas_diarias_cidade")
        .select(
          "data, cidade_id, variacao_media_preco, num_produtos_disponiveis, preco_medio_geral"
        )
        .eq("cidade_id", cidadeSelecionada.id)
        .order("data", { ascending: true });

      if (error) {
        setError(`Erro ao carregar métricas: ${error.message}`);
        setMetricas([]);
        setDataMinima(null);
      } else {
        const metricasProcessadas = processMetricas(data || []);
        setMetricas(metricasProcessadas);

        // pega a data mais antiga
        if (metricasProcessadas.length > 0) {
          setDataMinima(metricasProcessadas[0].data);
        } else {
          setDataMinima(null);
        }
      }

      setLoading(false);
    };

    fetchMetricas();
  }, [cidadeSelecionada]);

  return { metricas, dataMinima, loading, error };
};
