from django.shortcuts import render
import requests
import re
import time
from django.http import HttpResponse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options




def scraper(self):
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_driver = '/mnt/c/webdrivers/chromedriver.exe'
	driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
	page = ''
	trip_advisor_url = 'https://www.tripadvisor.com/Attraction_Review-g28970-d3161320-Reviews-Washington_DC_Urban_Adventures-Washington_DC_District_of_Columbia.html'
	
	driver.get(trip_advisor_url)
	html = driver.page_source
	soup = BeautifulSoup(html, "lxml")
	last_page = soup.find("a", {"class": "last"}).text

	

	name = "Guergana"
	date = ''
	data_list = []
	i = 0
	while i < int(last_page):
	# while i < 3:
		page = '-or' + str(i * 10)
		if i == 0:
			page = ''
		i += 1
		trip_advisor_url = 'https://www.tripadvisor.com/Attraction_Review-g28970-d3161320-Reviews' + page + '-Washington_DC_Urban_Adventures-Washington_DC_District_of_Columbia.html'
		driver.get(trip_advisor_url)
		time.sleep(1)
		elem = driver.find_element_by_class_name('ulBlueLinks')
		elem.click()
		time.sleep(1)
		html = driver.page_source
		soup = BeautifulSoup(html, "lxml")
		data = soup.find_all("div", {"class": "innerBubble"})
		for item in data:
			entry = {}
			p = item.find("p").text
			if re.search(name, p, re.IGNORECASE):
				rating = item.find("span", {"class": "ui_bubble_rating"})
				if rating.get("class")[1] == "bubble_50": 
					entry['link'] = trip_advisor_url
					entry['date'] = item.find("span", {"class": "ratingDate"}).text.replace("Reviewed ", "")
					entry['user'] = item.find("span", {"class": "thankUser"}).text.replace("Thank ", "")
					data_list.append(entry)

	total = "Holy cow, " + name + "! You have " + str(len(data_list)) + " FIVE STAR REVIEWS between today and " + data_list[-1]['date'] + "!  "
	data_list.insert(0, total)

	return HttpResponse(data_list)