import acclient
from time import sleep
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

# ACInstrument Form code as provided by the assessmentcenter's API

painInstrumentOID = "6CAD2A91-2182-408F-BAF8-1F1F10F9D6BD"
painInstrument = acclient.acmodel.Form(painInstrumentOID, "Pain Inference")

# Create Client

client = acclient.ACClient(config.get('auth', 'accessIdentifier'), config.get('auth', 'accessToken'), config.get('instance', 'demo'))
client.fromLocalFile = False


# Create new Session in Assessment Center
session = client.startAssessment(painInstrument, "usr-name-test")
sleep(1)


# Begin Q/A 

questionForm = client.getQuestion(session)
while questionForm is not None:
    qform = questionForm.staticText() 
    print(qform)
    choice = input("Please enter your choice: ")
    # Ask for next question by sending the answer choice
    questionForm = client.getQuestion(session, questionForm.answerItems[int(choice)-1])
    # repeats until no new question is sent

# no new Question sent, get score
client.getScoreForSession(session)

