import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import prebundleWorkers from "vite-plugin-prebundle-workers";

// https://vitejs.dev/config/
export default defineConfig({
  base: "/cloud-prices/",
  plugins: [vue(),
    // prebundleWorkers({
    //     include: "node_modules/sqlite-wasm-http/dist/sqlite-worker.js"
    // })
  ],
  // build: {
  //   lib: {
  //     entry: path.resolve(__dirname, "src/main.js"),
  //     name: "ViteUmdBug"
  //   },
  //   rollupOptions: {
  //     external: ["vue"],
  //     output: {
  //       inlineDynamicImports: true, // <== here the entry
  //       globals: {
  //         vue: "Vue"
  //       }
  //     },

  //   }
  // },
  worker: {
    format: 'es'
  }
  // worker: {
  //   format: "iife"
  // },
  // optimizeDeps: {
  //   exclude: [
  //     "sqlite-wasm-http"
  //   ]
  // }
})
