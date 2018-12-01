# Predatory Battle
MIT License

This is a little script in python which takes as input a bibtex/biblatex file and tries to recognize predatory publications.

It maintains a list of predatory sources from:
* https://predatoryjournals.com/journals/
* https://beallslist.weebly.com/
* https://beallslist.weebly.com/standalone-journals.html
* https://docs.google.com/spreadsheets/d/1Y_Sza4rPDkf-NNX9kwiErGrKeNTM75md9B63A_gVpaQ/
* https://libguides.caltech.edu/c.php?g=512665&p=3503029

It checks if journals, books or conferences are present in such lists.

WARNING! The script is highly imprecise and should be used as a helper to human force. You should careful check suggestions coming from the script!

## Installation

* Download the repository
* Install the following modules with your package manager or (not recommended) with `pip`: 
    `pip3 install --upgrade fuzzywuzzy latexcodec requests`

## Usage

* Download the repository
* Enter in the directory: `cd PredatoryBattle`
* Launch the script with a bibtex/biblatex file as argument: `python3 check_references.py bibtex_file.bib`