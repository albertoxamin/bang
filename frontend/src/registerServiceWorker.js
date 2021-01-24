import { Workbox } from 'workbox-window';

if ('serviceWorker' in navigator) {
	const wb = new Workbox('service-worker.js');

	wb.addEventListener('installed', event => {
		if (event.isUpdate) {
			if (confirm(`Update available. Click OK to update`)) {
				window.location.reload();
			}
		}
	});

	wb.register();
}