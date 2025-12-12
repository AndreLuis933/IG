import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import { AppProviders } from "./context/AppProviders.tsx";
import { CssBaseline } from "@mui/material";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppProviders>
      <CssBaseline />
      <App />
    </AppProviders>
  </StrictMode>
);
