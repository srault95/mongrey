

@REM sphinx-build -v -N -w _build/errors-fr.log -d _build/doctrees_fr -b html docs/fr _build/html/fr

sphinx-build -a -v -N -w docs/_build/errors-fr.log -b html docs/docs/fr docs/_build/html/fr
sphinx-build -a -v -N -w docs/_build/errors-en.log -b html docs/docs/en docs/_build/html/en

sphinx-build -a -v -N -b changes docs/docs/fr docs/_build/html/fr/changes


python -m SimpleHTTPServer 8000

#firefox http://127.0.0.1:8080/your_project_name/