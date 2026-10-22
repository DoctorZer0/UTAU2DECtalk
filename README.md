# UTAU2DECtalk

Converts UTAU `.ust` files into DECtalk singing strings and renders them to a WAV with [DECtalk](https://github.com/dectalk/dectalk).

Both CV and VCV UST files are supported. Lyrics can be hiragana or romaji.

## Setup

Requires Python 3 (no extra packages). To get DECtalk on Linux, run the included script:

```bash
bash get_dectalk.sh
mkdir -p project
```

By default, the `say` binary is expected at `./dectalk/say` and output goes to `project/`.

## Usage

```bash
python src/main.py song.ust
```

```
usage: main.py [-h] [-s DECTALK_STRING_PATH] [-p DEFAULT_PREUTTERANCE]
               [-o WAV_PATH] [-b BINARY_PATH]
               ust_filepath
```

| Argument | Description | Default |
|---|---|---|
| `ust_filepath` | Source `.ust` file (Shift-JIS) | required |
| `-s` | Where the DECtalk string is written | `project/temp.txt` |
| `-p` | Default pre-utterance in ms | `40` |
| `-o` | Output WAV file | `project/result.wav` |
| `-b` | Path to the DECtalk `say` binary | `dectalk/say` |

## Notes

- Lyrics not found in `phoneme_map.py` are replaced with rests. Add your own entries there as `[consonant, glide, vowel]`.
- Timing is not perfect. You will likely need to slightly adjust the start of some parts afterwards to get correct timing.
- Pitch bending and enveloping are not implemented.
- Mid-song tempo changes are ignored.

## License

MIT