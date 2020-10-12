// argv[2]: url
// argv[3]: timeout

argv = process.argv;
console.log("***********************************i am in**********************************")
const CDP = require('chrome-remote-interface');

function sleep(time = 0) {
	return new Promise((resolve, reject) => {
		setTimeout(() => {
			resolve();
		}, time);
	});
}

async function example() {
	let client;

	var in_url = argv[2];
	var in_timeout = parseInt(argv[3]);

	try {
		// connect to endpoint
		client = await CDP();
		// extract domains
		const {Network, Page, Runtime, Target} = client;

		async function invoke(in_expression, success_function) {
			startTime = process.uptime();
			result = await Runtime.evaluate({expression: in_expression});
			console.log(result);
			while (!success_function()) {
				curTime = process.uptime();
				if (curTime - startTime > in_timeout) {
					console.log(">>> TimeOut ");
					break;
				}
				result = await Runtime.evaluate({expression: in_expression});
				console.log(result);
			}
		}

		// setup handlers
		// Network.requestWillBeSent((params) => {
		// 	console.log(params.request.url);
		// });
		// enable events then start!
		await Network.enable();
		await Page.enable();
		await Page.navigate({url: in_url});
		//await Page.loadEventFired();
			result = await Runtime.evaluate({expression: 'document.readyState'});
		//console.log(result);
		while (result.result.value == "loading") {
			result = await Runtime.evaluate({expression: 'document.readyState'});
		}
		startTime = process.uptime();
		while (result.result.value != "complete") {
			curTime = process.uptime();
			if (curTime - startTime > in_timeout) {
				console.log(">>> TimeOut ");
				break;
			}
			result = await Runtime.evaluate({expression: 'document.readyState'});
			console.log(result);
		}
		console.log(result);

		result = await Runtime.evaluate({expression: 'document.body.getElementsByTagName("div").length'});
        if(result.result.value == 0) {
            console.log("ERROR WHEN RUNNING TELEMETRY")
        } else {
            // wait the page
            await invoke(
                'var ele = document.getElementById("histograms").shadowRoot.querySelector(\'tr-v-ui-histogram-set-table[id="table"]\').shadowRoot;' +
                'var ele_0 = ele.querySelector(\'tr-ui-b-table[id="table"]\').shadowRoot;' +
                'var ele_1 = ele_0.querySelector(\'tbody[id="body"]\');' +
                'ele_1.querySelectorAll(\'tr\').length',
                function() {return result.result.description > 0});
            // select the item
            await invoke(
                'var ele = document.getElementById("histograms").shadowRoot.querySelector(\'tr-v-ui-histogram-set-controls[id="controls"]\').shadowRoot;' +
                'ele.querySelector(\'select[id="reference_display_label"]\').selectedIndex = 2;' +
                'ele.querySelector(\'select[id="reference_display_label"]\').selectedIndex',
                function() {return result.result.value == 2}
            );

            // download the file
            await invoke(
                'var ele = document.getElementById("histograms").shadowRoot.querySelector(\'tr-v-ui-histogram-set-controls[id="controls"]\').shadowRoot;' +
                'var ele_0 = ele.querySelector(\'tr-ui-b-dropdown[label="Export"]\');' +
                'ele_0.shadowRoot.querySelector(\'button[id="button"]\').click();' +
                'var ele_1 = ele_0.getElementsByTagName("tr-v-ui-histogram-set-controls-export")[0].shadowRoot;' +
                'var btn = [...ele_1.querySelectorAll(\'button\')].filter(e=>e.innerText=="merged JSON")[0];' +
                'btn.click();btn.innerText',
                function() {return result.result.value == 'merged JSON'}
            );

            sleep(15000);

            console.log("DONE FOR RUNNING TELEMETRY");
        }

	} catch (err) {
		console.error(err);
	} finally {
		if (client) {
			await client.close();
		}
	}
}


example();
