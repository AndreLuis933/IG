SELECT
  cron.schedule(
    'processar-metricas-diarias',
    '10 16 * * *',
    $$
      SELECT processar_metricas_diarias();
    $$
  );