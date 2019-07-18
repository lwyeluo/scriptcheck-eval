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
			const {Network, Page, Runtime, Target} = client;
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

			console.log(">>> Prepare to get frames's information");

			// save the results for frames
			var frames_info = {};
			var received_message_id = -1;

			// 1. register the message receiver function
			Target.receivedMessageFromTarget(function (args) {
				console.log(">>> receive");
				console.log(args);
				var url = frames_info[args.targetId]['url'];
				var data = JSON.parse(args.message);
				var domain = data.result.result.value;
				console.log("******\t" + args.targetId + "\t" + url + "\t" + domain);
				console.log(data.id);
				received_message_id = data.id;
			});
			// 2. get all target ids
			var target_ids = await Target.getTargets();
			var max_id = target_ids.targetInfos.length - 1;
			for(var i = 0; i < max_id; i ++) {
				frames_info[target_ids.targetInfos[i].targetId] = {
					"url": target_ids.targetInfos[i].url,
				};
			}

			// 3. get the domains for all frames
			for(var i = 0; i < max_id; i ++) {
				console.log(target_ids.targetInfos[i].url);
				target_id = target_ids.targetInfos[i].targetId;
				// 2. attach to target
				var session_id = await Target.attachToTarget({targetId: target_id});
				console.log(session_id);
				msg = `{"id": ` + i + `, "method": "Runtime.evaluate",
					"params": {"expression": "console.log(document.domain);document.domain"}}`;
				console.log(">>> send message " + i);
				await Target.sendMessageToTarget({
					sessionId: session_id.sessionId, message: msg
				});
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
