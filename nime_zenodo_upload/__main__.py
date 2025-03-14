########################################################
'''
Written by Benedikte Wallace, 2018, edited by Charles Martin, 2024, and Stefano Fasciani 2025.

This script reads .bib files in NIME archive and creates a deposition record 
on the Zenodo website. The metadata from the .bib entries are tied to the 
article (.pdf file) and are publishedd to Zenodo resulting in the creation 
of a DOI. When this script is used to upload a new batch of papers the DOI
and file name of each paper are added to the text file nime_dois.txt. 

Additional files:

If a resource contains supplementary files that should be uploaded together with the paper this 
additional file should have the same file name with an additional _file01 _file02 etc.  appended to the end.
Uploading files larger than 100 MB may fail (workaround: rename them to skip the automatic upload, then
upload them manually) - TODO, handle upload fail exception renaming file. 
Zenodo displays the files alphabetically.

The .bib file:

Special characters in the .bib file should be written in UTF-8 symbols (not latex code).
'''
########################################################


import json
import requests
import datetime
#import latexcodec # TODO: remove this.
import click
import os
import tomllib
import pprint

from pybtex.database.input import bibtex

# Bibtex parser
parser = bibtex.Parser()

UPLOAD_FOLDER = './upload/'
PUBLICATION_DATE = '2025-03-14'
CONFERENCE_DATES = '4 September - 6 September, 2024'
CONFERENCE_TITLE = 'International Conference on New Interfaces for Musical Expression'
CONFERENCE_ACRONYM = 'NIME'

# New dois and file names are appended to the text file nime_dois.txt 
DOI_FILENAME = "nime_dois.txt"
# Add date and time for this upload
with open(DOI_FILENAME, 'a') as doi_file:
    doi_file.write(datetime.datetime.now().strftime("Uploaded %Y-%m-%d %H:%M \n"))

# Tokens, replace with public and sandbox tokens from Zenodo: 
with open("secrets.toml", "rb") as f:
    secret_data = tomllib.load(f)


def upload_to_zenodo(metadata, pdf_path, production_zenodo=False):
  ''' 
  upload(metadata, pdf_path):
  - connects to zenodo REST API, 
  - creates a new record, 
  - enters metadata, 
  - uploads the .pdf and supplementary files
  - publishes it
  '''

  if production_zenodo:
    ZENODO_URL = 'https://zenodo.org'
    TOKEN = secret_data['PUBLIC_TOKEN'] # either SANDBOX_TOKEN or PUBLIC_TOKEN
  else:
    ZENODO_URL = 'https://sandbox.zenodo.org'
    TOKEN = secret_data['SANDBOX_TOKEN']

  click.secho(f"Starting new upload for: {pdf_path} to {ZENODO_URL}", fg='yellow')
  url = ZENODO_URL + '/api/deposit/depositions'
  access_depositions = requests.get(url, params={'access_token': TOKEN})
  click.secho(f"Access depositions: {access_depositions.status_code}", fg='yellow')
  # Create new paper submission - add parsed metadata
  headers = {"Content-Type": "application/json"}
  new_deposition = requests.post(url,params={'access_token': TOKEN}, json=metadata, headers=headers)

  # If creation of new deposition is unsuccessful, abort
  if new_deposition.status_code > 210:
    click.secho("Error happened during submission {}, status code: ".format(pdf_path) + str(new_deposition.status_code), fg='red')
    click.secho(new_deposition.json(), fg='red')
    return

  submission_id = json.loads(new_deposition.text)["id"]

  # Upload the pdf file
  url = ZENODO_URL+"/api/deposit/depositions/{id}/files?access_token={token}".format(id=str(submission_id), token=TOKEN)
  upload_metadata = {'filename': pdf_path}
  with open(UPLOAD_FOLDER + pdf_path, 'rb') as pdf_file:
    add_file = requests.post(url, data=upload_metadata, files={'file': pdf_file}) # attempt to add files to record

  # If upload of file is unsuccessful, abort
  if add_file.status_code > 210:
    click.secho("Error happened during file upload, status code: " + str(add_file.status_code), fg='red')
    click.secho(add_file.json(), fg='red')
    return

  all_files = os.listdir(UPLOAD_FOLDER)
  pdf_fname = pdf_path[:-4]+"_"
  matching_files = [file for file in all_files if file.startswith(pdf_fname)]
  for extra_file_path in matching_files:
    if extra_file_path != pdf_path:
      
      click.secho(f"Starting upload for supplementary file: {extra_file_path} to {ZENODO_URL}", fg='yellow')
      upload_metadata = {'filename': extra_file_path}
      with open(UPLOAD_FOLDER + extra_file_path, 'rb') as extra_file:
        add_file = requests.post(url, data=upload_metadata, files={'file': extra_file}) # attempt to add files to record
        
        # If upload of file is unsuccessfull, abort
        if add_file.status_code > 210:
          click.secho("Error happened during file upload, status code: " + str(add_file.status_code), fg='red')
          click.secho(add_file.json(), fg='red')
          return
        
  click.secho(f"{pdf_path} submitted with ID {submission_id}", fg='green')
  
  # publish the new deposition
  publish_record = requests.post(ZENODO_URL+'/api/deposit/depositions/%s/actions/publish' % submission_id,params={'access_token': TOKEN})
  # If publish unsuccessful, abort
  if publish_record.status_code > 210:
    click.secho("Error happened during file upload, status code: " + str(publish_record.status_code), fg='red')
    click.secho(publish_record.json(), fg='red')
    return
  click.secho(f"{pdf_path} PUBLISHED with ID {submission_id}", fg='green')

  # get back the deposition to confirm the DOI (it's usually/always the submission ID but good to be sure)
  retrieved_deposition = requests.get(f"{ZENODO_URL}/api/deposit/depositions/{submission_id}", params={'access_token': TOKEN})
  retrieved_doi = retrieved_deposition.json()['doi']
  click.secho(f"{pdf_path} confirmed DOI is {retrieved_doi}", fg='green')

  # Record in the csv file.
  with open(DOI_FILENAME, 'a') as doi_file:
    doi_file.write(f'{pdf_path},{submission_id},{retrieved_doi}\n')



def format_metadata(bibfilename, verbose=False, upload_pdf=False, print_authors=False, production_zenodo=False):
  ''' 
  format_metadata(bibfilename):
  - formats contents of entries in the .bib file referenced by bibfilename
  - for each entry, metadata is formatted and the upload function 
  above is called in order to publish record
  '''
  bibdata = parser.parse_file(bibfilename)

  title = 'title'
  abstract = 'abstract'
  address = 'address'
  creators = 'creators'
  pubdate = '20XX-06-01'
  pages = 'x-x'
  conf_url = ''
  pdf_name = ''
  creators = []

  #loop through the individual entries
  for bib_id in bibdata.entries:
    title = 'title'
    abstract = 'abstract'
    address = 'address'
    creators = 'creators'
    pubdate = '20XX-06-01'
    pages = 'x-x'
    conf_url = ''
    pdf_name = ''
    creators = []

    b = bibdata.entries[bib_id].fields
    try:
      conf_url = b['Url']
      pdf_name = conf_url.rsplit('/', 1)[-1]

      if not os.path.exists(UPLOAD_FOLDER + pdf_name):
        click.secho(f'PDF: {pdf_name} does not exist in the upload folder!', fg='red')
        raise Exception(f'The PDF {pdf_name} did not exist in the upload folder.')

      title = b['Title']
      for author in bibdata.entries[bib_id].persons["Author"]:
        author_name = str(author) 
        # TODO: would be better to use https://github.com/phfaist/pylatexenc for decoding latex characters
        # author_name = bytes(author_name,"utf-8").decode("latex","ignore") # TODO: this decoding scheme works for Latex encoded special characters but not UTF-8 which is the current norm.
        author_name = author_name.replace("}","")
        author_name = author_name.replace("{","")
        author_name = author_name.replace("\\\"","")
        creators.append({'name': author_name})
        if print_authors:
          pprint.pp(author_name)

      yr_seg = conf_url.rsplit('/', 1)[-2]
      yr = yr_seg.rsplit('/', 1)[-1]
      pubdate = yr + pubdate[4:]

      address = b.get('Address', 'Address')
      pages = b.get('Pages', None)
      abstract = b.get('Abstract', '---') # if no abstract is found, --- will be used as default
      track = b.get('track') # could be used for conference_session key
      partof_title = b.get('booktitle')
      conf_session = b.get('note', None)
      isbn = b.get('isbn')
      issn = b.get('issn')

      data = {
      'metadata': {
      'title': title, 
      'upload_type': 'publication', 
      'publication_type' : 'conferencepaper',
      'description': abstract,
      'conference_title':CONFERENCE_TITLE,
      'conference_acronym':CONFERENCE_ACRONYM,
      'conference_dates': CONFERENCE_DATES, # hard coded, needs to be fixed
      'conference_place': address,
      'conference_url':'https://nime.org',
      'publication_date' : PUBLICATION_DATE, # pubdate, # TODO fix this aspect
      'partof_title' : partof_title,
      'creators': creators,
      'communities': [{'identifier': 'nime_conference'}], # adds the record to the zenodo NIME community
      'imprint_isbn': isbn,
      'journal_issn': issn
      }}

      if conf_session is not None:
        data['metadata']['conference_session'] = conf_session

      if pages is not None:
        data['metadata']['partof_pages'] = pages 

      if verbose:
        pprint.pp(data['metadata'])
      
      if upload_pdf:
        upload_to_zenodo(data, pdf_name, production_zenodo=production_zenodo)

    except(KeyError): # TODO Write failed bib ID's to a text file?
      print("KeyError! Entry did not contain fields needed, continuing to next id - failed bib id: ", bib_id)
      raise


@click.command()
@click.argument('bibfile', type=click.Path(exists=True))
@click.option('--production', is_flag=True)
def upload(bibfile, production):
  """Process metadata from a .bibtex file and upload to Zenodo."""
  # Bibtex file to be used for the upload
  # bibfile = UPLOAD_FOLDER + 'zenodo.bib'
  if production:
    click.secho("WARNING! You are uploading to the production Zenodo server! Make sure you are ready! Cancel if not!", fg="red")
  else:
    click.secho("You are uploading to the sandbox Zenodo server! Test here as much as you want.", fg="green")
  wait = input("Press Enter to continue or Ctrl-C to abort.")
  format_metadata(bibfile, upload_pdf=True, verbose=False, print_authors=False, production_zenodo=production)


@click.command()
@click.argument('bibfile', type=click.Path(exists=True))
@click.option('--authors', is_flag=True)
def check(bibfile, authors):
  """Process metadata from a .bibtex file and print out to check it."""
  # bibfile = UPLOAD_FOLDER + 'zenodo.bib'
  if authors:
    format_metadata(bibfile, upload_pdf=False, verbose=False, print_authors=True, production_zenodo=False)
  else:
    format_metadata(bibfile, upload_pdf=False, verbose=True, print_authors=False, production_zenodo=False)


@click.group()
def cli():
  pass


if __name__ == '__main__':
  cli.add_command(upload)
  cli.add_command(check)
  cli()
