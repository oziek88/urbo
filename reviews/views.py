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
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options


from .forms import findMyReviewsForm

def scraper(request):
	proxies = {
		"http": 'http://159.203.152.83:8080', 
		"https": 'http://159.203.152.83:8080'
	}

	PROXY = "79.1.255.238:8080" # IP:PORT or HOST:PORT

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--proxy-server=%s' % PROXY)

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
		first_date = form.cleaned_data['From'].strftime("%Y%m%d")
		last_date = form.cleaned_data['To'].strftime("%Y%m%d")
		# for viator dates
		first_date_m = form.cleaned_data['From'].strftime("%Y%m")
		last_date_m = form.cleaned_data['To'].strftime("%Y%m")

		# confirm_message = "SEARCHING FOR YOUR REVIEWS"
		page = ''
		trip_advisor_url = 'https://www.tripadvisor.com/Attraction_Review-g28970-d3161320-Reviews-Washington_DC_Urban_Adventures-Washington_DC_District_of_Columbia.html'
		viator_unveiled_url = 'https://www.viator.com/tours/Washington-DC/Capitol-Hill-and-DC-Monuments-Tour-by-Electric-Cart/d657-5713UNVEILED?subPageType=TR&reviewSortBy=-PRODUCT_RATING+D-PUBLISHED_TIMESTAMP+D-'

		### Scrape Viator ###

		## From Scrape
		# driver.get(viator_unveiled_url)
		# # WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'line pvm light-border-t small')))
		# time.sleep(35)
		# html = driver.page_source
		
		## Using File
		scrape_file_path = '/Users/oziek/Documents/urbo/viator_scrape_ex.txt'
		viator_scrape_file = open(scrape_file_path,'r')
		html = viator_scrape_file.read()

		soup = BeautifulSoup(html, "lxml")
		
		pagination = soup.find("div", {"class": "line pvm light-border-t small"})
		term = pagination.find("div", {"class": "man"}).text
		last_page = term.replace("Viewing 1 of ","")

		## Rewrite Scrape File on Successful Scrape
		# scrape_file_path = '/Users/oziek/Documents/urbo/viator_scrape_ex.txt'
		# viator_scrape_file = open(scrape_file_path,'w')
		# viator_scrape_file.write(html)
		
		## Close File
		viator_scrape_file.close()

		i = 0
		while i < int(last_page):
			time.sleep(randint(2, 7))
			data = soup.find_all("div", {"class": "media man"})[:-2]
			# print(data)
			for item in data:
				d = item.find_all("span", {"class": "xsmall note"})[1].text
				temp_date_m = datetime.strptime(d, ' %B %Y ').strftime("%Y%m")
				if int(temp_date_m) > int(last_date_m):
					print("TOO NEW")
				elif int(temp_date_m) < int(first_date_m):
					print("TOO OLD")
					i = int(last_page) + 1
				else:
					print("LOOKING GOOD")
					review = item.find("div", {"class": "unit mrs mlm"})

					if review.get("title") == "5 star rating: Highly Recommended":
						comment_div = item.find("div", {"class": "cms-content mhm"})
						p = comment_div.find_all("p")[1].text
						if re.search(name, p, re.IGNORECASE):
							print("YES")
							entry = {}
							entry['link'] = "Viator"
							entry['user'] = item.find("p").text
							entry['date'] = temp_date_m + " *"
							entry['tour'] = "Capitol Hill and DC Monuments Tour by Electric Cart"
							data_list.append(entry)
		

		# Scrape TripAdvisor ##

		## From Scrape
		driver.get(trip_advisor_url)
		time.sleep(randint(2, 7))
		html = driver.page_source
		soup = BeautifulSoup(html, "lxml")

		## Using File
		# scrape_file_path = '/Users/oziek/Documents/urbo/tripadvisor_scrape_ex.txt'
		# tripadvisor_scrape_file = open(scrape_file_path,'r')
		# html = tripadvisor_scrape_file.read()
		# soup = BeautifulSoup(html, "lxml")
		# tripadvisor_scrape_file.close()

		last_page = soup.find("a", {"class": "last"}).text
		time.sleep(1)

		i = 0
		while i < int(last_page):
			time.sleep(randint(2, 7))
			
			## From Scrape
			html = driver.page_source
			soup = BeautifulSoup(html, "lxml")
			time.sleep(randint(1, 3))

			## Rewrite Scrape File on Successful Scrape
			elem = driver.find_element_by_xpath("//span[contains(@class,'ulBlueLinks')][contains(text(),'More')]")
			elem.click()
			scrape_file_path = '/Users/oziek/Documents/urbo/tripadvisor_scrape_ex.txt'
			tripadvisor_scrape_file = open(scrape_file_path,'r')
			if i == 0:
				tripadvisor_scrape_file.close()
				tripadvisor_scrape_file = open(scrape_file_path,'w')
			tripadvisor_scrape_file.write(html)
			tripadvisor_scrape_file.close()

			data = soup.find_all("div", {"class": "reviewSelector"})
	
			for item in data:
				print("TRIPADVISOR")
				d = item.find("span", {"class": "ratingDate"})["title"]
				temp_date = datetime.strptime(d, '%B %d, %Y').strftime("%Y%m%d")
				if int(temp_date) > int(last_date):
					print("TOO NEW")
				elif int(temp_date) < int(first_date):
					print("TOO OLD")
					i = int(last_page) + 1
				else:
					p = item.find("p").text
					print("LOOKING GOOD")
					if re.search(name, p, re.IGNORECASE):
						rating = item.find("span", {"class": "ui_bubble_rating"})
						if rating.get("class")[1] == "bubble_50": 
							entry = {}
							entry['link'] = "Trip Advisor"
							entry['user'] = item.find("span", {"class": "thankUser"}).text.replace("Thank ", "")
							entry['date'] = temp_date
							entry['tour'] = "DC Unveiled"
							data_list.append(entry)
			time.sleep(randint(2, 5))
			if i < int(last_page):
				next_page = driver.find_element_by_xpath("//div[(@id='REVIEWS')] //a[contains(@class,'next')] [contains(text(),'Next')]")
				next_page.click()

		total = "Holy cow, " + name + "! You have " + str(len(data_list)) + " FIVE STAR REVIEWS between " + first_date + " and " + last_date + "!  "
	context = {'title': 'Search for Reviews', 'form': form, 'confirm_message': confirm_message, 'total': total, 'data_list': data_list, }
	template = 'home.html'
	return render(request,template,context)