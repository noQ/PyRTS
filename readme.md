PyRTS
=====

Python Real Time Game Server

	Author:  Adrian Costia
	Version: 0.0.1

 RESTful

	* Get controller authorize token (development)
 		http://localhost:8080/token/

		Response:
			{'token': '603fccbc9a9ec13532d7f3259d184f5de35360da',
			 'is_valid': True, 
			 'id': u'4fe81c8a6ee7220cd4000000', 
			 'expire_at': 1372168648, u'address': 
			 '192.168.123.11'
			}


	* Server list
		{"c":"4534564","m":"serverlist","p" :{"token":"c01066836281a24534e335fe22052378f7f2f5300d"}}

	* Add new controller
		{"c":"4534564","m":"addcontroller","p" :{"token":"c01066836281a24534e335fe22052378f7f2f5300d"}}

	* register new node
		{"c":"4534564","m":"registernode","p" :{"token":"c01066836281a24534e335fe22052378f7f2f5300d","controllerid":"4fe190596ee7224b28000000","address":"192.168.190.29","name":"L-MOB-COSTIA-NODE1"}}

	* Unregister (delete) controller node
		{"c":"4534564","m":"unregisternode","p" :{"token":"c01066836281a24534e335fe22052378f7f2f5300d","controllerid":"4fe190596ee7224b28000000","nodeid":"4fe1d4066ee7225440000002"}}

	* List nodes
		{"c":"4534564","m":"listnodes","p" :{"token":"603fccbc9a9ec13532d7f3259d184f5de35360da","controllerid":"4fe190596ee7224b28000000"}}

	* Check node
		{"c":"4534564","m":"checknode","p" :{"token":"603fccbc9a9ec13532d7f3259d184f5de35360da","nodeid":"4fed61596ee722aeb0000000"}}

	* Delete node
		{"c":"4534564","m":"deletenode","p" :{"token":"c01066836281a24534e335fe22052378f7f2f5300d","nodeid":"4fe1dbed6ee7225b9c000000"}}

	* Register application
		{"c":"4534564","m":"registerapp","p" :{"token":"603fccbc9a9ec13532d7f3259d184f5de35360da","nodeid":"4fe194b06ee7224064000000","app":{"application_name":"Tetris","connections":12}}}
		{"c":"4534564","m":"registerapp","p" :{"token":"603fccbc9a9ec13532d7f3259d184f5de35360da","nodeid":"4fe194b06ee7224064000000","app":{"application_name":"Tetris","connections":12,"slots":3}}}

	* RealTimeServer update

		{"c":"4534564","m":"rtupdate","p" :{"token":"603fccbc9a9ec13532d7f3259d184f5de35360da","apps":{"Tetris":{"slots":2},"Bejeweled":{}},"ports":{"udp":110002,"tcp":110003,"http":80}}}

	* RealTimeServer Info

		{"p": {"load": {"Tetris": 0, "Bejeweled": 0}, "token": "603fccbc9a9ec13532d7f3259d184f5de35360da", "system": {"ram": 9.17578125, "cpu": 0.3}}, "c": "6523", "m": "rtinfo"}
		{"p": {"load": {"Tetris": 1, "Bejeweled": 3}, "token": "603fccbc9a9ec13532d7f3259d184f5de35360da", "system": {"ram": 9.17578125, "cpu": 0.3}}, "c": "6523", "m": "rtinfo"}



	* Unregister application 
		{"c":"4534564","m":"unregisterapp","p" :{"token":"603fccbc9a9ec13532d7f3259d184f5de35360da","nodeid":"4fe194b06ee7224064000000","appid":"4fe826ad6ee72221b0000000"}}


	* Create/join game session
		{"c":"4534564","m":"getsession","p" :{"token":"603fccbc9a9ec13532d7f3259d184f5de35360da","game":"Tetris","uid":"7999o944"}}

			GC - get or create
			C  - create

			- session by random UID - default mode (GC)
				{"c":"4534564","m":"getsession","p" :{"token":"0c8d4ef958eeb5e793f9b963686595781171b6e2","game":"gametemplate","uid":"8","restriction":{"type":"RANDOM_UID","data":""}}}
         		- session by specific UID (GC):
				{"c":"4534564","m":"getsession","p" :{"token":"0c8d4ef958eeb5e793f9b963686595781171b6e2","game":"gametemplate","uid":"1","restriction":{"type":"SPECIFIC_UID","data":"2"}}}
			- session by specific session name (G)
				{"c":"4534564","m":"getsession","p" :{"token":"0c8d4ef958eeb5e793f9b963686595781171b6e2","game":"gametemplate","uid":"3","restriction":{"type":"SPECIFIC_SESSION","data":"eD4Xe"}}}
			-- session by specific uids (C)
				{"c":"4534564","m":"getsession","p" :{"token":"0c8d4ef958eeb5e793f9b963686595781171b6e2","game":"gametemplate","uid":"8","filter":{"type":"SPECIFIC_UIDS","data":["9","10","11","12"]}}}	
			-- session by random uids (C)
				{"c":"4534564","m":"getsession","p" :{"token":"0c8d4ef958eeb5e793f9b963686595781171b6e2","game":"gametemplate","uid":"8","filter":{"type":"RANDOM_UIDS","data":""}}}		
	
	* Delete session
		{"c":"4534564","m":"delete_session","p" :{"token":"603fccbc9a9ec13532d7f3259d184f5de35360da","name":"g9Pkv"}}

	* Plugin call example (used by client)
		{"c":"4534564","m":"total_players","p" :{"token":"0c8d4ef958eeb5e793f9b963686595781171b6e2","session":"g9Pkv"}}


