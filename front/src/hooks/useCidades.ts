// src/hooks/useCidades.ts
import { useEffect, useState } from "react";
import { supabase } from "../services/supabaseClient";
import type { Cidade } from "../types";
import { formatCidadeNome } from "../utils/dataProcessing";

export const useCidades = () => {
  const [cidades, setCidades] = useState<Cidade[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCidades = async () => {
      setLoading(true);
      setError(null);

      const { data, error } = await supabase
        .from("cidades")
        .select("id, nome")
        .order("nome", { ascending: true });

      if (error) {
        setError(`Erro ao carregar cidades: ${error.message}`);
      } else {
        const cidadesFormatadas = (data || []).map((cidade) => ({
          ...cidade,
          nome: formatCidadeNome(cidade.nome, cidade.id),
        }));
        setCidades(cidadesFormatadas);
      }

      setLoading(false);
    };

    fetchCidades();
  }, []);

  return { cidades, loading, error };
};
