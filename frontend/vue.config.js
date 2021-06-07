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
			swSrc: 'src/service-worker.js'
		}
	},
	configureWebpack: {
		output: {
			crossOriginLoading: 'anonymous'
		},
	}
};