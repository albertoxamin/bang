const { GenerateSW } = require("workbox-webpack-plugin");

module.exports = {
	publicPath: "./",
	pwa: {
		name: 'PewPew!',
		appleMobileWebAppCache: "yes",
		manifestOptions: {
			display: 'standalone',
		},
		workboxPluginMode: 'InjectManifest',
		workboxOptions: {
			swSrc: 'src/registerServiceWorker.js'
		}
	},
	configureWebpack: {
		plugins: [new GenerateSW({
			clientsClaim: true,
			skipWaiting: true,
			cleanupOutdatedCaches: true,
			navigateFallback: 'index.html',
		})],
		output: {
			crossOriginLoading: 'anonymous'
		},
	}
};