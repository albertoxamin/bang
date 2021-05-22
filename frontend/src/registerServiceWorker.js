if ('serviceWorker' in navigator) {
	const { Workbox } = new Workbox('service-worker.js');

	const wb = new Workbox('/service-worker.js');
	wb.addEventListener('activated', event => {
		// `event.isUpdate` will be true if another version of the service
		// worker was controlling the page when this version was registered.
		if (!event.isUpdate) {
			console.log('Service worker activated for the first time!');

			// If your service worker is configured to precache assets, those
			// assets should all be available now.
		}
	});

	wb.addEventListener('waiting', () => {
		console.log(
			`A new service worker has installed, but it can't activate` +
				`until all tabs running the current version have fully unloaded.`,
		);
	});

	wb.addEventListener('message', event => {
		if (event.data.type === 'CACHE_UPDATE') {
			const { updatedURL } = event.data.payload;

			console.log(`A newer version of ${updatedURL} is available!`);
		}
	});

	wb.addEventListener('installed', event => {
		if (!event.isUpdate) {
			console.log('First install');
		} else {
			console.log('updated install');
		}
	});

	wb.addEventListener('controlling', event => {
		if (!event.isUpdate) {
			console.log('First control');
		} else {
			console.log('updated control');
		}
	});

	wb.addEventListener('externalinstalled', event => {
		if (!event.isUpdate) {
			console.log('external first install');
		} else {
			console.log('external update install');
		}
	});

	wb.addEventListener('externalwaiting', event => {
		if (!event.isUpdate) {
			console.log('external first waiting');
		} else {
			console.log('external update waiting');
		}
	});

	wb.addEventListener('externalactivated', event => {
		if (!event.isUpdate) {
			console.log('external first acvtive');
		} else {
			console.log('external update acvtive');
		}
	});

	wb.addEventListener('redundant', event => {
		// `event.isUpdate` will be true if another version of the service
		// worker was controlling the page when this version was registered.
		if (!event.isUpdate) {
			console.log('Service worker redundant for the first time!');

			// If your service worker is configured to precache assets, those
			// assets should all be available now.
		}
		console.log(event);
	});

	wb.register();
}