import type { Components } from "@mui/material/styles";

const components: Components = {
  MuiAppBar: {
    styleOverrides: {
      root: {
        backgroundColor: "#1F1B24",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      },
    },
  },
  MuiTableCell: {
    styleOverrides: {
      root: {
        borderBottom: "1px solid rgba(255,255,255,0.08)",
        fontSize: "0.875rem",
      },
      head: {
        color: "#A5A2AC",
        fontWeight: 500,
      },
    },
  },
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        textTransform: "none",
        fontWeight: 600,
        "&:hover": {},
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 6,
        fontWeight: 500,
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        backgroundImage: "none",
        backgroundColor: "#1F1B24",
      },
    },
  },
};

export default components;
