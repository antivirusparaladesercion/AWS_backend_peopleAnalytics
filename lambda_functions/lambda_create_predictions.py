"""
    LAMBDA: create_predictions
    Esta funcion lambda se encarga de invocar el endpoint del modelo para generar las predicciones, despues de esto envia dichas predicciones a un bucket S3 habilitado para almacenarlas.
    Esta funcioón es activada cuando en el bucket de carga de archivos llega un nuevo csv de datos.
    

"""

#importacion de librerias
import os
import io
import boto3
import json
import boto3
import csv
import numpy as np

# Crear una variable de entorno para el nombre del ENDPOINT en la configuracion de la lambda
ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
runtime = boto3.client('runtime.sagemaker')

# call s3 bucket
s3 = boto3.resource('s3')
#BUCKET_NAME = 'reportesies'
bucket2 = s3.Bucket('reportesies')  # Enter your bucket name, e.g 'Data'

# key path, ejmplo.'miuniversidad/miarchivo.csv'


#funcion para convertir arreglo en csv
def np2csv(arr):
    """
        funcion que convierte un array de datos a un csv.
        
        :params  arry: arrego de datos estudiantes
        :return  valores del csv 
    """
    csv = io.BytesIO()
    np.savetxt(csv, arr, delimiter=',', fmt='%s')
    return csv.getvalue().decode().rstrip()


# lambda function
def lambda_handler(event, context):
    
    BUCKET_NAME = event["Records"][0]["s3"]["bucket"]["name"]
    key_bucket_origen = event["Records"][0]["s3"]["object"]["key"]
    
    # descargamos archivo csv a un archivo temporal local
    local_file_name = '/tmp/temporal.csv'  #
    s3.Bucket(BUCKET_NAME).download_file(key_bucket_origen, local_file_name)
   
    with open('/tmp/temporal.csv', 'r') as infile:
        reader = list(csv.reader(infile))

    data = np.array(reader)

    id_estudiantes= list(data[:,0])
    data_to_model = data [:,1:]

    payload = np2csv(data_to_model) #convierto data que va al modelo en csv
    print(payload)

    
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       ContentType='text/csv',
                                       Body=payload)
    print('respuesta', response)

    #se decodifica el la respuesta del modelo con las predicciones
    result = response['Body'].read().decode()
   
    #se redondean los resultados a enteros, laos resultados llegan en formato sting
    re = [np.round(float(resp)) for resp in result.split(',')]
    print('resultado', re)

    predicted_label = ['En riesgo' if pred == 1 else 'No riesgo' for pred in re] #convierto las salidas a frase para visionarlo mejor en desarrollo , el valor real es el la probabilidad de deserc.
    
    #arreglo de id de estudiantes y predicciones
    reporte = (np.array([id_estudiantes,predicted_label])).T
    print("reporte array",reporte)
    
    reporte = list(reporte) # lista de id_estudiantes con su respectiva prediccion.
    print('reporte final', reporte)
    
    with open('/tmp/temporal_reporte.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Id_estudiantes','Prediccion'])
        for line in reporte:  # reverse order
            writer.writerow(line)

    # secarga el csv con el reporte temporal desde la carpeta tmp a el s3 key destino
    key_aux=key_bucket_origen.split('/')
    key_bucket_destino= '{}/reporte_{}'.format(key_aux[0],key_aux[1])
    bucket2.upload_file('/tmp/temporal_reporte.csv', key_bucket_destino)
    
    return {
        'message': 'success!!'
    }
