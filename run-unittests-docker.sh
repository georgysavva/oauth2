#!/usr/bin/env bash
docker run -it --rm oauth2-server pytest
docker run -it --rm resource-server pytest
docker run -it --rm webapp pytest

