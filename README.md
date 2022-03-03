# Toji - 東寺
Toji is standalone web application that collect a lot of speech audio efficiently.

![](docs/animation.gif)

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

### Use Web App

1. Prepare the speech texts with line breaks and paste it into the text area.
2. Press `START` button to start recording
3. When you have finished speaking, press the `STOP` button
4. Press `Next` to move on to the next utterance.
5. When all tasks are finished, click `Proceed to Download` button to download the wav files.

