@REM extrait les chaines à traduire
@REM --sort-output         generate sorted output (default False)
@REM --sort-by-file        sort output by file location (default False)
@REM --version=VERSION     set project version in output
pybabel extract -F babel\babel.cfg -k gettext -k _gettext -k _ngettext -k lazy_gettext -k _ -o babel\mongrey.pot --project Greylist-Server mongrey

@REM créé un fichier pour traduire en Français
@REM pybabel init -i babel\mongrey.pot -d mongrey\translations -l fr

@REM met à jour les nouvelles chaines
pybabel update -i babel\mongrey.pot -d mongrey\translations

@REM compile les fichiers de traductions
@REM dans les .po, enlever la chaine #, fuzzy avant de compiler
@REM -l LOCALE, --locale=LOCALE
@REM -f, --use-fuzzy 
pybabel compile -d mongrey\translations --statistics

