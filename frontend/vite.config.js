import { defineConfig } from "vite";
// import vue from '@vitejs/plugin-vue' // vue 3
import { createVuePlugin as vue } from "vite-plugin-vue2"; //vue 2
import { createHtmlPlugin } from 'vite-plugin-html'
import { VitePWA } from 'vite-plugin-pwa'

const path = require("path");

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		vue(),
		VitePWA({ registerType: 'autoUpdate' }),
		createHtmlPlugin({
			minify: true,
			inject: {
				data: {}
			}
		}),
	],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
	},
});