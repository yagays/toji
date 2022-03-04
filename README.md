# Toji - 東寺
Toji is standalone web application for collecting a large amount of voices read aloud from the manuscript efficiently.

Collect voice readings easily! All you need is the manuscripts to read out. The manuscript will appear on the screen, and then press the Record button to record the voice corresponding to the manuscript. Finally, you can download the recorded voices as a zip file.

![](docs/animation.gif)

Toji (東寺) is the name of Japanese temple. The name of this repository is derived from a phrase that appears in the lead of the first sentence of [Voice Actress Corpus](http://voice-statistics.github.io/).

## Usage
### Start-up
You can use docker,

```shell
$ docker build -t toji .
$ docker run -p 8501:8501 --rm -t -i toji
```

or start locally.

```shell
$ poetry install
$ poetry run streamlit run toji/app.py
```

And access to [http://localhost:8501/](http://localhost:8501/)

### Use Web App

1. Prepare the manuscripts with line breaks and paste it into the text area.
2. Press `START` button to start recording.
3. When you have finished reading, press the `STOP` button.
4. Press `Next` to move on to the next utterance.
5. When all tasks are finished, click `Proceed to Download` button to download the wav files.

