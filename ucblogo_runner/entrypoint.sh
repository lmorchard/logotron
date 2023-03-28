#!/bin/sh
TIMEOUT=15
WIDTH=800
HEIGHT=600
TRIM_DURATION=1.5

export DISPLAY=:42

echo -n "Starting Xvfb..."
Xvfb "${DISPLAY}" -listen tcp -nocursor -screen 0 ${WIDTH}x${HEIGHT}x24 &
PID_XVFB=$!
echo " PID ${PID_XVFB}"

# https://unix.stackexchange.com/a/418903
MAX_ATTEMPTS=120 # About 60 seconds
COUNT=0
echo -n "Waiting for Xvfb to be ready..."
while ! xdpyinfo -display "${DISPLAY}" >/dev/null 2>&1; do
  echo -n "."
  sleep 0.05s
  COUNT=$(( COUNT + 1 ))
  if [ "${COUNT}" -ge "${MAX_ATTEMPTS}" ]; then
    echo "  Gave up waiting for X server on ${DISPLAY}"
    exit 1
  fi
done
echo " ready!"

echo -n "Starting ucblogo..."
/logo/ucblogo &
PID_LOGO=$!
echo " PID ${PID_LOGO}"

echo -n "Looking for ucblogo window..."
MAX_ATTEMPTS=120
COUNT=0
while true
do
  WID_LOGO=$(xdotool search --onlyvisible --pid ${PID_LOGO})
  if [ -n "$WID_LOGO" ]; then
    break
  fi
  echo -n "."
  sleep 0.05s
  COUNT=$(( COUNT + 1 ))
  if [ "${COUNT}" -ge "${MAX_ATTEMPTS}" ]; then
    echo "  Gave up waiting for ucblogo window"
    exit 1
  fi
done
echo " WID ${WID_LOGO}"

echo -n "Maximizing ucblogo window..."
xdotool mousemove 0 0
xdotool windowmove $WID_LOGO 0 0
xdotool windowsize $WID_LOGO $WIDTH $HEIGHT 
echo " maximized!"

# https://malinowski.dev/recording-headless-selenium-tests-to-mp4.html
echo -n "Starting recording..."
tmux new-session -d -s Recording 'ffmpeg -hide_banner -loglevel info -video_size 800x600 -f x11grab -i :42 -codec:v libx264 -r 30 /output/raw.mp4 2>&1 >/output/ffmpeg.log'
MAX_ATTEMPTS=120
COUNT=0
until [ -f /output/raw.mp4 ]
do
  echo -n "."
  sleep 0.05s
  COUNT=$(( COUNT + 1 ))
  if [ "${COUNT}" -ge "${MAX_ATTEMPTS}" ]; then
    echo "  Gave up waiting for recording to start"
    exit 1
  fi
done
echo " started!"

echo -n "Loading input program..."
xdotool type --window $WID_LOGO 'load "/input/program' 2>/dev/null
xdotool key --window $WID_LOGO Return 2>/dev/null
echo " done!"

echo -n "Waiting for ucblogo to exit..."
timeout $TIMEOUT tail --pid=$PID_LOGO -f /dev/null
echo " done!"

echo -n "Ending recording..."
tmux send-keys -t Recording q
sleep 2
echo " ended"

echo -n "Trimming video..."
duration=$(ffprobe -i /output/raw.mp4 -show_entries format=duration -v quiet -of csv="p=0")
trim=$(echo ${duration}-${TRIM_DURATION} | bc)
ffmpeg -hide_banner -loglevel error -t $trim -i /output/raw.mp4 -c copy /output/output.mp4 2>&1 >>/output/ffmpeg.log
echo " done!"

echo -n "Cleaning up processes..."
kill $PID_LOGO $PID_XVFB 2>/dev/null
echo " done!"
