argv = process.argv
console.log("***********************************i am in**********************************")
const CDP = require('chrome-remote-interface');
async function example() {
    let client;
	
		try {
			// connect to endpoint
			client = await CDP();
			// extract domains
			const {Network, Page, Runtime} = client;
			// setup handlers
			Network.requestWillBeSent((params) => {
				console.log(params.request.url);
			});
			// enable events then start!
			await Network.enable();
			await Page.enable();
			await Page.navigate({url: argv[2]});
			//await Page.loadEventFired();
		    result = await Runtime.evaluate({expression: 'document.readyState'});
			//console.log(result);
			while(result.result.value != "complete")
			{
				console.log(result);
				result = await Runtime.evaluate({expression: 'document.readyState'});
			}
			console.log(result);
		} catch (err) {
			console.error(err);
		} finally {
			if (client) {
				await client.close();
			}
		}
	}


example();
