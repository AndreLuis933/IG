CREATE OR REPLACE FUNCTION processar_metricas_diarias()
RETURNS boolean
LANGUAGE plpgsql
AS $$
DECLARE
  v_data_mais_antiga    date;
  v_data_ultima_metrica date;
  v_data                date;
  v_data_previa         date;
  v_gap                 boolean;
  v_cidade_id           integer;
  v_count               integer;
  old_timeout text;
BEGIN
  SELECT current_setting('statement_timeout') INTO old_timeout;
  PERFORM set_config('statement_timeout', '300000', true);

  -------------------------------------------------------------------------
  -- 1. Pegar a data mais antiga disponível em historico_precos
  -------------------------------------------------------------------------
  SELECT MIN(data_inicio)::date
  INTO v_data_mais_antiga
  FROM historico_precos;

  IF v_data_mais_antiga IS NULL THEN
    PERFORM set_config('statement_timeout', old_timeout, true);
    RETURN FALSE;
  END IF;

  -------------------------------------------------------------------------
  -- 2. Descobrir a última data já processada em metricas_diarias_cidade
  -------------------------------------------------------------------------
  SELECT MAX(data)::date
  INTO v_data_ultima_metrica
  FROM metricas_diarias_cidade;

  -------------------------------------------------------------------------
  -- 3. Escolher a PRÓXIMA data a processar
  -------------------------------------------------------------------------
  SELECT MIN(data_inicio)::date
  INTO v_data
  FROM historico_precos
  WHERE data_inicio::date > COALESCE(v_data_ultima_metrica, v_data_mais_antiga - 1);

  IF v_data IS NULL THEN
    PERFORM set_config('statement_timeout', old_timeout, true);
    RETURN FALSE;
  END IF;

  -------------------------------------------------------------------------
  -- 4. Verificar se há "gap" em relação à última data processada
  -------------------------------------------------------------------------
  v_data_previa := v_data_ultima_metrica;
  v_gap := v_data_previa IS NULL OR (v_data - v_data_previa) > 1;

  -------------------------------------------------------------------------
  -- 5. Loop por todas as cidades existentes (exceto 1 = global)
  -------------------------------------------------------------------------
  FOR v_cidade_id IN
      SELECT id
      FROM cidades
      WHERE id <> 1
      ORDER BY id
  LOOP
    SET LOCAL statement_timeout = '30000';

    SELECT COUNT(*) INTO v_count
    FROM disponibilidade_cidades
    WHERE disponivel
      AND cidade_id = v_cidade_id
      AND data_inicio <= v_data
      AND COALESCE(data_fim, v_data) >= v_data;

    IF v_count = 0 THEN
      CONTINUE;
    END IF;

    WITH
      produtos AS (
        SELECT DISTINCT produto_id
        FROM disponibilidade_cidades
        WHERE disponivel
          AND cidade_id = v_cidade_id
          AND data_inicio <= v_data
          AND COALESCE(data_fim, v_data) >= v_data
      ),
      p_hoje AS (
        SELECT
          p.produto_id,
          COALESCE(
            (SELECT preco
             FROM historico_precos
             WHERE produto_id = p.produto_id
               AND cidade_id = v_cidade_id
               AND data_inicio <= v_data
               AND COALESCE(data_fim, v_data) >= v_data
             ORDER BY data_inicio DESC
             LIMIT 1),
            (SELECT preco
             FROM historico_precos
             WHERE produto_id = p.produto_id
               AND cidade_id = 1
               AND data_inicio <= v_data
               AND COALESCE(data_fim, v_data) >= v_data
             ORDER BY data_inicio DESC
             LIMIT 1)
          ) AS preco
        FROM produtos p
      ),
      p_ontem AS (
        SELECT
          p.produto_id,
          CASE
            WHEN NOT v_gap THEN
              COALESCE(
                (SELECT preco
                 FROM historico_precos
                 WHERE produto_id = p.produto_id
                   AND cidade_id = v_cidade_id
                   AND data_inicio < v_data
                 ORDER BY data_inicio DESC
                 LIMIT 1),
                (SELECT preco
                 FROM historico_precos
                 WHERE produto_id = p.produto_id
                   AND cidade_id = 1
                   AND data_inicio < v_data
                 ORDER BY data_inicio DESC
                 LIMIT 1)
              )
          END AS preco
        FROM produtos p
      ),
      joined AS (
        SELECT
          h.produto_id,
          h.preco AS preco_hoje,
          o.preco AS preco_ontem
        FROM p_hoje h
        LEFT JOIN p_ontem o USING (produto_id)
        WHERE h.preco IS NOT NULL
      )
    INSERT INTO metricas_diarias_cidade
      (data,
       cidade_id,
       variacao_media_preco,
       num_produtos_disponiveis,
       preco_medio_geral)
    SELECT
      v_data,
      v_cidade_id,
      CASE
        WHEN v_gap THEN 0
        ELSE AVG(
          CASE
            WHEN preco_ontem IS NOT NULL AND preco_ontem <> 0
            THEN (preco_hoje - preco_ontem) / preco_ontem
          END
        )
      END AS variacao_media_preco,
      COUNT(*) AS num_produtos_disponiveis,
      AVG(preco_hoje) AS preco_medio_geral
    FROM joined
    HAVING COUNT(*) > 0
    ON CONFLICT (data, cidade_id) DO UPDATE SET
      variacao_media_preco     = EXCLUDED.variacao_media_preco,
      num_produtos_disponiveis = EXCLUDED.num_produtos_disponiveis,
      preco_medio_geral        = EXCLUDED.preco_medio_geral;
  END LOOP;

  -------------------------------------------------------------------------
  -- 6. Agregado global (cidade_id = 1) para v_data
  -------------------------------------------------------------------------
  INSERT INTO metricas_diarias_cidade
    (data,
     cidade_id,
     variacao_media_preco,
     num_produtos_disponiveis,
     preco_medio_geral)
  SELECT
    v_data,
    1,
    CASE WHEN v_gap THEN 0 ELSE AVG(variacao_media_preco) END,
    SUM(num_produtos_disponiveis),
    AVG(preco_medio_geral)
  FROM metricas_diarias_cidade
  WHERE data = v_data
    AND cidade_id <> 1
  HAVING COUNT(*) > 0
  ON CONFLICT (data, cidade_id) DO UPDATE SET
    variacao_media_preco     = EXCLUDED.variacao_media_preco,
    num_produtos_disponiveis = EXCLUDED.num_produtos_disponiveis,
    preco_medio_geral        = EXCLUDED.preco_medio_geral;

  PERFORM set_config('statement_timeout', old_timeout, true);

  RETURN TRUE;
END;
$$;