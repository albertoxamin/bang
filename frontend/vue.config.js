module.exports = {
	publicPath: "./",
	pwa: {
		name: 'Bang!',
		appleMobileWebAppCache: "yes",
		manifestOptions: {
			display: 'standalone',
		},
	},
	configureWebpack: {
		output: {
			crossOriginLoading: 'anonymous'
		},
	}
};