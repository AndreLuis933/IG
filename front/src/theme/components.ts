import type { Components } from "@mui/material/styles";

const components: Components = {
  MuiPaper: {
    styleOverrides: {
      root: {
        backgroundImage: "none",
        backgroundColor: "#1F1B24",
      },
    },
  },
  MuiOutlinedInput: {
    styleOverrides: {
      root: {
        color: "#E0E0E0",
        "& .MuiInputAdornment-root, & svg": {
          color: "#E0E0E0",
        },
        "& input[type='date']::-webkit-calendar-picker-indicator": {
          filter: "invert(1)",
          cursor: "pointer",
        },
      },
    },
  },
};

export default components;
