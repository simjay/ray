#!/usr/bin/env python

import click
import os
from watchgod import watch
from ray.serve.config import DeploymentMode
from ray.serve.util import logger

import ray
from ray import serve
from ray.serve.constants import DEFAULT_HTTP_HOST, DEFAULT_HTTP_PORT


@click.group(
    help="[EXPERIMENTAL] CLI for managing Serve instances on a Ray cluster.")
@click.option(
    "--address",
    "-a",
    default="auto",
    required=False,
    type=str,
    help="Address of the running Ray cluster to connect to. "
    "Defaults to \"auto\".")
@click.option(
    "--namespace",
    "-n",
    default="serve",
    required=False,
    type=str,
    help="Ray namespace to connect to. Defaults to \"serve\".")
def cli(address, namespace):
    ray.init(address=address, namespace=namespace)


@cli.command(help="Start a detached Serve instance on the Ray cluster.")
@click.option(
    "--http-host",
    default=DEFAULT_HTTP_HOST,
    required=False,
    type=str,
    help="Host for HTTP servers to listen on. "
    f"Defaults to {DEFAULT_HTTP_HOST}.")
@click.option(
    "--http-port",
    default=DEFAULT_HTTP_PORT,
    required=False,
    type=int,
    help="Port for HTTP servers to listen on. "
    f"Defaults to {DEFAULT_HTTP_PORT}.")
@click.option(
    "--http-location",
    default=DeploymentMode.HeadOnly,
    required=False,
    type=click.Choice(list(DeploymentMode)),
    help="Location of the HTTP servers. Defaults to HeadOnly.")
def start(http_host, http_port, http_location):
    serve.start(
        detached=True,
        http_options=dict(
            host=http_host,
            port=http_port,
            location=http_location,
        ))


@cli.command(help="Shutdown the running Serve instance on the Ray cluster.")
def shutdown():
    serve.connect().shutdown()


@cli.command(
    help="Run and reload a deployment script for development purposes.")
@click.option(
    "--filepath",
    required=True,
    type=str,
    help="Filepath for a deployment script")
@click.option(
    "--verbose",
    default=True,
    required=False,
    type=bool,
    help="Enable verbose mode.")
def run(filepath, verbose):
    for _ in watch(filepath):
        if verbose:
            logger.info("Deployment script is modified. Redeploying...\n")
        os.system(f"python {filepath}")
