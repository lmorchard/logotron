# logotron

A bot that wants to help you play with Logo

## Installation

```
docker build -t lmorchard/logotron:latest .
cd ucblogo-runner
docker build -t lmorchard/ucblogo-runner .
cd ..
```

## Configuration

TBD

## Usage

```
docker run --privileged \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-v `pwd`/log:/app/log \
	-v `pwd`/data:/app/data \
	lmorchard/logotron:latest
```
