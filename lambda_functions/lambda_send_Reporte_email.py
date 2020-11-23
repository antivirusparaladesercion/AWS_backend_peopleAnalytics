"""
    LAMBDA: send_Reporte_Email
    Esta funcion lambda se encarga de enviar notificacion via email, de un nuevo reporte generado con el respectivo csv adjunto.
    Es invocada cuando en el bucket de s3 de almacenamiento de reportes es añadido un nuevo archivo CSV.
    Los direcciones de correo utilizadas tento remitente como destinatario, deben estar verificadas en aws SES.

"""

#importación de librerias
import os
import json
import boto3
import csv
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


#Info universidades, Remplazar valor de 'email' por los correos destinos asociado a cada universidad.

ies={
      'udea':{'nombre':'Universidad de Antioquia','email':'correouniversidad1@examble.com'},
      'univalle':{'nombre':'Universidad del Valle', 'email':'correouniversidad2@example.com'}
}

# llama a s3 bucket
s3 = boto3.resource('s3')

def lambda_handler(event, context):   
    BUCKET_NAME = event["Records"][0]["s3"]["bucket"]["name"]
    key_bucket_origen = event["Records"][0]["s3"]["object"]["key"] # 'udea/reporte_.csv'
    
    
    
    #extraigo el nombre de la ies que genera e levento
    name_ies= key_bucket_origen.split('/')[0]
    
    
    # descargamos archivo csv a un archivo temporal local
    local_file_name = '/tmp/{}'.format(key_bucket_origen.split('/')[1])
    print(local_file_name)
   
    s3.Bucket(BUCKET_NAME).download_file(key_bucket_origen, local_file_name)
    
    # Remplace sender@example.com con el email origen.
    # este email debe estar verificado en Amazon SES.
    SENDER = "sender@example.com"
    
    # Remplace recipient@example.com con email destino 
    # esta direccion de correo ya debe haber sido verificada en AWS SES.
    RECIPIENT = ies[name_ies]['email']
    print(RECIPIENT)
    # Aqui se puede especificar alguna configuracion adicional, se puede 
    # dejar comentado: 
    # ConfigurationSetName=CONFIGURATION_SET este argumento mas abajo.
    #CONFIGURATION_SET = "ConfigSet"
    
    # Si es necesario, reemplace con la region de AWS que esté usando en Amazon SES.
    AWS_REGION = "us-east-1"
    
    # El asunto para el email.
    SUBJECT = "Reporte Prediccion: {}".format(key_bucket_origen)
    
    # El path completo del archivo que será adjuntado en el email.
    ATTACHMENT = local_file_name
    
    # El body del email con non-HTML.
    BODY_TEXT = "Hello,\r\nPorfavor miere el documento adjunto."
    
    # El HTML body de el email. Modificar src de la imagen que desee como encabezado del correo.
    BODY_HTML = """\
    <html>
    <head></head>
    <body>
    <img src="https://ruav.edu.co/wp-content/uploads/2017/07/logo_Glow.png" alt="ruav logo">
    <h3>Asociado: {}</h3>
    
    <p>El Modelo de prediccion de desercion estudiantil ha generado un nuevo reborte de estudiantes con su probabilidad de deserción.</p>
    <h4>Descarguelo, analicelo y tome acciones !</h4>
    
    </html>
    """.format(ies[name_ies]['nombre'])
    
    # Encoding para el email.
    CHARSET = "utf-8"
    
    # Creaamos un nuevo recurso SES y especificamos la region.
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # Creamos un multipart/mixed container padre.
    msg = MIMEMultipart('mixed')
    
    # Añadimos la info para el mensaje.
    msg['Subject'] = SUBJECT 
    msg['From'] = SENDER 
    msg['To'] = RECIPIENT
    
    # CreaAMOS un multipart/alternative container hijo.
    msg_body = MIMEMultipart('alternative')
    
    # Encode de el contenido text y HTML . es necesario si enviamos caracteres diferentes a ASCII
    
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    
    # Añadimos el texto y el hml al container hijo.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    
    # Definimos el archivo adjunto a enviar.
    att = MIMEApplication(open(ATTACHMENT, 'rb').read())
   
    # añadimos un header paraque el cleinte lea el adjunto,
    # pasamos el nombre del archivo.
    att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))
    
    # adjuntar el multipart/alternative container hijo multipart/mixed
    # container padre.
    msg.attach(msg_body)
    
    # añadimos el adjunto al container padre.
    msg.attach(att)
    #print(msg)
    try:
        #Aqui va el contenido del mansaje.
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=[
                RECIPIENT
            ],
            RawMessage={
                'Data':msg.as_string(),
            },
            #ConfigurationSetName=CONFIGURATION_SET
        )
    # Mostramos error si algo sale mal.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        
    return {
             'statusCode': 200,
             'body': json.dumps('Susses!')
            }