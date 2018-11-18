from django.shortcuts import render
import json
import requests
import re
import time
import timestring
from itertools import chain
from datetime import datetime
from random import randint
from django.http import HttpResponse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options

from .models import Reviews

from .forms import findMyReviewsForm

def review_description(request):
	if request.method == 'POST':
		for id in request.POST:
			description = Reviews.objects.get(id=id).description
			json_return = json.dumps({"description" : description})
			return HttpResponse(json_return, content_type ="application/json")

def review_results(request):
		if request.method == 'POST':
			form = findMyReviewsForm(request.POST or None)
			data_list = []
			if form.is_valid():
				name = form.cleaned_data['name']
				city = form.cleaned_data['city']
				first_date = int(form.cleaned_data['From'].strftime("%Y%m%d"))
				last_date = int(form.cleaned_data['To'].strftime("%Y%m%d"))
				first_date_printed = form.cleaned_data['From'].strftime("%B %d, %Y")
				last_date_printed = form.cleaned_data['To'].strftime("%B %d, %Y")
				# for viator dates
				first_date_m = int(form.cleaned_data['From'].strftime("%Y%m" + "00"))
				last_date_m = int(form.cleaned_data['To'].strftime("%Y%m" + "00"))

				tripadvisor_reviews = Reviews.objects.filter(city=city, source="Trip Advisor", date_of_review__gte=first_date, date_of_review__lte=last_date).order_by('-date_of_review')
				viator_reviews = Reviews.objects.filter(city=city, source="Viator", date_of_review__gte=first_date_m, date_of_review__lte=last_date_m).order_by('-date_of_review')

				reviews = list(chain(tripadvisor_reviews, viator_reviews))

				for review in reviews:
					names = name.split(", ")
					for n in names:
						if re.search(n, review.description, re.IGNORECASE):
							r = Reviews.objects.get(tour=review.tour, reviewer_name=review.reviewer_name, date_of_review=review.date_of_review)
							r.guide = names[0].lower()
							r.save()

							printed_date = None
							try:
								printed_date = datetime.strptime(str(review.date_of_review), '%Y%m%d').strftime("%B %d, %Y")
							except:
								printed_date = datetime.strptime(str(review.date_of_review), '%Y%m00').strftime("%B, %Y")

							if review.rating == 5:
								entry = {}
								entry['link'] = review.source
								entry['user'] = review.reviewer_name
								entry['date'] = printed_date
								entry['tour'] = review.tour
								entry['id'] = review.id
								data_list.append(entry)
				json_return = json.dumps({"reviews" : data_list})
				return HttpResponse(json_return, content_type ="application/json")
			else:
				return HttpResponse('failed')  

def scrape_sites(city):
	PROXY = "206.189.145.96:8080" # IP:PORT or HOST:PORT

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--proxy-server=%s' % PROXY)
	chrome_options.add_argument("--headless")

	## windows ##
	# chrome_driver = '/mnt/c/webdrivers/chromedriver.exe'
	## mac ##
	chrome_driver = '/usr/local/bin/chromedriver'

	driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
	driver.maximize_window()

	page = ''

	urls = {
		"barcelona": {
			"tripadvisor": 'https://www.tripadvisor.co.uk/Attraction_Review-g187497-d1856792-Reviews-Barcelona_Urban_Adventures-Barcelona_Catalonia.html',
			"city": 'Barcelona'
		},
		"washington_dc": {
			"tripadvisor": 'https://www.tripadvisor.co.uk/Attraction_Review-g28970-d3161320-Reviews-Washington_DC_Urban_Adventures-Washington_DC_District_of_Columbia.html',
			"viator": ['https://www.viator.com/tours/Washington-DC/Capitol-Hill-and-DC-Monuments-Tour-by-Electric-Cart/d657-5713UNVEILED?subPageType=TR', 'https://www.viator.com/tours/Washington-DC/Washington-DC-Monuments-by-Moonlight-Electric-Cart-Tour/d657-5713UASEA12?subPageType=TR', 'https://www.viator.com/tours/Washington-DC/Politics-and-Pints-Small-Group-Capitol-Hill-Tour-with-Local-Guide/d657-5713P55?subPageType=TR', 'https://www.viator.com/tours/Washington-DC/Sample-Tastes-of-H-Street-Walking-Tour-With-Craft-Beer-Tasting/d657-5713P68?subPageType=TR', 'https://www.viator.com/tours/Washington-DC/Museum-of-American-History-Through-Music-Small-Group-Tour/d657-5713P75', 'https://www.viator.com/tours/Washington-DC/Smithsonian-American-Art-Small-Group-Adventure/d657-5713P79', 'https://www.viator.com/tours/Washington-DC/DC-Craft-Cocktail-Evening-Tour/d657-5713P74/important-info', 'https://www.viator.com/tours/Washington-DC/Total-DC-Tour-DC-Unveiled-and-Music-History/d657-5713P80', 'https://www.viator.com/tours/Washington-DC/Total-DC-Evening-Tour-Art-and-Cocktails/d657-5713P78', 'https://www.viator.com/tours/Washington-DC/Total-DC-Evening-Tour-American-Art-and-Monuments-by-Night/d657-5713P77'],
			"city": 'Washington DC'
		}
	}

	current_city = None
	trip_advisor_url = None
	viator_urls = None
	new_reviews_saved = 0

	if str(city) in urls:
		if "city" in urls[str(city)]:
			current_city = urls[str(city)]["city"]
			print(current_city + " exists in urls")
		if "tripadvisor" in urls[str(city)]:
			trip_advisor_url = urls[str(city)]["tripadvisor"]
			print("Contains Tripadvisor URL")
		if "viator" in urls[str(city)]:
			viator_urls = urls[str(city)]["viator"]
			print("Contains Viator URL")

	# Scrape TripAdvisor ##
	if trip_advisor_url != None:
		print("Initiating Tripadvisor Scrape")

		driver.get(trip_advisor_url)
		time.sleep(randint(4, 7))
		html = driver.page_source
		time.sleep(randint(4, 7))
		soup = BeautifulSoup(html, "lxml")

		last_page = soup.find("a", {"class": "last"}).text
		time.sleep(1)

		i = 0
		while i < int(last_page):
			time.sleep(randint(2, 7))

			try:
				elem = driver.find_element_by_xpath("//span[contains(@class,'ulBlueLinks')][contains(text(),'More')]")
				elem.click()
				print("'MORE' WAS CLICKED")
			except:
				print("'More' not clicked!")

			time.sleep(randint(2, 4))
			html = driver.page_source
			time.sleep(randint(3, 4))
			soup = BeautifulSoup(html, "lxml")

			data = soup.find_all("div", {"class": "reviewSelector"})
		
			for item in data:
				# print("TRIPADVISOR")
				d = item.find("span", {"class": "ratingDate"})["title"]
				temp_date = ''
				try:
					temp_date = datetime.strptime(d, '%B %d, %Y').strftime("%Y%m%d")
				except:
					temp_date = datetime.strptime(d, '%d %B %Y').strftime("%Y%m%d")
				## Store to database ##
				tour = "Not Specified"
				if item.find("div", {"class": "review_location_attribution"}):
					tour = item.find("div", {"class": "review_location_attribution"}).find("a").text
				date_of_review = int(temp_date)
				source = "Trip Advisor"
				reviewer_name = item.find("span", {"class": "thankUser"}).text.replace("Thank ", "")
				rating = int(item.find("span", {"class": "ui_bubble_rating"}).get("class")[1].replace("bubble_", "")[0])
				description = item.find("p").text
				print(description)
				new_review = Reviews(city=current_city, tour=tour, date_of_review=date_of_review, source=source, reviewer_name=reviewer_name, rating=rating, description=description, guide='')
				if len(Reviews.objects.filter(tour=tour, date_of_review=date_of_review, source=source, reviewer_name=reviewer_name, rating=rating)) == 0:
					new_review.save()
					print("SAVED")
					new_reviews_saved += 1
				else:
					print("DONT SAVE")
					i = int(last_page) + 1
					break
				#######################
			time.sleep(randint(2, 5))
			if i < int(last_page):
				next_page = driver.find_element_by_xpath("//div[(@id='REVIEWS')] //a[contains(@class,'next')] [contains(text(),'Next')]")
				next_page.click()
				i += 1
		print("Tripadvisor Scrape Completed")
	else:
		print("No URL for Tripadvisor")
	
	### Scrape Viator ###
	if viator_urls != None:
		print("Initiating Viator Scrape")
		for viator_url in viator_urls:
			driver.get(viator_url)
			time.sleep(randint(5, 7))
			html = driver.page_source
			time.sleep(randint(2, 4))
			soup = BeautifulSoup(html, "html.parser")

			tour = soup.find("h1").text
			print(tour)
			
			try:
				term = soup.find("div", {"class": "reviews-page-count"}).text
				last_page = term.replace("1 / ","")
			except:
				last_page = "1"
				print("Only One Page")

			i = 0
			while i < int(last_page):
				time.sleep(randint(3, 5))
				try:
					elem = driver.find_elements_by_xpath("//a[contains(@class,'review-more pseudo-link') and not(contains(@class,'d-none'))]")
					for x in range(0,len(elem)):
						elem[x].click()
						time.sleep(randint(1, 3))
					print("'MORE' CLICKED")
				except:
					print("'MORE' NOT CLICKED")
				
				time.sleep(randint(2, 4))
				html = driver.page_source
				soup = BeautifulSoup(html, "html.parser")
				data = None
				try:
					data = soup.find_all("div", {"itemprop": "review"})
				except:
					print("NO REVIEWS")
					break
				for item in data:
					## Store to database ##
					head = item.find("div", {"class": "d-flex flex-row"})
					head_items = head.find_all("span", {"class": "small"})
					d = head_items[1].text.replace(',' + u'\xa0', "")
					temp_date_m = datetime.strptime(d, '%b %Y').strftime("%Y%m")
					comment_div = item.find("div", {"class": "row mt-1"})

					date_of_review = int(temp_date_m + "00")
					source = "Viator"
					reviewer_name = head_items[0].text
					rating = int(item.find("meta", {"itemprop": "ratingValue"}).get("content"))
					description = comment_div.find("p").text
					
					new_review = Reviews(city=current_city, tour=tour, date_of_review=date_of_review, source=source, reviewer_name=reviewer_name, rating=rating, description=description, guide='')
					if len(Reviews.objects.filter(tour=tour, date_of_review=date_of_review, source=source, reviewer_name=reviewer_name, rating=rating)) == 0:
						new_review.save()
						print("SAVED")
						new_reviews_saved += 1
					else:
						print("DONT SAVE")
						i = int(last_page) + 1
						break
					#######################
				time.sleep(randint(2, 4))
				try:
					next_page = driver.find_element_by_xpath("//a[contains(@class,'reviews-load-more')]")
					next_page.click()
					i += 1
				except:
					print("LAST PAGE")
					i = int(last_page) + 1
			print("COMPLETED " + tour)
		print("Viator Scrape Completed")
	else:
		print("No URL for Viator")

	print(f"Saved {new_reviews_saved} new reviews to database for {current_city}")

def scraper(request):
	form = findMyReviewsForm(request.POST or None)
	context = {'title': 'Search for Reviews', 'form': form, }
	template = 'home.html'
	return render(request,template,context)