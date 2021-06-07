const { GenerateSW } = require("workbox-webpack-plugin");

module.exports = {
	publicPath: "./",
	pwa: {
		name: 'PewPew!',
		appleMobileWebAppCache: "yes",
		manifestOptions: {
			display: 'standalone',
		}
	},
	configureWebpack: {
		plugins: [new GenerateSW({
			clientsClaim: true,
			skipWaiting: true,
			navigateFallback: 'index.html',
		})],
		output: {
			crossOriginLoading: 'anonymous'
		},
	}
};