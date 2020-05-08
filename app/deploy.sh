#!/bin/bash
gcloud config set account abc@sophize.org && \
gcloud config set project sophize-machines && \
gcloud app deploy
