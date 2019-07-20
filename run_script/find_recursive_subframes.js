// argv[2]: url
// argv[3]: timeout

argv = process.argv
console.log("***********************************i am in**********************************")
const CDP = require('chrome-remote-interface');
function sleep(d){
  for(var t = Date.now();Date.now() - t <= d;);
}


function code() {
	var results = [];
	var all_frames = []; 
	var parent_frames = ["\ts", location.href, document.domain, "parent frame"];
	all_frames.push(parent_frames);
	while(all_frames.length != 0){
		var temp = all_frames[0];
		results.push(temp);
		all_frames.shift();
		var sub = temp[0].split('-');
		var expression_str = "window";
		for(var i = 1; i<sub.length; i++){
			expression_str = expression_str + ".frames[" + sub[i] + "]";
		}
		var expression_str_frames_length = expression_str + ".frames.length";
		result_subframes_length = eval(expression_str_frames_length); 
		for (var i = 0; i < result_subframes_length; i++){
			var expression_str_frames_sub_href = expression_str + ".frames[" + i + "].location.href";
			var expression_str_frames_sub_domain = expression_str + ".frames[" + i + "].document.domain";
			try {
				result_sub_frame_href = eval(expression_str_frames_sub_href);
				result_sub_frame_domain = eval(expression_str_frames_sub_domain);
				var sub_frame = [temp[0] + "-" + i, result_sub_frame_href, result_sub_frame_domain, "subframe Yes"];
				all_frames.push(sub_frame);
			} catch (err) {
				var sub_frame = [temp[0] + "-" + i, "Not same domain", "Not same domain", "subframe No"];
				all_frames.push(sub_frame);
			}
		}
	}
	
	return results.toString();
}

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
				
			sleep(2000); //当前方法暂停5秒

			console.log(">>> Prepare to get frames's information");
	
			var expression_str = code.toString().replace(/\n/g, '') + "console.log(code);result=code();result";
			result_result = await Runtime.evaluate({expression: expression_str});
			var result_list = result_result.result.value.split("\t");
			for(var i = 1; i < result_list.length; i++)
			{
				console.log("**********\t" + result_list[i].toString().replace(/,/g, '\t'));
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
