from flask import (Flask, request, Response, render_template, make_response, jsonify)
import boto3
import mysql.connector

app = Flask(__name__)


@app.route("/load/s3")
def loadS3():
    NomMatiere = ''
    if 'matiere' in request.args:
        NomMatiere = request.args['matiere']
    s3 = S3()
    resultS3 = s3.load(NomMatiere)
    response = Response(resultS3)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/load/rds")
def loadRDS():
    NomMatiere = ''
    if 'matiere' in request.args:
        NomMatiere = request.args['matiere']
    rds = RDS()
    resultRDS = rds.load(NomMatiere)
    response = Response(resultRDS)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
    
@app.route("/empty")
def emptyRDS():
    rds = RDS()
    resultRDS = rds.empty()
    response = Response("empty")
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
                               aws_access_key_id='AKIAVXK5RXNCUOIGFJ52',
                               aws_secret_access_key='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')

    def load(self, filter):
        if(filter == ''):
            request = "SELECT * FROM s3object s"
        else:
            request = F"SELECT * FROM s3object s WHERE s._1 LIKE '%{filter}%'"
        response = self.s3.select_object_content(
            Bucket='projetfinalaws',
            Key='matiers-esgi.csv',
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
        self.cnx =  mysql.connector.connect(user='projet-final-user', password='adminadmin',
                          host='notes-ges.c4z9zltlpz3y.us-east-2.rds.amazonaws.com',
                          database='notes-ges')
 
    def empty(self):
        cursor = self.cnx.cursor()
        cursor.execute("delete from notes-ges")
        self.cnx.commit()
        return 
        
    def insert(self, data):
        cursor = self.cnx.cursor()
        sql_querry = ("INSERT INTO notes-ges "
                   "(matiere, intervenant, coef, ects, CC1, CC2) "
                   "VALUES (%s, %s, %s, %s, %s, %s)")
        for i in data[0].split("|"):
            if(len(i) == 0):
                continue
            split_data = i.split(",")
            print(split_data)
            insert_data = (split_data[0], split_data[1], split_data[2], split_data[3], split_data[4], split_data[5])
            print(insert_data)
            cursor.execute(sql_querry, insert_data)
        self.cnx.commit()
        return
    
    def load(self, filter):
        
        cursor = self.cnx.cursor()
        if(filter == ''):
            cursor.execute("SELECT * FROM notes-ges")
        else:
            cursor.execute("SELECT * FROM notes-ges WHERE matiere LIKE '%{filter}%'")
        
        data = []
        for (matiere, intervenant, CC1, CC2, coef, ects) in cursor:
            data.append(F"{matiere} - {intervenant} - {coef} - {ects} - {CC1} - {CC2}<br>")
            
        return "Empty" if len(data) == 0 else data


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
