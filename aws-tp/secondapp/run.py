from flask import (Flask, request, Response, render_template, make_response, jsonify)
import boto3
import mysql.connector

app = Flask(__name__)


@app.route("/load/s3")
def loadS3():
    matiere = ''
    if 'matiere' in request.args:
        matiere = request.args['matiere']
    s3 = S3()
    result = s3.load(matiere)
    response = Response(result)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/load/rds")
def loadRDS():
    matiere = ''
    if 'matiere' in request.args:
        matiere = request.args['matiere']
    rds = RDS()
    result = rds.load(matiere)
    response = Response(result)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
    
@app.route("/clear")
def clearRDS():
    rds = RDS()
    result = rds.clear()
    response = Response("Clear")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
    
@app.route("/transfert/rds")
def transfertToRDS():
    s3 = S3()
    result = s3.load('')
    
    rds = RDS()
    rds.insert(result)
    response = Response("Success")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response  


class S3:
    def __init__(self):
        self.s3 = boto3.client('s3',
                               aws_access_key_id='AKIAQZRPYR55AKQNZNWI',
                               aws_secret_access_key='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')

    def load(self, filter):
        if(filter == ''):
            request = "SELECT * FROM s3object s"
        else:
            request = F"SELECT * FROM s3object s WHERE s._1 LIKE '%{filter}%'"
        response = self.s3.select_object_content(
            Bucket='projet-final',
            Key='notes-ges.csv',
            ExpressionType='SQL',
            Expression=request,
            InputSerialization={
                    'CSV': {
                        'RecordDelimiter': '\n',
                        'FieldDelimiter': ',',
                    }
            },
            OutputSerialization={
                'CSV': {
                    'RecordDelimiter': '|',
                    'FieldDelimiter': ',',
                }
            }
        )

        records = []

        for event in response['Payload']:
            if 'Records' in event:
                records.append(event['Records']['Payload'].decode('utf-8'))
            elif 'Stats' in event:
                stats = event['Stats']['Details']
        return records
        
class RDS:

    def __init__(self):
        self.cnx =  mysql.connector.connect(user='admin', password='adminadmin',
                          host='database-projet-final.cr3gygd34o8b.us-east-1.rds.amazonaws.com',
                          database='notes')
 
    def clear(self):
        cursor = self.cnx.cursor()
        cursor.execute("delete from notes")
        self.cnx.commit()
        return 
        
    def insert(self, data):
        cursor = self.cnx.cursor()
        add_query = ("INSERT INTO notes "
                   "(matiere, intervenant, coef, ects, CC1, CC2) "
                   "VALUES (%s, %s, %s, %s, %s, %s)")
        for i in data[0].split("|"):
            if(len(i) == 0):
                continue
            split_data = i.split(",")
            print(split_data)
            insert_data = (split_data[0], split_data[1], split_data[2], split_data[3], split_data[4], split_data[5])
            print(insert_data)
            cursor.execute(add_query, insert_data)
        self.cnx.commit()
        return
    
    def load(self, filter):
        
        cursor = self.cnx.cursor()
        if(filter == ''):
            cursor.execute("SELECT * FROM notes")
        else:
            cursor.execute("SELECT * FROM notes WHERE matiere LIKE '%{filter}%'")
        
        data = []
        for (matiere, intervenant, CC1, CC2, coef, ects) in cursor:
            data.append(F"{matiere} - {intervenant} - {coef} - {ects} - {CC1} - {CC2}<br>")
            
        return "Empty" if len(data) == 0 else data


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
