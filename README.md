# nime-zenodo-upload

This Python project is for uploading NIME proceedings to Zenodo for archiving submissions and generating DOIs.

> **DANGER!** Uploading and publishing to Zenodo should only happen ONCE for each proceedings entry. You **must** test the script using Zenodo's sandbox multiple times and make super sure that your metadata records (`.bib` file) are absolutely correct before uploading to production Zenodo.

The python script reads a `.bib file` as used for the [NIME archive](https://github.com/NIME-conference/NIME-bibliography) and creates a deposition record on the [Zenodo website](https://zenodo.org/communities/nime_conference/). 

The metadata from the .bib entries are tied to the article (.pdf file) and are published to Zenodo resulting in the creation of a DOI. 

When this script is used to upload a new batch of papers the DOI and file name of each paper are added to the text file `nime_dois.txt`.

This project uses [Poetry](https://python-poetry.org) to manage dependencies.

For the proceedings chair of the conference, your workflow should be:

1. (before the conference) make sure **all** camera-ready submissions for each track are correct and hassle authors to update if there are errors---do this before the conference and emphasise that submissions cannot be updated after the conference.
2. (after the conference) create an accurate spreadsheet for all submissions that should be in the proceedings for each track. Create a `.bib` file from these data following the format in the [NIME bibliography](https://github.com/NIME-conference/NIME-bibliography). All fields must be filled in except for `doi`.
3. put the `.bib` file and pdf submission files into the `upload` directory of this project.
4. follow the "Install" and "Run" instructions below and test multiple times with the Zenodo sandbox to make sure that your metadata is correct and working.
5. upload to production Zenodo. The output file `nime_dois.txt` will show the DOI for each pdf you have uploaded.

Then you can pass the `nime_dois.txt` file to the proceedings officer of NIME who will:

6. use the data from `nime_dois.txt` to make a `.csv` file associating each bibtex item key with the DOI.
7. use the `nime_bib` program in the [bibliography repo](https://github.com/NIME-conference/NIME-bibliography) to add DOIs to the correct bib file using the `csv` created in step 6.
8. use the `get_publications` script on the NIME website repo and deploy the website to update with DOIs.

## Install:

You can install the project by running:

    poetry install

## Run:

You can test run the program by running:

    poetry run python nime_zenodo_upload --help

To run the program you will need to:

- place all pdfs to be uploaded into the `upload` directory
- find your bibtex file (e.g., `nime2036_music.bib`)  with metadata for the PDFs
- place a file named `secrets.toml` in the same directory as this readme file. The `secrets.toml` file should have two records:


      PUBLIC_TOKEN = 'replace-with-your-zenodo-public-token'
      SANDBOX_TOKEN = 'replace-with-your-zenodo-sandbox-token'


Once you have your data in place, you can view the metadata that will be created (without uploading) by running:

    poetry run python nime_zenodo_upload check upload/nime2036_music.bib

It's a good idea to check the author names carefully as they may have been processed incorrectly:

    poetry run python nime_zenodo_upload check upload/nime2036_music.bib --authors

Typically you would run the checks many times to make sure the metadata is perfect.

When your metadata is ready you can try uploading to the sandbox server:

    poetry run python nime_zenodo_upload upload upload/nime2023_music.bib

By default, the program uploads to the Zenodo sandbox. When you are **absolutely ready to commit to the production server** you can run:

    poetry run python nime_zenodo_upload upload upload/nime2023_music.bib --production

to do you final uploads.

## Conference Metadata

Some of the conference metadata is still hardcoded in the file, look inside `nime_zenodo_upload/__main__.py` and update the lines:

```
PUBLICATION_DATE = '2023-05-31'
CONFERENCE_DATES = '31 May - 3 June, 2023'
CONFERENCE_TITLE = 'International Conference on New Interfaces for Musical Expression'
CONFERENCE_ACRONYM = 'NIME'
```

as needed for your edition.

## Additional files

There's some commented out code for adding an addition pdf file. This needs further work. Basically it would be good to upload files referenced in the supplementary file fields:

```
  urlsuppl1 = {},
  urlsuppl2 = {},
  urlsuppl3 = {},
```

<!-- If a resource contains an additional file that should be uploaded together with the paper this additional file should have the same file name with an additional `file01` appended to the end. Zenodo displays the files alphabetically. Today this script only allows for adding one additional file per resource. -->

## The `.bib` file

The .bib file: Special characters in the .bib file should be written with UTF-8 symbols and **not** in LaTeX code. This follows the convention for the bibliography repo.

## Acknowledgements

- Thanks to [Benedikte Wallace](https://www.linkedin.com/in/benedikte-wallace-8b489782/) for developing the Zenodo upload script in 2017-2018 or so.
- Charles Martin did some work on this in 2024.
- Stefano Fasciani did some work on this in 2025.
