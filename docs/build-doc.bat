

sphinx-build -v -N -w docs/_build/errors-fr.log -d docs/_build/doctrees_fr -b html docs/docs/fr docs/_build/html/fr

sphinx-build -v -N -w docs/_build/errors-en.log -d docs/_build/doctrees_en -b html docs/docs/en docs/_build/html/en

python -m SimpleHTTPServer 8000
