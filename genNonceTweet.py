#!/usr/bin/python
# Tested with tsschecker v232, img4tool v92

# See here for implementation https://twitter.com/iPhone6_1
# only for latest public version - support manual specification feature later as signing window needs to be open anyways
# symlinks in /usr/bin pointing to /usr/local/bin binaries - add support for symlinking if needed and chmoding - will requre interactive for sudo pass
## sudo ln -s /usr/local/bin/tsschecker /usr/bin/tsschecker && sudo chmod +x /usr/bin/tsschecker
## sudo ln -s /usr/local/bin/img4tool /usr/bin/img4tool && sudo chmod +x /usr/bin/img4tool
# add threading to monitor dms - for admin user sleep timer adjustment

import os, sys, time, paramiko, random, tweepy, datetime, ConfigParser
from colorCodes import *

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
		self.ssh.connect(self.address, self.port, self.user, self.passwd)

	def execute(self, command):
		return self.ssh.exec_command(command)

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
    current = datetime.datetime.now()
    return str(current) + ' EST'

if __name__ == '__main__': #exception handling needed
	print UTCtoEST(),'::','Loading configuration...'
	user_config = Config() #config instance
	my_twitter = Twitter(user_config.consumerKey, user_config.consumerSecret, user_config.accessToken, user_config.accessTokenSecret) #twitter auth instance
	print UTCtoEST(),'::','Logging into twitter...'
	my_twitter.authenticate() #log into twitter
	print UTCtoEST(),'::','Connecting to localhost...'
	local_ssh = SSH('127.0.0.1', 22, os.getlogin(), user_config.selfPasswordSSH) #ssh instance
	local_ssh.connect() #local connect
	while 1:
		print
		print UTCtoEST(),'::',RED+'Moving any existing blobs in '+rootDirectory+' to Blobs folder...'+COLOR_END
		local_ssh.execute("cd "+rootDirectory+'; mv *.shsh2 Blobs/')
		print UTCtoEST(),'::','Executing tsschecker, one moment please...'
		tsscheck_command = "tsschecker -d "+user_config.deviceIdentifier+" -l --boardconfig "+user_config.deviceBoardConfig+" -e "+user_config.deviceECID+" -s ."
		tsschecker_output = local_ssh.execute("cd "+rootDirectory+'; '+tsscheck_command)[1].read()
		assert 'Saved shsh blobs!' in tsschecker_output and 'success' in tsschecker_output and 'IS signed' in tsschecker_output, "Assertion Error: Blob not saved || Not signed"
		version = tsschecker_output.split("iOS ")[1].split('\n')[0]
		#assert ls of shsh2s returns entry		
		print UTCtoEST(),':: Execution finished! Parsing for generator!'
		#parsing
		full_blob = local_ssh.execute("cd "+rootDirectory+'; cat *.shsh2')[1].read()
		generator = full_blob.split("<key>generator</key>")[1].split("<string>")[1].split("</string>")[0]
		img4tool_command = "img4tool -s *.shsh2" #assuming removal of blob works before each pass - only one blob, no need for file name
		img4tool_output = local_ssh.execute("cd "+rootDirectory+'; '+img4tool_command)[1].read()
		nonce = img4tool_output.split("BNCH: ")[2].split('\n')[0]
		colorText = random.choice(colorCodes.values())
		print UTCtoEST(),'::',colorText+'Tweeting '+user_config.deviceIdentifier+' :: ['+version+'] :: '+generator+' -> '+nonce,COLOR_END
		my_twitter.tweet(UTCtoEST()+' :: '+user_config.deviceIdentifier+' :: ['+version+'] ::\n'+generator+' -> '+nonce)
		print UTCtoEST(),":: Tweet posted! Sleeping..."
		for i in range(300):
			sys.stdout.write("\r" +UTCtoEST()+ ' :: Sleeping for '+str(300-i)+' seconds before next generation...')
			sys.stdout.flush()
			time.sleep(1)
		print
		