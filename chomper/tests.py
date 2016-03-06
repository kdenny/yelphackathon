from django.test import TestCase
from django.test import Client



class YelpTestCase(TestCase):
	def testYelpPost(self):
		resp = self.client.post('/chomper/yelp/', {'location': 'yelp-san-francisco'})
		self.assertEqual(resp.status_code, 200)

	def testYelpContent(self):
		resp = self.client.post('/chomper/yelp/', {'location': 'yelp-san-francisco'})
		self.assertNotEqual(resp.content, '')

	def testYelpContentNotNone(self):
		resp = self.client.post('/chomper/yelp/', {'location': 'yelp-san-francisco'})
		self.assertIsNotNone(resp.content)

	def testGetYelpPage(self):
		resp = self.client.get('/chomper/yelp')
		self.assertEqual(resp.status_code, 301)

class ScraperTestCase(TestCase):
	def testScraperPage(self):
		resp = self.client.get('/chomper/steamDiscountedGames/')
		self.assertEqual(resp.status_code, 200)

	def testScraperContent(self):
		resp = self.client.get('/chomper/steamDiscountedGames/')
		self.assertNotEqual(resp.content, '')

class NewYorkTimesTestCase(TestCase):
	def testPopularArticles(self):
		resp = self.client.get('/chomper/nytimespop/')
		self.assertEqual(resp.status_code, 200)

	def testPopularArticlesContent(self):
		resp = self.client.get('/chomper/nytimespop/')
		self.assertNotEqual(resp.content, '')

	def testTopArticles(self):
		resp = self.client.get('/chomper/nytimestop/')
		self.assertEqual(resp.status_code, 200)

	def testTopArticlesContent(self):
		resp = self.client.get('/chomper/nytimestop/')
		self.assertNotEqual(resp.content, '')

	def testNewYorkTimesArticles(self):
		resp = self.client.get('/chomper/nytimesarticles/')
		self.assertEqual(resp.status_code, 200)

	def testNewYorkTimesArticlesContent(self):
		resp = self.client.get('/chomper/nytimesarticles/')
		self.assertNotEqual(resp.content, '')
