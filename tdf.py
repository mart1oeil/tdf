from bottle import Bottle, run
from bottle import template

from bottle import request,  static_file
import wikipedia
import requests
from bs4 import BeautifulSoup
wikipedia.set_lang("fr")
app = Bottle()



def scrappingWP():
	url = 'https://fr.wikipedia.org/wiki/Palmar%C3%A8s_du_Tour_de_France'
	# Scrape the HTML at the url
	r = requests.get(url)
	

	# Turn the HTML into a Beautiful Soup object
	soup = BeautifulSoup(r.text, 'lxml')
	# Create an object of the first object that is class=dataframe
	table = soup.find(class_='wikitable sortable')

	return table


@app.route("/credits")
def display_credits():
	return template('static/templated-retrospect/credits.tpl')
	


@app.route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')



@app.get('/')
def tdf():
	htm='''
<form value="form" action="/" method="post">
  <div id='container'>
  <label for="year">Renseignez l'année de votre naissance</label>
  <p><select  name="year" id="year">'''

	table=scrappingWP()
	for single in table.find_all('tr')[1:]:
		col = single.find_all('td')
		column_1 = col[0]
		col1=column_1.text.split(" ")
		anneecol=col1[0]
		yellow=col[1].text
		mountain=col[6]
		green=col[7]
		htmopt='<option value="{0}">{1}</option>'.format(anneecol,anneecol)
		htm=htm+htmopt
	htm=htm+'''</select></div>

  <input type="submit" value="Envoyer" class="button big special">

</form>
<p>Votre année de naissance n'est pas dans la liste&nbsp;? C'est qu'il n'y a pas eu de Tour de France cette année là. Désolé.</p>
    '''

	return template('static/templated-retrospect/index.tpl', title="Le Tour de votre naissance", body=htm)


@app.post('/')
def do_tdf():
	year = request.forms.get('year')
	htmYellow=''
	htmMountain=''
	htmGreen=''
	table = scrappingWP()

	for single in table.find_all('tr')[1:]:
		
		col = single.find_all('td')
		column_1 = col[0]
		col1=column_1.text.split(" ")
		anneecol=col1[0]
		yellow=col[1].text
		mountain=col[6].text
		green=col[7].text

		if year==anneecol:
			htm=''
			
			if 'non attribu' in yellow:
				htmYellow=htmYellow+"<h1>En {0} </h1><p>Le maillot jaune n'a pas été attribué cette année là.</p><p>Les titres de Lance Armstrong gagné entre 1999 et 2005 ont été révoqués par l'UCI le 22 octobre 2012 pour dopage.</p>".format(year)
			else:
				try:
					vainqueurWP = wikipedia.page(yellow)
					vainqueur=vainqueurWP.title
					sentence=wikipedia.summary(vainqueur, sentences=2)
				except wikipedia.exceptions.DisambiguationError:
					vainqueurWP = wikipedia.page(yellow+' cyclisme')
					vainqueur=vainqueurWP.title
					sentence=wikipedia.summary(vainqueur, sentences=2)
				except:
					sentence="Pas de fiche WP"

				htmYellow=htmYellow+"<h1>En {0} </h1><h2>le vainqueur du tour était {1}.</h2><p>{2}</p>".format(year,yellow,sentence)

			if 'non attribu' in mountain or mountain=='':
				htmMountain=htmMountain+"<p>Le grand prix de la Montagne n'a pas été attribué cette année là.</p>".format(year)
			else:
				try:
					mountainWP = wikipedia.page(mountain)
					montagne=mountainWP.title
					sentence=wikipedia.summary(montagne, sentences=2)
				except wikipedia.exceptions.DisambiguationError:
					mountainWP = wikipedia.page(mountain+' cyclisme')
					montagne=mountainWP.title
					sentence=wikipedia.summary(montagne, sentences=2)
				except:
					sentence="Pas de fiche WP"
				htmMountain=htmMountain+"<h2>Le meilleur grimpeur était {0}.</h2><p>{1}</p>".format(mountain,sentence)

			if 'non attribu' in green or green=='':
				htmGreen=htmGreen+"<p>Le prix du meilleur sprinter n'a pas été attribué cette année là.</p>"
			else:
				try:
					greenWP = wikipedia.page(green)
					vert=greenWP.title
					sentence=wikipedia.summary(vert, sentences=2)
				except wikipedia.exceptions.DisambiguationError:
					greenWP = wikipedia.page(green+' cyclisme')
					vert=greenWP.title
					sentence=wikipedia.summary(vert, sentences=2)
				except:
					sentence="Pas de fiche WP"

				htmGreen=htmGreen+"<h2>Le meilleur sprinter était {0}.</h2><p>{1}</p>".format(green,sentence)


			title="Le Tour de votre naissance: {0}".format(year)
			return template('static/templated-retrospect/result.tpl',title=title,bodyYellow=htmYellow,bodyMountain=htmMountain, bodyGreen=htmGreen)


	return "Vous êtes né en ", year


run(app, host='localhost', port=8080)
