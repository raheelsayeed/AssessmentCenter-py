import base64, acmodel, json
import  urllib.request, urllib.parse

class ACClient(object):


    def writeJsonToFile(self, data, filename):

        with open(filename, 'w') as output:
            dump = json.dumps(data, sort_keys=True, indent=4)
            output.write(dump)
            output.close()
            
    def __init__(self, accessID, accessToken, baseURLStr):
        self.accessID = accessID
        self.accessToken = accessToken
        self.baseURLStr = baseURLStr
        self.request = urllib.request
        self.questionNumberSequence = 0
        self.fromLocalFile = False 

    
    def performRequest(self,  endpoint, postData=None):

        string = '%s:%s' % (self.accessID, self.accessToken)
        encoded = string.encode() # utf_8
        base64string = base64.b64encode(encoded)
        authstring = 'Basic %s' % base64string.decode() # utf_8
        url = urllib.parse.urljoin(self.baseURLStr, endpoint)
        print(url)
        req = self.request.Request(url)
        req.add_header("Authorization", authstring)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.get_method = lambda: 'POST'

        # print(postData)
        data = None 
        if postData is not None:
            data = urllib.parse.urlencode(postData).encode() 

        result = urllib.request.urlopen(req, data).read()

        jsondict = json.loads(result.decode())
        if jsondict is not None:
           return jsondict
        else:
            return None


    def allForms(self):

        if not self.fromLocalFile:
            jsonDict = self.performRequest('Forms/.json')
            # self.writeJsonToFile(jsonDict, 'sample_results/allforms.txt')
        else:
            with open('sample_results/allforms.txt') as json_data:
                jsonDict = json.load(json_data)
        forms = jsonDict['Form']
        formsarray = [] 
        for form in forms:
            formObj = acmodel.Form(form['OID'], form['Name'])
            formsarray.append(formObj)
        
        return formsarray



    def getCompleteForm(self, form=acmodel.Form):

        endpoint = "Forms/" + form.oid + ".json"
        filename = "sample_results/form_paininference.txt"
        # jsonDict = self.performRequest(endpoint)
        # self.writeJsonToFile(jsonDict, filename)
        with open(filename) as json_data:
            jsonDict = json.load(json_data)

        questionForms = []
        for jsonQItem in jsonDict['Items']:
            qf = self.parseQuestionForm(jsonQItem)
            questionForms.append(qf)

        form.questionForms = questionForms
        return form 

        


    def parseQuestionForm(self,jsonDict):
        
        qForm = acmodel.QuestionForm(jsonDict['FormItemOID'],jsonDict['Order'],jsonDict['ID'] )
        questions = []
        questionsArr = jsonDict['Elements']
        for e in questionsArr:
            qi = acmodel.QuestionItem(e['ElementOID'], e['ElementOrder'],e['Description'])
            questions.append(qi)        
        qForm.questionItems = questions

        answers   = [] 
        answersArr = questionsArr[-1]['Map']
        for a in answersArr:
            ans = acmodel.AnswerItem(a['ItemResponseOID'],a['Position'],a['Value'],a['Description'])
            answers.append(ans)
        qForm.answerItems = answers
        return qForm


    def startAssessment(self, form=acmodel.Form, userDefinedString=None, expirationDate=None):

        endpoint = 'Assessments/' + form.oid + '.json'
        filename = "sample_results/start_assessments.txt"

        headers = None
        if userDefinedString is not None:
            if headers is None:
                headers = {}
            headers['UID'] = userDefinedString
        
        if expirationDate is not None:
            if headers is None:
                headers = {}
            headers['Expiration'] = 'Date'

        jsonDict = self.performRequest(endpoint,headers)
        # self.writeJsonToFile(jsonDict, filename)
        
        # with open(filename) as json_data:
        #     jsonDict = json.load(json_data)

        sessionItem = acmodel.Session(jsonDict['OID'], jsonDict['UID'], jsonDict['Expiration'])
        return sessionItem


        
    def getQuestion(self, session=acmodel.Session, responseItem=None):

        data = None
        questionForm = None 
        endpoint = 'Participants/' + session.oid + '.json'        
        filename = "sample_results/first_questionform_" + str(self.questionNumberSequence) + ".txt"
        self.questionNumberSequence += 1
        data = None 
        if responseItem is not None and isinstance(responseItem, acmodel.AnswerItem):
            data = responseItem.responseBody()
        
        jsonDict = self.performRequest(endpoint, data)

        if 'Error' in jsonDict:
            # some error occured. send None
            return None 


        dateFinishedKey = 'DateFinished'
        print(jsonDict)







        if dateFinishedKey in jsonDict and len(jsonDict['DateFinished']) > 0:
            filename = "sample_results/endedQuestionnare.txt"
        else:
            questionForm = self.parseQuestionForm(jsonDict['Items'][0])
            # print(questionForm.staticText())

        # self.writeJsonToFile(jsonDict, filename)
        return questionForm




    def getScoreForSession(self, session=acmodel.Session):
        
        endpoint = 'Results/' + session.oid + '.json'
        filename = 'sample_results/result.txt' 
        jsonDict = self.performRequest(endpoint)
        # self.writeJsonToFile(jsonDict, filename)
        # with open(filename) as json_data:
            # jsonDict = json.load(json_data)

        theta = jsonDict['Theta']
        user  = jsonDict['UID']
        instrument = jsonDict['Name']
        stdError = jsonDict['StdError']

        
        tscore = round((float(theta) * 10) + 50.0)
        standardError = round(float(stdError) * 10)
        # print()
        result = { "Success":"Done",
                    "Instrument" : instrument,
                    "UserID" : user,
                    "Theta": str(theta),
                    "StdError":str(stdError),
                    "T-Score": str(tscore),
                    "StandardError" : str(standardError)
        }
        print(result)
        return result 







        






    

