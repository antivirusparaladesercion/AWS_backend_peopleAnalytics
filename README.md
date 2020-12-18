# BACKEND AWS - PEOPLEANALITYCS

_Documentación de los procesos mas relevantes y del codigo generado en la parte del backend en AWS para el proyecto de desercion universitaria
usando tecnicas de peopleAnalytics_

## Comenzemos 🚀

_Estas instrucciones le permitirán implementar la arquitectura de la solución correspondiente a  AWS._

![image](https://drive.google.com/uc?export=view&id=1DXaW577NdrAVi47vM9EcWlQoz5Zbd8NZ)

### Pre-requisitos 📋

_Contar con una cuenta de AWS y dominio en el uso de servicios como Amazon S3, Sagemaker, Lambda, API Gateway, SES. A parte de conocimientos basicos en 
Python y ML_

## Entrenamiento del Modelo en Sagemaker 🧮 

_Para entrenar el modelo en en sagemaker se crea una instancia de block de nota en la cual vamos a crear el notebook donde se escribira el script para
crear e implementar modelo a partir de los datos de estudiantes de una universidad. Ademas de cargar en dicha instancias los csv correspondientes._

_El script se puede observar en el notebook [mdelo_prediccion_desercion_XGBoost.ipynb](https://github.com/antivirusparaladesercion/AWS_backend_peopleAnalytics/blob/master/jupyter_notebooks/mdelo_prediccion_desercion_XGBoost.ipynb)_

```
#En este punto es necesario establecer la politicas de permiso para el rol en sagemaker de tal 
#manera que tenga full acceso a Amazon S3:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*"
        }
    ]
}
```

_⚠️Es recomendable que despues de hacer pruebas en procesos de entrenamiento de modelos eliminar los recursos o servicios creados, con el fin de no generar costos innecesarios._

_Al ejecutar el script se crea un **ENDPOINT** del modelo, el cual es almacenado en un busket de S3. Este endpoint es utilizado en las funciones LAMBDAS
A la hora de invocar el modelo generado con el finde obtener las predicciones._

## FUNCIONES LAMBDAS CREADAS
_La logica de los procesos como generar predicciones, enviar notificacion y predicciones viea correo electronico, obtener los links de descarga de los archivos .csv
de los reportes. Son implementados por medio de funciones lambdas, las cuales se activaran despues de un evento especifico._

_Para la creación de una funcion lambda, debe usar el servicio AWS Lambda en la opcion **Crear función.** Allí debe darle un mobre  y elegir el lenguaje de programacion
de la funcion con su respectiva version (en nuestro caso usamos Python 3.7)._

_Cada funcion landa debe tener asociada diferentes politicas de permisos segun las funcionalidades que requiera._

### Funcion Lambda: [create_predictions()](https://github.com/antivirusparaladesercion/AWS_backend_peopleAnalytics/blob/master/lambda_functions/lambda_create_predictions.py) ⚙️

_Esta función busca que cuando un archivo .csv con la data de los estudiantes para ser analizad sea cargado a un bucket de S3. Este sera procesado por la lambda para que se puedan hacer predicciones.
Posterior a esto se crea un reporte en otro archivo .csv con dichas predicciones y que de igualmanera es almacenado en otro bucket de S3 destinado para almacenar reportes generados._

_La funcion en mención invoca entonces al modelo entrenado en sagemaker a través de su endpoint. Nombre del Endpoint que debe ser almacenado en una la variable de entorno de la lambda a la hora de crearla._
```
ENDPOINT_NAME : nombredelendpoint-2020-11-18-20-43-01-038
```
_Esta función es activada cada que se carga un nuevo archivo .csv en el bucket de S3 correspondiente. Para que esto ocurra a la hora de crear la función
se le asigna como evento disparador un "**Put en el bucket de S3 de carga de datos:**"_

![image](https://drive.google.com/uc?export=view&id=1QK9wJ786Yen0I5ypKoaO55jAkTQIUWnV)

_De igualmanera se debe configurar una capa que contenga las librerias de numpy y pandas para que estas puedadan ser importadas dentro de la funcion lambda._
_Las politicas de permiso del rol de la función son los siguiientes:_
![image](https://drive.google.com/uc?export=view&id=1EZc2kEKdH5irPcjB4KwVCsuTIIZFDTFM)

### Función Lambda: [send_Reporte_email()](https://github.com/antivirusparaladesercion/AWS_backend_peopleAnalytics/blob/master/lambda_functions/lambda_send_Reporte_email.py)🔔📩
_Esta función se activa cuando un nuevo arvhivo .csv de predicciones es cargado al bucket S3 de reportes. Tiene como objetivo, generar
una notificacion a una universidad especifica via email de que un nuevo reporte ha sido creado y de adjuntar el archivo .csv del reporte correspondiente._
```
Por ejemplo: 

Si la universidad del valle Carga un nuevo archivo .csv con informacion de los estudiantes,para
obtener las predicciones del riesgo de desercion. Este archivo llega al bucket S3 de "Cargadedatos"
la lambda que genera el reporte es activada y posteriormente almacena este reporte en el bucket "Reportes/universidaddelvalle";
Es en este instante que se activa la lambda "send_Reporte_email()" la cual extrae del "key" del archivo generador del evento
el nombre da la universidad dueña del reporte. de esta manera la lambda sabrá el destino de dicho reporte, y procedera con el envio.
```
_De igualmanera se le asigna como evento disparador un "**Put en el bucket S3 de reportes:**", de tal manera que sepa cuando ejecutarse._

_La politica de permisos es igual que al de la funcion lambda creada previamente._
![image](https://drive.google.com/uc?export=view&id=1EZc2kEKdH5irPcjB4KwVCsuTIIZFDTFM)

### Función Lambda: [get_urls_reportes()](https://github.com/antivirusparaladesercion/AWS_backend_peopleAnalytics/blob/master/lambda_functions/lambda_get_urls_reporte.py)📎♾
_Esta función es llamada atraves de la API Gateway de AWS desde el frontend de la aplicacion web mediante metodo POST. Tiene como objetivo obtener los enlaces de descarga
de los reportes generados para una universidad especifica y que se encuentran almacenados en el bucket S3 de reportes. La funcion retornará una lista
Con la informacion de cada url generada:_
```

##Return de la funcion
return {
        'statusCode': 200,
        'body': json.dumps('Urls creadas!'),
        'data':list_urls
        
            }
            
            
#Estructura de cada elemento de list_urls
{
     'url':url,
     'file_name': key['Key'][ len(prefix_ies): ],
     'date': '{:%Y %m %d %H:%M:%S}'.format(key['LastModified'])
 }
```

_Y la forma de invocar la funcion lambda desde el frontend por medio de la API Gateway atrves de POST es de la forma:_
```
##Ejemlo del Body del request via POST

{
  "nombre_ies": "universidaddelvalle"
}

```

_Como se mencionó anteriormente el evento disparador de esta función proviene de la API Gateway, por lo cual se debe configurar desde la consola
de lambda:_
![image](https://drive.google.com/uc?export=view&id=13z9uPYhjW_o0E_qWCIvD7Z2HeENoRC5i)

_Las politicas de permisos son similar a las funciones lambdas anteriormente descritas._
## API Gateway 🔌
_Para la creacion de las APIs se hace uso del servicio API Gateway de AWS. Ingresando a la opcion **Crear API**_

### API Gateway: get-urls-report-api 
_Esta API recibirá request desde el frontend con la infor del nopmbre de la universidad que requiere los enlaces de descarga de los reportes. Y devuelve como respuesta la información de los links de descargas que luego el frontend procesará y mostrará  al usuario._
```
##Ejemlo del Body del request via POST

{
  "nombre_ies": "universidaddelvalle"
}

```

_Para para implementarla sedebe crear un nuevo metodo "**Post**" y expecificarle que el tipo de integración  sea mediante una función lambda._
![image](https://drive.google.com/uc?export=view&id=1GWw-TQkKtooM5Tv4MVz1l277zE_FTq30)

## Despliegue 📦

_Para desplegar la solución es necesario que todos los servicios usados esten encendidos, como lo es el caso del endpoint del modelo, y los buckets S3
Previamente creados._

_El proyecto se desplegó usando AWS CodePipeline para CI/CD. El front se publicó con buckets de s3 y el backend se publicó como una instancia de NodeJS en AWS ElasticBeanstalk_

_**Frontend**: Se creó un bucket en AWS S3, el cual se llama frontend-antivirus-prod, el cual se habilitó como público y se le habilitó la opción para alojar sitios web estáticos. En este se alojan los estáticos de la página._
_Se crea un flujo de trabajo en CodePipeline llamado "CiCD-frontend-antivirus-prod" En el cual se configura como source: Github, apuntando a este repositorio, para esto es necesario tener acceso al proyecto como administrador. En la etapa de Build, se configura a AWS CodeBuild como proveedor de compilación y se crea un proyecto de compilación nuevo, este usa una máquina con Linux AWS en su ultima versión. y En la etapa de deploy se selecciona el bucket de S3 creado con anterioridad para hacer el deploy_

_**Backend**: Para este se crean un flujo de trabajo en CodePipeline llamado "CiCD-backend-antivirus-dev", en el cual se configura como fuente, el repositorio backend_peopleAnalytics. Para la etapa de deploy es necesario haber creado previamente una instancia de AWS Elastic Beanstalk configurada con NodeJS en su versión 12, y con un código de muestra. Para así al momento de seleccionar una instancia de Beanstalk, hacerlo con la que se tenía ya creada.  En este no hay etapa de compilación. Una vez terminado el proceso, este arroja el Endpoint al cual se deben hacer las peticiones HTTP._

## Construido con 🛠️

_Estos fueron los servicios utilizados en la parte de aws:_

* [AWS Sagemaker](https://docs.aws.amazon.com/es_es/sagemaker/?id=docs_gateway) - Entrenamiento del modelo.
* [AWS Lambda](https://docs.aws.amazon.com/es_es/lambda/?id=docs_gateway) - Logica de la solución.
* [AWS S3](https://docs.aws.amazon.com/es_es/s3/?id=docs_gateway) - Almacenamiento.
* [API Gateway](https://docs.aws.amazon.com/es_es/apigateway/?id=docs_gateway) - Creación de API.
* [AWS SES](https://docs.aws.amazon.com/es_es/ses/?id=docs_gateway) - Servicio de Email Simple.
* [AWS CodePipeline](https://aws.amazon.com/es/codepipeline/) - Automatización de Pipelines de entrega continua.
* [AWS Elastic Beanstalk](https://aws.amazon.com/es/elasticbeanstalk/) - Servicio de PaaS.
* [AWS CodeBuild](https://aws.amazon.com/es/codebuild/) - Compilación de código con escalado continuo.


## Autores ✒️

* **Arcangel Marin** - *Desarrollo* - *Documentación* -  [ArcangelM](https://github.com/ArcangelM)
* **Equipo Antivirus para la deserción**

## Licencia 📄

Este proyecto está bajo la Licencia ().

## Expresiones de Gratitud 🎁
* Comenta a otros sobre este proyecto y anímate a contribuir📢
*Gracias a todo el equipo de Antivirus para la deserción




---

