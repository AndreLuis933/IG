import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const MAX_DIAS_POR_RUN = 3;

serve(async (_req) => {
  let dias = 0;

  while (dias < MAX_DIAS_POR_RUN) {
    const { data, error } = await supabase.rpc("processar_metricas_diarias");

    if (error) {
      console.error("Erro RPC:", error);
      return new Response(JSON.stringify({ error: error.message }), {
        headers: { "Content-Type": "application/json" },
        status: 500,
      });
    }

    if (data === false) {
      break;
    }

    dias += 1;
  }

  return new Response(JSON.stringify({ diasProcessados: dias }), {
    headers: { "Content-Type": "application/json" },
    status: 200,
  });
});
