import kopf
import logging
from kubernetes import client

@kopf.on.create('simple-app')
def create_fn(spec, name, namespace, **kwargs):
    logging.info(f'Creating `simple-app` named {name} in namespace {namespace}...')
    image = spec.get('image')
    replicas = spec.get('replicas')
    create_service_deployment(name, namespace)
    create_deployment(name, namespace, image, replicas)
    logging.info(f'Simple App: {name} created in namespace {namespace}!')

@kopf.on.delete('simple-app')
def delete_fn(spec, name, namespace, **kwargs):
    logging.info(f'Deleting `simple-app` named {name} in namespace {namespace}...')
    delete_deployment(name, namespace)
    delete_service_deployment(name, namespace)
    logging.info(f'Simple App: {name} deleted in namespace {namespace}!')

def create_service_deployment(app_name, namespace):
    api = client.CoreV1Api()    
    spec = client.V1ServiceSpec(
        selector={"simple-app": app_name},
        ports=[client.V1ServicePort(port=80, target_port=8080)],
        type="ClusterIP"
    )
    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name=f"{app_name}-simple-service"),
        spec=spec
    )
    api_response = api.create_namespaced_service(
        namespace=namespace,
        body=service
    )
    logging.info("Service created. status='%s'" % api_response.status)

def delete_service_deployment(app_name, namespace):
    api = client.CoreV1Api()    
    api_response = api.delete_namespaced_service(
        name=f"{app_name}-simple-service",
        namespace=namespace,
        body=client.V1DeleteOptions()
    )
    logging.info("Service deleted. status='%s'" % str(api_response.status))

def delete_deployment(app_name, namespace):
    api = client.AppsV1Api()
    deployment_name = f'{app_name}-simple-deployment'
    api_response = api.delete_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
        )
    )
    logging.info("Deployment deleted. status='%s'" % str(api_response.status))

def create_deployment(app_name, namespace, image, replicas):
    container = client.V1Container(
        name=f'{app_name}-simple-container',
        image=image
    )
    pod_template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={'simple-app': app_name}),
        spec=client.V1PodSpec(containers=[container])
    )
    spec = client.V1DeploymentSpec(
        replicas=replicas,
        template=pod_template,
        selector={'matchLabels': {'simple-app': app_name}}
    )
    deployment = client.V1Deployment(
        api_version='apps/v1',
        kind='Deployment',
        metadata=client.V1ObjectMeta(name=f'{app_name}-simple-deployment'),
        spec=spec
    )
    api = client.AppsV1Api()
    api_response = api.create_namespaced_deployment(
        body=deployment,
        namespace=namespace
    )
    logging.info("Deployment created. status='%s'" % str(api_response.status))
