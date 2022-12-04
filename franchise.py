from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.http import FormRequest
import re
from itemadapter import ItemAdapter

import schedule
import time

import openpyxl

# class CustomExporter(XlsxItemExporter):
#     def __init__(self, file, **kwargs):
#         super().__init__(file, include_header_row=False, **kwargs)

class FranchiseScrapy(scrapy.Spider):
	name="Franchise"
	base_url = "https://www.franchiseball.com"

	custom_settings={
		"ITEM_PIPELINES": {
			'__main__.XLSXPipeline': 100
			},
		"CONCURRENT_REQUESTS":32
	}

	def start_requests(self):
		yield scrapy.Request(url="https://www.franchiseball.com/login.php",callback=self.parse)
	
	def parse(self,response):
		formdata = {
			'login_email':'cincinnati-reds@outlook.com',
			'login_password':'Oicu812',
			'submit': 'Login'
		}
		yield FormRequest.from_response(response,
                                formdata=formdata,
                                clickdata={'name': 'submit'},
                                callback=self.parse1)
	def parse1(self, response):
		# yield scrapy.Request(url = "https://www.franchiseball.com/player.php?id=938370", callback = self.parse6)
		yield scrapy.Request(url = "https://www.franchiseball.com/research/data/index/leagues", callback = self.parse2)

	def parse2(self, response):

		leagues = response.xpath('//tr[@class]/td/a/@href').getall()
		for league in leagues:
			url = self.base_url + league
			yield scrapy.Request(url = url, callback= self.parse3)

	def parse3(self, response):
		teams = response.xpath('//div[contains(@class,"standings-team-row")]/div[contains(@style,"overflow:hidden")]/a/@href').getall()
		for team in teams:
			url = self.base_url + team
			yield scrapy.Request(url = url, callback= self.parse4)

		# url = self.base_url + teams[0]
		# yield scrapy.Request(url = url, callback= self.parse4)

	def parse4(self, response):
		tid = re.search(r'id=(.*)', response.url).group(1)
		researchUrl = "https://www.franchiseball.com/research.php?view=rosters&tid=" + tid

		yield scrapy.Request(url = researchUrl, callback = self.parse5)

	def parse5(self, response):
		players = response.xpath('//tr[@class="stat-row"]/td/a/@href').getall()

		for i, player in enumerate(players):

			url = self.base_url + player
			yield scrapy.Request(url=url, callback = self.parse6)

	def parse6(self, response):
		if response.css('#captchacharacters').extract_first():
			self.log("Captcha found")
		pid = re.search(r'id=(.*)', response.url).group(1)

		item = Item()
		
		item["player_link"] = response.url
		item["player_name"] = response.xpath(selectors["player_name"]).get(default="NA")
		item["team_name"] = response.xpath(selectors["team_name"]).get(default="NA")
		item["salary"] = response.xpath(selectors["salary"]).get(default="NA")
		item["ftv"] = response.xpath(selectors["ftv"]).get(default="NA")
		item["age"] = response.xpath(selectors["age"]).get(default="NA")

		item["pos"] =  self.remainAlpabetNumeric(response.xpath(selectors["pos"]).get(default = "NA"))
		if item["pos"] == "P":
			item["tbhrows"] = self.remainAlpabet(response.xpath(selectors["tbhrows_p"]).get(default="NA"))
			item["bats"] = self.remainAlpabet(response.xpath(selectors["bats_p"]).get(default="NA"))
		else:
			item["tbhrows"] = self.remainAlpabet(response.xpath(selectors["tbhrows"]).get(default="NA"))
			item["bats"] = self.remainAlpabet(response.xpath(selectors["bats"]).get(default="NA"))
		
		item["avg"] = response.xpath(selectors["avg"]).get(default="NA")
		item["slg"] = response.xpath(selectors["slg"]).get(default="NA")
		item["rbi"] = response.xpath(selectors["rbi"]).get(default="NA")
	    #season data
		item['season_ab'] = response.xpath(selectors["season_ab"]).get(default="NA")
		item["season_hits"] = response.xpath(selectors["season_hits"]).get(default="NA")
		item['season_avg'] = response.xpath(selectors["season_avg"]).get(default="NA")
		item['season_rbi'] = response.xpath(selectors["season_rbi"]).get(default="NA")
		item['season_slg'] = response.xpath(selectors["season_slg"]).get(default="NA")
		item['season_2b'] = response.xpath(selectors["season_2b"]).get(default="NA")
		item['season_3b'] = response.xpath(selectors["season_3b"]).get(default="NA")
		item['season_hr'] = response.xpath(selectors["season_hr"]).get(default="NA")
		item['season_bb'] = response.xpath(selectors["season_bb"]).get(default="NA")
		item['season_runs'] = response.xpath(selectors["season_runs"]).get(default="NA")
		item['season_tb'] = response.xpath(selectors["season_tb"]).get(default="NA")
		item['season_sb'] = response.xpath(selectors["season_sb"]).get(default="NA")
		item['season_sb_percent'] = response.xpath(selectors["season_sb_percent"]).get(default="NA")
		item['season_obp'] = response.xpath(selectors["season_obp"]).get(default="NA")
		item['season_obps'] = response.xpath(selectors["season_obps"]).get(default="NA")
		item['season_xbh'] = response.xpath(selectors["season_xbh"]).get(default="NA")
		item['season_ab_hr'] = response.xpath(selectors["season_ab_hr"]).get(default="NA")
		item['season_iso'] = response.xpath(selectors["season_iso"]).get(default="NA")
		item['season_rc'] = response.xpath(selectors["season_rc"]).get(default="NA")
		item['season_e'] = response.xpath(selectors["season_e"]).get(default="NA")

	    #minors data 
		item['minors_ab'] = response.xpath(selectors["minors_ab"]).get(default="NA")
		item['minors_hits'] = response.xpath(selectors["minors_hits"]).get(default="NA")
		item['minors_avg'] = response.xpath(selectors["minors_avg"]).get(default="NA")
		item['minors_rbi'] = response.xpath(selectors["minors_rbi"]).get(default="NA")
		item['minors_slg'] = response.xpath(selectors["minors_slg"]).get(default="NA")
		item['minors_2b'] = response.xpath(selectors["minors_2b"]).get(default="NA")
		item['minors_3b'] = response.xpath(selectors["minors_3b"]).get(default="NA")
		item['minors_hr'] = response.xpath(selectors["minors_hr"]).get(default="NA")
		item['minors_bb'] = response.xpath(selectors["minors_bb"]).get(default="NA")
		item['minors_tb'] = response.xpath(selectors["minors_tb"]).get(default="NA")
		item['minors_pa'] = response.xpath(selectors["minors_pa"]).get(default="NA")
		item['minors_obp'] = response.xpath(selectors["minors_obp"]).get(default="NA")
		item['minors_ops'] = response.xpath(selectors["minors_ops"]).get(default="NA")
		item['minors_bb_pa'] = response.xpath(selectors["minors_bb_pa"]).get(default="NA")
		item['minors_xbh'] = response.xpath(selectors["minors_xbh"]).get(default="NA")
		item['minors_ab_hr'] = response.xpath(selectors["minors_ab_hr"]).get(default="NA")
		item['minors_iso'] = response.xpath(selectors["minors_iso"]).get(default="NA")
		item['minors_rc'] = response.xpath(selectors["minors_rc"]).get(default="NA")

	    #scoutp data
		item['scoutp_control'] = response.xpath(selectors["scoutp_control"]).get(default="NA")
		item['scoutp_movement'] = response.xpath(selectors["scoutp_movement"]).get(default="NA")
		item['scoutp_velocity'] = response.xpath(selectors["scoutp_velocity"]).get(default="NA")
		item['scoutp_stamina'] = response.xpath(selectors["scoutp_stamina"]).get(default="NA")

	    #scouth data
		item['scouth_power'] = response.xpath(selectors["scouth_power"]).get(default="NA")
		item['scouth_contact'] = response.xpath(selectors["scouth_contact"]).get(default="NA")
		item['scouth_speed'] = response.xpath(selectors["scouth_speed"]).get(default="NA")
		item['scouth_defense'] = response.xpath(selectors["scouth_defense"]).get(default="NA")

	    #scoutr data
		item['scoutr_lf'] = self.clean(response.xpath(selectors["scoutr_lf"]).get(default="NA"))
		item['scoutr_lc'] = self.clean(response.xpath(selectors["scoutr_lc"]).get(default="NA"))
		item['scoutr_c'] = self.clean(response.xpath(selectors["scoutr_c"]).get(default="NA"))
		item['scoutr_rc'] = self.clean(response.xpath(selectors["scoutr_rc"]).get(default="NA"))
		item['scoutr_rf'] = self.clean(response.xpath(selectors["scoutr_rf"]).get(default="NA"))
		
		url = self.base_url + "/request.php?m=player&f=stats_career&pid=" + pid + '&limit=0'
		yield scrapy.Request(url = url, callback= self.parse7, cb_kwargs={'item': item})

	def parse7(self, response, item):

		no_career_data = True
		career_table_rows = response.xpath(selectors["career_table"])
		for row in range(0, len(career_table_rows)):
			#career data
			row_selector = selectors["career_table"] + "["+str(row+1)+"]"
			season_data = response.xpath(row_selector+selectors["career_season"]).get(default="NA")
			if season_data.isnumeric() :
				no_career_data = False
				item['career_season'] = season_data
				item['career_team'] = response.xpath(row_selector+selectors["career_team"]).get(default="NA")
				item['career_ab'] = response.xpath(row_selector+selectors["career_ab"]).get(default="NA")
				item['career_hits'] = response.xpath(row_selector+selectors["career_hits"]).get(default="NA")
				item['career_avg'] = response.xpath(row_selector+selectors["career_avg"]).get(default="NA")
				item['career_rbi'] = response.xpath(row_selector+selectors["career_rbi"]).get(default="NA")
				item['career_slg'] = response.xpath(row_selector+selectors["career_slg"]).get(default="NA")
				item['career_2b'] = response.xpath(row_selector+selectors["career_2b"]).get(default="NA")
				item['career_3b'] = response.xpath(row_selector+selectors["career_3b"]).get(default="NA")
				item['career_hr'] = response.xpath(row_selector+selectors["career_hr"]).get(default="NA")
				item['career_sb'] = response.xpath(row_selector+selectors["career_sb"]).get(default="NA")

				# self.log(item)
				yield item

		if no_career_data:
			item["career_season"] = "NA"
			item["career_team"] = "NA"
			item["career_ab"] = "NA"
			item["career_hits"] = "NA"
			item["career_avg"] = "NA"
			item["career_rbi"] = "NA"
			item["career_slg"] = "NA"
			item["career_2b"] = "NA"
			item["career_3b"] = "NA"
			item["career_hr"] = "NA"
			item["career_sb"] = "NA"
			yield item


	def clean(self,value):
		new_str = re.sub(r'[\t\n\r]',"",value)
		return new_str

	def remainAlpabet(self, value):

		value_1 = re.sub(r'[^a-zA-Z]',"",value)
		return value_1

	def remainAlpabetNumeric(self, value):

		value_1 = re.sub(r'[^a-zA-Z0-9]',"",value)
		return value_1

class Item(scrapy.Item):
    # define the fields for your item here like:
    
    player_link = scrapy.Field()
    player_name = scrapy.Field()
    team_name = scrapy.Field()
    salary = scrapy.Field()
    ftv = scrapy.Field()
    age = scrapy.Field()
    tbhrows = scrapy.Field()
    bats = scrapy.Field()
    avg = scrapy.Field()
    slg = scrapy.Field()
    rbi = scrapy.Field()
    pos = scrapy.Field()

    #season data
    season_ab = scrapy.Field()
    season_hits = scrapy.Field()
    season_avg = scrapy.Field()
    season_rbi = scrapy.Field()
    season_slg = scrapy.Field()
    season_2b = scrapy.Field()
    season_3b = scrapy.Field()
    season_hr = scrapy.Field()
    season_bb = scrapy.Field()
    season_runs = scrapy.Field()
    season_tb = scrapy.Field()
    season_sb = scrapy.Field()
    season_sb_percent = scrapy.Field()
    season_obp = scrapy.Field()
    season_obps = scrapy.Field()
    season_xbh = scrapy.Field()
    season_ab_hr = scrapy.Field()
    season_iso = scrapy.Field()
    season_rc = scrapy.Field()
    season_e = scrapy.Field()

    #career data
    career_season = scrapy.Field()
    career_team = scrapy.Field()
    career_ab = scrapy.Field()
    career_hits = scrapy.Field()
    career_avg = scrapy.Field()
    career_rbi = scrapy.Field()
    career_slg = scrapy.Field()
    career_2b = scrapy.Field()
    career_3b = scrapy.Field()
    career_hr = scrapy.Field()
    career_sb = scrapy.Field()

    #minors data 
    minors_ab = scrapy.Field()
    minors_hits = scrapy.Field()
    minors_avg = scrapy.Field()
    minors_rbi = scrapy.Field()
    minors_slg = scrapy.Field()
    minors_2b = scrapy.Field()
    minors_3b = scrapy.Field()
    minors_hr = scrapy.Field()
    minors_bb = scrapy.Field()
    minors_tb = scrapy.Field()
    minors_pa = scrapy.Field()
    minors_obp = scrapy.Field()
    minors_ops = scrapy.Field()
    minors_bb_pa = scrapy.Field()
    minors_xbh = scrapy.Field()
    minors_ab_hr = scrapy.Field()
    minors_iso = scrapy.Field()
    minors_rc = scrapy.Field()

    #scoutp data
    scoutp_control = scrapy.Field()
    scoutp_movement = scrapy.Field()
    scoutp_velocity = scrapy.Field()
    scoutp_stamina = scrapy.Field()

    #scouth data
    scouth_power = scrapy.Field()
    scouth_contact = scrapy.Field()
    scouth_speed = scrapy.Field()
    scouth_defense = scrapy.Field()

    #scoutr data
    scoutr_lf = scrapy.Field()
    scoutr_lc = scrapy.Field()
    scoutr_c = scrapy.Field()
    scoutr_rc = scrapy.Field()
    scoutr_rf = scrapy.Field()



FIELDNAMES = [
			"PLAYERLINK",
			"PLAYERNAME",
			"TEAMNAME",
			"SALARY",
			"FTV",
			"AGE",
			"TBHROWS",
			"BATS",
			"AVE",
			"SLG",
			"RBI",
			"POS",
			"SEASON-AB",
			"SEASON-HITS",
			"SEASON-AVG",
			"SEASON-RBI",
			"SEASON-SLG",
			"SEASON-2B",
			"SEASON-3B",
			"SEASON-HR",
			"SEASON-BB",
			"SEASON-RUNS",
			"SEASON-TB",
			"SEASON-SB",
			"SEASON-SB%",
			"SEASON-OBP",
			"SEASON-OPS",
			"SEASON-XBH",
			"SEASON-AB/HR",
			"SEASON-ISO",
			"SEASON-RC",
			"SEASON-E",
			"CAREER-SEASON",
			"CAREER-TEAM",
			"CAREER-AB",
			"CAREER-HITS",
			"CAREER-AVG",
			"CAREER-RBI",
			"CAREER-SLG",
			"CAREER-2B",
			"CAREER-3B",
			"CAREER-HR",
			"CAREER-SB",
			"MINORS-AB",
			"MINORS-HITS",
			"MINORS-AVG",
			"MINORS-RBI",
			"NINORS-SLG",
			"MINORS-2B",
			"MINORS-3B",
			"MINORS-HR",
			"MINORS-BB",
			"MINORS-TB",
			"MINORS-PA",
			"MINORS-OBP",
			"MINORS-OPS",
			"MINORS-BB/PA",
			"MINORS-XBH",
			"MINORS-AB/HR",
			"MINORS-ISO",
			"MINORS-RC",
			"SCOUTP-CONTROL",
			"SCOUTP-MOVEMENT",
			"SCOUTP-VELOCITY",
			"SCOUTP-STAMINA",
			"SCOUTH-POWER",
			"SCOUTH-CONTACT",
			"SCOUTH-SPEED",
			"SCOUTH-DEFENSE",
			"SCOUTR-LF",
			"SCOUTR-LC",
			"SCOUTR-C",
			"SCOUTR-RC",
			"SCOUTR-RF"
]

class XLSXPipeline(object):
    wb = None
    ws = None

    def open_spider(self, spider):
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active

        self.ws.append(FIELDNAMES)
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.ws.append([
        	adapter.get("player_link"),
        	adapter.get("player_name"), 
        	adapter.get("team_name"),
        	adapter.get("salary"),
        	adapter.get("ftv"),
        	adapter.get("age"),
        	adapter.get("tbhrows"),
        	adapter.get("bats"),
        	adapter.get("avg"),
        	adapter.get("slg"),
        	adapter.get("rbi"),
        	adapter.get("pos"),
        	adapter.get("season_ab"),
        	adapter.get("season_hits"),
        	adapter.get("season_avg"),
        	adapter.get("season_rbi"),
        	adapter.get("season_slg"),
        	adapter.get("season_2b"),
        	adapter.get("season_3b"),
        	adapter.get("season_hr"),
        	adapter.get("season_bb"),
        	adapter.get("season_runs"),
        	adapter.get("season_tb"),
        	adapter.get("season_sb"),
        	adapter.get("season_sb_percent"),
        	adapter.get("season_obp"),
        	adapter.get("season_obps"),
        	adapter.get("season_xbh"),
        	adapter.get("season_ab_hr"),
        	adapter.get("season_iso"),
        	adapter.get("season_rc"),
        	adapter.get("season_e"),
        	adapter.get("career_season"),
        	adapter.get("career_team"),
        	adapter.get("career_ab"),
        	adapter.get("career_hits"),
        	adapter.get("career_avg"),
        	adapter.get("career_rbi"),
        	adapter.get("career_slg"),
        	adapter.get("career_2b"),
        	adapter.get("career_3b"),
        	adapter.get("career_hr"),
        	adapter.get("career_sb"),
        	adapter.get("minors_ab"),
        	adapter.get("minors_hits"),
        	adapter.get("minors_avg"),
        	adapter.get("minors_rbi"),
        	adapter.get("minors_slg"),
        	adapter.get("minors_2b"),
        	adapter.get("minors_3b"),
        	adapter.get("minors_hr"),
        	adapter.get("minors_bb"),
        	adapter.get("minors_tb"),
        	adapter.get("minors_pa"),
        	adapter.get("minors_obp"),
        	adapter.get("minors_ops"),
        	adapter.get("minors_bb_pa"),
        	adapter.get("minors_xbh"),
        	adapter.get("minors_ab_hr"),
        	adapter.get("minors_iso"),
        	adapter.get("minors_rc"),
        	adapter.get("scoutp_control"),
        	adapter.get("scoutp_movement"),
        	adapter.get("scoutp_velocity"),
        	adapter.get("scoutp_stamina"),
        	adapter.get("scouth_power"),
        	adapter.get("scouth_contact"),
        	adapter.get("scouth_speed"),
        	adapter.get("scouth_defense"),
        	adapter.get("scoutr_lf"),
        	adapter.get("scoutr_lc"),
        	adapter.get("scoutr_c"),
        	adapter.get("scoutr_rc"),
        	adapter.get("scoutr_rf")
        	])

        return item

    def close_spider(self, spider):
        self.wb.save('output.xlsx')


selectors = {
	"player_name" : '//div[@id="player-general-info"]/div[1]/span[1]/text()',
    "team_name" : '//div[@id="player-general-info"]/div[1]/span/a/text()',
    "salary" : '//div[@id="player-general-info"]/div[2]/a/text()',
    "ftv" : '//*[@id="player-general-info"]/div[3]/span[2]/text()',
    "age" : '//*[@id="player-general-info"]/div[4]/span[2]/text()',
    "pos" : '//*[@id="player-general-info"]/div[1]/span/span[@style="color:#000;"]/text()',
    "tbhrows_p" : '//*[@id="player-general-info"]/div[1]/div/span[2]/text()',
    "tbhrows" : '//*[@id="player-general-info"]/div[1]/div/span[1]/text()',
    "bats_p" : '//*[@id="player-general-info"]/div[1]/div/span[4]/text()',
    "bats" : '//*[@id="player-general-info"]/div[1]/div/span[3]/text()',
    "avg" : '//*[@id="player-feature-stats"]/div[@title="Batting Avg"]/div/text()',
    "slg" : '//*[@id="player-feature-stats"]/div[@title="Slugging %"]/div/text()',
    "rbi" : '//*[@id="player-feature-stats"]/div[@title="Runs Batted In"]/div/text()',

    "season_ab" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="At-Bats"]/div[2]/text()',
    "season_hits" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Hits"]/div[2]/text()',
    "season_avg" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Batting Average"]/div[2]/text()',
    "season_rbi" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Runs Batted In"]/div[2]/text()',
    "season_slg" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Slugging %"]/div[2]/text()',
    "season_2b" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Doubles"]/div[2]/text()',
    "season_3b" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Triples"]/div[2]/text()',
    "season_hr" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Homeruns"]/div[2]/text()',
    "season_bb" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Walks"]/div[2]/text()',
    "season_runs" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Runs Scored"]/div[2]/text()',
    "season_tb" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Total Bases"]/div[2]/text()',
    "season_sb" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Stolen Bases"]/div[2]/text()',
    "season_sb_percent" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Steal Success %"]/div[2]/text()',
    "season_obp" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="On-Base %"]/div[2]/text()',
    "season_obps" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="On-Base % + Slugging %"]/div[2]/text()',
    "season_xbh" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Extra Basehits"]/div[2]/text()',
    "season_ab_hr" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="At-Bats Per Homerun"]/div[2]/text()',
    "season_iso" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Isolated Power"]/div[2]/text()',
    "season_rc" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Runs Created"]/div[2]/text()',
    "season_e" : '//div[@id="tab-content-stats-season"]/div/div/div[@title="Fielding Errors"]/div[2]/text()',

    "career_table": '//*[@id="tab-content-stats-career-table"]/tr',
    "career_season" : '/td[1]/text()',
    "career_team" : '/td[2]/a/text()',
    "career_ab" : '/td[3]/text()',
    "career_hits" : '/td[4]/text()',
    "career_avg" : '/td[5]/text()',
    "career_rbi" : '/td[6]/text()',
    "career_slg" : '/td[7]/text()',
    "career_2b" : '/td[8]/text()',
    "career_3b" : '/td[9]/text()',
    "career_hr" : '/td[10]/text()',
    "career_sb" : '/td[11]/text()',

    "minors_ab" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="At-Bats"]/div[2]/text()',
    "minors_hits" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Hits"]/div[2]/text()',
    "minors_avg" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Batting Average"]/div[2]/text()',
    "minors_rbi" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Runs Batted In"]/div[2]/text()',
    "minors_slg" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Slugging %"]/div[2]/text()',
    "minors_2b" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Doubles"]/div[2]/text()',
    "minors_3b" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Triples"]/div[2]/text()',
    "minors_hr" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Homeruns"]/div[2]/text()',
    "minors_bb" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Walks"]/div[2]/text()',
    "minors_tb" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Total Bases"]/div[2]/text()',
    "minors_pa" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Plate Appearances"]/div[2]/text()',
    "minors_obp" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="On-Base %"]/div[2]/text()',
    "minors_ops" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="On-Base % + Slugging %"]/div[2]/text()',
    "minors_bb_pa" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Walks Per Plate Appearance"]/div[2]/text()',
    "minors_xbh" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Extra Basehits"]/div[2]/text()',
    "minors_ab_hr" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="At-Bats Per Homerun"]/div[2]/text()',
    "minors_iso" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Isolated Power"]/div[2]/text()',
    "minors_rc" : '//*[@id="tab-content-stats-minor"]/div/div/div[@title="Runs Created"]/div[2]/text()',

    "scoutp_control" : '//*[@id="ratings-pitching-bars-container"]/div/div[1]/div/div[1]/span/text()',
    "scoutp_movement" : '//*[@id="ratings-pitching-bars-container"]/div/div[2]/div/div[1]/span/text()',
    "scoutp_velocity" : '//*[@id="ratings-pitching-bars-container"]/div/div[3]/div/div[1]/span/text()',
    "scoutp_stamina" : '//*[@id="ratings-pitching-bars-container"]/div/div[4]/div/div[1]/span/text()',

    "scouth_power" : '//*[@id="ratings-hitting-bars-container"]/div/div/div[1]/div/div[1]/span/text()',
    "scouth_contact" : '//*[@id="ratings-hitting-bars-container"]/div/div/div[2]/div/div[1]/span/text()',
    "scouth_speed" : '//*[@id="ratings-hitting-bars-container"]/div/div/div[3]/div/div[1]/span/text()',
    "scouth_defense" : '//*[@id="ratings-hitting-bars-container"]/div/div/div[4]/div/div[1]/span/text()',

    "scoutr_lf" : '//*[@id="range-grid-container"]/div/svg/text[1]/text()',
    "scoutr_lc" : '//*[@id="range-grid-container"]/div/svg/text[2]/text()',
    "scoutr_c" : '//*[@id="range-grid-container"]/div/svg/text[3]/text()',
    "scoutr_rc" : '//*[@id="range-grid-container"]/div/svg/text[4]/text()',
    "scoutr_rf" : '//*[@id="range-grid-container"]/div/svg/text[5]/text()',
}

def start_crawl():
	print("Start Crawling...")
	configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
	runner = CrawlerRunner()
	d = runner.crawl(FranchiseScrapy)
	d.addBoth(lambda _: reactor.stop())
	reactor.run()

start_crawl()
schedule.every().monday.do(start_crawl)

while True:
	schedule.run_pending()
    # time.sleep(1)