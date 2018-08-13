# -*- encoding: utf-8 -*-

'''
this module is used to make a web site
to give information about the Tour de France
of your birth year
'''
import sys
import requests
from bs4 import BeautifulSoup
import wikipedia
from bottle import Bottle, run
from bottle import template
from bottle import request, static_file

wikipedia.set_lang("fr")
APP = Bottle()

def scrapping_wp():
	'''
	This function is scrapping the wikipedia page
	of le Tour de France
	where the palmares is.
	'''
	url = 'https://fr.wikipedia.org/wiki/Palmar%C3%A8s_du_Tour_de_France'
	# Scrape the HTML at the url
	req = requests.get(url)


	# Turn the HTML into a Beautiful Soup object
	soup = BeautifulSoup(req.text, 'lxml')
	# Create an object of the first object that is class=dataframe
	table = soup.find(class_='wikitable sortable')

	return table

@APP.route("/credits")
def display_credits():
	'''
	display the credits page with the good template
	'''
	return template('static/templated-retrospect/credits.tpl')

@APP.route('/static/:path#.+#', name='static')
def static(path):
	'''
	return the static file
	'''
	return static_file(path, root='static')


@APP.get('/')
def tdf():
	'''
	principal app to launch tdf
	'''
	htm = '''
	<form value="form" action="/" method="post">
	<div id='container'>
	<label for="year">Renseignez l'année de votre naissance</label>
	<p><select  name="year" id="year">'''
	table = scrapping_wp()
	for single in table.find_all('tr')[1:]:
		col = single.find_all('td')
		column_1 = col[0]
		col1 = column_1.text.split(" ")
		anneecol = col1[0]
		htmopt = '<option value="{0}">{1}</option>'.format(anneecol, anneecol)
		htm = htm + htmopt
	htm = htm + ('''</select></div>
	<input type="submit" value="Envoyer"''' +
              ''' class="button big special">
</form>
<p>Votre année de naissance n'est pas dans la liste&nbsp;?''' +
              '''C'est qu'il n'y a pas eu de Tour de France cette année là. Désolé.</p>''')

	return template('static/templated-retrospect/index.tpl',
                 title="Le Tour de votre naissance", body=htm)


@APP.post('/')
def do_tdf():
	'''
	create the tdf app
	'''
	year = request.forms.get('year')
	htm_yellow = ''
	htm_mountain = ''
	htm_green = ''
	table = scrapping_wp()

	for single in table.find_all('tr')[1:]:

		col = single.find_all('td')
		col1 = col[0]
		col1 = col1.text.split(" ")
		anneecol = col1[0]
		yellow = col[1].text
		mountain = col[8].text
		green = col[9].text

		if year == anneecol:

			if 'non attribu' in yellow:
				htm_yellow = (htm_yellow +
				              "<h1>En {0} </h1><p>".format(year) +
				              "Le maillot jaune n'a pas été attribué cette année là.</p>" +
				              "<p>Les titres de Lance Armstrong gagné entre 1999 et 2005" +
				              " ont été révoqués par l'UCI le 22 octobre 2012 pour dopage.</p>")
			else:
				sentence = wiki_request(yellow)

				htm_yellow = (htm_yellow +
				              "<h1>En {0} </h1><h2>le vainqueur du tour était {1}.</h2><p>{2}</p>".
							           format(year, yellow, sentence))

			if 'non attribu' in mountain or mountain == '':
				htm_mountain = (htm_mountain +
	 			               "<p>Le grand prix de la Montagne n'a pas été attribué cette année là.</p>")
			else:
				sentence = wiki_request(mountain)
				htm_mountain = (htm_mountain +
 				               "<h2>Le meilleur grimpeur était {0}.</h2><p>{1}</p>".
 				               format(mountain, sentence))

			if 'non attribu' in green or green == '':
				htm_green = (htm_green +
                 "<p>Le prix du meilleur sprinter n'a pas été" +
                 " attribué cette année là.</p>")
			else:
				sentence = wiki_request(green)

				htm_green = (htm_green +
				             "<h2>Le meilleur sprinter était {0}.</h2><p>{1}</p>".
				         	   format(green, sentence))

			title = "Le Tour de votre naissance: {0}".format(year)
			return template('static/templated-retrospect/result.tpl',
			                title=title, bodyYellow=htm_yellow,
			                bodyMountain=htm_mountain,
			                bodyGreen=htm_green)


	return "Vous êtes né en ", year

def wiki_request(name):
	'''
	This method will return the 2 first sentences of the wikipedia page
	of the given name
	'''
	try:
		name_wpp = wikipedia.page(name)
		name_wpp = name_wpp.title
		sentence = wikipedia.summary(name_wpp, sentences=2)
	except wikipedia.exceptions.DisambiguationError:
		name_wpp = wikipedia.page(name + ' cyclisme')
		name_wpp = name_wpp.title
		sentence = wikipedia.summary(name_wpp, sentences=2)
	except wikipedia.exceptions.PageError:
		sentence = "Pas de fiche WP"
	return sentence



run(APP, host='0.0.0.0', port=sys.argv[1])
#run(APP, host='0.0.0.0')
