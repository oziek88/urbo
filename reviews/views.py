from django.shortcuts import render
import requests
import re
import time
import timestring
from datetime import datetime
from random import randint
from django.http import HttpResponse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.chrome.options import Options


from .forms import findMyReviewsForm

def scraper(request):
	proxies = {
		"http": 'http://159.203.152.83:8080', 
		"https": 'http://159.203.152.83:8080'
	}

	PROXY = "188.166.83.6:8080" # IP:PORT or HOST:PORT

	chrome_options = webdriver.ChromeOptions()
	# chrome_options.add_argument('--proxy-server=%s' % PROXY)

	# chrome_options = Options()
	chrome_options.add_argument("--headless")
	## windows ##
	# chrome_driver = '/mnt/c/webdrivers/chromedriver.exe'
	## mac ##
	chrome_driver = '/usr/local/bin/chromedriver'
	driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
	driver.maximize_window()
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
		viator_unveiled_url = 'https://www.viator.com/tours/Washington-DC/Capitol-Hill-and-DC-Monuments-Tour-by-Electric-Cart/d657-5713UNVEILED?subPageType=TR'

		## Scrape Viator ##
		# r  = requests.get(viator_unveiled_url, proxies=proxies)
		# time.sleep(25)
		# html = r.text
		# time.sleep(5)


		driver.get(viator_unveiled_url)
		# WebDriverWait(driver, 60).until(lambda x: x.find_element_by_class_name('line pvm light-border-t small'))
		time.sleep(25)
		html = driver.page_source
		# time.sleep(25)
		soup = BeautifulSoup(html, "lxml")
		print(soup)
		# time.sleep(5)
		# root = soup.Element('root')
		# print(soup)
		# filename = "/tmp/viator_scrape.xml"
		
		pagination = soup.find("div", {"class": "line pvm light-border-t small"})
		print(pagination)
		term = pagination.find("div", {"class": "man"}).text
		last_page = term.replace("Viewing 1 of ","")

		time.sleep(1)

		i = 0
		while i < int(last_page):
			time.sleep(randint(2, 7))
			data = soup.find_all("div", {"class": "media man"})[:-2]
			print(data)
			for item in data:
				d = item.find_all("span", {"class": "xsmall note"})[1].text
				temp_date = datetime.strptime(d, ' %B %Y ').strftime('%B %Y')
				print(first_date)
				print(temp_date)
				print(last_date)
				if temp_date < first_date:
					if temp_date > last_date:
						print("TOO RECENT")
					else:
						i = int(last_page) + 1
						print("TOO OLD")
				else:
					print("Just Right")
				print("CHECK THE CONTINUE")
			i = int(last_page) + 1
		return

		# Scrape TripAdvisor ##

		driver.get(trip_advisor_url)
		# driver.maximize_window()
		time.sleep(3)
		html = driver.page_source
		soup = BeautifulSoup(html, "lxml")
		last_page = soup.find("a", {"class": "last"}).text
		time.sleep(1)

		i = 0
		while i < int(last_page):
			time.sleep(randint(2, 7))
			elem = driver.find_element_by_xpath("//span[contains(@class,'ulBlueLinks')][contains(text(),'More')]")
			elem.click()
			time.sleep(1)
			# html = driver.page_source
			# soup = BeautifulSoup(html, "lxml")
			data = soup.find_all("div", {"class": "reviewSelector"})
	
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
			time.sleep(randint(2, 5))
			next_page = driver.find_element_by_xpath("//div[(@id='REVIEWS')] //a[contains(@class,'next')] [contains(text(),'Next')]")
			next_page.click()

		total = "Holy cow, " + name + "! You have " + str(len(data_list)) + " FIVE STAR REVIEWS between " + first_date + " and " + last_date + "!  "
	context = {'title': 'Search for Reviews', 'form': form, 'confirm_message': confirm_message, 'total': total, 'data_list': data_list, }
	template = 'home.html'
	return render(request,template,context)