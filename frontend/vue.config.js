module.exports = {
	publicPath: "./",
	pwa: {
		name: 'Bang!',
		appleMobileWebAppCache: "yes",
		manifestOptions: {
			display: 'standalone',
		},
		workboxPluginMode: 'GenerateSW',
		workboxOptions: {
			navigateFallback: '/index.html',
			cleanupOutdatedCaches: true,
		}
	},
	configureWebpack: {
		output: {
			crossOriginLoading: 'anonymous'
		},
	}
};