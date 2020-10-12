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
			// wait the benchmark finishes
			startTime = process.uptime();
			var result_href = "https://krakenbenchmark.mozilla.org/kraken-1.1/results.html";
			while (result.result.value.indexOf(result_href) != 0) {
				curTime = process.uptime();
				if (curTime - startTime > in_timeout) {
					console.log(">>> TimeOut ");
					break;
				}
				result = await Runtime.evaluate({expression: 'location.href'});
				console.log(result);
			}
			// read the benchamrk results
			startTime = process.uptime();
			var result_dom_id = "console";
			var result_title = "RESULTS (means and 95% confidence intervals)";
			while (result.result.value.indexOf(result_title) == -1) {
				curTime = process.uptime();
				if (curTime - startTime > in_timeout) {
					console.log(">>> TimeOut ");
					break;
				}
				result = await Runtime.evaluate({expression: 'document.getElementById("'+ result_dom_id +'").innerText'});
				console.log(result);
			}
			sleep(2000);

		} catch (err) {
			console.error(err);
		} finally {
			if (client) {
				await client.close();
			}
		}
	}


example();
