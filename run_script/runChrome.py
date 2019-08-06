# coding=utf-8


import asyncio
import time
import json

from chromewhip.chromewhip import Chrome
from chromewhip.chromewhip.protocol import browser, page, target

# see logging from chromewhip
# logging.basicConfig(level=logging.DEBUG)

class ChromeDev(object):

	def __init__(self, url):
		self.HOST = '127.0.0.1'
		self.PORT = 9222

		self.url = url

		self.chrome = None
		self.loop = None
		self.tab = None

		self.init()

	def init(self):
		# 1. connect to Chrome
		self.loop = asyncio.get_event_loop()
		self.chrome = Chrome(host=self.HOST, port=self.PORT)
		self.loop.run_until_complete(self.chrome.connect())

		# 2. get the tab
		# use the startup tab or create a new one
		self.tab = self.chrome.tabs[0]
		# tab = loop.run_until_complete(c.create_tab())

		# 3. enable events
		self.loop.run_until_complete(self.tab.enable_page_events())

		# 4. navigate
		# send_command will return once the frameStoppedLoading event is received THAT matches
		# the frameId that it is in the returned command payload.
		result = self.sync_cmd(page.Page.navigate(url=self.url),
							   await_on_event_type=page.FrameStoppedLoadingEvent)

		# 5. just test
		# send_command always returns a dict with keys `ack` and `event`
		# `ack` contains the payload on response of a command
		# `event` contains the payload of the awaited event if `await_on_event_type` is provided
		ack = result['ack']['result']
		event = result['event']
		assert ack['frameId'] == event.frameId

		time.sleep(2)

	def sync_cmd(self, *args, **kwargs):
		return self.loop.run_until_complete(self.tab.send_command(*args, **kwargs))

	def getFrameDomain(self):
		domains = {}
		# 1. get targets
		result = self.sync_cmd(target.Target.getTargets())
		# trverse all frames
		for info in result['ack']['result']['targetInfos']:
			targetId, url, frame_type = info['targetId'], info['url'], info['type']

			if frame_type == 'background_page':
				# here is Chrome extension, ignore
				continue

			ret = self.sync_cmd(target.Target.attachToTarget(targetId))
			sessionId, msg_id = ret['ack']['result']['sessionId'], ret['ack']['id']

			msg = '{"method": "Runtime.evaluate", "id": %d, "params": {"expression": "console.log(document.domain);document.domain"}}' % (int(msg_id) + 1)
			ret = self.sync_cmd(target.Target.sendMessageToTarget(message=msg, sessionId=sessionId, targetId=targetId),
								await_on_event_type=target.ReceivedMessageFromTargetEvent)
			if 'event' in ret.keys():
				recv_msg, recv_target_id = ret['event'].message, ret['event'].targetId
				recv_msg_json = json.loads(recv_msg)
				recv_data = recv_msg_json['result']['result']['value']
				assert recv_target_id == targetId

				# append results
				domains[targetId] = {
					'type': frame_type,
					'url': url,
					'domain': recv_data
				}
		return domains

	def close(self):
		# close the tab
		self.loop.run_until_complete(self.chrome.close_tab(self.tab))

		# or close the browser via Devtools API
		#tab = c.tabs[0]
		self.sync_cmd(browser.Browser.close())

if __name__ == '__main__':
	dev = ChromeDev(url="http://www.chewen.com")
	domains = dev.getFrameDomain()
	print(domains)