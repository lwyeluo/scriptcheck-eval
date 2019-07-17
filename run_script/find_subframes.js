// argv[2]: url
// argv[3]: timeout

argv = process.argv
console.log("***********************************i am in**********************************")
const CDP = require('chrome-remote-interface');
async function example() {
    let client;

    var in_url = argv[2]
    var in_timeout = parseInt(argv[3])
	
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
			//find message of subframes
			// console.log("**********url is : " + argv[2]);
			//result = await Runtime.evaluate({expression: ''});
			result_domain = await Runtime.evaluate({expression: 'document.domain'});
			result_href = await Runtime.evaluate({expression: 'window.location.href'});
			//console.log(result_href);
			//console.log(result_domain);
			console.log("##########\t" + result_href.result.value + "\t" + result_domain.result.value + "\tparent frame");
			result_subframes_length = await Runtime.evaluate({expression: 'window.frames.length'});
			if (result_subframes_length.result.value == 0)
			{
				console.log("@@@@@@@@@@NO subframes");
			}
			else {
				//console.log("*****Parent frame has  " + result_subframes_length.result.value + " subframes");
				for (var i = 0; i < result_subframes_length.result.value; i++) {
					//console.log("********************************* in for*****************");
					var str_frame_url = "window.frames[" + i + "].location.href";
					result_subframes_href = await Runtime.evaluate({expression: str_frame_url});
					//console.log("*************************??????????????????????")
					//console.log(result_subframes_href);
					//console.log("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^");
					//console.log(result_subframes_href.result.exceptionDetails.exceptionId);
					//console.log("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^");
					//console.log(result_subframes_href.result.className);
					//result_subframes_href = await Runtime.evaluate({expression: 'window.frames[i].location.href'});
					if (result_subframes_href.exceptionDetails) {
						console.log("**********\t" + i + "\t\t\tsubframe No");
						continue;
					}
					var str_frame_domain = "window.frames[" + i + "].document.domain";
					result_subframes_domain = await Runtime.evaluate({expression: str_frame_domain});
					// result_subframes_domain = await Runtime.evaluate({expression: 'window.frames[i].document.domain'});
					console.log("**********\t" + i + "\t" + result_subframes_href.result.value + "\t" + result_subframes_domain.result.value + "\tsubframe Yes");
					//console.log("**************"+ i + "******** ");
					//console.log(result_subframes_href);
				}
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
