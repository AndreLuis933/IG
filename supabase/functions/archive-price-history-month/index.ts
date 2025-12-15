import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    console.log(
      "🔍 Buscando a data mais antiga para arquivar na tabela historico_precos..."
    );

    // 1) Buscar a data_fim mais antiga
    const { data: oldestRecord, error: oldestError } = await supabase
      .from("historico_precos")
      .select("data_fim")
      .not("data_fim", "is", null)
      .order("data_fim", { ascending: true })
      .limit(1)
      .single();

    if (oldestError || !oldestRecord) {
      return new Response(
        JSON.stringify({
          success: false,
          message:
            "Nenhum registro com data_fim encontrado na tabela historico_precos",
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
          status: 200,
        }
      );
    }

    const oldestDate = new Date(oldestRecord.data_fim);

    const monthToArchive = new Date(
      oldestDate.getFullYear(),
      oldestDate.getMonth(),
      1
    );

    const today = new Date();
    const cutoffMonth = new Date(today.getFullYear(), today.getMonth() - 6, 1);

    console.log(
      `📅 Mês mais antigo no banco (historico_precos): ${
        monthToArchive.toISOString().split("T")[0]
      }`
    );
    console.log(
      `📅 Mês de corte (6 meses atrás): ${
        cutoffMonth.toISOString().split("T")[0]
      }`
    );

    // 2) Verificar se o mês a ser arquivado está fora da janela de 6 meses
    if (monthToArchive >= cutoffMonth) {
      return new Response(
        JSON.stringify({
          success: false,
          message: `O mês mais antigo (${
            monthToArchive.toISOString().split("T")[0]
          }) da tabela historico_precos ainda está dentro da janela de 6 meses. Nada para arquivar.`,
          oldest_month_in_db: monthToArchive.toISOString().split("T")[0],
          cutoff_month: cutoffMonth.toISOString().split("T")[0],
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
          status: 200,
        }
      );
    }

    // 3) Definir o mês a ser arquivado
    const year = monthToArchive.getFullYear();
    const month = monthToArchive.getMonth();

    const startOfMonth = monthToArchive;
    const endOfMonth = new Date(year, month + 1, 1);

    const startStr = startOfMonth.toISOString().split("T")[0];
    const endStr = endOfMonth.toISOString().split("T")[0];

    const fileName = `price_history_${year}_${String(month + 1).padStart(
      2,
      "0"
    )}.csv`;
    const storagePath = `price-history/${fileName}`;

    console.log(
      `📦 Arquivando mês (historico_precos): ${year}-${String(
        month + 1
      ).padStart(2, "0")}`
    );
    console.log(`📂 Caminho no Storage: ${storagePath}`);

    // 3.1) Verificar se o arquivo já existe no Storage
    const { data: existingFiles } = await supabase.storage
      .from("archive-data")
      .list("price-history", {
        search: fileName,
      });

    if (existingFiles && existingFiles.length > 0) {
      return new Response(
        JSON.stringify({
          success: false,
          message: `Arquivo ${fileName} já existe no Storage. Operação cancelada para evitar duplicação.`,
          file: storagePath,
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
          status: 200,
        }
      );
    }

    // 4) Contar quantas linhas serão arquivadas
    const { count: expectedCount, error: countError } = await supabase
      .from("historico_precos")
      .select("*", { count: "exact", head: true })
      .gte("data_fim", startStr)
      .lt("data_fim", endStr)
      .not("data_fim", "is", null);

    if (countError) {
      console.error(
        "❌ Erro ao contar registros (historico_precos):",
        countError
      );
      throw countError;
    }

    console.log(
      `📊 Total de registros a arquivar (historico_precos): ${expectedCount}`
    );

    if (expectedCount === 0) {
      return new Response(
        JSON.stringify({
          success: false,
          message: `Nenhum registro encontrado para o mês ${year}-${String(
            month + 1
          ).padStart(2, "0")} na tabela historico_precos`,
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
          status: 200,
        }
      );
    }

    // 5) Gerar CSV com paginação
    const pageSize = 1000;
    let offset = 0;
    let totalRows = 0;
    let csvContent = "id,produto_id,preco,cidade_id,data_inicio,data_fim\n";

    while (true) {
      const { data: rows, error: fetchError } = await supabase
        .from("historico_precos")
        .select("id,produto_id,preco,cidade_id,data_inicio,data_fim")
        .gte("data_fim", startStr)
        .lt("data_fim", endStr)
        .not("data_fim", "is", null)
        .order("id", { ascending: true })
        .range(offset, offset + pageSize - 1);

      if (fetchError) {
        console.error(
          "❌ Erro ao buscar dados (historico_precos):",
          fetchError
        );
        throw fetchError;
      }

      if (!rows || rows.length === 0) {
        console.log(
          "📥 Nenhuma linha retornada, fim da paginação (historico_precos)."
        );
        break;
      }

      const chunk =
        rows
          .map(
            (r) =>
              `${r.id},${r.produto_id},${r.preco},${r.cidade_id},${
                r.data_inicio
              },${r.data_fim ?? ""}`
          )
          .join("\n") + "\n";

      csvContent += chunk;
      totalRows += rows.length;
      offset += rows.length;

      if (rows.length < pageSize) {
        console.log(
          "📥 Última página (menos que pageSize linhas) (historico_precos)."
        );
        break;
      }
    }

    console.log(
      `✅ Total de ${totalRows} linhas processadas (historico_precos)`
    );

    // 6) VALIDAÇÃO CRÍTICA: Verificar se o número de linhas bate
    if (totalRows !== expectedCount) {
      console.error(
        `❌ ERRO CRÍTICO (historico_precos): Esperado ${expectedCount} linhas, mas processadas ${totalRows}`
      );
      return new Response(
        JSON.stringify({
          success: false,
          error: `Inconsistência detectada (historico_precos): esperado ${expectedCount} linhas, mas processadas ${totalRows}. Operação cancelada.`,
          expected: expectedCount,
          actual: totalRows,
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
          status: 500,
        }
      );
    }

    // 7) Upload para Storage
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from("archive-data")
      .upload(storagePath, csvContent, {
        contentType: "text/csv",
        upsert: false,
      });

    if (uploadError) {
      console.error("❌ Erro ao fazer upload (historico_precos):", uploadError);
      throw uploadError;
    }

    console.log(`✅ Arquivo salvo (historico_precos): ${storagePath}`);

    // 8) VALIDAÇÃO PÓS-UPLOAD: Verificar se o arquivo realmente existe
    const { data: uploadedFile, error: verifyError } = await supabase.storage
      .from("archive-data")
      .list("price-history", {
        search: fileName,
      });

    if (verifyError || !uploadedFile || uploadedFile.length === 0) {
      console.error(
        "❌ ERRO CRÍTICO (historico_precos): Arquivo não encontrado após upload!"
      );
      return new Response(
        JSON.stringify({
          success: false,
          error:
            "Arquivo não foi encontrado no Storage após upload (historico_precos). DELETE cancelado por segurança.",
          file: storagePath,
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
          status: 500,
        }
      );
    }

    const fileInfo = uploadedFile[0];
    console.log(
      `✅ Arquivo verificado no Storage (historico_precos): ${
        fileInfo.name
      }, tamanho: ${fileInfo.metadata?.size || "desconhecido"}`
    );

    // 9) VALIDAÇÃO EXTRA: Contar linhas do CSV baixado
    const { data: downloadedData, error: downloadError } =
      await supabase.storage.from("archive-data").download(storagePath);

    let csvIntegrityOk = false;

    if (downloadError) {
      console.error(
        "❌ Erro ao baixar arquivo para validação (historico_precos):",
        downloadError
      );
      console.warn(
        "⚠️ Não foi possível validar integridade do CSV (historico_precos). Prosseguindo com cautela."
      );
    } else {
      const downloadedText = await downloadedData.text();
      const downloadedLines = downloadedText
        .split("\n")
        .filter((line) => line.trim().length > 0);
      const downloadedRowCount = downloadedLines.length - 1;

      console.log(
        `📥 Linhas no arquivo baixado (historico_precos): ${downloadedRowCount}`
      );

      if (downloadedRowCount !== totalRows) {
        console.error(
          `❌ ERRO CRÍTICO (historico_precos): CSV tem ${downloadedRowCount} linhas, mas esperado ${totalRows}`
        );
        return new Response(
          JSON.stringify({
            success: false,
            error: `CSV corrompido (historico_precos): esperado ${totalRows} linhas, mas arquivo tem ${downloadedRowCount}. DELETE cancelado.`,
            expected: totalRows,
            actual: downloadedRowCount,
          }),
          {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
            status: 500,
          }
        );
      }

      console.log("✅ Validação de integridade do CSV (historico_precos): OK");
      csvIntegrityOk = true;
    }

    // 11) DELETE
    console.log("🗑️  Deletando registros do banco (historico_precos)...");

    const { error: deleteError, count: deletedCount } = await supabase
      .from("historico_precos")
      .delete({ count: "exact" })
      .gte("data_fim", startStr)
      .lt("data_fim", endStr)
      .not("data_fim", "is", null);

    if (deleteError) {
      console.error("❌ Erro ao deletar (historico_precos):", deleteError);
      return new Response(
        JSON.stringify({
          success: false,
          error: `Arquivo foi salvo com sucesso, mas houve erro ao deletar do banco (historico_precos): ${deleteError.message}`,
          file: storagePath,
          rows_archived: totalRows,
          note: "ATENÇÃO: Os dados foram arquivados mas NÃO foram deletados do banco. Você pode deletar manualmente ou tentar novamente.",
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
          status: 500,
        }
      );
    }

    console.log(
      `✅ ${deletedCount} registros deletados com sucesso (historico_precos)`
    );

    // Verificar se deletou o número correto
    if (deletedCount !== totalRows) {
      console.warn(
        `⚠️ AVISO (historico_precos): Esperado deletar ${totalRows} linhas, mas foram deletadas ${deletedCount}`
      );
    }

    return new Response(
      JSON.stringify({
        success: true,
        message: `Mês ${year}-${String(month + 1).padStart(
          2,
          "0"
        )} da tabela historico_precos arquivado e deletado com sucesso`,
        file: storagePath,
        rows_archived: totalRows,
        rows_deleted: deletedCount,
        file_size_bytes: fileInfo.metadata?.size,
        period: {
          start: startStr,
          end: endStr,
        },
        validations: {
          count_match: true,
          file_exists: true,
          csv_integrity: csvIntegrityOk,
          delete_count_match: deletedCount === totalRows,
        },
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 200,
      }
    );
  } catch (error) {
    console.error("❌ Erro geral (historico_precos):", error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 500,
      }
    );
  }
});
