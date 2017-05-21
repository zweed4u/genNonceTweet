#!/usr/bin/python
# See here for implementation https://twitter.com/iPhone6_1
import os, paramiko, tweepy, datetime, ConfigParser

rootDirectory = os.getcwd()
c = ConfigParser.ConfigParser()
configFilePath = os.path.join(rootDirectory, 'config.cfg')
c.read(configFilePath)

class Config:
    deviceIdentifier = c.get('device','deviceIdentifier')
    deviceECID = c.get('device','ecid')                   #ensure this a hex number
    deviceBoardConfig = c.get('device','boardConfig')
    selfPasswordSSH = c.get('ssh','localPassword')
    blobsPath = c.get('shsh2_path','pathToBlobs')
    binariesNeeded = c.get('tools','binNeeded')
    consumerKey = c.get('twitter','consumerKey')
    consumerSecret = c.get('twitter','consumerSecret')
    accessToken = c.get('twitter','accessToken')
    accessTokenSecret = c.get('twitter','accessTokenSecret')

class SSH:
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	def __init__(self, address, port, user, passwd):
		self.address = address
		self.port = port
		self.user = user
		self.passwd = passwd

	def connect(self):
		SSH.ssh.connect(self.address, self.port, self.user, self.passwd)

class Twitter:
	'''Twitter integration'''
	def __init__(self, apiKey, apiSecret, token, tokenSecret):
		self.apiKey = apiKey
		self.apiSecret = apiSecret
		self.token = token
		self.tokenSecret = tokenSecret

	def authenticate(self):
		global api
		auth = tweepy.auth.OAuthHandler(self.apiKey, self.apiSecret)
		auth.set_access_token(self.token, self.tokenSecret)
		api = tweepy.API(auth)

	def tweet(self, message):
		api.update_status(status=message)

def UTCtoEST():
    current = datetime.now()
    return str(current) + ' EST'

if __name__ == '__main__':
	user_config = Config() #config instance

	my_twitter = Twitter(user_config.consumerKey, user_config.consumerSecret, user_config.accessToken, user_config.accessTokenSecret) #twitter auth instance
	my_twitter.authenticate() #log into twitter
	#my_twitter.tweet("Hello World") #example tweet
	local_ssh = SSH('127.0.0.1', 22, os.getlogin(), user_config.selfPasswordSSH) #ssh instance
	local_ssh.connect() #local connect
