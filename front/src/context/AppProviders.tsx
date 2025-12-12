import type { ReactNode } from "react";
import { ThemeProvider } from "@mui/material/styles";
import { darkTheme } from "@/theme";

type Props = {
  children: ReactNode;
};

export const AppProviders = ({ children }: Props) => {
  return <ThemeProvider theme={darkTheme}>{children}</ThemeProvider>;
};
