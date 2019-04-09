import { createGlobalStyle } from "styled-components";

const GlobalStyles = createGlobalStyle`
  * {
    box-sizing: border-box;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
  }
  html,body {
    scroll-behavior: smooth;
  }
  img {
    display: block;
    margin: auto;
  }
  table {
    width: 100%;
  }
`;

export default GlobalStyles;
