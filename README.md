# Zenodo-upload

The python script in the Zenodo folder (NIME_upload.py) reads a .bib file from the [NIME archive](https://github.com/NIME-conference/NIME-bibliography) and creates a deposition record on the [Zenodo website](https://zenodo.org/communities/nime_conference/). The metadata from the .bib entries are tied to the article (.pdf file) and are published to Zenodo resulting in the creation of a DOI. When this script is used to upload a new batch of papers the DOI and file name of each paper are added to the text file [NIME_dois.txt](Zenodo/NIME_dois.txt).

- Run: Place script in the directory which contains the .bib file and all .pdf's. Then run using 'python NIME_upload.py'
- Additional files: If a resource contains an additional file that should be uploaded together with the paper this additional file should have the same file name with an additional file01 appended to the end. Zenodo displays the files alphabetically. Today this script only allows for adding one additional file per resource.
- The .bib file: Special charachters in the .bib file should be written in LaTeX code.

Thanks to [Benedikte Wallace](https://www.linkedin.com/in/benedikte-wallace-8b489782/) for developing the Zenodo upload script. 
