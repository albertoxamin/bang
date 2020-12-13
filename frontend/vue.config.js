const { GenerateSW } = require("workbox-webpack-plugin");

module.exports = {
	publicPath: "./",
	pwa: {
		name: 'PewPew!',
		appleMobileWebAppCache: "yes",
		manifestOptions: {
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