# Color Palette Changer

![Color Palette Changer Preview](https://raw.githubusercontent.com/Chatr0uge/ThemeChanger/main/image/cp.png)

Color Palette Changer is an automated and configurable tool for parsing files, analyzing color data, and replacing color palettes. It can use a given palette or create a palette from an image.

Then the possibility for customizations infite and it's up to you to decide which directory you want to customize with your own color palette or from an image colors.

## Installation

You can install the latest release version of Color Palette Changer:

```bash
pip install theme-changer
# pip install --upgrade color-palette-changer  # To upgrade in case a new version is released.
```

## Preview

Here is a preview of what the Color Palette Changer can do:

![Color Palette Changer Preview](path_to_image)

## Usage

You can run the script from the command line like this:

```bash
python FILE_handler.py --dir_path /path/to/dir --replace_directory /path/to/replace/dir --extensions .txt .docx .pdf --path_image /path/to/image.jpg --replace True
```

Or this:

```bash
python FILE_handler.py --dir_path /path/to/dir --replace_directory /path/to/replace/dir --extensions .txt .docx .pdf --palette #FFFFFF #000000 #FF0000 --replace False
```

## CLI parameter

The following parameter are avalaible for the cli :

- -h, --help show this help message and exit

- --path PATH The directory or file path to process

- --replace_path REPLACE_PATH
  The directory to replace

- --extensions EXTENSIONS [EXTENSIONS ...]
  The file extensions to process

- --palette PALETTE The palette to use for the file

- --image IMAGE The path to image to use for the palette

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

MIT
