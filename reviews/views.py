from django.shortcuts import render
import requests
import re
import time
import timestring
from django.http import HttpResponse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .forms import findMyReviewsForm

def scraper(request):
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_driver = '/mnt/c/webdrivers/chromedriver.exe'
	driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

	form = findMyReviewsForm(request.POST or None)
	confirm_message = None
	data_list = []
	total = ""

	if form.is_valid():
		name = form.cleaned_data['name']
		first_date = form.cleaned_data['From'].strftime("%B %d, %Y")
		last_date = form.cleaned_data['To'].strftime("%B %d, %Y")
		# confirm_message = "SEARCHING FOR YOUR REVIEWS"

		page = ''
		trip_advisor_url = 'https://www.tripadvisor.com/Attraction_Review-g28970-d3161320-Reviews-Washington_DC_Urban_Adventures-Washington_DC_District_of_Columbia.html'
		
		driver.get(trip_advisor_url)
		driver.maximize_window()
		time.sleep(3)
		html = driver.page_source
		soup = BeautifulSoup(html, "lxml")
		last_page = soup.find("a", {"class": "last"}).text
		time.sleep(1)

		i = 0
		while i < int(last_page):
			# page = '-or' + str(i * 10)
			# if i == 0:
			# 	page = ''
			# i += 1
			# trip_advisor_url = 'https://www.tripadvisor.com/Attraction_Review-g28970-d3161320-Reviews' + page + '-Washington_DC_Urban_Adventures-Washington_DC_District_of_Columbia.html'
			# driver.get(trip_advisor_url)
			time.sleep(1)
			# elem = driver.find_element_by_class_name('ulBlueLinks')
			elem = driver.find_element_by_xpath("//span[contains(@class,'ulBlueLinks')][contains(text(),'More')]")
			# elem = driver.find_element_by_xpath("//span[contains(text(), 'More') and @class='ulBlueLinks']")
			elem.click()
			time.sleep(1)
			html = driver.page_source
			soup = BeautifulSoup(html, "lxml")
			print(soup)
			data = soup.find_all("div", {"class": "reviewSelector"})
			print(data)
			for item in data:
				temp_date = item.find("span", {"class": "ratingDate"})["title"]
				if temp_date < first_date:
					i = int(last_page) + 1
					print("END!!!!!!!!!!!!!!")
				else:
					p = item.find("p").text
					if re.search(name, p, re.IGNORECASE) and temp_date <= last_date:
						rating = item.find("span", {"class": "ui_bubble_rating"})
						if rating.get("class")[1] == "bubble_50": 
							entry = {}
							entry['link'] = "Trip Advisor"
							entry['user'] = item.find("span", {"class": "thankUser"}).text.replace("Thank ", "")
							entry['date'] = temp_date
							entry['tour'] = "DC Unveiled"
							data_list.append(entry)
			time.sleep(1)
			next_page = driver.find_element_by_xpath("//div[(@id='REVIEWS')] //a[contains(@class,'next')] [contains(text(),'Next')]")
			next_page.click()

		total = "Holy cow, " + name + "! You have " + str(len(data_list)) + " FIVE STAR REVIEWS between " + first_date + " and " + last_date + "!  "
	context = {'title': 'Search for Reviews', 'form': form, 'confirm_message': confirm_message, 'total': total, 'data_list': data_list, }
	template = 'home.html'
	return render(request,template,context)