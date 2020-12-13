const { GenerateSW } = require("workbox-webpack-plugin");

module.exports = {
	pwa: {
		name: 'PewPew!',
		appleMobileWebAppCache: "yes",
		manifestOptions: {
		}
	},
	configureWebpack: {
		plugins: [new GenerateSW()],
		output: {
			crossOriginLoading: 'anonymous'
		},
	}
};