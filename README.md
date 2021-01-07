# DealzSeeker
Seeker for mydealz.de & idealo.de that also offers bot functionalities for Telegram. Not affiliated with MyDealz in any way. Parts copied from [MyDealzScraper](https://github.com/mhvuze/MydealzScraper).

## Requirements
Install python requirements:
```bash
  $ sudo python3 -m pip install -r requirements.txt
```

## Usage
You can control the following settings in `settings.txt`:
* debug_mode: Enable/disable debug messages
* sleep_time: Set time to sleep after each cycle in seconds
* telegram: Enable/disable Telegram messages for new deals
* tg_token: Set token of your Telegram bot
* tg_cid: Set recipient chat id on Telegram
* tg_cid2: Set second recipient chat id on Telegram (0 for disabled)

You can use the following commands on Telegram:
* /addMyDealz [item]: Add item to list of wanted products
* /addIdealo [URL];[PRICEasIntegerValue]: Add idealo URL and wanted price to list of wanted products
* /removeMyDealz [item]: Remove item from list of wanted products
* /removeIdealo [URL];[PRICEasIntegerValue]: Remove url and price alert from list of wanted products
* /list: Show list of all wanted products
* /reset: Reset list of discovered deals
* /hello: Ask for life sign without changing anything
