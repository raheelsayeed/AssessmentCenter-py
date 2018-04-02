#!/usr/bin/env python
from datetime import datetime, tzinfo, timezone


class Element(object):

    def __init__(self, oid, order, title=None):
        self.oid = oid
        self.order = order 
        self.title = title
    
    def __repr__(self):
        return f"Element('{self.oid}', '{self.order}','{self.title}')"

    def __str__(self):
        return "OID: %s, title: %s"  % (self.oid, self.title)

class Form(Element):

    def __init__(self, oid, title, questionForms = None):
        super().__init__(oid, 0, title)
        self.questionForms = questionForms


class QuestionItem(Element):

    def __init__(self, oid, order, title):
        super().__init__(oid, 0, title)


    def __str__(self):
        return "Question: %s"  % (self.title)

class AnswerItem(Element):

    def __init__(self, responseOID, order, responseValue, title):
        super().__init__(responseOID, order, title)
        self.responseOID = responseOID
        self.responseValue = responseValue

    def responseBody(self):
        return {'ItemResponseOID' : self.responseOID,
                'Response'        : self.responseValue} 


    
class Session(object):

    def __init__(self, oid, uid, expiration):
        self.oid = oid 
        self.uid = uid 
        self.expiration = expiration
        self.expirationDate = datetime.strptime(expiration, '%m/%d/%Y %I:%M:%S %p').replace(tzinfo=timezone.utc)
        self.form = None

    def __str__(self):
        return "OID: %s UID: %s expiry: %s"  % (self.oid, self.uid, self.expirationDate)


class QuestionForm(Element):

    def __init__(self, oid, order, title, questionItems=None, answerItems=None, responseOID=None, responseValue=None):
        super().__init__(oid, order, title)
        self.questionItems = questionItems
        self.answerItems   = answerItems
        self.responseOID = responseOID
        self.responseValue = responseValue
    
    def questionString(self):
        qstr = ', '.join([q.title for q in self.questionItems if "Container" not in  q.title and "PICT" not in q.title ])
        return qstr

    def staticText(self):
        # print(self.questionString())
        formString = ('\n=============\n[%s]: %s\n' % (self.order, self.title)) 
        formString += '- ' + self.questionString() + '\n'
        for i,a in enumerate(self.answerItems, start=1):
            formString += '['+str(i)+']: ' + a.title + '\n'
        formString += '============='
        return formString

    def answersWithGrammer2(self):
        astr = ""
        secondLastIdx = len(self.answerItems) - 2
        lastIdx = len(self.answerItems) - 1
        for i,a in enumerate(self.answerItems):

            if i == secondLastIdx: #if second Last, add "or"
                 astr += a.title + ',<break time=\"0.4s\"/> or  '
            elif i == lastIdx:
                astr +=  a.title + '. '
            else:
                astr += a.title + ',<break time=\"0.4s\"/>  '
        return astr


    def answersWithGrammer(self):
        astr = ""
        secondLastIdx = len(self.answerItems) - 2
        lastIdx = len(self.answerItems) - 1
        for i,a in enumerate(self.answerItems):

            if i == secondLastIdx: #if second Last, add "or"
                 astr += str(i+1) + ':<break time=\"0.4s\"/> ' + a.title + ', or ... '
            elif i == lastIdx:
                astr += str(i+1) + ': <break time=\"0.4s\"/>' + a.title + '. '
            else:
                astr += str(i+1) + ':<break time=\"0.4s\"/> ' + a.title + ',  <break time=\"0.4s\"/>'
        return astr


    # <break time=\"1s\"/>
    def questionAndAnswers(self):
        return '<p>'+ self.questionString() + '</p><break time=\"0.3s\"/><p>' + self.answersWithGrammer() + '</p>'

    def questionAndAnswers2(self):
        return '<p>'+ self.questionString() + '</p><break time=\"0.3s\"/><p>' + self.answersWithGrammer2() + '</p>'




